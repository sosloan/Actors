import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, RadialBarChart, RadialBar 
} from 'recharts';

interface CircuitBreaker {
  id: string;
  name: string;
  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  failureCount: number;
  failureThreshold: number;
  lastFailureTime: string;
  successCount: number;
  responseTime: number;
  errorRate: number;
}

interface EventStore {
  id: string;
  eventType: string;
  timestamp: string;
  aggregateId: string;
  version: number;
  data: any;
  metadata: any;
}

interface Trace {
  id: string;
  traceId: string;
  spanId: string;
  operationName: string;
  startTime: string;
  duration: number;
  status: 'success' | 'error' | 'timeout';
  tags: Record<string, string>;
  logs: Array<{ timestamp: string; message: string; level: string }>;
}

interface Saga {
  id: string;
  sagaId: string;
  status: 'running' | 'completed' | 'compensating' | 'failed';
  steps: Array<{
    id: string;
    name: string;
    status: 'pending' | 'completed' | 'failed' | 'compensated';
    compensationAction?: string;
  }>;
  startTime: string;
  endTime?: string;
  compensationCount: number;
}

const ProductionPatternsDashboard: React.FC = () => {
  const [circuitBreakers, setCircuitBreakers] = useState<CircuitBreaker[]>([
    {
      id: '1',
      name: 'Trading API Gateway',
      state: 'CLOSED',
      failureCount: 2,
      failureThreshold: 5,
      lastFailureTime: '2024-01-15T10:30:00Z',
      successCount: 1247,
      responseTime: 45,
      errorRate: 0.16
    },
    {
      id: '2',
      name: 'Market Data Service',
      state: 'CLOSED',
      failureCount: 0,
      failureThreshold: 5,
      lastFailureTime: '',
      successCount: 8934,
      responseTime: 23,
      errorRate: 0.02
    },
    {
      id: '3',
      name: 'Portfolio Service',
      state: 'HALF_OPEN',
      failureCount: 3,
      failureThreshold: 5,
      lastFailureTime: '2024-01-15T11:15:00Z',
      successCount: 567,
      responseTime: 89,
      errorRate: 0.52
    },
    {
      id: '4',
      name: 'Risk Management',
      state: 'OPEN',
      failureCount: 7,
      failureThreshold: 5,
      lastFailureTime: '2024-01-15T11:45:00Z',
      successCount: 234,
      responseTime: 156,
      errorRate: 2.89
    }
  ]);

  const [eventStore, setEventStore] = useState<EventStore[]>([
    {
      id: '1',
      eventType: 'OrderPlaced',
      timestamp: '2024-01-15T12:00:00Z',
      aggregateId: 'order-12345',
      version: 1,
      data: { symbol: 'AAPL', quantity: 100, price: 152.50 },
      metadata: { userId: 'user-789', sessionId: 'session-abc' }
    },
    {
      id: '2',
      eventType: 'OrderExecuted',
      timestamp: '2024-01-15T12:00:05Z',
      aggregateId: 'order-12345',
      version: 2,
      data: { executionPrice: 152.45, executionTime: '2024-01-15T12:00:05Z' },
      metadata: { exchange: 'NASDAQ', orderId: 'exec-67890' }
    },
    {
      id: '3',
      eventType: 'PortfolioUpdated',
      timestamp: '2024-01-15T12:00:10Z',
      aggregateId: 'portfolio-user-789',
      version: 15,
      data: { totalValue: 125000, positions: [{ symbol: 'AAPL', quantity: 100 }] },
      metadata: { updateSource: 'order-execution' }
    }
  ]);

  const [traces, setTraces] = useState<Trace[]>([
    {
      id: '1',
      traceId: 'trace-abc123',
      spanId: 'span-001',
      operationName: 'POST /api/orders',
      startTime: '2024-01-15T12:00:00Z',
      duration: 245,
      status: 'success',
      tags: { 'http.method': 'POST', 'http.status_code': '200', 'service': 'trading-api' },
      logs: [
        { timestamp: '2024-01-15T12:00:00Z', message: 'Order request received', level: 'INFO' },
        { timestamp: '2024-01-15T12:00:02Z', message: 'Risk check passed', level: 'INFO' },
        { timestamp: '2024-01-15T12:00:04Z', message: 'Order placed successfully', level: 'INFO' }
      ]
    },
    {
      id: '2',
      traceId: 'trace-def456',
      spanId: 'span-002',
      operationName: 'GET /api/portfolio',
      startTime: '2024-01-15T12:01:00Z',
      duration: 89,
      status: 'success',
      tags: { 'http.method': 'GET', 'http.status_code': '200', 'service': 'portfolio-api' },
      logs: [
        { timestamp: '2024-01-15T12:01:00Z', message: 'Portfolio request received', level: 'INFO' },
        { timestamp: '2024-01-15T12:01:01Z', message: 'Portfolio data retrieved', level: 'INFO' }
      ]
    }
  ]);

  const [sagas, setSagas] = useState<Saga[]>([
    {
      id: '1',
      sagaId: 'saga-order-12345',
      status: 'completed',
      steps: [
        { id: 'step-1', name: 'Validate Order', status: 'completed' },
        { id: 'step-2', name: 'Check Risk Limits', status: 'completed' },
        { id: 'step-3', name: 'Place Order', status: 'completed' },
        { id: 'step-4', name: 'Update Portfolio', status: 'completed' }
      ],
      startTime: '2024-01-15T12:00:00Z',
      endTime: '2024-01-15T12:00:10Z',
      compensationCount: 0
    },
    {
      id: '2',
      sagaId: 'saga-order-67890',
      status: 'compensating',
      steps: [
        { id: 'step-1', name: 'Validate Order', status: 'completed' },
        { id: 'step-2', name: 'Check Risk Limits', status: 'completed' },
        { id: 'step-3', name: 'Place Order', status: 'failed', compensationAction: 'Cancel Order' },
        { id: 'step-4', name: 'Update Portfolio', status: 'compensated', compensationAction: 'Revert Portfolio' }
      ],
      startTime: '2024-01-15T11:30:00Z',
      compensationCount: 2
    }
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setCircuitBreakers(prev => prev.map(cb => ({
        ...cb,
        successCount: cb.successCount + Math.floor(Math.random() * 5),
        responseTime: Math.max(10, cb.responseTime + (Math.random() - 0.5) * 10),
        errorRate: Math.max(0, cb.errorRate + (Math.random() - 0.5) * 0.1)
      })));

      setEventStore(prev => [...prev, {
        id: (prev.length + 1).toString(),
        eventType: ['OrderPlaced', 'OrderExecuted', 'PortfolioUpdated', 'RiskCheck'][Math.floor(Math.random() * 4)],
        timestamp: new Date().toISOString(),
        aggregateId: `aggregate-${Math.random().toString(36).substr(2, 9)}`,
        version: Math.floor(Math.random() * 100) + 1,
        data: { sample: 'data' },
        metadata: { source: 'system' }
      }].slice(-50)); // Keep only last 50 events
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getStateColor = (state: string) => {
    switch (state) {
      case 'CLOSED': return 'text-green-400';
      case 'OPEN': return 'text-red-400';
      case 'HALF_OPEN': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getStateBgColor = (state: string) => {
    switch (state) {
      case 'CLOSED': return 'bg-green-500';
      case 'OPEN': return 'bg-red-500';
      case 'HALF_OPEN': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const renderCircuitBreakers = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🔌 Circuit Breaker Status
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {circuitBreakers.map(cb => (
          <div key={cb.id} className="bg-gray-700 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold">{cb.name}</h4>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${getStateBgColor(cb.state)}`}></div>
                <span className={`text-sm font-semibold ${getStateColor(cb.state)}`}>
                  {cb.state}
                </span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Success Count:</span>
                <span className="text-green-400 font-semibold">{cb.successCount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Failure Count:</span>
                <span className="text-red-400 font-semibold">{cb.failureCount}/{cb.failureThreshold}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Response Time:</span>
                <span className="text-blue-400 font-semibold">{cb.responseTime}ms</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Error Rate:</span>
                <span className="text-orange-400 font-semibold">{cb.errorRate.toFixed(2)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderEventStore = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        📝 Event Store - Recent Events
      </h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {eventStore.slice(-10).reverse().map(event => (
          <div key={event.id} className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-blue-400">{event.eventType}</h4>
              <span className="text-sm text-gray-400">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
              <div>
                <span className="text-gray-400">Aggregate ID:</span>
                <p className="font-mono text-xs">{event.aggregateId}</p>
              </div>
              <div>
                <span className="text-gray-400">Version:</span>
                <p className="font-semibold">{event.version}</p>
              </div>
              <div>
                <span className="text-gray-400">Data:</span>
                <p className="font-mono text-xs text-green-400">
                  {JSON.stringify(event.data).substring(0, 50)}...
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDistributedTracing = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🔍 Distributed Tracing - Request Flow
      </h3>
      <div className="space-y-4">
        {traces.map(trace => (
          <div key={trace.id} className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-cyan-400">{trace.operationName}</h4>
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  trace.status === 'success' ? 'bg-green-600' :
                  trace.status === 'error' ? 'bg-red-600' : 'bg-yellow-600'
                }`}>
                  {trace.status.toUpperCase()}
                </span>
                <span className="text-sm text-gray-400">{trace.duration}ms</span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Trace ID:</span>
                <p className="font-mono text-xs">{trace.traceId}</p>
              </div>
              <div>
                <span className="text-gray-400">Span ID:</span>
                <p className="font-mono text-xs">{trace.spanId}</p>
              </div>
            </div>
            <div className="mt-3">
              <span className="text-gray-400 text-sm">Tags:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {Object.entries(trace.tags).map(([key, value]) => (
                  <span key={key} className="bg-gray-600 px-2 py-1 rounded text-xs">
                    {key}: {value}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-3">
              <span className="text-gray-400 text-sm">Logs:</span>
              <div className="space-y-1 mt-1">
                {trace.logs.map((log, index) => (
                  <div key={index} className="text-xs text-gray-300">
                    <span className="text-gray-500">[{log.timestamp}]</span>
                    <span className={`ml-2 ${
                      log.level === 'ERROR' ? 'text-red-400' :
                      log.level === 'WARN' ? 'text-yellow-400' : 'text-green-400'
                    }`}>
                      [{log.level}]
                    </span>
                    <span className="ml-2">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderSagaManagement = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🔄 Saga Pattern - Distributed Transactions
      </h3>
      <div className="space-y-4">
        {sagas.map(saga => (
          <div key={saga.id} className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-purple-400">{saga.sagaId}</h4>
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  saga.status === 'completed' ? 'bg-green-600' :
                  saga.status === 'running' ? 'bg-blue-600' :
                  saga.status === 'compensating' ? 'bg-yellow-600' : 'bg-red-600'
                }`}>
                  {saga.status.toUpperCase()}
                </span>
                <span className="text-sm text-gray-400">
                  {saga.compensationCount} compensations
                </span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-3">
              <div>
                <span className="text-gray-400">Start Time:</span>
                <p className="font-mono text-xs">{new Date(saga.startTime).toLocaleString()}</p>
              </div>
              {saga.endTime && (
                <div>
                  <span className="text-gray-400">End Time:</span>
                  <p className="font-mono text-xs">{new Date(saga.endTime).toLocaleString()}</p>
                </div>
              )}
            </div>
            <div>
              <span className="text-gray-400 text-sm">Steps:</span>
              <div className="space-y-2 mt-2">
                {saga.steps.map(step => (
                  <div key={step.id} className="flex items-center justify-between bg-gray-600 rounded p-2">
                    <span className="font-medium">{step.name}</span>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        step.status === 'completed' ? 'bg-green-600' :
                        step.status === 'pending' ? 'bg-yellow-600' :
                        step.status === 'failed' ? 'bg-red-600' : 'bg-orange-600'
                      }`}>
                        {step.status.toUpperCase()}
                      </span>
                      {step.compensationAction && (
                        <span className="text-xs text-orange-400">
                          {step.compensationAction}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center">
            🏭 Production-Grade Patterns Dashboard
          </h1>
          <p className="text-gray-400 text-lg">
            Monitor Circuit Breakers, Event Sourcing, Distributed Tracing, and Saga Patterns
          </p>
        </div>

        {/* System Health Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-200 text-sm">Circuit Breakers</p>
                <p className="text-3xl font-bold">
                  {circuitBreakers.filter(cb => cb.state === 'CLOSED').length}/{circuitBreakers.length}
                </p>
                <p className="text-sm text-green-200">Healthy</p>
              </div>
              <div className="text-4xl">🔌</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm">Events Stored</p>
                <p className="text-3xl font-bold">{eventStore.length.toLocaleString()}</p>
                <p className="text-sm text-blue-200">Total Events</p>
              </div>
              <div className="text-4xl">📝</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-cyan-500 to-cyan-700 rounded-2xl p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-cyan-200 text-sm">Active Traces</p>
                <p className="text-3xl font-bold">{traces.length}</p>
                <p className="text-sm text-cyan-200">Request Flows</p>
              </div>
              <div className="text-4xl">🔍</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-200 text-sm">Active Sagas</p>
                <p className="text-3xl font-bold">
                  {sagas.filter(saga => saga.status === 'running').length}
                </p>
                <p className="text-sm text-purple-200">Transactions</p>
              </div>
              <div className="text-4xl">🔄</div>
            </div>
          </div>
        </div>

        {/* Circuit Breakers */}
        {renderCircuitBreakers()}

        {/* Event Store */}
        {renderEventStore()}

        {/* Distributed Tracing */}
        {renderDistributedTracing()}

        {/* Saga Management */}
        {renderSagaManagement()}
      </div>
    </div>
  );
};

export default ProductionPatternsDashboard;
