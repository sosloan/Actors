import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, RadialBarChart, RadialBar 
} from 'recharts';

interface AgentData {
  id: number;
  name: string;
  dimension: string;
  resonance: number;
  status: 'active' | 'idle' | 'error';
  energy: number;
  lastUpdate: string;
}

interface SystemMetrics {
  // 🏎️ Ferrari Speed Metrics
  activeAgents: number;
  avgNarrativeEnergy: number;
  avgJackieResonance: number;
  systemHealth: number;
  financialGap: number;
  fireTimeline: number;
  circuitBreakerStatus: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  eventStoreSize: number;
  traceCount: number;
  
  // ⭐ Starry Precision Metrics
  executionLatency: number;        // Sub-millisecond execution time
  throughputPerSecond: number;     // Operations per second
  successRate: number;            // Success rate percentage
  precisionScore: number;         // Calculation precision score
  dataAccuracy: number;           // Data accuracy percentage
  
  // 🎡 Ferris Wheel Dynamics
  rotationSpeed: number;          // System rotation speed
  stateTransitions: number;       // State transitions per minute
  circularBufferSize: number;     // Circular buffer utilization
  dynamicLoad: number;           // Dynamic load factor
  wheelPosition: number;         // Current wheel position (0-360)
}

const ACTORSDashboard: React.FC = () => {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    // 🏎️ Ferrari Speed Metrics
    activeAgents: 18,
    avgNarrativeEnergy: 1.101,
    avgJackieResonance: 0.907,
    systemHealth: 98.7,
    financialGap: 108000,
    fireTimeline: 3,
    circuitBreakerStatus: 'CLOSED',
    eventStoreSize: 15420,
    traceCount: 892,
    
    // ⭐ Starry Precision Metrics
    executionLatency: 0.847,        // Sub-millisecond execution time
    throughputPerSecond: 125000,     // Operations per second
    successRate: 99.97,            // Success rate percentage
    precisionScore: 99.99,         // Calculation precision score
    dataAccuracy: 99.95,           // Data accuracy percentage
    
    // 🎡 Ferris Wheel Dynamics
    rotationSpeed: 2.4,            // System rotation speed
    stateTransitions: 45,          // State transitions per minute
    circularBufferSize: 78,        // Circular buffer utilization
    dynamicLoad: 0.65,            // Dynamic load factor
    wheelPosition: 127             // Current wheel position (0-360)
  });

  // 🎡 Ferris Wheel Animation State
  const [wheelRotation, setWheelRotation] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  const [agents, setAgents] = useState<AgentData[]>([
    { id: 1, name: '🏎️ Market Data Agent', dimension: 'SPEED', resonance: 0.880, status: 'active', energy: 1.12, lastUpdate: '2s ago' },
    { id: 2, name: '⭐ Technical Analysis', dimension: 'SPEED', resonance: 0.890, status: 'active', energy: 1.08, lastUpdate: '1s ago' },
    { id: 3, name: '🎡 Personal Finance', dimension: 'LOYALTY', resonance: 0.950, status: 'active', energy: 1.15, lastUpdate: '3s ago' },
    { id: 4, name: '🔥 DeFi Integration', dimension: 'SACRED', resonance: 0.980, status: 'active', energy: 1.18, lastUpdate: '1s ago' },
    { id: 5, name: '🧠 Neural Network', dimension: 'PASSION', resonance: 0.920, status: 'active', energy: 1.09, lastUpdate: '2s ago' },
    { id: 6, name: '⏰ Time Orchestration', dimension: 'WISDOM', resonance: 0.975, status: 'active', energy: 1.21, lastUpdate: '1s ago' },
    { id: 7, name: '🔌 Circuit Breaker', dimension: 'COURAGE', resonance: 0.965, status: 'active', energy: 1.14, lastUpdate: '2s ago' },
    { id: 8, name: '📝 Event Sourcing', dimension: 'TRUTH', resonance: 0.990, status: 'active', energy: 1.16, lastUpdate: '1s ago' }
  ]);

  const [marketData] = useState([
    { time: '09:30', price: 150.50, volume: 1200, signal: 'HOLD', pnl: 0 },
    { time: '10:00', price: 151.20, volume: 1500, signal: 'BUY', pnl: 0.7 },
    { time: '10:30', price: 152.00, volume: 1800, signal: 'BUY', pnl: 1.5 },
    { time: '11:00', price: 151.75, volume: 1400, signal: 'HOLD', pnl: 1.25 },
    { time: '11:30', price: 152.50, volume: 2100, signal: 'STRONG_BUY', pnl: 2.0 },
    { time: '12:00', price: 153.20, volume: 1900, signal: 'STRONG_BUY', pnl: 2.7 }
  ]);

  const navigationItems = [
    { id: 'dashboard', label: '🏠 Command Center', icon: '🏠', color: 'from-blue-500 to-blue-700' },
    { id: 'agents', label: '🤖 Agent Network', icon: '🤖', color: 'from-purple-500 to-purple-700' },
    { id: 'trading', label: '📊 Trading Floor', icon: '📊', color: 'from-green-500 to-green-700' },
    { id: 'patterns', label: '🏭 Production Patterns', icon: '🏭', color: 'from-orange-500 to-orange-700' },
    { id: 'time', label: '⏰ Time Orchestration', icon: '⏰', color: 'from-cyan-500 to-cyan-700' },
    { id: 'freedom', label: '💎 Financial Freedom', icon: '💎', color: 'from-pink-500 to-pink-700' },
    { id: 'analytics', label: '📈 Analytics', icon: '📈', color: 'from-indigo-500 to-indigo-700' }
  ];

  const dimensionColors = {
    'SPEED': '#FF6B6B',
    'LOYALTY': '#4ECDC4', 
    'PASSION': '#45B7D1',
    'SACRED': '#96CEB4',
    'COURAGE': '#FFEAA7',
    'WISDOM': '#DDA0DD',
    'LOVE': '#FFB6C1',
    'TRUTH': '#98D8C8'
  };

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        ...prev,
        // 🏎️ Ferrari Speed Updates
        avgNarrativeEnergy: +(prev.avgNarrativeEnergy + (Math.random() - 0.5) * 0.02).toFixed(3),
        avgJackieResonance: +(prev.avgJackieResonance + (Math.random() - 0.5) * 0.01).toFixed(3),
        systemHealth: +(prev.systemHealth + (Math.random() - 0.5) * 0.5).toFixed(1),
        eventStoreSize: prev.eventStoreSize + Math.floor(Math.random() * 10),
        traceCount: prev.traceCount + Math.floor(Math.random() * 5),
        
        // ⭐ Starry Precision Updates
        executionLatency: +(Math.max(0.1, Math.min(2.0, prev.executionLatency + (Math.random() - 0.5) * 0.1))).toFixed(3),
        throughputPerSecond: Math.max(50000, Math.min(200000, prev.throughputPerSecond + (Math.random() - 0.5) * 5000)),
        successRate: +(Math.max(99.0, Math.min(100, prev.successRate + (Math.random() - 0.5) * 0.1))).toFixed(2),
        precisionScore: +(Math.max(99.5, Math.min(100, prev.precisionScore + (Math.random() - 0.5) * 0.05))).toFixed(2),
        dataAccuracy: +(Math.max(99.0, Math.min(100, prev.dataAccuracy + (Math.random() - 0.5) * 0.1))).toFixed(2),
        
        // 🎡 Ferris Wheel Dynamics Updates
        rotationSpeed: +(Math.max(1.0, Math.min(5.0, prev.rotationSpeed + (Math.random() - 0.5) * 0.2))).toFixed(1),
        stateTransitions: Math.max(20, Math.min(100, prev.stateTransitions + Math.floor((Math.random() - 0.5) * 10))),
        circularBufferSize: Math.max(50, Math.min(100, prev.circularBufferSize + (Math.random() - 0.5) * 5)),
        dynamicLoad: +(Math.max(0.1, Math.min(1.0, prev.dynamicLoad + (Math.random() - 0.5) * 0.1))).toFixed(2),
        wheelPosition: (prev.wheelPosition + prev.rotationSpeed) % 360
      }));

      setAgents(prev => prev.map(agent => ({
        ...agent,
        resonance: +(agent.resonance + (Math.random() - 0.5) * 0.01).toFixed(3),
        energy: +(agent.energy + (Math.random() - 0.5) * 0.02).toFixed(2),
        lastUpdate: '1s ago'
      })));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // 🎡 Ferris Wheel Animation Effect
  useEffect(() => {
    if (!isAnimating) return;
    
    const animationInterval = setInterval(() => {
      setWheelRotation(prev => (prev + systemMetrics.rotationSpeed) % 360);
    }, 50);

    return () => clearInterval(animationInterval);
  }, [isAnimating, systemMetrics.rotationSpeed]);

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm">Active Agents</p>
              <p className="text-3xl font-bold">{systemMetrics.activeAgents}</p>
            </div>
            <div className="text-4xl">🤖</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-200 text-sm">System Health</p>
              <p className="text-3xl font-bold">{systemMetrics.systemHealth}%</p>
            </div>
            <div className="text-4xl">🏥</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-200 text-sm">Narrative Energy</p>
              <p className="text-3xl font-bold">{systemMetrics.avgNarrativeEnergy}</p>
            </div>
            <div className="text-4xl">⚡</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-200 text-sm">Jackie Resonance</p>
              <p className="text-3xl font-bold">{systemMetrics.avgJackieResonance}</p>
            </div>
            <div className="text-4xl">🌟</div>
          </div>
        </div>
      </div>

      {/* 🏎️ Ferrari Speed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-red-500 to-red-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-200 text-sm">🏎️ Execution Latency</p>
              <p className="text-3xl font-bold">{systemMetrics.executionLatency}ms</p>
              <p className="text-red-300 text-xs">Sub-millisecond performance</p>
            </div>
            <div className="text-4xl">🏎️</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-yellow-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-200 text-sm">⚡ Throughput</p>
              <p className="text-3xl font-bold">{(systemMetrics.throughputPerSecond / 1000).toFixed(0)}K</p>
              <p className="text-yellow-300 text-xs">Operations per second</p>
            </div>
            <div className="text-4xl">⚡</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-indigo-200 text-sm">🎯 Success Rate</p>
              <p className="text-3xl font-bold">{systemMetrics.successRate}%</p>
              <p className="text-indigo-300 text-xs">High reliability</p>
            </div>
            <div className="text-4xl">🎯</div>
          </div>
        </div>
      </div>

      {/* ⭐ Starry Precision Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-cyan-500 to-cyan-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-cyan-200 text-sm">⭐ Precision Score</p>
              <p className="text-3xl font-bold">{systemMetrics.precisionScore}%</p>
              <p className="text-cyan-300 text-xs">Mathematical accuracy</p>
            </div>
            <div className="text-4xl">⭐</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-pink-500 to-pink-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-pink-200 text-sm">🌟 Data Accuracy</p>
              <p className="text-3xl font-bold">{systemMetrics.dataAccuracy}%</p>
              <p className="text-pink-300 text-xs">Quality assurance</p>
            </div>
            <div className="text-4xl">🌟</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-teal-500 to-teal-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-teal-200 text-sm">💎 System Health</p>
              <p className="text-3xl font-bold">{systemMetrics.systemHealth}%</p>
              <p className="text-teal-300 text-xs">Optimal performance</p>
            </div>
            <div className="text-4xl">💎</div>
          </div>
        </div>
      </div>

      {/* 🎡 Ferris Wheel Dynamics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-200 text-sm">🎡 Rotation Speed</p>
              <p className="text-3xl font-bold">{systemMetrics.rotationSpeed}x</p>
              <p className="text-emerald-300 text-xs">Dynamic motion</p>
            </div>
            <div className="text-4xl" style={{ transform: `rotate(${wheelRotation}deg)` }}>🎡</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-violet-500 to-violet-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-violet-200 text-sm">🔄 State Transitions</p>
              <p className="text-3xl font-bold">{systemMetrics.stateTransitions}</p>
              <p className="text-violet-300 text-xs">Per minute</p>
            </div>
            <div className="text-4xl">🔄</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-rose-500 to-rose-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-rose-200 text-sm">⭕ Buffer Size</p>
              <p className="text-3xl font-bold">{systemMetrics.circularBufferSize}%</p>
              <p className="text-rose-300 text-xs">Circular utilization</p>
            </div>
            <div className="text-4xl">⭕</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-amber-500 to-amber-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-amber-200 text-sm">⚖️ Dynamic Load</p>
              <p className="text-3xl font-bold">{(systemMetrics.dynamicLoad * 100).toFixed(0)}%</p>
              <p className="text-amber-300 text-xs">Load balancing</p>
            </div>
            <div className="text-4xl">⚖️</div>
          </div>
        </div>
      </div>

      {/* Production Patterns Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            🔌 Circuit Breaker Status
          </h3>
          <div className="flex items-center space-x-3">
            <div className={`w-4 h-4 rounded-full ${
              systemMetrics.circuitBreakerStatus === 'CLOSED' ? 'bg-green-500' :
              systemMetrics.circuitBreakerStatus === 'OPEN' ? 'bg-red-500' : 'bg-yellow-500'
            }`}></div>
            <span className="text-lg font-semibold">{systemMetrics.circuitBreakerStatus}</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            📝 Event Store
          </h3>
          <p className="text-2xl font-bold text-blue-400">{systemMetrics.eventStoreSize.toLocaleString()}</p>
          <p className="text-gray-400 text-sm">Events Stored</p>
        </div>

        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            🔍 Distributed Traces
          </h3>
          <p className="text-2xl font-bold text-cyan-400">{systemMetrics.traceCount.toLocaleString()}</p>
          <p className="text-gray-400 text-sm">Active Traces</p>
        </div>
      </div>

      {/* Market Data Chart */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-6 flex items-center">
          📊 Real-Time Market Data
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={marketData}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: 'white'
              }} 
            />
            <Area 
              type="monotone" 
              dataKey="price" 
              stroke="#3B82F6" 
              fillOpacity={1} 
              fill="url(#priceGradient)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const renderAgentNetwork = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-6 flex items-center">
          🤖 Distributed Agent Network
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map(agent => (
            <div key={agent.id} className="bg-gray-700 rounded-xl p-4 hover:bg-gray-600 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold">{agent.name}</h4>
                <div className={`w-3 h-3 rounded-full ${
                  agent.status === 'active' ? 'bg-green-500' :
                  agent.status === 'idle' ? 'bg-yellow-500' : 'bg-red-500'
                }`}></div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Dimension:</span>
                  <span style={{ color: dimensionColors[agent.dimension as keyof typeof dimensionColors] }}>
                    {agent.dimension}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Resonance:</span>
                  <span className="text-blue-400">{agent.resonance}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Energy:</span>
                  <span className="text-green-400">{agent.energy}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Updated:</span>
                  <span className="text-gray-300">{agent.lastUpdate}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTradingFloor = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-6 flex items-center">
          📊 Trading Floor - Real-Time Execution
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={marketData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: 'white'
              }} 
            />
            <Line type="monotone" dataKey="price" stroke="#10B981" strokeWidth={3} />
            <Line type="monotone" dataKey="pnl" stroke="#F59E0B" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
          <h4 className="text-lg font-bold mb-4">📈 Portfolio Performance</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>Total Value:</span>
              <span className="text-green-400 font-semibold">$1,234,567</span>
            </div>
            <div className="flex justify-between">
              <span>Today's P&L:</span>
              <span className="text-green-400 font-semibold">+$12,345</span>
            </div>
            <div className="flex justify-between">
              <span>YTD Return:</span>
              <span className="text-green-400 font-semibold">+24.5%</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
          <h4 className="text-lg font-bold mb-4">⚡ Active Orders</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Buy AAPL 100 @ $152.50</span>
              <span className="text-yellow-400">Pending</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Sell TSLA 50 @ $245.80</span>
              <span className="text-green-400">Filled</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Buy SPY 200 @ $445.20</span>
              <span className="text-yellow-400">Pending</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard': return renderDashboard();
      case 'agents': return renderAgentNetwork();
      case 'trading': return renderTradingFloor();
      default: return renderDashboard();
    }
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-gray-900' : 'bg-gray-100'}`}>
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-900 to-purple-900 text-white p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-4xl">🦞</div>
            <div>
              <h1 className="text-3xl font-bold">ACTORS</h1>
              <p className="text-indigo-200">Distributed Autonomous Agents for Financial Trading & Freedom</p>
            </div>
          </div>
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <nav className={`w-64 ${isDarkMode ? 'bg-gray-800' : 'bg-white'} border-r ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} min-h-screen p-4`}>
          <div className="space-y-2">
            {navigationItems.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center space-x-3 ${
                  activeSection === item.id
                    ? `bg-gradient-to-r ${item.color} text-white shadow-lg`
                    : `${isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'}`
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </button>
            ))}
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default ACTORSDashboard;
