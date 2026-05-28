import React, { useState, useEffect, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, RadialBarChart, RadialBar 
} from 'recharts';

// ── FIRE variant type ─────────────────────────────────────────────────────────

type FIREVariant = 'lean' | 'regular' | 'fat' | 'coast' | 'barista';

interface FIREVariantConfig {
  label: string;
  emoji: string;
  withdrawalRate: number;
  description: string;
  color: string;
}

const FIRE_VARIANTS: Record<FIREVariant, FIREVariantConfig> = {
  lean:    { label: 'Lean FIRE',    emoji: '🥗', withdrawalRate: 0.035, description: 'Frugal lifestyle, < $40k/yr', color: '#10B981' },
  regular: { label: 'Regular FIRE', emoji: '🔥', withdrawalRate: 0.04,  description: 'Comfortable living expenses',  color: '#3B82F6' },
  fat:     { label: 'Fat FIRE',     emoji: '💎', withdrawalRate: 0.03,  description: 'Affluent lifestyle, > $100k/yr', color: '#8B5CF6' },
  coast:   { label: 'Coast FIRE',   emoji: '🏄', withdrawalRate: 0.04,  description: 'Coast on current savings',     color: '#F59E0B' },
  barista: { label: 'Barista FIRE', emoji: '☕', withdrawalRate: 0.04,  description: 'Part-time work covers gap',    color: '#EF4444' },
};

// ── SWR scenario ──────────────────────────────────────────────────────────────

interface SWRScenario {
  rate: number;
  label: string;
  requiredPortfolio: number;
  monthlyWithdrawal: number;
  successProbability: number;
  color: string;
}

// ── Monte Carlo result ────────────────────────────────────────────────────────

interface MonteCarloResult {
  successRate: number;
  median: number;
  p10: number;
  p90: number;
  paths: number[][];
}

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

// ── Pure FIRE calculation helpers ─────────────────────────────────────────────

function calcFINumber(annualExpenses: number, withdrawalRate: number): number {
  return annualExpenses / withdrawalRate;
}

function calcCoastFI(fiNumber: number, yearsToRetirement: number, annualReturn: number): number {
  return fiNumber / Math.pow(1 + annualReturn, yearsToRetirement);
}

function calcMonthsToFI(
  currentSavings: number,
  monthlySavings: number,
  fiNumber: number,
  annualReturn: number,
): number | null {
  if (currentSavings >= fiNumber) return 0;
  if (monthlySavings <= 0) return null;

  const r = annualReturn / 12;
  const fv = (n: number) => {
    if (Math.abs(r) < 1e-10) return currentSavings + monthlySavings * n;
    const f = Math.pow(1 + r, n);
    return currentSavings * f + monthlySavings * ((f - 1) / r);
  };

  if (fv(1200) < fiNumber) return null;
  let lo = 0, hi = 1200;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (fv(mid) >= fiNumber) hi = mid; else lo = mid + 1;
  }
  return lo;
}

function calcSWRScenarios(annualExpenses: number): SWRScenario[] {
  const configs = [
    { rate: 0.03,  label: '3%',   successProb: 0.98, color: '#10B981' },
    { rate: 0.035, label: '3.5%', successProb: 0.95, color: '#3B82F6' },
    { rate: 0.04,  label: '4%',   successProb: 0.90, color: '#F59E0B' },
    { rate: 0.045, label: '4.5%', successProb: 0.82, color: '#F97316' },
    { rate: 0.05,  label: '5%',   successProb: 0.70, color: '#EF4444' },
  ];
  return configs.map(c => ({
    rate: c.rate,
    label: c.label,
    requiredPortfolio: annualExpenses / c.rate,
    monthlyWithdrawal: annualExpenses / 12,
    successProbability: c.successProb,
    color: c.color,
  }));
}

/** Lightweight seeded LCG Monte Carlo – runs entirely in the browser. */
function runMonteCarlo(
  portfolioValue: number,
  annualWithdrawal: number,
  years: number,
  meanReturn: number,
  volatility: number,
  simulations = 500,
): MonteCarloResult {
  let seed = 42;
  const rand = () => {
    seed = (seed * 1664525 + 1013904223) & 0xffffffff;
    return (seed >>> 0) / 0xffffffff;
  };
  const normal = () => {
    const u1 = Math.max(rand(), 1e-10);
    const u2 = rand();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  };

  let successes = 0;
  const finalValues: number[] = [];
  const samplePaths: number[][] = [];

  for (let s = 0; s < simulations; s++) {
    let balance = portfolioValue;
    const path: number[] = [balance];
    let survived = true;

    for (let y = 0; y < years; y++) {
      const ret = meanReturn + volatility * normal();
      balance = balance * (1 + ret) - annualWithdrawal;
      path.push(Math.max(balance, 0));
      if (balance <= 0) { survived = false; break; }
    }

    if (survived) successes++;
    finalValues.push(balance);
    if (s < 20) samplePaths.push(path); // Keep 20 paths for charting
  }

  finalValues.sort((a, b) => a - b);
  return {
    successRate: successes / simulations,
    median: finalValues[Math.floor(finalValues.length / 2)],
    p10: finalValues[Math.floor(finalValues.length * 0.1)],
    p90: finalValues[Math.floor(finalValues.length * 0.9)],
    paths: samplePaths,
  };
}

function classifyFIREProgress(
  currentSavings: number,
  fiNumber: number,
  coastFI: number,
): { stage: string; emoji: string; color: string } {
  if (currentSavings >= fiNumber)          return { stage: 'Full FI',       emoji: '🏆', color: '#10B981' };
  if (currentSavings >= fiNumber * 0.70)  return { stage: 'Barista FIRE',  emoji: '☕', color: '#F59E0B' };
  if (currentSavings >= coastFI)           return { stage: 'Coast FIRE',    emoji: '🏄', color: '#3B82F6' };
  return                                          { stage: 'Accumulation', emoji: '🌱', color: '#6B7280' };
}

const FinancialFreedomDashboard: React.FC = () => {
  // 🎡 Ferris Wheel Animation State
  const [wheelRotation, setWheelRotation] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  // ── FIRE variant selector ──────────────────────────────────────────────────
  const [selectedVariant, setSelectedVariant] = useState<FIREVariant>('regular');
  const [activeTab, setActiveTab] = useState<'overview' | 'swr' | 'montecarlo' | 'goals' | 'income'>('overview');
  
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
  const [monthlyIncome, setMonthlyIncome] = useState(12000);
  const [expectedAnnualReturn, setExpectedAnnualReturn] = useState(7);
  const [portfolioVolatility, setPortfolioVolatility] = useState(15);

  // Calculate FIRE metrics
  const totalPassiveIncome = passiveIncome.reduce((sum, income) => sum + income.monthlyAmount, 0);
  const totalMonthlyContributions = fireGoals.reduce((sum, goal) => sum + goal.monthlyContribution, 0);
  const annualExpenses = monthlyExpenses * 12;
  const variantConfig = FIRE_VARIANTS[selectedVariant];
  const fireNumber = useMemo(
    () => calcFINumber(annualExpenses, variantConfig.withdrawalRate),
    [annualExpenses, variantConfig.withdrawalRate],
  );
  const yearsToFIRE = targetFIREAge - currentAge;
  const coastFINumber = useMemo(
    () => calcCoastFI(fireNumber, yearsToFIRE, expectedAnnualReturn / 100),
    [fireNumber, yearsToFIRE, expectedAnnualReturn],
  );
  const monthsToFI = useMemo(
    () => calcMonthsToFI(
      currentNetWorth,
      totalMonthlyContributions + totalPassiveIncome,
      fireNumber,
      expectedAnnualReturn / 100,
    ),
    [currentNetWorth, totalMonthlyContributions, totalPassiveIncome, fireNumber, expectedAnnualReturn],
  );
  const fireAge = monthsToFI !== null ? currentAge + Math.ceil(monthsToFI / 12) : null;
  const savingsRate = monthlyIncome > 0
    ? ((totalMonthlyContributions / monthlyIncome) * 100).toFixed(1)
    : '0.0';
  const progressStage = classifyFIREProgress(currentNetWorth, fireNumber, coastFINumber);
  const swrScenarios = useMemo(() => calcSWRScenarios(annualExpenses), [annualExpenses]);
  const monteCarlo = useMemo(
    () => runMonteCarlo(
      fireNumber,
      annualExpenses,
      Math.max(yearsToFIRE + 30, 30),
      expectedAnnualReturn / 100,
      portfolioVolatility / 100,
      500,
    ),
    [fireNumber, annualExpenses, yearsToFIRE, expectedAnnualReturn, portfolioVolatility],
  );

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

  // ── Render helpers ──────────────────────────────────────────────────────────

  const renderFIREVariantSelector = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 mb-8">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        🔥 FIRE Variant
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {(Object.entries(FIRE_VARIANTS) as [FIREVariant, FIREVariantConfig][]).map(([key, cfg]) => (
          <button
            key={key}
            onClick={() => setSelectedVariant(key)}
            className={`rounded-xl p-4 text-left transition-all border-2 ${
              selectedVariant === key
                ? 'border-white bg-gray-600 scale-105'
                : 'border-gray-600 bg-gray-700 hover:border-gray-400'
            }`}
          >
            <div className="text-2xl mb-1">{cfg.emoji}</div>
            <div className="text-white font-semibold text-sm">{cfg.label}</div>
            <div className="text-gray-400 text-xs mt-1">{cfg.description}</div>
            <div className="mt-2 text-xs font-bold" style={{ color: cfg.color }}>
              SWR {(cfg.withdrawalRate * 100).toFixed(1)}%
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  const renderFIREOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-200 text-sm">Current Net Worth</p>
            <p className="text-3xl font-bold">${(currentNetWorth / 1000).toFixed(0)}K</p>
            <p className="text-blue-200 text-xs mt-1">{progressStage.emoji} {progressStage.stage}</p>
          </div>
          <div className="text-4xl">💰</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-green-200 text-sm">FIRE Number ({variantConfig.label})</p>
            <p className="text-3xl font-bold">${(fireNumber / 1000000).toFixed(2)}M</p>
            <p className="text-green-200 text-xs mt-1">SWR {(variantConfig.withdrawalRate * 100).toFixed(1)}%</p>
          </div>
          <div className="text-4xl">🎯</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-purple-200 text-sm">Years to FIRE</p>
            <p className="text-3xl font-bold">
              {monthsToFI !== null ? (monthsToFI / 12).toFixed(1) : '—'}
            </p>
            <p className="text-purple-200 text-xs mt-1">Savings rate {savingsRate}%</p>
          </div>
          <div className="text-4xl">⏰</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-orange-200 text-sm">FIRE Age</p>
            <p className="text-3xl font-bold">{fireAge ?? '—'}</p>
            <p className="text-orange-200 text-xs mt-1">
              {monteCarlo.successRate >= 0 ? `${(monteCarlo.successRate * 100).toFixed(0)}% MC success` : ''}
            </p>
          </div>
          <div className="text-4xl">🚀</div>
        </div>
      </div>
    </div>
  );

  const renderFIREInputs = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 mb-8">
      <h3 className="text-xl font-bold text-white mb-4">⚙️ FIRE Parameters</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: 'Current Age', value: currentAge, setter: setCurrentAge, min: 18, max: 70, step: 1 },
          { label: 'Target FIRE Age', value: targetFIREAge, setter: setTargetFIREAge, min: 25, max: 80, step: 1 },
          { label: 'Net Worth ($K)', value: currentNetWorth / 1000, setter: (v: number) => setCurrentNetWorth(v * 1000), min: 0, max: 10000, step: 10 },
          { label: 'Monthly Expenses ($)', value: monthlyExpenses, setter: setMonthlyExpenses, min: 1000, max: 50000, step: 500 },
          { label: 'Monthly Income ($)', value: monthlyIncome, setter: setMonthlyIncome, min: 1000, max: 100000, step: 500 },
          { label: 'Expected Return (%)', value: expectedAnnualReturn, setter: setExpectedAnnualReturn, min: 1, max: 15, step: 0.5 },
        ].map(({ label, value, setter, min, max, step }) => (
          <div key={label} className="bg-gray-700 rounded-xl p-3">
            <label className="text-gray-400 text-xs block mb-1">{label}</label>
            <input
              type="number"
              value={value}
              min={min}
              max={max}
              step={step}
              onChange={e => setter(parseFloat(e.target.value) || 0)}
              className="w-full bg-gray-600 text-white rounded px-2 py-1 text-sm font-semibold focus:outline-none focus:ring-1 focus:ring-blue-400"
            />
          </div>
        ))}
      </div>
    </div>
  );

  const renderSWRAnalysis = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 mb-8">
      <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
        📊 Safe Withdrawal Rate Analysis
      </h3>
      <p className="text-gray-400 text-sm mb-6">
        Annual expenses: <span className="text-white font-semibold">${annualExpenses.toLocaleString()}</span>
        &nbsp;·&nbsp;Based on Trinity Study success rates over 30 years
      </p>

      {/* SWR bar chart */}
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={swrScenarios} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="label" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
          <YAxis stroke="#9CA3AF" tick={{ fontSize: 11 }}
            tickFormatter={v => `$${(v / 1e6).toFixed(1)}M`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px', color: 'white' }}
            formatter={(value: number, name: string) => [
              name === 'requiredPortfolio' ? `$${(value / 1e6).toFixed(2)}M required` : `${(value * 100).toFixed(0)}% success`,
              name === 'requiredPortfolio' ? 'Portfolio Target' : 'Historical Success',
            ]}
          />
          <Bar dataKey="requiredPortfolio" name="requiredPortfolio" radius={[4, 4, 0, 0]}>
            {swrScenarios.map((s, i) => (
              <Cell key={i} fill={s.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Scenario cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-6">
        {swrScenarios.map(s => {
          const isCurrent = Math.abs(s.rate - variantConfig.withdrawalRate) < 0.001;
          return (
            <div
              key={s.label}
              className={`rounded-xl p-4 border-2 ${isCurrent ? 'border-white' : 'border-transparent'}`}
              style={{ backgroundColor: s.color + '22' }}
            >
              <div className="text-center">
                <p className="font-bold text-lg" style={{ color: s.color }}>{s.label}</p>
                <p className="text-white text-sm font-semibold mt-1">
                  ${(s.requiredPortfolio / 1e6).toFixed(2)}M
                </p>
                <p className="text-gray-400 text-xs mt-1">
                  ${(s.monthlyWithdrawal).toLocaleString('en-US', { maximumFractionDigits: 0 })}/mo
                </p>
                <div className="mt-2 bg-gray-700 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full"
                    style={{ width: `${s.successProbability * 100}%`, backgroundColor: s.color }}
                  />
                </div>
                <p className="text-xs mt-1" style={{ color: s.color }}>
                  {(s.successProbability * 100).toFixed(0)}% success
                </p>
                {isCurrent && (
                  <p className="text-xs text-white font-bold mt-1">← {variantConfig.label}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderMonteCarlo = () => {
    const pathData = Array.from({ length: Math.max(...monteCarlo.paths.map(p => p.length)) }, (_, i) => {
      const point: Record<string, number> = { year: i };
      monteCarlo.paths.slice(0, 10).forEach((p, j) => { point[`path${j}`] = p[i] ?? 0; });
      point.median = monteCarlo.median;
      point.fireTarget = fireNumber;
      return point;
    });

    const successColor = monteCarlo.successRate >= 0.9 ? '#10B981'
      : monteCarlo.successRate >= 0.75 ? '#F59E0B' : '#EF4444';

    return (
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 mb-8">
        <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
          🎲 Monte Carlo Success Probability
        </h3>
        <p className="text-gray-400 text-sm mb-6">
          500 simulated portfolios · Mean return {expectedAnnualReturn}% · Volatility {portfolioVolatility}%
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-700 rounded-xl p-4 text-center">
            <p className="text-gray-400 text-xs mb-1">Success Rate</p>
            <p className="text-3xl font-bold" style={{ color: successColor }}>
              {(monteCarlo.successRate * 100).toFixed(0)}%
            </p>
          </div>
          <div className="bg-gray-700 rounded-xl p-4 text-center">
            <p className="text-gray-400 text-xs mb-1">Median Final Value</p>
            <p className="text-xl font-bold text-blue-400">
              ${(Math.max(monteCarlo.median, 0) / 1e6).toFixed(2)}M
            </p>
          </div>
          <div className="bg-gray-700 rounded-xl p-4 text-center">
            <p className="text-gray-400 text-xs mb-1">10th Percentile</p>
            <p className="text-xl font-bold text-red-400">
              ${(Math.max(monteCarlo.p10, 0) / 1e6).toFixed(2)}M
            </p>
          </div>
          <div className="bg-gray-700 rounded-xl p-4 text-center">
            <p className="text-gray-400 text-xs mb-1">90th Percentile</p>
            <p className="text-xl font-bold text-green-400">
              ${(Math.max(monteCarlo.p90, 0) / 1e6).toFixed(2)}M
            </p>
          </div>
        </div>

        <div className="mb-2">
          <label className="text-gray-400 text-xs">Portfolio Volatility: {portfolioVolatility}%</label>
          <input
            type="range" min={5} max={30} step={1} value={portfolioVolatility}
            onChange={e => setPortfolioVolatility(parseInt(e.target.value))}
            className="w-full mt-1 accent-blue-500"
          />
        </div>

        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={pathData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" label={{ value: 'Year', position: 'insideBottom', fill: '#9CA3AF', fontSize: 11 }} />
            <YAxis stroke="#9CA3AF" tickFormatter={v => `$${(v / 1e6).toFixed(1)}M`} tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px', color: 'white' }}
              formatter={(v: number) => [`$${(v / 1e6).toFixed(2)}M`]}
            />
            {Array.from({ length: 10 }, (_, j) => (
              <Line key={j} type="monotone" dataKey={`path${j}`} stroke="#3B82F6"
                strokeOpacity={0.25} dot={false} strokeWidth={1} />
            ))}
            <Line type="monotone" dataKey="fireTarget" stroke="#EF4444" strokeDasharray="6 3"
              dot={false} strokeWidth={2} name="FIRE Target" />
          </LineChart>
        </ResponsiveContainer>
        <p className="text-gray-500 text-xs mt-2 text-center">
          Blue lines = sample simulation paths · Red dashed = FIRE target
        </p>
      </div>
    );
  };

  const renderCoastFIPanel = () => (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 mb-8">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        🏄 FIRE Milestones
      </h3>
      <div className="space-y-3">
        {[
          { label: '25% FI',        value: fireNumber * 0.25,  emoji: '🌱' },
          { label: 'CoastFIRE',     value: coastFINumber,       emoji: '🏄' },
          { label: '50% FI',        value: fireNumber * 0.50,  emoji: '🌿' },
          { label: 'BaristaFIRE',   value: fireNumber * 0.70,  emoji: '☕' },
          { label: 'Full FI',       value: fireNumber,          emoji: '🏆' },
        ].map(m => {
          const pct = Math.min((currentNetWorth / m.value) * 100, 100);
          const reached = currentNetWorth >= m.value;
          return (
            <div key={m.label} className="bg-gray-700 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{m.emoji}</span>
                  <span className={`font-semibold text-sm ${reached ? 'text-green-400' : 'text-white'}`}>
                    {m.label} {reached && '✓'}
                  </span>
                </div>
                <span className="text-gray-300 text-sm font-mono">
                  ${(m.value / 1000).toFixed(0)}K
                </span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: reached ? '#10B981' : variantConfig.color }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">{pct.toFixed(1)}% of milestone reached</p>
            </div>
          );
        })}
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
        <div className="flex justify-between items-center mt-2">
          <span className="text-gray-400">Coverage of Annual Expenses:</span>
          <span className="font-bold text-yellow-400">
            {((totalPassiveIncome * 12 / annualExpenses) * 100).toFixed(1)}%
          </span>
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
          <p className="text-2xl font-bold text-green-400">Age {fireAge ?? '—'}</p>
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

  const tabStyle = (tab: typeof activeTab) =>
    `px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
      activeTab === tab
        ? 'bg-blue-600 text-white'
        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
    }`;

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

        {/* FIRE Variant Selector */}
        {renderFIREVariantSelector()}

        {/* FIRE Parameters */}
        {renderFIREInputs()}

        {/* FIRE Overview */}
        {renderFIREOverview()}

        {/* Tab navigation */}
        <div className="flex flex-wrap gap-2 mb-6">
          <button className={tabStyle('overview')}    onClick={() => setActiveTab('overview')}>📈 Projection</button>
          <button className={tabStyle('swr')}         onClick={() => setActiveTab('swr')}>📊 SWR Analysis</button>
          <button className={tabStyle('montecarlo')}  onClick={() => setActiveTab('montecarlo')}>🎲 Monte Carlo</button>
          <button className={tabStyle('goals')}       onClick={() => setActiveTab('goals')}>🎯 Goals</button>
          <button className={tabStyle('income')}      onClick={() => setActiveTab('income')}>💰 Income</button>
        </div>

        {activeTab === 'overview' && (
          <>
            {renderCoastFIPanel()}
            {renderProjectionChart()}
          </>
        )}
        {activeTab === 'swr'        && renderSWRAnalysis()}
        {activeTab === 'montecarlo' && renderMonteCarlo()}
        {activeTab === 'goals'      && renderFIREGoals()}
        {activeTab === 'income'     && renderPassiveIncomeOverview()}

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
