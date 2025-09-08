import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const OctotrieUXDesign = () => {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [agentData, setAgentData] = useState({
    activeAgents: 18,
    avgNarrativeEnergy: 1.101,
    avgJackieResonance: 0.907,
    systemHealth: 98.7,
    financialGap: 108000,
    fireTimeline: 3
  });
  
  const [marketData, setMarketData] = useState([
    { time: '09:30', price: 150.50, volume: 1200, signal: 'HOLD' },
    { time: '10:00', price: 151.20, volume: 1500, signal: 'BUY' },
    { time: '10:30', price: 152.00, volume: 1800, signal: 'BUY' },
    { time: '11:00', price: 151.75, volume: 1400, signal: 'HOLD' },
    { time: '11:30', price: 152.50, volume: 2100, signal: 'STRONG_BUY' }
  ]);

  const agents = [
    { id: 1, name: '🏎️ Market Data Agent', dimension: 'SPEED', resonance: 0.880, status: 'active', energy: 1.12 },
    { id: 2, name: '📈 Technical Analysis', dimension: 'SPEED', resonance: 0.890, status: 'active', energy: 1.08 },
    { id: 3, name: '💰 Personal Finance', dimension: 'LOYALTY', resonance: 0.950, status: 'active', energy: 1.15 },
    { id: 4, name: '🔥 DeFi Integration', dimension: 'SACRED', resonance: 0.980, status: 'active', energy: 1.18 },
    { id: 5, name: '🧠 Neural Network', dimension: 'PASSION', resonance: 0.920, status: 'active', energy: 1.09 },
    { id: 6, name: '🐉 Dragon Patterns', dimension: 'SACRED', resonance: 0.975, status: 'active', energy: 1.21 }
  ];

  const navigationItems = [
    { id: 'dashboard', label: '🏠 Command Center', icon: '🏠' },
    { id: 'agents', label: '🤖 Agent Network', icon: '🤖' },
    { id: 'trading', label: '📊 Trading Floor', icon: '📊' },
    { id: 'dragons', label: '🐉 Dragon Patterns', icon: '🐉' },
    { id: 'onnx', label: '🧠 ONNX Models', icon: '🧠' },
    { id: 'narrative', label: '🎭 Narrative Space', icon: '🎭' },
    { id: 'freedom', label: '💎 Financial Freedom', icon: '💎' },
    { id: 'analytics', label: '📈 Analytics', icon: '📈' }
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
      setAgentData(prev => ({
        ...prev,
        avgNarrativeEnergy: +(prev.avgNarrativeEnergy + (Math.random() - 0.5) * 0.02).toFixed(3),
        avgJackieResonance: +(prev.avgJackieResonance + (Math.random() - 0.5) * 0.01).toFixed(3),
        systemHealth: +(prev.systemHealth + (Math.random() - 0.5) * 0.5).toFixed(1)
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const renderDashboard = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* System Overview */}
      <div className="lg:col-span-2 bg-gradient-to-br from-indigo-900 to-purple-900 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">🎭 OCTOTRIE Command Center</h2>
            <p className="text-indigo-200">Distributed Autonomous Agents • Jackie Robinson Resonance • 8D Narrative</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-green-400">{agentData.systemHealth}%</div>
            <div className="text-sm text-indigo-200">System Health</div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white/10 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-cyan-400">{agentData.activeAgents}</div>
            <div className="text-sm text-indigo-200">Active Agents</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-400">{agentData.avgNarrativeEnergy}</div>
            <div className="text-sm text-indigo-200">Narrative Energy</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-400">{agentData.avgJackieResonance}</div>
            <div className="text-sm text-indigo-200">Jackie Resonance</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-red-400">&lt;50ms</div>
            <div className="text-sm text-indigo-200">Inference Time</div>
          </div>
        </div>

        {/* Real-time Market Chart */}
        <div className="bg-white/5 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3">📊 Real-time Market Data</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={marketData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="time" stroke="rgba(255,255,255,0.7)" />
              <YAxis stroke="rgba(255,255,255,0.7)" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Area type="monotone" dataKey="price" stroke="#00D9FF" fill="url(#gradient)" strokeWidth={2} />
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00D9FF" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#00D9FF" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Agent Status Panel */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">🧠 Model Performance Benchmarks</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={[
            { model: 'GPT', latency: 45, accuracy: 94.2, throughput: 22.2 },
            { model: 'ViT', latency: 32, accuracy: 91.8, throughput: 31.3 },
            { model: 'Dragon', latency: 18, accuracy: 96.7, throughput: 55.6 },
            { model: 'LSTM', latency: 12, accuracy: 88.3, throughput: 83.3 },
            { model: 'Fusion', latency: 58, accuracy: 92.1, throughput: 17.2 }
          ]}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="model" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="latency" fill="#3B82F6" name="Latency (ms)" />
            <Bar dataKey="accuracy" fill="#10B981" name="Accuracy (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const renderNarrativeSpace = () => (
    <div className="space-y-6">
      {/* 8D Narrative Visualization */}
      <div className="bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 rounded-2xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-4">🎭 8-Dimensional Narrative Space</h2>
        <p className="text-purple-200 mb-6">Jackie Robinson Resonance • Sacred Transformation • OCTOTRIE Dimensions</p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(dimensionColors).map(([dimension, color]) => (
            <div key={dimension} className="bg-white/10 rounded-lg p-4 text-center">
              <div 
                className="w-8 h-8 rounded-full mx-auto mb-2"
                style={{ backgroundColor: color }}
              ></div>
              <div className="font-semibold text-sm">{dimension}</div>
              <div className="text-xs text-gray-300 mt-1">
                {Math.random().toFixed(3)} resonance
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Jackie Robinson Integration */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">⚾ Jackie Robinson Sacred Principles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">🏆 Breaking Barriers</h4>
              <p className="text-blue-700 text-sm">Financial freedom through algorithmic innovation</p>
              <div className="text-2xl font-bold text-blue-600 mt-2">{agentData.avgJackieResonance}</div>
            </div>
            <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800 mb-2">💎 Perseverance</h4>
              <p className="text-green-700 text-sm">Continuous learning and adaptation</p>
              <div className="text-2xl font-bold text-green-600 mt-2">98.7%</div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
              <h4 className="font-semibold text-purple-800 mb-2">🌟 Excellence</h4>
              <p className="text-purple-700 text-sm">Superior performance in all dimensions</p>
              <div className="text-2xl font-bold text-purple-600 mt-2">{agentData.avgNarrativeEnergy}</div>
            </div>
            <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg">
              <h4 className="font-semibold text-orange-800 mb-2">🔥 Courage</h4>
              <p className="text-orange-700 text-sm">Bold decisions in uncertain markets</p>
              <div className="text-2xl font-bold text-orange-600 mt-2">94.2%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFinancialFreedom = () => (
    <div className="space-y-6">
      {/* FIRE Plan Overview */}
      <div className="bg-gradient-to-br from-emerald-600 to-green-700 rounded-2xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-4">💎 Financial Independence Plan</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2">Current Status</h3>
            <div className="text-3xl font-bold">${agentData.financialGap.toLocaleString()}</div>
            <div className="text-sm text-green-200">Annual income gap</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2">Target Timeline</h3>
            <div className="text-3xl font-bold">{agentData.fireTimeline} Years</div>
            <div className="text-sm text-green-200">To financial freedom</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2">Strategy Mix</h3>
            <div className="text-lg font-semibold">12% + 8%</div>
            <div className="text-sm text-green-200">Aggressive + Passive</div>
          </div>
        </div>
      </div>

      {/* Strategy Implementation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-gray-800">📈 Investment Strategies</h3>
          <div className="space-y-4">
            {[
              { name: 'Aggressive Growth Portfolio', allocation: '60%', return: '12%', risk: 'High' },
              { name: 'Dividend Growth Stocks', allocation: '20%', return: '8%', risk: 'Medium' },
              { name: 'Options Trading Income', allocation: '15%', return: '15%', risk: 'High' },
              { name: 'Emergency Cash Fund', allocation: '5%', return: '2%', risk: 'Low' }
            ].map((strategy, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">{strategy.name}</div>
                  <div className="text-sm text-gray-600">Risk: {strategy.risk}</div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-green-600">{strategy.return}</div>
                  <div className="text-sm text-gray-600">{strategy.allocation}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-gray-800">🎯 Milestones</h3>
          <div className="space-y-3">
            {[
              { milestone: 'Emergency Fund Complete', status: 'completed', amount: '$25,000' },
              { milestone: 'High-Interest Debt Eliminated', status: 'completed', amount: '$15,000' },
              { milestone: 'Investment Portfolio $100K', status: 'in-progress', amount: '$78,000' },
              { milestone: 'Passive Income $50K/year', status: 'pending', amount: '$32,000' },
              { milestone: 'Financial Independence', status: 'pending', amount: '$108,000' }
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    item.status === 'completed' ? 'bg-green-500' :
                    item.status === 'in-progress' ? 'bg-yellow-500' : 'bg-gray-400'
                  }`}></div>
                  <div>
                    <div className="font-medium text-sm">{item.milestone}</div>
                  </div>
                </div>
                <div className="text-sm font-semibold text-gray-700">{item.amount}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Options Trading Integration */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">📊 Advanced Options Trading System</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">47</div>
            <div className="text-sm text-blue-800">Active Strategies</div>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">$12,450</div>
            <div className="text-sm text-green-800">Monthly Income</div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">73%</div>
            <div className="text-sm text-purple-800">Win Rate</div>
          </div>
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">1.8</div>
            <div className="text-sm text-orange-800">Profit Factor</div>
          </div>
        </div>
        
        <div className="mt-6">
          <h4 className="font-semibold mb-3">🎯 Active Options Strategies</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { strategy: 'Covered Calls', positions: 12, pnl: '+$2,450', iv: '23.5%' },
              { strategy: 'Cash-Secured Puts', positions: 8, pnl: '+$1,890', iv: '28.2%' },
              { strategy: 'Iron Condors', positions: 15, pnl: '+$3,120', iv: '31.7%' },
              { strategy: 'Calendar Spreads', positions: 6, pnl: '+$890', iv: '26.8%' },
              { strategy: 'Butterfly Spreads', positions: 4, pnl: '+$650', iv: '29.1%' },
              { strategy: 'Straddles', positions: 2, pnl: '-$280', iv: '35.4%' }
            ].map((strategy, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-sm">{strategy.strategy}</div>
                  <div className="text-xs text-gray-600">{strategy.positions} positions • IV: {strategy.iv}</div>
                </div>
                <div className={`font-semibold text-sm ${
                  strategy.pnl.startsWith('+') ? 'text-green-600' : 'text-red-600'
                }`}>
                  {strategy.pnl}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      {/* System Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-gray-800">📊 System Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={[
              { time: '00:00', cpu: 45, memory: 62, network: 23 },
              { time: '04:00', cpu: 52, memory: 68, network: 31 },
              { time: '08:00', cpu: 78, memory: 85, network: 67 },
              { time: '12:00', cpu: 82, memory: 89, network: 72 },
              { time: '16:00', cpu: 65, memory: 75, network: 45 },
              { time: '20:00', cpu: 58, memory: 71, network: 38 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="cpu" stroke="#3B82F6" strokeWidth={2} name="CPU %" />
              <Line type="monotone" dataKey="memory" stroke="#10B981" strokeWidth={2} name="Memory %" />
              <Line type="monotone" dataKey="network" stroke="#F59E0B" strokeWidth={2} name="Network %" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-gray-800">🎯 Trading Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={[
              { date: 'Mon', profit: 1200, volume: 15000 },
              { date: 'Tue', profit: 1890, volume: 18500 },
              { date: 'Wed', profit: 2340, volume: 22000 },
              { date: 'Thu', profit: 1950, volume: 19800 },
              { date: 'Fri', profit: 2680, volume: 26500 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value, name) => [
                name === 'profit' ? `${value}` : value.toLocaleString(),
                name === 'profit' ? 'Profit' : 'Volume'
              ]} />
              <Area type="monotone" dataKey="profit" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">📈 Advanced Analytics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { metric: 'Total PnL', value: '$47,230', change: '+12.3%', color: 'green' },
            { metric: 'Win Rate', value: '68.7%', change: '+2.1%', color: 'blue' },
            { metric: 'Sharpe Ratio', value: '1.84', change: '+0.15', color: 'purple' },
            { metric: 'Max Drawdown', value: '3.2%', change: '-0.8%', color: 'red' },
            { metric: 'Avg Trade', value: '$340', change: '+$23', color: 'green' },
            { metric: 'Profit Factor', value: '2.1', change: '+0.3', color: 'blue' }
          ].map((item, index) => (
            <div key={index} className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-sm text-gray-600 mb-1">{item.metric}</div>
              <div className="text-lg font-bold text-gray-800">{item.value}</div>
              <div className={`text-xs ${
                item.change.startsWith('+') ? 'text-green-600' : 
                item.change.startsWith('-') ? 'text-red-600' : 'text-gray-600'
              }`}>
                {item.change}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Agent Performance Distribution */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">🤖 Agent Performance Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={[
                { name: 'Market Data', value: 25, fill: '#3B82F6' },
                { name: 'Technical Analysis', value: 22, fill: '#10B981' },
                { name: 'Risk Management', value: 18, fill: '#F59E0B' },
                { name: 'Options Trading', value: 15, fill: '#8B5CF6' },
                { name: 'DeFi Integration', value: 12, fill: '#EF4444' },
                { name: 'Other Agents', value: 8, fill: '#6B7280' }
              ]}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard': return renderDashboard();
      case 'agents': return renderAgentNetwork();
      case 'trading': return renderTradingFloor();
      case 'dragons': return renderDragonPatterns();
      case 'onnx': return renderONNXModels();
      case 'narrative': return renderNarrativeSpace();
      case 'freedom': return renderFinancialFreedom();
      case 'analytics': return renderAnalytics();
      default: return renderDashboard();
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Sidebar */}
      <div className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg z-50">
        <div className="p-6">
          <h1 className="text-xl font-bold text-gray-800 mb-2">🎭 OCTOTRIE</h1>
          <p className="text-sm text-gray-600">Autonomous Trading Agents</p>
        </div>
        
        <nav className="px-4">
          {navigationItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full text-left px-4 py-3 rounded-lg mb-2 transition-all ${
                activeSection === item.id
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
        
        {/* System Status */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-800">System Online</span>
            </div>
            <div className="text-xs text-green-600 mt-1">
              {agentData.activeAgents} agents active • {agentData.systemHealth}% health
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 p-6">
        {renderContent()}
      </div>

      {/* Floating Action Button */}
      <button className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center">
        <span className="text-2xl">🚀</span>
      </button>
    </div>
  );
};

export default OctotrieUXDesign; text-gray-800">🤖 Agent Network Status</h3>
        <div className="space-y-3">
          {agents.slice(0, 6).map(agent => (
            <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: dimensionColors[agent.dimension] }}
                ></div>
                <div>
                  <div className="font-medium text-sm">{agent.name}</div>
                  <div className="text-xs text-gray-500">{agent.dimension}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-semibold text-green-600">{agent.resonance}</div>
                <div className="text-xs text-gray-500">Energy: {agent.energy}</div>
              </div>
            </div>
          ))}
        </div>
        
        <button className="w-full mt-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:shadow-lg transition-all">
          View All Agents →
        </button>
      </div>

      {/* Financial Freedom Progress */}
      <div className="lg:col-span-3 bg-gradient-to-r from-green-600 to-emerald-700 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-4">💎 Financial Freedom Journey</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/10 rounded-lg p-4">
            <h4 className="font-semibold mb-2">Current Gap Analysis</h4>
            <div className="text-2xl font-bold">${agentData.financialGap.toLocaleString()}</div>
            <div className="text-sm text-green-200">Annual passive income needed</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h4 className="font-semibold mb-2">FIRE Timeline</h4>
            <div className="text-2xl font-bold">{agentData.fireTimeline} Years</div>
            <div className="text-sm text-green-200">To financial independence</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h4 className="font-semibold mb-2">Strategy Mix</h4>
            <div className="text-sm">12% Aggressive + 8% Passive</div>
            <div className="text-sm text-green-200">Optimized return strategy</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAgentNetwork = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">🤖 Distributed Agent Network</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {agents.map(agent => (
            <div key={agent.id} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-800">{agent.name}</h3>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-green-600 font-medium">ACTIVE</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Dimension:</span>
                  <span 
                    className="px-2 py-1 rounded-full text-xs font-medium text-white"
                    style={{ backgroundColor: dimensionColors[agent.dimension] }}
                  >
                    {agent.dimension}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Jackie Resonance:</span>
                  <span className="text-sm font-semibold text-purple-600">{agent.resonance}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Narrative Energy:</span>
                  <span className="text-sm font-semibold text-blue-600">{agent.energy}</span>
                </div>
                
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Performance</span>
                    <span>{Math.round(agent.resonance * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${agent.resonance * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Agent Communication Matrix */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">📡 Inter-Agent Communication</h3>
        <div className="bg-black rounded-lg p-4 font-mono text-green-400 text-sm max-h-64 overflow-y-auto">
          <div>[10:30:15] 🏎️ Market Data → 📈 Technical Analysis: "AAPL significant move detected: $152.00 (+1.0%)"</div>
          <div>[10:30:17] 📈 Technical Analysis → 💰 Personal Finance: "BUY signal generated (confidence: 0.89)"</div>
          <div>[10:30:20] 🐉 Dragon Patterns → 🧠 Neural Network: "Fractal dimension: 1.67, complexity: 0.84"</div>
          <div>[10:30:22] 🔥 DeFi Integration → 📊 Trading Floor: "Yield opportunity: 12.5% APY on USDC"</div>
          <div>[10:30:25] 🎭 Narrative Space → All Agents: "Jackie resonance elevated to 0.91"</div>
          <div>[10:30:28] 💎 Financial Freedom → 💰 Personal Finance: "FIRE timeline updated: 2.8 years"</div>
        </div>
      </div>
    </div>
  );

  const renderTradingFloor = () => (
    <div className="space-y-6">
      {/* Trading Signals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-gray-800">📊 Live Trading Signals</h3>
          <div className="space-y-3">
            {[
              { symbol: 'AAPL', signal: 'STRONG_BUY', confidence: 0.92, price: '$152.00', change: '+1.0%' },
              { symbol: 'TSLA', signal: 'BUY', confidence: 0.78, price: '$245.50', change: '+0.5%' },
              { symbol: 'SPY', signal: 'HOLD', confidence: 0.65, price: '$425.30', change: '-0.1%' },
              { symbol: 'BTC', signal: 'SELL', confidence: 0.83, price: '$42,150', change: '-2.3%' }
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="font-bold text-lg">{item.symbol}</div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    item.signal === 'STRONG_BUY' ? 'bg-green-600 text-white' :
                    item.signal === 'BUY' ? 'bg-green-500 text-white' :
                    item.signal === 'HOLD' ? 'bg-yellow-500 text-white' :
                    'bg-red-500 text-white'
                  }`}>
                    {item.signal}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{item.price}</div>
                  <div className={`text-sm ${item.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {item.change}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">Conf: {item.confidence}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Portfolio Performance */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-gray-800">💼 Portfolio Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={[
              { time: '09:00', value: 100000 },
              { time: '10:00', value: 101200 },
              { time: '11:00', value: 102800 },
              { time: '12:00', value: 101900 },
              { time: '13:00', value: 103500 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Portfolio Value']} />
              <Line type="monotone" dataKey="value" stroke="#10B981" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk Management */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">⚠️ Risk Management Dashboard</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">2.1%</div>
            <div className="text-sm text-green-800">Portfolio VaR</div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">0.85</div>
            <div className="text-sm text-blue-800">Sharpe Ratio</div>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">68%</div>
            <div className="text-sm text-yellow-800">Win Rate</div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">1.45</div>
            <div className="text-sm text-purple-800">Profit Factor</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDragonPatterns = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-purple-900 to-indigo-900 rounded-2xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-4">🐉 Black Mirror Siamese Dragons</h2>
        <p className="text-purple-200 mb-6">Recursive pattern generation with JAX42 optimization and Prince Sloan rainbow transformations</p>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Dragon Alpha */}
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">🐉 Dragon Alpha</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Complexity Score:</span>
                <span className="font-semibold">0.847</span>
              </div>
              <div className="flex justify-between">
                <span>Fractal Dimension:</span>
                <span className="font-semibold">1.632</span>
              </div>
              <div className="flex justify-between">
                <span>Siamese Connection:</span>
                <span className="font-semibold">0.923</span>
              </div>
              <div className="flex justify-between">
                <span>Rainbow Factor:</span>
                <span className="font-semibold text-yellow-300">1.156</span>
              </div>
            </div>
            
            {/* Simulated pattern visualization */}
            <div className="mt-4 h-32 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-lg flex items-center justify-center">
              <div className="text-6xl animate-spin-slow">🌀</div>
            </div>
          </div>

          {/* Dragon Beta */}
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">🐉 Dragon Beta</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Complexity Score:</span>
                <span className="font-semibold">0.791</span>
              </div>
              <div className="flex justify-between">
                <span>Fractal Dimension:</span>
                <span className="font-semibold">1.485</span>
              </div>
              <div className="flex justify-between">
                <span>Siamese Connection:</span>
                <span className="font-semibold">0.923</span>
              </div>
              <div className="flex justify-between">
                <span>Courage Factor:</span>
                <span className="font-semibold text-orange-300">0.934</span>
              </div>
            </div>
            
            {/* Simulated pattern visualization */}
            <div className="mt-4 h-32 bg-gradient-to-br from-green-500/30 to-teal-500/30 rounded-lg flex items-center justify-center">
              <div className="text-6xl animate-pulse">✨</div>
            </div>
          </div>
        </div>

        {/* Pattern Generation Controls */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors">
            Generate Patterns
          </button>
          <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium transition-colors">
            Merge Sort
          </button>
          <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium transition-colors">
            Spiral Display
          </button>
          <button className="bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded-lg font-medium transition-colors">
            JAX42 Optimize
          </button>
        </div>
      </div>

      {/* Pattern Analytics */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-gray-800">📊 Pattern Analytics</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={[
            { iteration: 1, alpha: 0.65, beta: 0.58, fusion: 0.72 },
            { iteration: 2, alpha: 0.72, beta: 0.68, fusion: 0.78 },
            { iteration: 3, alpha: 0.84, beta: 0.79, fusion: 0.85 },
            { iteration: 4, alpha: 0.85, beta: 0.81, fusion: 0.92 },
            { iteration: 5, alpha: 0.87, beta: 0.85, fusion: 0.94 }
          ]}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="iteration" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="alpha" stackId="1" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
            <Area type="monotone" dataKey="beta" stackId="1" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
            <Area type="monotone" dataKey="fusion" stackId="1" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.6} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const renderONNXModels = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">🧠 Advanced ONNX Models</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[
            { name: '🤖 Transformer GPT', params: '117M', latency: '45ms', accuracy: '94.2%', status: 'loaded' },
            { name: '👁️ Vision Transformer', params: '86M', latency: '32ms', accuracy: '91.8%', status: 'loaded' },
            { name: '🎨 Diffusion U-Net', params: '860M', latency: '120ms', accuracy: '89.5%', status: 'loading' },
            { name: '🐉 Dragon Classifier', params: '25M', latency: '18ms', accuracy: '96.7%', status: 'loaded' },
            { name: '📈 Time Series LSTM', params: '5.4M', latency: '12ms', accuracy: '88.3%', status: 'loaded' },
            { name: '🌈 Multi-Modal Fusion', params: '45M', latency: '58ms', accuracy: '92.1%', status: 'loaded' }
          ].map((model, index) => (
            <div key={index} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-800">{model.name}</h3>
                <div className={`w-3 h-3 rounded-full ${
                  model.status === 'loaded' ? 'bg-green-500' : 
                  model.status === 'loading' ? 'bg-yellow-500 animate-pulse' : 'bg-gray-400'
                }`}></div>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Parameters:</span>
                  <span className="font-medium">{model.params}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Latency:</span>
                  <span className="font-medium text-blue-600">{model.latency}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Accuracy:</span>
                  <span className="font-medium text-green-600">{model.accuracy}</span>
                </div>
              </div>
              
              <button className="w-full mt-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:shadow-lg transition-all">
                Run Inference
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Model Performance Chart */}
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4