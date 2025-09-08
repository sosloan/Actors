const feathers = require('@feathersjs/feathers');
const express = require('@feathersjs/express');
const socketio = require('@feathersjs/socketio');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express(feathers());
// CORS: expose APIs broadly
const corsOptions = {
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
};
app.use(cors(corsOptions));
app.options('*', cors(corsOptions));
app.use(express.json());
app.configure(express.rest());
app.configure(socketio());

// Configuration
const CONFIG = {
  DATA_FILE: path.join(__dirname, '..', 'data', 'metrics.json'),
  HISTORY_FILE: path.join(__dirname, '..', 'data', 'metrics_history.json'),
  MAX_HISTORY: 1000,
  UPDATE_INTERVAL: 3000,
  SAVE_INTERVAL: 60000
};

// Thresholds for alerting
const THRESHOLDS = {
  carbonFootprint: { min: 100, max: 200, unit: 'kg CO2' },
  waterSavings: { min: 20, max: 50, unit: 'liters' },
  energyEfficiency: { min: 70, max: 100, unit: '%' },
  confidence: { min: 80, max: 100, unit: '%' },
  waterdruckPsi: { min: 30, max: 80, unit: 'PSI' }
};

// In-memory metrics
let metrics = {
  carbonFootprint: 150.5,
  waterSavings: 30.2,
  energyEfficiency: 85.7,
  confidence: 92.4,
  waterdruckPsi: 62.0
};

// Historical data storage
let metricsHistory = [];

// Ensure data directory exists
async function ensureDataDirectory() {
  const dataDir = path.dirname(CONFIG.DATA_FILE);
  try {
    await fs.mkdir(dataDir, { recursive: true });
  } catch (error) {
    console.error('Error creating data directory:', error);
  }
}

// Load metrics from file
async function loadMetrics() {
  try {
    const data = await fs.readFile(CONFIG.DATA_FILE, 'utf8');
    const parsed = JSON.parse(data);
    if (parsed.metrics) {
      metrics = { ...metrics, ...parsed.metrics };
      console.log('Loaded metrics from file');
    }
  } catch (error) {
    console.log('No existing metrics file found, using defaults');
  }
}

// Save metrics to file
async function saveMetrics() {
  try {
    const data = {
      timestamp: new Date().toISOString(),
      metrics
    };
    await fs.writeFile(CONFIG.DATA_FILE, JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Error saving metrics:', error);
  }
}

// Load historical data
async function loadHistory() {
  try {
    const data = await fs.readFile(CONFIG.HISTORY_FILE, 'utf8');
    metricsHistory = JSON.parse(data);
    console.log(`Loaded ${metricsHistory.length} historical records`);
  } catch (error) {
    console.log('No existing history file found, starting fresh');
    metricsHistory = [];
  }
}

// Save historical data
async function saveHistory() {
  try {
    await fs.writeFile(CONFIG.HISTORY_FILE, JSON.stringify(metricsHistory, null, 2));
  } catch (error) {
    console.error('Error saving history:', error);
  }
}

// Check thresholds and generate alerts
function checkThresholds(currentMetrics) {
  const alerts = [];
  
  for (const [key, value] of Object.entries(currentMetrics)) {
    if (THRESHOLDS[key]) {
      const threshold = THRESHOLDS[key];
      if (value < threshold.min || value > threshold.max) {
        const severity = value < threshold.min * 0.8 || value > threshold.max * 1.2 ? 'critical' : 'warning';
        alerts.push({
          metric: key,
          value,
          threshold,
          severity,
          message: `${key} is ${value} ${threshold.unit} (${severity === 'critical' ? 'CRITICAL' : 'WARNING'}: outside ${threshold.min}-${threshold.max} range)`,
          timestamp: new Date().toISOString()
        });
      }
    }
  }
  
  if (alerts.length > 0) {
    console.log('Alerts generated:', alerts);
    app.io.emit('alerts', alerts);
  }
  
  return alerts;
}

// REST endpoints
app.get('/metrics', (_req, res) => {
  res.json({
    timestamp: new Date().toISOString(),
    metrics,
    thresholds: THRESHOLDS
  });
});

// Historical metrics endpoint
app.get('/metrics/history', (_req, res) => {
  const limit = parseInt(_req.query.limit) || 100;
  const offset = parseInt(_req.query.offset) || 0;
  
  const paginatedHistory = metricsHistory
    .slice(-limit - offset, -offset || undefined)
    .reverse();
  
  res.json({
    data: paginatedHistory,
    total: metricsHistory.length,
    limit,
    offset
  });
});

// Thresholds endpoint
app.get('/thresholds', (_req, res) => {
  res.json(THRESHOLDS);
});

// Health endpoint with more details
app.get('/healthz', (_req, res) => {
  res.json({ 
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    historyRecords: metricsHistory.length
  });
});

// Route discovery
app.get('/routes', (_req, res) => {
  const routes = [];
  if (app && app._router && app._router.stack) {
    app._router.stack.forEach((middleware) => {
      if (middleware.route) {
        const path = middleware.route.path;
        const methods = Object.keys(middleware.route.methods).map((m) => m.toUpperCase());
        routes.push({ path, methods });
      } else if (middleware.name === 'router' && middleware.handle && middleware.handle.stack) {
        middleware.handle.stack.forEach((handler) => {
          if (handler.route) {
            const path = handler.route.path;
            const methods = Object.keys(handler.route.methods).map((m) => m.toUpperCase());
            routes.push({ path, methods });
          }
        });
      }
    });
  }
  res.json({
    routes,
    sockets: { path: '/socket.io', events: ['metrics'] }
  });
});

// Periodic update + broadcast
setInterval(async () => {
  const rand = () => Math.random() - 0.5;
  const previousMetrics = { ...metrics };
  
  metrics = {
    carbonFootprint: +(metrics.carbonFootprint + rand() * 2).toFixed(1),
    waterSavings: +(metrics.waterSavings + rand() * 1).toFixed(1),
    energyEfficiency: +(metrics.energyEfficiency + rand() * 0.5).toFixed(1),
    confidence: +(metrics.confidence + rand() * 0.5).toFixed(1),
    waterdruckPsi: +Math.max(20, Math.min(100, metrics.waterdruckPsi + rand() * 0.8)).toFixed(1)
  };
  
  // Add to history
  const historyEntry = {
    timestamp: new Date().toISOString(),
    metrics: { ...metrics },
    changes: Object.keys(metrics).reduce((acc, key) => {
      acc[key] = +(metrics[key] - previousMetrics[key]).toFixed(2);
      return acc;
    }, {})
  };
  
  metricsHistory.push(historyEntry);
  
  // Maintain history size
  if (metricsHistory.length > CONFIG.MAX_HISTORY) {
    metricsHistory.shift();
  }
  
  // Check for alerts
  const alerts = checkThresholds(metrics);
  
  // Emit updates
  app.emit('metrics updated', {
    timestamp: historyEntry.timestamp,
    metrics,
    changes: historyEntry.changes,
    alerts
  });
}, CONFIG.UPDATE_INTERVAL);

// Socket channel
app.on('connection', connection => app.channel('everybody').join(connection));
app.publish(() => app.channel('everybody'));

// Emit as Socket.IO custom event
app.on('metrics updated', data => {
  try {
    app.io.emit('metrics', data);
  } catch (error) {
    console.error('Error emitting metrics:', error);
  }
});

// Periodic save to disk
setInterval(async () => {
  await saveMetrics();
  await saveHistory();
  console.log('Data saved to disk');
}, CONFIG.SAVE_INTERVAL);

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');
  await saveMetrics();
  await saveHistory();
  console.log('Data saved. Goodbye!');
  process.exit(0);
});

// Initialize server
async function startServer() {
  try {
    await ensureDataDirectory();
    await loadMetrics();
    await loadHistory();
    
    const port = process.env.PORT || 3030;
    app.listen(port, () => {
      console.log(`🌿 Environmental Metrics Server running on http://localhost:${port}`);
      console.log(`📊 Tracking ${Object.keys(metrics).length} metrics with ${metricsHistory.length} historical records`);
      console.log(`🚨 Monitoring ${Object.keys(THRESHOLDS).length} thresholds for alerts`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();


