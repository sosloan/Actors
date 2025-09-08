/**
 * Environmental Metrics Client Example
 * Demonstrates how to connect to the enhanced metrics server
 * 
 * Usage: node client-example.js
 * 
 * This client connects to the environmental metrics server and:
 * - Receives real-time metric updates via WebSocket
 * - Displays alerts when thresholds are exceeded
 * - Fetches historical data via REST API
 * - Shows server health status
 */

const io = require('socket.io-client');

class EnvironmentalMetricsClient {
  constructor(serverUrl = 'http://localhost:3030') {
    this.serverUrl = serverUrl;
    this.socket = null;
    this.isConnected = false;
    this.metrics = {};
    this.alerts = [];
    this.history = [];
  }

  async connect() {
    try {
      this.socket = io(this.serverUrl);
      
      this.socket.on('connect', () => {
        this.isConnected = true;
        console.log('🌿 Connected to Environmental Metrics Server');
        this.fetchInitialData();
      });

      this.socket.on('disconnect', () => {
        this.isConnected = false;
        console.log('❌ Disconnected from server');
      });

      this.socket.on('metrics', (data) => {
        this.handleMetricsUpdate(data);
      });

      this.socket.on('alerts', (alerts) => {
        this.handleAlerts(alerts);
      });

      this.socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
      });

    } catch (error) {
      console.error('Failed to connect:', error);
    }
  }

  async fetchInitialData() {
    try {
      // Fetch current metrics
      const metricsResponse = await fetch(`${this.serverUrl}/metrics`);
      const metricsData = await metricsResponse.json();
      this.metrics = metricsData.metrics;
      console.log('📊 Current metrics:', this.metrics);

      // Fetch thresholds
      const thresholdsResponse = await fetch(`${this.serverUrl}/thresholds`);
      const thresholds = await thresholdsResponse.json();
      console.log('🚨 Monitoring thresholds:', thresholds);

      // Fetch recent history
      const historyResponse = await fetch(`${this.serverUrl}/metrics/history?limit=10`);
      const historyData = await historyResponse.json();
      this.history = historyData.data;
      console.log('📈 Recent history loaded:', this.history.length, 'records');

    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  }

  handleMetricsUpdate(data) {
    this.metrics = data.metrics;
    
    console.log('\n🔄 Metrics Update:', {
      timestamp: data.timestamp,
      metrics: this.metrics,
      changes: data.changes
    });

    // Display changes
    Object.entries(data.changes).forEach(([key, change]) => {
      if (Math.abs(change) > 0.1) {
        const direction = change > 0 ? '📈' : '📉';
        console.log(`  ${direction} ${key}: ${change > 0 ? '+' : ''}${change}`);
      }
    });

    // Check for alerts in the update
    if (data.alerts && data.alerts.length > 0) {
      this.handleAlerts(data.alerts);
    }
  }

  handleAlerts(alerts) {
    this.alerts = [...this.alerts, ...alerts];
    
    alerts.forEach(alert => {
      const emoji = alert.severity === 'critical' ? '🚨' : '⚠️';
      console.log(`\n${emoji} ALERT: ${alert.message}`);
      console.log(`   Severity: ${alert.severity.toUpperCase()}`);
      console.log(`   Time: ${alert.timestamp}`);
    });
  }

  async getHealthStatus() {
    try {
      const response = await fetch(`${this.serverUrl}/healthz`);
      const health = await response.json();
      console.log('💚 Server Health:', health);
      return health;
    } catch (error) {
      console.error('Error fetching health status:', error);
      return null;
    }
  }

  async getHistoricalData(limit = 50, offset = 0) {
    try {
      const response = await fetch(`${this.serverUrl}/metrics/history?limit=${limit}&offset=${offset}`);
      const data = await response.json();
      console.log(`📊 Historical data: ${data.data.length} records (${data.total} total)`);
      return data;
    } catch (error) {
      console.error('Error fetching historical data:', error);
      return null;
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.isConnected = false;
      console.log('👋 Disconnected from server');
    }
  }

  // Utility method to format metrics for display
  formatMetrics() {
    return Object.entries(this.metrics).map(([key, value]) => {
      const unit = this.getUnit(key);
      return `${key}: ${value} ${unit}`;
    }).join('\n');
  }

  getUnit(metric) {
    const units = {
      carbonFootprint: 'kg CO2',
      waterSavings: 'liters',
      energyEfficiency: '%',
      confidence: '%',
      waterdruckPsi: 'PSI'
    };
    return units[metric] || '';
  }
}

// Example usage
async function main() {
  const client = new EnvironmentalMetricsClient();
  
  // Connect to server
  await client.connect();
  
  // Check server health
  await client.getHealthStatus();
  
  // Get some historical data
  await client.getHistoricalData(20);
  
  // Keep the client running to receive real-time updates
  console.log('\n🔄 Listening for real-time updates...');
  console.log('Press Ctrl+C to disconnect\n');
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n👋 Shutting down client...');
    client.disconnect();
    process.exit(0);
  });
}

// Run the example
if (require.main === module) {
  main().catch(console.error);
}

module.exports = EnvironmentalMetricsClient;
