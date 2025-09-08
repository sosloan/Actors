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
        <div className="text-center text-gray-600">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">🎭 OCTOTRIE Command Center</h2>
          <p>Distributed Autonomous Agents • Jackie Robinson Resonance • 8D Narrative</p>
        </div>
      </div>

      {/* Floating Action Button */}
      <button className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center">
        <span className="text-2xl">🚀</span>
      </button>
    </div>
  );
};

export default OctotrieUXDesign; 