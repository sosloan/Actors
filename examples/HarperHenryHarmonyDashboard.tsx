import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Radar, Legend
} from 'recharts';

interface PortfolioAsset {
  id: string;
  name: string;
  type: 'harmony' | 'homestay' | 'cultural' | 'traditional_craft';
  harmonyType: 'Family' | 'Cultural' | 'Farm' | 'Urban' | 'Religious' | 'Artistic' | 'Academic' | 'Healing';
  weight: number;
  value: number;
  culturalScore: number;
  economicScore: number;
  sustainabilityScore: number;
  harmonyScore: number;
}

interface HarmonyBuilder {
  id: string;
  name: string;
  builderType: string;
  optimizationTarget: number;
  currentValue: number;
  isOptimized: boolean;
  slotsUsed: number;
  maxSlots: number;
  harmonyTypes: string[];
}

interface OptimizationResult {
  id: string;
  timestamp: string;
  engine: 'value_creation' | 'concrete_type_inference' | 'portfolio_optimization' | 'homestay_first_class' | 'cem_portfolio' | 'harper_henry_harmony';
  score: number;
  confidence: number;
  culturalImpact: number;
  economicVelocity: number;
  sustainability: number;
  harmony: number;
}

interface TraditionalCraft {
  id: string;
  craftName: string;
  craftType: string;
  difficultyLevel: number;
  culturalSignificance: number;
  learningDurationHours: number;
  materialsAvailable: number;
  masterArtisanAvailable: boolean;
  culturalStoryScore: number;
  economicValueScore: number;
  sustainabilityScore: number;
  communityImpactScore: number;
}

const HarperHenryHarmonyDashboard: React.FC = () => {
  const [portfolioAssets, setPortfolioAssets] = useState<PortfolioAsset[]>([
    {
      id: '1',
      name: '🏡 Family Homestay Portfolio',
      type: 'homestay',
      harmonyType: 'Family',
      weight: 0.15,
      value: 15000,
      culturalScore: 0.92,
      economicScore: 0.78,
      sustainabilityScore: 0.88,
      harmonyScore: 0.94
    },
    {
      id: '2',
      name: '🎭 Cultural Exchange Portfolio',
      type: 'cultural',
      harmonyType: 'Cultural',
      weight: 0.20,
      value: 20000,
      culturalScore: 0.98,
      economicScore: 0.72,
      sustainabilityScore: 0.90,
      harmonyScore: 0.96
    },
    {
      id: '3',
      name: '🌾 Farm Stay Portfolio',
      type: 'homestay',
      harmonyType: 'Farm',
      weight: 0.12,
      value: 12000,
      culturalScore: 0.85,
      economicScore: 0.80,
      sustainabilityScore: 0.95,
      harmonyScore: 0.88
    },
    {
      id: '4',
      name: '🏙️ Urban Experience Portfolio',
      type: 'homestay',
      harmonyType: 'Urban',
      weight: 0.18,
      value: 18000,
      culturalScore: 0.75,
      economicScore: 0.90,
      sustainabilityScore: 0.70,
      harmonyScore: 0.82
    },
    {
      id: '5',
      name: '🙏 Religious Pilgrimage Portfolio',
      type: 'harmony',
      harmonyType: 'Religious',
      weight: 0.08,
      value: 8000,
      culturalScore: 0.95,
      economicScore: 0.65,
      sustainabilityScore: 0.85,
      harmonyScore: 0.93
    },
    {
      id: '6',
      name: '🎨 Artistic Retreat Portfolio',
      type: 'cultural',
      harmonyType: 'Artistic',
      weight: 0.15,
      value: 15000,
      culturalScore: 0.97,
      economicScore: 0.68,
      sustainabilityScore: 0.82,
      harmonyScore: 0.91
    },
    {
      id: '7',
      name: '📚 Academic Exchange Portfolio',
      type: 'harmony',
      harmonyType: 'Academic',
      weight: 0.10,
      value: 10000,
      culturalScore: 0.88,
      economicScore: 0.85,
      sustainabilityScore: 0.78,
      harmonyScore: 0.87
    },
    {
      id: '8',
      name: '🧘 Healing & Wellness Portfolio',
      type: 'harmony',
      harmonyType: 'Healing',
      weight: 0.02,
      value: 2000,
      culturalScore: 0.90,
      economicScore: 0.75,
      sustainabilityScore: 0.92,
      harmonyScore: 0.89
    }
  ]);

  const [harmonyBuilders, setHarmonyBuilders] = useState<HarmonyBuilder[]>([
    {
      id: 'builder-1',
      name: 'Primary Harmony Builder',
      builderType: 'standard',
      optimizationTarget: 0.90,
      currentValue: 0.87,
      isOptimized: false,
      slotsUsed: 6,
      maxSlots: 9,
      harmonyTypes: ['Family', 'Cultural', 'Farm', 'Urban', 'Artistic', 'Academic']
    },
    {
      id: 'builder-2',
      name: 'Elite BÏG Builder',
      builderType: 'elite',
      optimizationTarget: 0.95,
      currentValue: 0.92,
      isOptimized: true,
      slotsUsed: 9,
      maxSlots: 9,
      harmonyTypes: ['Family', 'Cultural', 'Farm', 'Urban', 'Religious', 'Artistic', 'Academic', 'Healing']
    }
  ]);

  const [optimizationResults, setOptimizationResults] = useState<OptimizationResult[]>([
    {
      id: 'opt-1',
      timestamp: new Date().toISOString(),
      engine: 'harper_henry_harmony',
      score: 0.92,
      confidence: 0.95,
      culturalImpact: 0.94,
      economicVelocity: 0.82,
      sustainability: 0.88,
      harmony: 0.93
    },
    {
      id: 'opt-2',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      engine: 'portfolio_optimization',
      score: 0.89,
      confidence: 0.90,
      culturalImpact: 0.90,
      economicVelocity: 0.85,
      sustainability: 0.86,
      harmony: 0.88
    },
    {
      id: 'opt-3',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      engine: 'value_creation',
      score: 0.87,
      confidence: 0.88,
      culturalImpact: 0.92,
      economicVelocity: 0.78,
      sustainability: 0.85,
      harmony: 0.86
    }
  ]);

  const [traditionalCrafts, setTraditionalCrafts] = useState<TraditionalCraft[]>([
    {
      id: 'craft-1',
      craftName: 'Japanese Pottery',
      craftType: 'ceramic',
      difficultyLevel: 0.75,
      culturalSignificance: 0.95,
      learningDurationHours: 120,
      materialsAvailable: 0.85,
      masterArtisanAvailable: true,
      culturalStoryScore: 0.98,
      economicValueScore: 0.82,
      sustainabilityScore: 0.90,
      communityImpactScore: 0.88
    },
    {
      id: 'craft-2',
      craftName: 'Indian Textile Weaving',
      craftType: 'textile',
      difficultyLevel: 0.68,
      culturalSignificance: 0.92,
      learningDurationHours: 80,
      materialsAvailable: 0.90,
      masterArtisanAvailable: true,
      culturalStoryScore: 0.94,
      economicValueScore: 0.78,
      sustainabilityScore: 0.88,
      communityImpactScore: 0.92
    },
    {
      id: 'craft-3',
      craftName: 'Mexican Woodcarving',
      craftType: 'wood',
      difficultyLevel: 0.72,
      culturalSignificance: 0.88,
      learningDurationHours: 100,
      materialsAvailable: 0.80,
      masterArtisanAvailable: true,
      culturalStoryScore: 0.90,
      economicValueScore: 0.85,
      sustainabilityScore: 0.82,
      communityImpactScore: 0.86
    }
  ]);

  const [systemMetrics, setSystemMetrics] = useState({
    totalValue: 100000,
    culturalImpactScore: 0.91,
    economicVelocity: 0.79,
    sustainabilityScore: 0.86,
    harmonyScore: 0.90,
    optimizationConfidence: 0.93,
    activeBuilders: 2,
    totalHarmonyTypes: 8,
    traditionalCraftsCount: 3
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        ...prev,
        culturalImpactScore: Math.max(0.5, Math.min(1.0, prev.culturalImpactScore + (Math.random() - 0.5) * 0.05)),
        economicVelocity: Math.max(0.5, Math.min(1.0, prev.economicVelocity + (Math.random() - 0.5) * 0.05)),
        sustainabilityScore: Math.max(0.5, Math.min(1.0, prev.sustainabilityScore + (Math.random() - 0.5) * 0.03)),
        harmonyScore: Math.max(0.5, Math.min(1.0, prev.harmonyScore + (Math.random() - 0.5) * 0.02))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B9D'];

  const renderSystemOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-purple-200 text-sm">Total Portfolio Value</p>
            <p className="text-3xl font-bold">${(systemMetrics.totalValue / 1000).toFixed(0)}K</p>
          </div>
          <div className="text-4xl">💼</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-cyan-500 to-cyan-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-cyan-200 text-sm">Cultural Impact</p>
            <p className="text-3xl font-bold">{(systemMetrics.culturalImpactScore * 100).toFixed(0)}%</p>
          </div>
          <div className="text-4xl">🎭</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-green-200 text-sm">Sustainability</p>
            <p className="text-3xl font-bold">{(systemMetrics.sustainabilityScore * 100).toFixed(0)}%</p>
          </div>
          <div className="text-4xl">🌿</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-orange-200 text-sm">Harmony Score</p>
            <p className="text-3xl font-bold">{(systemMetrics.harmonyScore * 100).toFixed(0)}%</p>
          </div>
          <div className="text-4xl">☯️</div>
        </div>
      </div>
    </div>
  );

  const renderPortfolioAllocation = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🎯 Portfolio Allocation
      </h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-700 rounded-xl p-4">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={portfolioAssets}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, weight }) => `${name.split(' ')[0]} ${(weight * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="weight"
              >
                {portfolioAssets.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="space-y-3">
          {portfolioAssets.map((asset, index) => (
            <div key={asset.id} className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{asset.name}</h4>
                <span className="text-sm px-2 py-1 bg-blue-600 rounded">{asset.harmonyType}</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-400">Weight:</span>
                  <span className="ml-2 text-blue-400 font-semibold">{(asset.weight * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-gray-400">Value:</span>
                  <span className="ml-2 text-green-400 font-semibold">${(asset.value / 1000).toFixed(0)}K</span>
                </div>
                <div>
                  <span className="text-gray-400">Cultural:</span>
                  <span className="ml-2 text-cyan-400 font-semibold">{(asset.culturalScore * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-gray-400">Harmony:</span>
                  <span className="ml-2 text-purple-400 font-semibold">{(asset.harmonyScore * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderHarmonyBuilders = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🏗️ Harmony Builders
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {harmonyBuilders.map(builder => (
          <div key={builder.id} className="bg-gray-700 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-lg">{builder.name}</h4>
              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                builder.isOptimized ? 'bg-green-500' : 'bg-yellow-500'
              }`}>
                {builder.isOptimized ? 'OPTIMIZED' : 'OPTIMIZING'}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Type:</span>
                <span className="font-semibold capitalize">{builder.builderType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Target:</span>
                <span className="text-green-400 font-semibold">{(builder.optimizationTarget * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Current:</span>
                <span className="text-blue-400 font-semibold">{(builder.currentValue * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Slots:</span>
                <span className="text-orange-400 font-semibold">{builder.slotsUsed}/{builder.maxSlots}</span>
              </div>
            </div>
            <div className="mt-3">
              <span className="text-gray-400 text-xs">Harmony Types:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {builder.harmonyTypes.map((type, idx) => (
                  <span key={idx} className="bg-gray-600 px-2 py-0.5 rounded text-xs">
                    {type}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderOptimizationEngines = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🧠 Optimization Engines
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {optimizationResults.map(result => (
          <div key={result.id} className="bg-gray-700 rounded-xl p-4">
            <h4 className="font-semibold mb-3 capitalize">{result.engine.replace(/_/g, ' ')}</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Score:</span>
                <span className="text-green-400 font-semibold">{(result.score * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Confidence:</span>
                <span className="text-blue-400 font-semibold">{(result.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Cultural Impact:</span>
                <span className="text-cyan-400 font-semibold">{(result.culturalImpact * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Harmony:</span>
                <span className="text-purple-400 font-semibold">{(result.harmony * 100).toFixed(0)}%</span>
              </div>
            </div>
            <div className="mt-2 text-xs text-gray-400">
              {new Date(result.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTraditionalCrafts = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🎨 Traditional Crafts Portfolio
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {traditionalCrafts.map(craft => (
          <div key={craft.id} className="bg-gray-700 rounded-xl p-4">
            <h4 className="font-semibold mb-3">{craft.craftName}</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Type:</span>
                <span className="font-semibold capitalize">{craft.craftType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Cultural Significance:</span>
                <span className="text-cyan-400 font-semibold">{(craft.culturalSignificance * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Learning Duration:</span>
                <span className="text-blue-400 font-semibold">{craft.learningDurationHours}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Economic Value:</span>
                <span className="text-green-400 font-semibold">{(craft.economicValueScore * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Sustainability:</span>
                <span className="text-green-400 font-semibold">{(craft.sustainabilityScore * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Master Available:</span>
                <span className={craft.masterArtisanAvailable ? 'text-green-400' : 'text-red-400'}>
                  {craft.masterArtisanAvailable ? '✓' : '✗'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderPerformanceMetrics = () => {
    const radarData = [
      {
        metric: 'Cultural Impact',
        value: systemMetrics.culturalImpactScore * 100
      },
      {
        metric: 'Economic Velocity',
        value: systemMetrics.economicVelocity * 100
      },
      {
        metric: 'Sustainability',
        value: systemMetrics.sustainabilityScore * 100
      },
      {
        metric: 'Harmony',
        value: systemMetrics.harmonyScore * 100
      },
      {
        metric: 'Confidence',
        value: systemMetrics.optimizationConfidence * 100
      }
    ];

    return (
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-6 flex items-center">
          📊 Performance Metrics
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-700 rounded-xl p-4">
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Performance" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-2">📈 Cultural Impact</h4>
              <div className="text-3xl font-bold text-cyan-400">
                {(systemMetrics.culturalImpactScore * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-gray-400 mt-1">Cultural exchange harmony</p>
            </div>
            <div className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-2">⚡ Economic Velocity</h4>
              <div className="text-3xl font-bold text-green-400">
                {(systemMetrics.economicVelocity * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-gray-400 mt-1">Value creation rate</p>
            </div>
            <div className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-2">🌿 Sustainability</h4>
              <div className="text-3xl font-bold text-green-400">
                {(systemMetrics.sustainabilityScore * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-gray-400 mt-1">Long-term viability</p>
            </div>
            <div className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-2">☯️ Harmony</h4>
              <div className="text-3xl font-bold text-purple-400">
                {(systemMetrics.harmonyScore * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-gray-400 mt-1">Overall balance</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center">
            🎭 HARPER HENRY HARMONY
          </h1>
          <p className="text-gray-400 text-lg">
            Advanced AI-Driven Portfolio Optimization with Cultural Exchange Harmony
          </p>
          <p className="text-gray-500 text-sm mt-1 italic">
            "Where mathematical precision meets cultural exchange harmony"
          </p>
        </div>

        {/* System Overview */}
        {renderSystemOverview()}

        {/* Portfolio Allocation */}
        {renderPortfolioAllocation()}

        {/* Harmony Builders */}
        {renderHarmonyBuilders()}

        {/* Optimization Engines */}
        {renderOptimizationEngines()}

        {/* Traditional Crafts */}
        {renderTraditionalCrafts()}

        {/* Performance Metrics */}
        {renderPerformanceMetrics()}
      </div>
    </div>
  );
};

export default HarperHenryHarmonyDashboard;
