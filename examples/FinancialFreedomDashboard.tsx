import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, RadialBarChart, RadialBar 
} from 'recharts';

interface FIREGoal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  targetDate: string;
  monthlyContribution: number;
  expectedReturn: number;
  priority: 'high' | 'medium' | 'low';
  category: 'retirement' | 'house' | 'education' | 'business' | 'travel' | 'emergency';
  
  // 🏎️ Ferrari Speed Metrics
  accelerationRate: number;        // Monthly growth acceleration
  velocity: number;               // Current growth velocity
  momentum: number;              // Financial momentum score
  
  // ⭐ Starry Precision Metrics
  precisionScore: number;        // Goal precision accuracy
  compoundAccuracy: number;      // Compound interest accuracy
  projectionConfidence: number;  // Projection confidence level
  
  // 🎡 Ferris Wheel Dynamics
  wheelPosition: number;         // Progress wheel position (0-360)
  rotationSpeed: number;         // Goal rotation speed
  circularProgress: number;      // Circular progress percentage
}

interface PassiveIncome {
  id: string;
  source: string;
  monthlyAmount: number;
  annualAmount: number;
  growthRate: number;
  riskLevel: 'low' | 'medium' | 'high';
  category: 'dividends' | 'rental' | 'defi' | 'royalties' | 'business';
  
  // 🏎️ Ferrari Speed Metrics
  incomeVelocity: number;         // Income growth velocity
  accelerationFactor: number;     // Growth acceleration factor
  momentumScore: number;          // Income momentum score
  
  // ⭐ Starry Precision Metrics
  yieldAccuracy: number;          // Yield calculation accuracy
  riskPrecision: number;          // Risk assessment precision
  growthConfidence: number;       // Growth projection confidence
  
  // 🎡 Ferris Wheel Dynamics
  incomeWheel: number;           // Income wheel position
  rotationFactor: number;        // Rotation speed factor
  circularYield: number;         // Circular yield percentage
}

const FinancialFreedomDashboard: React.FC = () => {
  // 🎡 Ferris Wheel Animation State
  const [wheelRotation, setWheelRotation] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);
  
  const [fireGoals, setFireGoals] = useState<FIREGoal[]>([
    {
      id: '1',
      name: '🏠 Dream Home',
      targetAmount: 500000,
      currentAmount: 125000,
      targetDate: '2027-12-31',
      monthlyContribution: 2500,
      expectedReturn: 7,
      priority: 'high',
      category: 'house',
      
      // 🏎️ Ferrari Speed Metrics
      accelerationRate: 1.15,
      velocity: 2850,
      momentum: 0.87,
      
      // ⭐ Starry Precision Metrics
      precisionScore: 99.2,
      compoundAccuracy: 99.8,
      projectionConfidence: 94.5,
      
      // 🎡 Ferris Wheel Dynamics
      wheelPosition: 75,
      rotationSpeed: 2.1,
      circularProgress: 25
    },
    {
      id: '2',
      name: '🎯 FIRE Target',
      targetAmount: 2000000,
      currentAmount: 450000,
      targetDate: '2035-12-31',
      monthlyContribution: 5000,
      expectedReturn: 8,
      priority: 'high',
      category: 'retirement',
      
      // 🏎️ Ferrari Speed Metrics
      accelerationRate: 1.08,
      velocity: 5200,
      momentum: 0.92,
      
      // ⭐ Starry Precision Metrics
      precisionScore: 99.5,
      compoundAccuracy: 99.9,
      projectionConfidence: 96.8,
      
      // 🎡 Ferris Wheel Dynamics
      wheelPosition: 135,
      rotationSpeed: 1.8,
      circularProgress: 22.5
    },
    {
      id: '3',
      name: '🎓 Kids Education',
      targetAmount: 300000,
      currentAmount: 75000,
      targetDate: '2030-12-31',
      monthlyContribution: 1000,
      expectedReturn: 6,
      priority: 'medium',
      category: 'education',
      
      // 🏎️ Ferrari Speed Metrics
      accelerationRate: 1.05,
      velocity: 1200,
      momentum: 0.78,
      
      // ⭐ Starry Precision Metrics
      precisionScore: 98.8,
      compoundAccuracy: 99.3,
      projectionConfidence: 91.2,
      
      // 🎡 Ferris Wheel Dynamics
      wheelPosition: 200,
      rotationSpeed: 1.5,
      circularProgress: 25
    }
  ]);

  const [passiveIncome, setPassiveIncome] = useState<PassiveIncome[]>([
    {
      id: '1',
      source: '📈 Dividend Stocks',
      monthlyAmount: 1200,
      annualAmount: 14400,
      growthRate: 5,
      riskLevel: 'medium',
      category: 'dividends',
      
      // 🏎️ Ferrari Speed Metrics
      incomeVelocity: 60,
      accelerationFactor: 1.05,
      momentumScore: 0.85,
      
      // ⭐ Starry Precision Metrics
      yieldAccuracy: 99.1,
      riskPrecision: 94.5,
      growthConfidence: 88.2,
      
      // 🎡 Ferris Wheel Dynamics
      incomeWheel: 45,
      rotationFactor: 1.2,
      circularYield: 5.0
    },
    {
      id: '2',
      source: '🏠 Rental Property',
      monthlyAmount: 2500,
      annualAmount: 30000,
      growthRate: 3,
      riskLevel: 'low',
      category: 'rental',
      
      // 🏎️ Ferrari Speed Metrics
      incomeVelocity: 125,
      accelerationFactor: 1.03,
      momentumScore: 0.92,
      
      // ⭐ Starry Precision Metrics
      yieldAccuracy: 99.5,
      riskPrecision: 98.8,
      growthConfidence: 95.1,
      
      // 🎡 Ferris Wheel Dynamics
      incomeWheel: 90,
      rotationFactor: 0.8,
      circularYield: 3.0
    },
    {
      id: '3',
      source: '🌐 DeFi Yield Farming',
      monthlyAmount: 800,
      annualAmount: 9600,
      growthRate: 12,
      riskLevel: 'high',
      category: 'defi',
      
      // 🏎️ Ferrari Speed Metrics
      incomeVelocity: 96,
      accelerationFactor: 1.12,
      momentumScore: 0.75,
      
      // ⭐ Starry Precision Metrics
      yieldAccuracy: 97.8,
      riskPrecision: 89.2,
      growthConfidence: 82.5,
      
      // 🎡 Ferris Wheel Dynamics
      incomeWheel: 180,
      rotationFactor: 2.5,
      circularYield: 12.0
    },
    {
      id: '4',
      source: '💼 Business Revenue',
      monthlyAmount: 3000,
      annualAmount: 36000,
      growthRate: 8,
      riskLevel: 'medium',
      category: 'business',
      
      // 🏎️ Ferrari Speed Metrics
      incomeVelocity: 240,
      accelerationFactor: 1.08,
      momentumScore: 0.88,
      
      // ⭐ Starry Precision Metrics
      yieldAccuracy: 98.9,
      riskPrecision: 92.3,
      growthConfidence: 90.7,
      
      // 🎡 Ferris Wheel Dynamics
      incomeWheel: 270,
      rotationFactor: 1.8,
      circularYield: 8.0
    }
  ]);

  const [currentAge, setCurrentAge] = useState(32);
  const [targetFIREAge, setTargetFIREAge] = useState(45);
  const [currentNetWorth, setCurrentNetWorth] = useState(650000);
  const [targetNetWorth, setTargetNetWorth] = useState(2000000);
  const [monthlyExpenses, setMonthlyExpenses] = useState(8000);

  // Calculate FIRE metrics
  const totalPassiveIncome = passiveIncome.reduce((sum, income) => sum + income.monthlyAmount, 0);
  const fireNumber = monthlyExpenses * 12 * 25; // 25x rule
  const yearsToFIRE = Math.ceil((fireNumber - currentNetWorth) / (totalPassiveIncome * 12 + fireGoals.reduce((sum, goal) => sum + goal.monthlyContribution, 0) * 12));
  const fireAge = currentAge + yearsToFIRE;

  // Generate projection data
  const generateProjectionData = () => {
    const data: any[] = [];
    const currentYear = new Date().getFullYear();
    
    for (let i = 0; i <= 20; i++) {
      const year = currentYear + i;
      const age = currentAge + i;
      const projectedNetWorth = currentNetWorth * Math.pow(1.08, i) + 
        (totalPassiveIncome * 12 + fireGoals.reduce((sum, goal) => sum + goal.monthlyContribution, 0) * 12) * 
        ((Math.pow(1.08, i) - 1) / 0.08);
      
      data.push({
        year,
        age,
        netWorth: Math.round(projectedNetWorth),
        fireNumber: fireNumber,
        passiveIncome: Math.round(totalPassiveIncome * 12 * Math.pow(1.05, i))
      });
    }
    
    return data;
  };

  const projectionData = generateProjectionData();

  const categoryColors = {
    'retirement': '#3B82F6',
    'house': '#10B981',
    'education': '#F59E0B',
    'business': '#8B5CF6',
    'travel': '#EF4444',
    'emergency': '#6B7280'
  };

  const riskColors = {
    'low': '#10B981',
    'medium': '#F59E0B',
    'high': '#EF4444'
  };

  const renderFIREOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-200 text-sm">Current Net Worth</p>
            <p className="text-3xl font-bold">${(currentNetWorth / 1000).toFixed(0)}K</p>
          </div>
          <div className="text-4xl">💰</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-green-200 text-sm">FIRE Number</p>
            <p className="text-3xl font-bold">${(fireNumber / 1000).toFixed(0)}K</p>
          </div>
          <div className="text-4xl">🎯</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-purple-200 text-sm">Years to FIRE</p>
            <p className="text-3xl font-bold">{yearsToFIRE}</p>
          </div>
          <div className="text-4xl">⏰</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-orange-200 text-sm">FIRE Age</p>
            <p className="text-3xl font-bold">{fireAge}</p>
          </div>
          <div className="text-4xl">🚀</div>
        </div>
      </div>
    </div>
  );

  const renderPassiveIncomeOverview = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        💰 Passive Income Streams
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {passiveIncome.map(income => (
          <div key={income.id} className="bg-gray-700 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold">{income.source}</h4>
              <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: riskColors[income.riskLevel] }}></div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Monthly:</span>
                <span className="text-green-400 font-semibold">${income.monthlyAmount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Annual:</span>
                <span className="text-blue-400 font-semibold">${income.annualAmount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Growth:</span>
                <span className="text-purple-400 font-semibold">{income.growthRate}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 p-4 bg-gray-700 rounded-xl">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold">Total Monthly Passive Income:</span>
          <span className="text-2xl font-bold text-green-400">${totalPassiveIncome.toLocaleString()}</span>
        </div>
        <div className="flex justify-between items-center mt-2">
          <span className="text-lg font-semibold">Annual Passive Income:</span>
          <span className="text-2xl font-bold text-blue-400">${(totalPassiveIncome * 12).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );

  const renderFIREGoals = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        🎯 Financial Goals Progress
      </h3>
      <div className="space-y-4">
        {fireGoals.map(goal => {
          const progress = (goal.currentAmount / goal.targetAmount) * 100;
          const monthsRemaining = Math.ceil((new Date(goal.targetDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24 * 30));
          
          return (
            <div key={goal.id} className="bg-gray-700 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-lg">{goal.name}</h4>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    goal.priority === 'high' ? 'bg-red-600' :
                    goal.priority === 'medium' ? 'bg-yellow-600' : 'bg-green-600'
                  }`}>
                    {goal.priority.toUpperCase()}
                  </span>
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: categoryColors[goal.category] }}></div>
                </div>
              </div>
              
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span>Progress: ${goal.currentAmount.toLocaleString()} / ${goal.targetAmount.toLocaleString()}</span>
                  <span className="text-green-400 font-semibold">{progress.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div 
                    className="h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${Math.min(progress, 100)}%`,
                      backgroundColor: categoryColors[goal.category]
                    }}
                  ></div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Target Date:</span>
                  <p className="font-semibold">{new Date(goal.targetDate).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-gray-400">Monthly Contribution:</span>
                  <p className="font-semibold text-green-400">${goal.monthlyContribution.toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-gray-400">Expected Return:</span>
                  <p className="font-semibold text-blue-400">{goal.expectedReturn}%</p>
                </div>
                <div>
                  <span className="text-gray-400">Months Remaining:</span>
                  <p className="font-semibold text-orange-400">{monthsRemaining}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderProjectionChart = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
      <h3 className="text-xl font-bold mb-6 flex items-center">
        📈 Net Worth Projection & FIRE Timeline
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={projectionData}>
          <defs>
            <linearGradient id="netWorthGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
            </linearGradient>
            <linearGradient id="fireNumberGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="age" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1F2937', 
              border: '1px solid #374151',
              borderRadius: '8px',
              color: 'white'
            }}
            formatter={(value, name) => [
              `$${(value as number).toLocaleString()}`,
              name === 'netWorth' ? 'Net Worth' : 'FIRE Number'
            ]}
          />
          <Area 
            type="monotone" 
            dataKey="netWorth" 
            stroke="#3B82F6" 
            fillOpacity={1} 
            fill="url(#netWorthGradient)" 
            name="netWorth"
          />
          <Area 
            type="monotone" 
            dataKey="fireNumber" 
            stroke="#10B981" 
            fillOpacity={0.3} 
            fill="url(#fireNumberGradient)" 
            name="fireNumber"
          />
        </AreaChart>
      </ResponsiveContainer>
      
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-700 rounded-xl p-4">
          <h4 className="font-semibold mb-2">🎯 FIRE Milestone</h4>
          <p className="text-2xl font-bold text-green-400">Age {fireAge}</p>
          <p className="text-sm text-gray-400">Target FIRE Age</p>
        </div>
        <div className="bg-gray-700 rounded-xl p-4">
          <h4 className="font-semibold mb-2">💰 Projected Net Worth</h4>
          <p className="text-2xl font-bold text-blue-400">
            ${(projectionData[projectionData.length - 1]?.netWorth / 1000).toFixed(0)}K
          </p>
          <p className="text-sm text-gray-400">At Age {projectionData[projectionData.length - 1]?.age}</p>
        </div>
        <div className="bg-gray-700 rounded-xl p-4">
          <h4 className="font-semibold mb-2">📊 Progress to FIRE</h4>
          <p className="text-2xl font-bold text-purple-400">
            {((currentNetWorth / fireNumber) * 100).toFixed(1)}%
          </p>
          <p className="text-sm text-gray-400">Current Progress</p>
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
            💎 Financial Freedom Dashboard
          </h1>
          <p className="text-gray-400 text-lg">
            Track your journey to Financial Independence, Retire Early (FIRE)
          </p>
        </div>

        {/* FIRE Overview */}
        {renderFIREOverview()}

        {/* Passive Income Overview */}
        {renderPassiveIncomeOverview()}

        {/* FIRE Goals */}
        {renderFIREGoals()}

        {/* Projection Chart */}
        {renderProjectionChart()}

        {/* Action Items */}
        <div className="mt-8 bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6">
          <h3 className="text-xl font-bold mb-6 flex items-center">
            🚀 Next Steps to Accelerate FIRE
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-2">💡 Optimize Investments</h4>
              <p className="text-sm text-gray-400 mb-3">
                Consider increasing your monthly contributions by 10% to reach FIRE 2 years earlier.
              </p>
              <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                Optimize Portfolio
              </button>
            </div>
            <div className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-2">🌐 Explore DeFi</h4>
              <p className="text-sm text-gray-400 mb-3">
                High-yield DeFi opportunities could increase your passive income by 15%.
              </p>
              <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                Explore DeFi
              </button>
            </div>
            <div className="bg-gray-700 rounded-xl p-4">
              <h4 className="font-semibold mb-2">📊 Tax Optimization</h4>
              <p className="text-sm text-gray-400 mb-3">
                Maximize tax-advantaged accounts to save an additional $5,000 annually.
              </p>
              <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                Tax Strategy
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialFreedomDashboard;
