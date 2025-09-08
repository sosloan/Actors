import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, RadialBarChart, RadialBar 
} from 'recharts';

interface ScheduledEvent {
  id: string;
  name: string;
  type: 'once' | 'daily' | 'weekly' | 'monthly' | 'cron';
  nextExecution: string;
  lastExecution?: string;
  status: 'scheduled' | 'running' | 'completed' | 'failed' | 'cancelled';
  priority: number;
  dependencies: string[];
  marketCondition?: string;
  threshold?: number;
  category: 'trading' | 'analysis' | 'maintenance' | 'reporting' | 'risk';
}

interface EventDependency {
  id: string;
  fromEvent: string;
  toEvent: string;
  type: 'sequential' | 'parallel' | 'conditional' | 'threshold' | 'market_condition';
  condition?: string;
  threshold?: number;
}

interface SmartSchedule {
  eventId: string;
  optimalTime: string;
  confidence: number;
  reasoning: string;
  expectedDuration: number;
  resourceRequirements: {
    cpu: number;
    memory: number;
    network: number;
  };
}

const TimeOrchestrationDashboard: React.FC = () => {
  const [scheduledEvents, setScheduledEvents] = useState<ScheduledEvent[]>([
    {
      id: '1',
      name: '📈 Pre-Market Analysis',
      type: 'daily',
      nextExecution: '2024-01-16T09:00:00Z',
      lastExecution: '2024-01-15T09:00:00Z',
      status: 'scheduled',
      priority: 9,
      dependencies: [],
      marketCondition: 'market_open',
      category: 'analysis'
    },
    {
      id: '2',
      name: '⚡ Market Open Positions',
      type: 'daily',
      nextExecution: '2024-01-16T09:30:00Z',
      lastExecution: '2024-01-15T09:30:00Z',
      status: 'scheduled',
      priority: 10,
      dependencies: ['1'],
      marketCondition: 'market_open',
      category: 'trading'
    },
    {
      id: '3',
      name: '📊 Hourly Portfolio Rebalance',
      type: 'cron',
      nextExecution: '2024-01-15T14:00:00Z',
      lastExecution: '2024-01-15T13:00:00Z',
      status: 'scheduled',
      priority: 7,
      dependencies: ['2'],
      threshold: 0.05,
      category: 'trading'
    },
    {
      id: '4',
      name: '🧠 ML Model Retraining',
      type: 'weekly',
      nextExecution: '2024-01-21T02:00:00Z',
      lastExecution: '2024-01-14T02:00:00Z',
      status: 'scheduled',
      priority: 6,
      dependencies: [],
      category: 'maintenance'
    },
    {
      id: '5',
      name: '📋 End-of-Day Report',
      type: 'daily',
      nextExecution: '2024-01-15T16:30:00Z',
      lastExecution: '2024-01-14T16:30:00Z',
      status: 'scheduled',
      priority: 8,
      dependencies: ['3'],
      marketCondition: 'market_close',
      category: 'reporting'
    }
  ]);

  const [dependencies, setDependencies] = useState<EventDependency[]>([
    {
      id: 'dep-1',
      fromEvent: '1',
      toEvent: '2',
      type: 'sequential',
      condition: 'analysis_complete'
    },
    {
      id: 'dep-2',
      fromEvent: '2',
      toEvent: '3',
      type: 'threshold',
      threshold: 0.05
    },
    {
      id: 'dep-3',
      fromEvent: '3',
      toEvent: '5',
      type: 'market_condition',
      condition: 'market_close'
    }
  ]);

  const [smartSchedules, setSmartSchedules] = useState<SmartSchedule[]>([
    {
      eventId: '1',
      optimalTime: '2024-01-16T08:45:00Z',
      confidence: 0.92,
      reasoning: 'Based on 15 historical executions with 92% success rate',
      expectedDuration: 1800,
      resourceRequirements: { cpu: 0.6, memory: 0.4, network: 0.3 }
    },
    {
      eventId: '2',
      optimalTime: '2024-01-16T09:30:00Z',
      confidence: 0.95,
      reasoning: 'Market open timing with optimal liquidity',
      expectedDuration: 300,
      resourceRequirements: { cpu: 0.8, memory: 0.6, network: 0.9 }
    },
    {
      eventId: '3',
      optimalTime: '2024-01-15T14:05:00Z',
      confidence: 0.87,
      reasoning: 'Post-lunch low volatility period',
      expectedDuration: 600,
      resourceRequirements: { cpu: 0.7, memory: 0.5, network: 0.4 }
    }
  ]);

  const [systemMetrics, setSystemMetrics] = useState({
    totalEvents: 5,
    activeEvents: 3,
    completedToday: 12,
    failedToday: 1,
    avgExecutionTime: 450,
    systemLoad: 0.65,
    dependencyResolutionTime: 2.3
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        ...prev,
        completedToday: prev.completedToday + Math.floor(Math.random() * 2),
        avgExecutionTime: Math.max(200, prev.avgExecutionTime + (Math.random() - 0.5) * 50),
        systemLoad: Math.max(0.1, Math.min(1.0, prev.systemLoad + (Math.random() - 0.5) * 0.1)),
        dependencyResolutionTime: Math.max(0.5, prev.dependencyResolutionTime + (Math.random() - 0.5) * 0.5)
      }));

      // Update event statuses
      setScheduledEvents(prev => prev.map(event => {
        if (event.status === 'scheduled' && Math.random() < 0.1) {
          return { ...event, status: 'running' };
        } else if (event.status === 'running' && Math.random() < 0.3) {
          return { 
            ...event, 
            status: Math.random() < 0.95 ? 'completed' : 'failed',
            lastExecution: new Date().toISOString()
          };
        }
        return event;
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'text-blue-400';
      case 'running': return 'text-yellow-400';
      case 'completed': return 'text-green-400';
      case 'failed': return 'text-red-400';
      case 'cancelled': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBgColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-500';
      case 'running': return 'bg-yellow-500';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'cancelled': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 9) return 'text-red-400';
    if (priority >= 7) return 'text-orange-400';
    if (priority >= 5) return 'text-yellow-400';
    return 'text-green-400';
  };

  const renderSystemOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-200 text-sm">Total Events</p>
            <p className="text-3xl font-bold">{systemMetrics.totalEvents}</p>
          </div>
          <div className="text-4xl">⏰</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-green-200 text-sm">Completed Today</p>
            <p className="text-3xl font-bold">{systemMetrics.completedToday}</p>
          </div>
          <div className="text-4xl">✅</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-orange-200 text-sm">Avg Execution Time</p>
            <p className="text-3xl font-bold">{systemMetrics.avgExecutionTime}ms</p>
          </div>
          <div className="text-4xl">⚡</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-purple-200 text-sm">System Load</p>
            <p className="text-3xl font-bold">{(systemMetrics.systemLoad * 100).toFixed(0)}%</p>
          </div>
          <div className="text-4xl">📊</div>
        </div>
      </div>
    </div>
  );

  const renderScheduledEvents = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        ⏰ Scheduled Events & Dependencies
      </h3>
      <div className="space-y-4">
        {scheduledEvents.map(event => {
          const smartSchedule = smartSchedules.find(s => s.eventId === event.id);
          const eventDependencies = dependencies.filter(dep => dep.toEvent === event.id);
          
          return (
            <div key={event.id} className="bg-gray-700 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-lg">{event.name}</h4>
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusBgColor(event.status)}`}>
                    {event.status.toUpperCase()}
                  </span>
                  <span className={`text-sm font-semibold ${getPriorityColor(event.priority)}`}>
                    P{event.priority}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Type:</span>
                  <p className="font-semibold capitalize">{event.type}</p>
                </div>
                <div>
                  <span className="text-gray-400">Next Execution:</span>
                  <p className="font-semibold text-blue-400">
                    {new Date(event.nextExecution).toLocaleString()}
                  </p>
                </div>
                <div>
                  <span className="text-gray-400">Category:</span>
                  <p className="font-semibold capitalize">{event.category}</p>
                </div>
                <div>
                  <span className="text-gray-400">Dependencies:</span>
                  <p className="font-semibold text-orange-400">{eventDependencies.length}</p>
                </div>
              </div>

              {smartSchedule && (
                <div className="mt-3 p-3 bg-gray-600 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-cyan-400">Smart Schedule Recommendation</span>
                    <span className="text-sm font-semibold text-green-400">
                      {(smartSchedule.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-gray-400">Optimal Time:</span>
                      <p className="font-semibold text-cyan-400">
                        {new Date(smartSchedule.optimalTime).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-400">Expected Duration:</span>
                      <p className="font-semibold text-blue-400">{smartSchedule.expectedDuration}s</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Reasoning:</span>
                      <p className="font-semibold text-green-400">{smartSchedule.reasoning}</p>
                    </div>
                  </div>
                </div>
              )}

              {eventDependencies.length > 0 && (
                <div className="mt-3">
                  <span className="text-gray-400 text-sm">Dependencies:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {eventDependencies.map(dep => (
                      <span key={dep.id} className="bg-gray-600 px-2 py-1 rounded text-xs">
                        {dep.type} from {scheduledEvents.find(e => e.id === dep.fromEvent)?.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderDependencyGraph = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🔗 Event Dependency Graph
      </h3>
      <div className="bg-gray-700 rounded-xl p-6">
        <div className="flex items-center justify-center space-x-8">
          {scheduledEvents.map((event, index) => (
            <div key={event.id} className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center text-xs font-semibold ${
                event.status === 'completed' ? 'bg-green-600' :
                event.status === 'running' ? 'bg-yellow-600' :
                event.status === 'failed' ? 'bg-red-600' : 'bg-blue-600'
              }`}>
                {event.name.split(' ')[0]}
              </div>
              <span className="text-xs mt-2 text-center">{event.name}</span>
              {index < scheduledEvents.length - 1 && (
                <div className="absolute top-8 left-16 w-8 h-0.5 bg-gray-500"></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSmartScheduling = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🧠 Smart Scheduling Analytics
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {smartSchedules.map(schedule => {
          const event = scheduledEvents.find(e => e.id === schedule.eventId);
          return (
            <div key={schedule.eventId} className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-3">{event?.name}</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Confidence:</span>
                  <span className="text-green-400 font-semibold">
                    {(schedule.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Duration:</span>
                  <span className="text-blue-400 font-semibold">{schedule.expectedDuration}s</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">CPU:</span>
                  <span className="text-orange-400 font-semibold">
                    {(schedule.resourceRequirements.cpu * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Memory:</span>
                  <span className="text-purple-400 font-semibold">
                    {(schedule.resourceRequirements.memory * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <div className="mt-3 p-2 bg-gray-600 rounded text-xs">
                <span className="text-gray-400">Reasoning:</span>
                <p className="text-gray-300 mt-1">{schedule.reasoning}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderPerformanceMetrics = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        📊 Performance Metrics
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-700 rounded-xl p-4">
          <h4 className="font-semibold mb-2">⚡ Execution Performance</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Avg Time:</span>
              <span className="text-green-400 font-semibold">{systemMetrics.avgExecutionTime}ms</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Success Rate:</span>
              <span className="text-blue-400 font-semibold">
                {((systemMetrics.completedToday / (systemMetrics.completedToday + systemMetrics.failedToday)) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        <div className="bg-gray-700 rounded-xl p-4">
          <h4 className="font-semibold mb-2">🔗 Dependency Resolution</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Resolution Time:</span>
              <span className="text-cyan-400 font-semibold">{systemMetrics.dependencyResolutionTime}ms</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Total Dependencies:</span>
              <span className="text-orange-400 font-semibold">{dependencies.length}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-700 rounded-xl p-4">
          <h4 className="font-semibold mb-2">🧠 Smart Scheduling</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Avg Confidence:</span>
              <span className="text-purple-400 font-semibold">
                {(smartSchedules.reduce((sum, s) => sum + s.confidence, 0) / smartSchedules.length * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Optimized Events:</span>
              <span className="text-green-400 font-semibold">{smartSchedules.length}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-700 rounded-xl p-4">
          <h4 className="font-semibold mb-2">📈 System Health</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">System Load:</span>
              <span className="text-yellow-400 font-semibold">
                {(systemMetrics.systemLoad * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Active Events:</span>
              <span className="text-blue-400 font-semibold">{systemMetrics.activeEvents}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center">
            ⏰ Time Orchestration Dashboard
          </h1>
          <p className="text-gray-400 text-lg">
            Intelligent scheduling, dependency management, and predictive optimization
          </p>
        </div>

        {/* System Overview */}
        {renderSystemOverview()}

        {/* Scheduled Events */}
        {renderScheduledEvents()}

        {/* Dependency Graph */}
        {renderDependencyGraph()}

        {/* Smart Scheduling */}
        {renderSmartScheduling()}

        {/* Performance Metrics */}
        {renderPerformanceMetrics()}
      </div>
    </div>
  );
};

export default TimeOrchestrationDashboard;
