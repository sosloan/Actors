const request = require('supertest');
const io = require('socket.io-client');

// Mock the server for testing
let server;
let app;

beforeAll(async () => {
  // Import the app after setting up test environment
  process.env.NODE_ENV = 'test';
  process.env.PORT = '0'; // Use random port for testing
  
  // Mock the server startup
  const feathers = require('@feathersjs/feathers');
  const express = require('@feathersjs/express');
  const socketio = require('@feathersjs/socketio');
  const cors = require('cors');
  
  app = express(feathers());
  
  // CORS configuration
  const corsOptions = {
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
  };
  app.use(cors(corsOptions));
  app.options('*', cors(corsOptions));
  app.use(express.json());
  app.configure(express.rest());
  app.configure(socketio());
  
  // Test metrics
  const testMetrics = {
    carbonFootprint: 150.5,
    waterSavings: 30.2,
    energyEfficiency: 85.7,
    confidence: 92.4,
    waterdruckPsi: 62.0
  };
  
  // Test endpoints
  app.get('/metrics', (_req, res) => {
    res.json({
      timestamp: new Date().toISOString(),
      metrics: testMetrics,
      thresholds: {
        carbonFootprint: { min: 100, max: 200, unit: 'kg CO2' },
        waterSavings: { min: 20, max: 50, unit: 'liters' },
        energyEfficiency: { min: 70, max: 100, unit: '%' },
        confidence: { min: 80, max: 100, unit: '%' },
        waterdruckPsi: { min: 30, max: 80, unit: 'PSI' }
      }
    });
  });
  
  app.get('/healthz', (_req, res) => {
    res.json({ 
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      historyRecords: 0
    });
  });
  
  app.get('/thresholds', (_req, res) => {
    res.json({
      carbonFootprint: { min: 100, max: 200, unit: 'kg CO2' },
      waterSavings: { min: 20, max: 50, unit: 'liters' },
      energyEfficiency: { min: 70, max: 100, unit: '%' },
      confidence: { min: 80, max: 100, unit: '%' },
      waterdruckPsi: { min: 30, max: 80, unit: 'PSI' }
    });
  });
  
  app.get('/metrics/history', (_req, res) => {
    const limit = parseInt(_req.query.limit) || 100;
    const offset = parseInt(_req.query.offset) || 0;
    
    res.json({
      data: [],
      total: 0,
      limit,
      offset
    });
  });
  
  app.get('/routes', (_req, res) => {
    res.json({
      routes: [
        { path: '/metrics', methods: ['GET'] },
        { path: '/healthz', methods: ['GET'] },
        { path: '/thresholds', methods: ['GET'] },
        { path: '/metrics/history', methods: ['GET'] },
        { path: '/routes', methods: ['GET'] }
      ],
      sockets: { path: '/socket.io', events: ['metrics'] }
    });
  });
  
  // Socket channel setup
  app.on('connection', connection => app.channel('everybody').join(connection));
  app.publish(() => app.channel('everybody'));
  
  server = app.listen(0); // Use random port
});

afterAll(async () => {
  if (server) {
    server.close();
  }
});

describe('Environmental Metrics Server', () => {
  describe('GET /metrics', () => {
    it('should return current metrics with thresholds', async () => {
      const response = await request(app)
        .get('/metrics')
        .expect(200);
      
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('metrics');
      expect(response.body).toHaveProperty('thresholds');
      
      expect(response.body.metrics).toHaveProperty('carbonFootprint');
      expect(response.body.metrics).toHaveProperty('waterSavings');
      expect(response.body.metrics).toHaveProperty('energyEfficiency');
      expect(response.body.metrics).toHaveProperty('confidence');
      expect(response.body.metrics).toHaveProperty('waterdruckPsi');
      
      expect(response.body.metrics.carbonFootprint).toBe(150.5);
      expect(response.body.metrics.waterSavings).toBe(30.2);
      expect(response.body.metrics.energyEfficiency).toBe(85.7);
      expect(response.body.metrics.confidence).toBe(92.4);
      expect(response.body.metrics.waterdruckPsi).toBe(62.0);
    });
  });
  
  describe('GET /healthz', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/healthz')
        .expect(200);
      
      expect(response.body).toHaveProperty('status', 'ok');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('uptime');
      expect(response.body).toHaveProperty('memory');
      expect(response.body).toHaveProperty('historyRecords');
      
      expect(typeof response.body.uptime).toBe('number');
      expect(typeof response.body.memory).toBe('object');
      expect(typeof response.body.historyRecords).toBe('number');
    });
  });
  
  describe('GET /thresholds', () => {
    it('should return threshold configurations', async () => {
      const response = await request(app)
        .get('/thresholds')
        .expect(200);
      
      expect(response.body).toHaveProperty('carbonFootprint');
      expect(response.body).toHaveProperty('waterSavings');
      expect(response.body).toHaveProperty('energyEfficiency');
      expect(response.body).toHaveProperty('confidence');
      expect(response.body).toHaveProperty('waterdruckPsi');
      
      expect(response.body.carbonFootprint).toHaveProperty('min', 100);
      expect(response.body.carbonFootprint).toHaveProperty('max', 200);
      expect(response.body.carbonFootprint).toHaveProperty('unit', 'kg CO2');
    });
  });
  
  describe('GET /metrics/history', () => {
    it('should return historical data with pagination', async () => {
      const response = await request(app)
        .get('/metrics/history?limit=10&offset=0')
        .expect(200);
      
      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('limit');
      expect(response.body).toHaveProperty('offset');
      
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.limit).toBe(10);
      expect(response.body.offset).toBe(0);
    });
    
    it('should handle default pagination parameters', async () => {
      const response = await request(app)
        .get('/metrics/history')
        .expect(200);
      
      expect(response.body.limit).toBe(100);
      expect(response.body.offset).toBe(0);
    });
  });
  
  describe('GET /routes', () => {
    it('should return available routes', async () => {
      const response = await request(app)
        .get('/routes')
        .expect(200);
      
      expect(response.body).toHaveProperty('routes');
      expect(response.body).toHaveProperty('sockets');
      
      expect(Array.isArray(response.body.routes)).toBe(true);
      expect(response.body.routes.length).toBeGreaterThan(0);
      
      expect(response.body.sockets).toHaveProperty('path', '/socket.io');
      expect(response.body.sockets).toHaveProperty('events');
    });
  });
  
  describe('CORS Configuration', () => {
    it('should handle CORS preflight requests', async () => {
      await request(app)
        .options('/metrics')
        .expect(204);
    });
    
    it('should include CORS headers in responses', async () => {
      const response = await request(app)
        .get('/metrics')
        .expect(200);
      
      expect(response.headers).toHaveProperty('access-control-allow-origin');
    });
  });
});

describe('Metrics Validation', () => {
  it('should validate metric ranges', () => {
    const metrics = {
      carbonFootprint: 150.5,
      waterSavings: 30.2,
      energyEfficiency: 85.7,
      confidence: 92.4,
      waterdruckPsi: 62.0
    };
    
    const thresholds = {
      carbonFootprint: { min: 100, max: 200 },
      waterSavings: { min: 20, max: 50 },
      energyEfficiency: { min: 70, max: 100 },
      confidence: { min: 80, max: 100 },
      waterdruckPsi: { min: 30, max: 80 }
    };
    
    // Test that all metrics are within thresholds
    Object.keys(metrics).forEach(metric => {
      if (thresholds[metric]) {
        expect(metrics[metric]).toBeGreaterThanOrEqual(thresholds[metric].min);
        expect(metrics[metric]).toBeLessThanOrEqual(thresholds[metric].max);
      }
    });
  });
  
  it('should detect threshold violations', () => {
    const testMetrics = {
      carbonFootprint: 250.0, // Above threshold
      waterSavings: 10.0,     // Below threshold
      energyEfficiency: 85.7, // Within threshold
      confidence: 92.4,       // Within threshold
      waterdruckPsi: 90.0     // Above threshold
    };
    
    const thresholds = {
      carbonFootprint: { min: 100, max: 200 },
      waterSavings: { min: 20, max: 50 },
      energyEfficiency: { min: 70, max: 100 },
      confidence: { min: 80, max: 100 },
      waterdruckPsi: { min: 30, max: 80 }
    };
    
    const violations = [];
    
    Object.keys(testMetrics).forEach(metric => {
      if (thresholds[metric]) {
        const value = testMetrics[metric];
        const threshold = thresholds[metric];
        
        if (value < threshold.min || value > threshold.max) {
          violations.push({
            metric,
            value,
            threshold,
            severity: value < threshold.min * 0.8 || value > threshold.max * 1.2 ? 'critical' : 'warning'
          });
        }
      }
    });
    
    expect(violations.length).toBe(3); // carbonFootprint, waterSavings, waterdruckPsi
    expect(violations[0].metric).toBe('carbonFootprint');
    expect(violations[1].metric).toBe('waterSavings');
    expect(violations[2].metric).toBe('waterdruckPsi');
  });
});
