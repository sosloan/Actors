#!/usr/bin/env python3
"""
🇲🇽 MEXICAN MARKETS VALUE CREATION PORTFOLIO ALLOCATOR
Focus on Mexican equities, bonds, real estate, and fintech assets
Strong emphasis on Guadalajara's tech and innovation ecosystem

"Where Mexican innovation meets strategic capital allocation for sustainable value creation"
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from pathlib import Path


class MexicanAssetClass(Enum):
    """Mexican market asset classes for value creation"""
    EQUITIES = "equities"                    # Mexican stock market (BMV)
    BONDS = "bonds"                          # Mexican government and corporate bonds
    REAL_ESTATE = "real_estate"              # Mexican real estate investments (FIBRAs)
    FINTECH = "fintech"                      # Mexican fintech and digital banking
    TECH_INNOVATION = "tech_innovation"      # Guadalajara tech ecosystem
    INFRASTRUCTURE = "infrastructure"        # Infrastructure and development projects
    ENERGY = "energy"                        # Energy sector investments
    MANUFACTURING = "manufacturing"          # Manufacturing and industrial clusters


class RegionalFocus(Enum):
    """Regional focus areas within Mexico"""
    GUADALAJARA = "guadalajara"              # Jalisco - Tech and innovation hub
    MEXICO_CITY = "mexico_city"              # Financial capital
    MONTERREY = "monterrey"                  # Industrial and manufacturing hub
    QUERETARO = "queretaro"                  # Aerospace and automotive
    TIJUANA = "tijuana"                      # Border manufacturing and tech
    PUEBLA = "puebla"                        # Automotive and manufacturing
    BAJIO = "bajio"                          # Agricultural and automotive region
    YUCATAN = "yucatan"                      # Tourism and services


@dataclass
class EconomicIndicator:
    """Regional economic indicators for Mexican markets"""
    region: RegionalFocus
    gdp_growth_rate: float                   # Annual GDP growth rate (%)
    industrial_cluster_score: float          # Industrial cluster strength (0.0-1.0)
    startup_growth_rate: float               # Annual startup growth rate (%)
    tech_ecosystem_score: float              # Tech ecosystem maturity (0.0-1.0)
    innovation_index: float                  # Innovation capability index (0.0-1.0)
    infrastructure_quality: float            # Infrastructure quality score (0.0-1.0)
    workforce_quality: float                 # Skilled workforce availability (0.0-1.0)
    business_environment: float              # Business environment score (0.0-1.0)
    fdi_growth_rate: float                   # Foreign direct investment growth (%)
    export_growth_rate: float                # Export growth rate (%)
    updated_at: datetime


@dataclass(frozen=True)
class MexicanAsset:
    """Mexican market asset with regional and sector data"""
    id: str
    name: str
    asset_class: MexicanAssetClass
    ticker: Optional[str]                    # Stock ticker or identifier
    region: RegionalFocus
    sector: str
    market_cap: float                        # In MXN
    current_price: float                     # In MXN
    expected_return: float                   # Expected annual return (%)
    volatility: float                        # Annual volatility (%)
    beta: float                              # Market beta
    pe_ratio: Optional[float]                # Price-to-earnings ratio
    dividend_yield: Optional[float]          # Annual dividend yield (%)
    liquidity_score: float                   # Market liquidity (0.0-1.0)
    esg_score: float                         # ESG rating (0.0-1.0)
    growth_potential: float                  # Growth potential score (0.0-1.0)
    innovation_score: float                  # Innovation capability (0.0-1.0)
    regional_economic_score: float           # Regional economic strength (0.0-1.0)
    updated_at: datetime
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class GuadalajaraEcosystem:
    """Guadalajara tech and innovation ecosystem metrics"""
    tech_companies_count: int
    unicorns_count: int
    startups_count: int
    venture_capital_invested: float          # In USD millions
    tech_jobs_count: int
    university_partnerships: int
    innovation_centers: int
    accelerators_count: int
    tech_talent_pool_score: float            # Talent availability (0.0-1.0)
    infrastructure_readiness: float          # Infrastructure for tech (0.0-1.0)
    government_support_score: float          # Government initiatives (0.0-1.0)
    global_connectivity_score: float         # International connections (0.0-1.0)
    innovation_output_score: float           # Patents, research output (0.0-1.0)
    ecosystem_maturity: float                # Overall ecosystem maturity (0.0-1.0)
    updated_at: datetime


@dataclass
class MexicanPortfolio:
    """Mexican markets portfolio with regional allocation"""
    id: str
    name: str
    total_value: float                       # In MXN
    assets: List[MexicanAsset]
    regional_allocation: Dict[RegionalFocus, float]  # Allocation by region (%)
    asset_class_allocation: Dict[MexicanAssetClass, float]  # Allocation by class (%)
    guadalajara_tech_allocation: float       # % allocated to Guadalajara tech ecosystem
    expected_return: float                   # Portfolio expected return (%)
    portfolio_volatility: float              # Portfolio volatility (%)
    sharpe_ratio: float                      # Risk-adjusted return
    diversification_score: float             # Diversification quality (0.0-1.0)
    regional_economic_score: float           # Weighted regional economics (0.0-1.0)
    innovation_exposure: float               # Innovation sector exposure (0.0-1.0)
    esg_score: float                         # Portfolio ESG rating (0.0-1.0)
    created_at: datetime
    updated_at: datetime


class MexicanMarketsAllocator:
    """
    Advanced portfolio allocator for Mexican markets
    Focus on value creation through regional economic indicators
    Strong emphasis on Guadalajara's tech and innovation ecosystem
    """
    
    def __init__(self):
        self.economic_indicators = {}
        self.guadalajara_ecosystem = None
        self.asset_universe = []
        self.optimization_history = []
        self.min_guadalajara_allocation = 0.15  # Minimum 15% to Guadalajara tech
        self.max_asset_class_allocation = 0.40   # Maximum 40% in any asset class
        
    async def initialize_economic_indicators(self) -> Dict[RegionalFocus, EconomicIndicator]:
        """Initialize regional economic indicators"""
        
        # Guadalajara (Jalisco) - Tech and Innovation Hub
        guadalajara_indicator = EconomicIndicator(
            region=RegionalFocus.GUADALAJARA,
            gdp_growth_rate=4.2,
            industrial_cluster_score=0.85,
            startup_growth_rate=28.5,
            tech_ecosystem_score=0.92,
            innovation_index=0.88,
            infrastructure_quality=0.82,
            workforce_quality=0.87,
            business_environment=0.84,
            fdi_growth_rate=15.3,
            export_growth_rate=12.8,
            updated_at=datetime.now()
        )
        
        # Mexico City - Financial Capital
        mexico_city_indicator = EconomicIndicator(
            region=RegionalFocus.MEXICO_CITY,
            gdp_growth_rate=3.8,
            industrial_cluster_score=0.78,
            startup_growth_rate=22.1,
            tech_ecosystem_score=0.85,
            innovation_index=0.82,
            infrastructure_quality=0.88,
            workforce_quality=0.90,
            business_environment=0.86,
            fdi_growth_rate=12.5,
            export_growth_rate=8.3,
            updated_at=datetime.now()
        )
        
        # Monterrey - Industrial Hub
        monterrey_indicator = EconomicIndicator(
            region=RegionalFocus.MONTERREY,
            gdp_growth_rate=4.5,
            industrial_cluster_score=0.90,
            startup_growth_rate=18.7,
            tech_ecosystem_score=0.78,
            innovation_index=0.80,
            infrastructure_quality=0.85,
            workforce_quality=0.85,
            business_environment=0.88,
            fdi_growth_rate=16.2,
            export_growth_rate=14.5,
            updated_at=datetime.now()
        )
        
        # Querétaro - Aerospace and Automotive
        queretaro_indicator = EconomicIndicator(
            region=RegionalFocus.QUERETARO,
            gdp_growth_rate=5.2,
            industrial_cluster_score=0.87,
            startup_growth_rate=14.3,
            tech_ecosystem_score=0.75,
            innovation_index=0.78,
            infrastructure_quality=0.86,
            workforce_quality=0.82,
            business_environment=0.85,
            fdi_growth_rate=18.7,
            export_growth_rate=16.2,
            updated_at=datetime.now()
        )
        
        self.economic_indicators = {
            RegionalFocus.GUADALAJARA: guadalajara_indicator,
            RegionalFocus.MEXICO_CITY: mexico_city_indicator,
            RegionalFocus.MONTERREY: monterrey_indicator,
            RegionalFocus.QUERETARO: queretaro_indicator
        }
        
        return self.economic_indicators
    
    async def initialize_guadalajara_ecosystem(self) -> GuadalajaraEcosystem:
        """Initialize Guadalajara tech and innovation ecosystem data"""
        
        self.guadalajara_ecosystem = GuadalajaraEcosystem(
            tech_companies_count=1850,
            unicorns_count=3,
            startups_count=450,
            venture_capital_invested=320.5,
            tech_jobs_count=75000,
            university_partnerships=28,
            innovation_centers=12,
            accelerators_count=18,
            tech_talent_pool_score=0.88,
            infrastructure_readiness=0.85,
            government_support_score=0.82,
            global_connectivity_score=0.84,
            innovation_output_score=0.86,
            ecosystem_maturity=0.87,
            updated_at=datetime.now()
        )
        
        return self.guadalajara_ecosystem
    
    async def build_asset_universe(self) -> List[MexicanAsset]:
        """Build universe of Mexican market assets"""
        
        assets = [
            # Guadalajara Tech and Innovation
            MexicanAsset(
                id="mx-tech-001",
                name="Guadalajara Tech Innovation Fund",
                asset_class=MexicanAssetClass.TECH_INNOVATION,
                ticker="GDLTECH",
                region=RegionalFocus.GUADALAJARA,
                sector="Technology",
                market_cap=5_000_000_000,
                current_price=125.50,
                expected_return=18.5,
                volatility=22.3,
                beta=1.35,
                pe_ratio=28.5,
                dividend_yield=1.2,
                liquidity_score=0.85,
                esg_score=0.88,
                growth_potential=0.92,
                innovation_score=0.94,
                regional_economic_score=0.90,
                updated_at=datetime.now()
            ),
            
            # Mexican Fintech
            MexicanAsset(
                id="mx-fintech-001",
                name="Mexican Digital Banking Platform",
                asset_class=MexicanAssetClass.FINTECH,
                ticker="MXFINTECH",
                region=RegionalFocus.MEXICO_CITY,
                sector="Financial Technology",
                market_cap=3_500_000_000,
                current_price=85.75,
                expected_return=22.3,
                volatility=28.5,
                beta=1.45,
                pe_ratio=35.2,
                dividend_yield=0.8,
                liquidity_score=0.82,
                esg_score=0.85,
                growth_potential=0.95,
                innovation_score=0.93,
                regional_economic_score=0.86,
                updated_at=datetime.now()
            ),
            
            # Mexican Real Estate (FIBRAs)
            MexicanAsset(
                id="mx-re-001",
                name="Guadalajara Industrial Real Estate",
                asset_class=MexicanAssetClass.REAL_ESTATE,
                ticker="FIBRAGDL",
                region=RegionalFocus.GUADALAJARA,
                sector="Real Estate",
                market_cap=8_200_000_000,
                current_price=32.45,
                expected_return=12.8,
                volatility=15.2,
                beta=0.85,
                pe_ratio=None,
                dividend_yield=6.5,
                liquidity_score=0.78,
                esg_score=0.82,
                growth_potential=0.78,
                innovation_score=0.65,
                regional_economic_score=0.88,
                updated_at=datetime.now()
            ),
            
            # Mexican Government Bonds
            MexicanAsset(
                id="mx-bonds-001",
                name="Mexican 10-Year Government Bond",
                asset_class=MexicanAssetClass.BONDS,
                ticker="MBONO10Y",
                region=RegionalFocus.MEXICO_CITY,
                sector="Fixed Income",
                market_cap=50_000_000_000,
                current_price=98.25,
                expected_return=8.5,
                volatility=8.2,
                beta=0.25,
                pe_ratio=None,
                dividend_yield=8.5,
                liquidity_score=0.95,
                esg_score=0.75,
                growth_potential=0.45,
                innovation_score=0.30,
                regional_economic_score=0.80,
                updated_at=datetime.now()
            ),
            
            # Mexican Blue-Chip Equities
            MexicanAsset(
                id="mx-equity-001",
                name="Mexican Industrial Conglomerate",
                asset_class=MexicanAssetClass.EQUITIES,
                ticker="MEXIND",
                region=RegionalFocus.MONTERREY,
                sector="Industrials",
                market_cap=15_000_000_000,
                current_price=245.80,
                expected_return=14.2,
                volatility=18.5,
                beta=1.15,
                pe_ratio=18.3,
                dividend_yield=3.2,
                liquidity_score=0.90,
                esg_score=0.78,
                growth_potential=0.82,
                innovation_score=0.75,
                regional_economic_score=0.89,
                updated_at=datetime.now()
            ),
            
            # Guadalajara Software and AI
            MexicanAsset(
                id="mx-tech-002",
                name="Guadalajara AI and Software Ventures",
                asset_class=MexicanAssetClass.TECH_INNOVATION,
                ticker="GDLAI",
                region=RegionalFocus.GUADALAJARA,
                sector="Software & AI",
                market_cap=2_800_000_000,
                current_price=68.90,
                expected_return=25.5,
                volatility=32.8,
                beta=1.55,
                pe_ratio=42.5,
                dividend_yield=0.5,
                liquidity_score=0.75,
                esg_score=0.90,
                growth_potential=0.96,
                innovation_score=0.97,
                regional_economic_score=0.91,
                updated_at=datetime.now()
            ),
            
            # Infrastructure Development
            MexicanAsset(
                id="mx-infra-001",
                name="Jalisco Infrastructure Development",
                asset_class=MexicanAssetClass.INFRASTRUCTURE,
                ticker="JALISCOINFRA",
                region=RegionalFocus.GUADALAJARA,
                sector="Infrastructure",
                market_cap=6_500_000_000,
                current_price=142.30,
                expected_return=11.5,
                volatility=14.8,
                beta=0.90,
                pe_ratio=16.8,
                dividend_yield=4.2,
                liquidity_score=0.72,
                esg_score=0.84,
                growth_potential=0.80,
                innovation_score=0.70,
                regional_economic_score=0.87,
                updated_at=datetime.now()
            ),
            
            # Automotive and Manufacturing
            MexicanAsset(
                id="mx-mfg-001",
                name="Bajío Automotive Cluster",
                asset_class=MexicanAssetClass.MANUFACTURING,
                ticker="BAJIOAUTO",
                region=RegionalFocus.QUERETARO,
                sector="Automotive",
                market_cap=7_800_000_000,
                current_price=156.75,
                expected_return=13.8,
                volatility=16.5,
                beta=1.05,
                pe_ratio=15.2,
                dividend_yield=2.8,
                liquidity_score=0.85,
                esg_score=0.76,
                growth_potential=0.83,
                innovation_score=0.78,
                regional_economic_score=0.86,
                updated_at=datetime.now()
            )
        ]
        
        self.asset_universe = assets
        return assets
    
    async def calculate_regional_score(
        self,
        region: RegionalFocus,
        asset_class: MexicanAssetClass
    ) -> float:
        """Calculate regional economic score for allocation"""
        
        if region not in self.economic_indicators:
            return 0.5  # Default neutral score
        
        indicator = self.economic_indicators[region]
        
        # Weight different factors based on asset class
        if asset_class == MexicanAssetClass.TECH_INNOVATION:
            score = (
                indicator.tech_ecosystem_score * 0.30 +
                indicator.innovation_index * 0.25 +
                indicator.startup_growth_rate / 100 * 0.20 +
                indicator.workforce_quality * 0.15 +
                indicator.fdi_growth_rate / 100 * 0.10
            )
        elif asset_class == MexicanAssetClass.FINTECH:
            score = (
                indicator.innovation_index * 0.25 +
                indicator.tech_ecosystem_score * 0.25 +
                indicator.business_environment * 0.20 +
                indicator.infrastructure_quality * 0.15 +
                indicator.workforce_quality * 0.15
            )
        elif asset_class == MexicanAssetClass.MANUFACTURING:
            score = (
                indicator.industrial_cluster_score * 0.35 +
                indicator.infrastructure_quality * 0.25 +
                indicator.export_growth_rate / 100 * 0.20 +
                indicator.workforce_quality * 0.20
            )
        elif asset_class == MexicanAssetClass.REAL_ESTATE:
            score = (
                indicator.gdp_growth_rate / 100 * 0.30 +
                indicator.infrastructure_quality * 0.25 +
                indicator.business_environment * 0.25 +
                indicator.fdi_growth_rate / 100 * 0.20
            )
        else:  # Generic scoring for other asset classes
            score = (
                indicator.gdp_growth_rate / 100 * 0.25 +
                indicator.business_environment * 0.25 +
                indicator.infrastructure_quality * 0.25 +
                indicator.industrial_cluster_score * 0.25
            )
        
        return min(1.0, max(0.0, score))
    
    async def optimize_portfolio(
        self,
        target_value: float,
        risk_tolerance: str = "moderate",
        guadalajara_focus: bool = True
    ) -> MexicanPortfolio:
        """
        Optimize Mexican markets portfolio with emphasis on regional economics
        
        Args:
            target_value: Target portfolio value in MXN
            risk_tolerance: "conservative", "moderate", or "aggressive"
            guadalajara_focus: Emphasize Guadalajara tech ecosystem
        """
        
        if not self.economic_indicators:
            await self.initialize_economic_indicators()
        
        if not self.guadalajara_ecosystem:
            await self.initialize_guadalajara_ecosystem()
        
        if not self.asset_universe:
            await self.build_asset_universe()
        
        # Set allocation constraints based on risk tolerance
        if risk_tolerance == "conservative":
            max_equity_allocation = 0.40
            min_bond_allocation = 0.30
            guadalajara_min = 0.10 if guadalajara_focus else 0.05
        elif risk_tolerance == "aggressive":
            max_equity_allocation = 0.70
            min_bond_allocation = 0.10
            guadalajara_min = 0.25 if guadalajara_focus else 0.10
        else:  # moderate
            max_equity_allocation = 0.55
            min_bond_allocation = 0.20
            guadalajara_min = 0.15 if guadalajara_focus else 0.08
        
        # Calculate asset scores incorporating regional economics
        asset_scores = []
        for asset in self.asset_universe:
            regional_score = await self.calculate_regional_score(
                asset.region,
                asset.asset_class
            )
            
            # Composite score: expected return, regional economics, innovation
            composite_score = (
                asset.expected_return * 0.30 +
                regional_score * 100 * 0.25 +
                asset.innovation_score * 100 * 0.20 +
                asset.growth_potential * 100 * 0.15 +
                asset.esg_score * 100 * 0.10
            )
            
            # Bonus for Guadalajara tech ecosystem
            if guadalajara_focus and asset.region == RegionalFocus.GUADALAJARA:
                composite_score *= 1.15
            
            asset_scores.append((asset, composite_score, regional_score))
        
        # Sort by composite score
        asset_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Allocate based on constraints and optimization
        allocations = {}
        regional_allocation = {region: 0.0 for region in RegionalFocus}
        asset_class_allocation = {ac: 0.0 for ac in MexicanAssetClass}
        
        remaining_allocation = 1.0
        selected_assets = []
        
        # First pass: ensure minimum allocations
        guadalajara_allocated = 0.0
        bond_allocated = 0.0
        
        for asset, score, regional_score in asset_scores:
            if remaining_allocation <= 0:
                break
            
            # Calculate tentative allocation
            allocation = 0.0
            
            # Prioritize Guadalajara if needed
            if (guadalajara_focus and 
                asset.region == RegionalFocus.GUADALAJARA and
                guadalajara_allocated < guadalajara_min):
                allocation = min(0.12, remaining_allocation)
                guadalajara_allocated += allocation
            
            # Ensure minimum bonds
            elif (asset.asset_class == MexicanAssetClass.BONDS and
                  bond_allocated < min_bond_allocation):
                allocation = min(0.15, remaining_allocation)
                bond_allocated += allocation
            
            # Regular allocation based on score
            elif remaining_allocation > 0.05:
                # Allocate proportionally to score with constraints
                max_single_allocation = 0.20  # Max 20% per asset
                allocation = min(
                    max_single_allocation,
                    remaining_allocation * 0.15,
                    remaining_allocation
                )
            
            if allocation > 0:
                allocations[asset] = allocation
                remaining_allocation -= allocation
                selected_assets.append(asset)
                regional_allocation[asset.region] += allocation
                asset_class_allocation[asset.asset_class] += allocation
        
        # Calculate portfolio metrics
        portfolio_return = sum(
            asset.expected_return * allocations[asset]
            for asset in selected_assets
        )
        
        portfolio_variance = sum(
            (asset.volatility * allocations[asset]) ** 2
            for asset in selected_assets
        )
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Risk-free rate assumption for Mexico (CETES rate ~10%)
        risk_free_rate = 10.0
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Calculate diversification score
        allocation_values = list(allocations.values())
        diversification_score = 1.0 - (np.std(allocation_values) / np.mean(allocation_values)) if allocation_values else 0
        diversification_score = max(0.0, min(1.0, diversification_score))
        
        # Calculate weighted scores
        regional_economic_score = sum(
            asset.regional_economic_score * allocations[asset]
            for asset in selected_assets
        )
        
        innovation_exposure = sum(
            asset.innovation_score * allocations[asset]
            for asset in selected_assets
        )
        
        esg_score = sum(
            asset.esg_score * allocations[asset]
            for asset in selected_assets
        )
        
        guadalajara_tech_allocation = sum(
            allocations[asset]
            for asset in selected_assets
            if (asset.region == RegionalFocus.GUADALAJARA and
                asset.asset_class == MexicanAssetClass.TECH_INNOVATION)
        )
        
        # Create portfolio
        portfolio = MexicanPortfolio(
            id=f"mx-portfolio-{int(time.time())}",
            name=f"Mexican Markets Portfolio - {risk_tolerance.title()}",
            total_value=target_value,
            assets=selected_assets,
            regional_allocation={k: v for k, v in regional_allocation.items() if v > 0},
            asset_class_allocation={k: v for k, v in asset_class_allocation.items() if v > 0},
            guadalajara_tech_allocation=guadalajara_tech_allocation,
            expected_return=portfolio_return,
            portfolio_volatility=portfolio_volatility,
            sharpe_ratio=sharpe_ratio,
            diversification_score=diversification_score,
            regional_economic_score=regional_economic_score,
            innovation_exposure=innovation_exposure,
            esg_score=esg_score,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.optimization_history.append(portfolio)
        return portfolio
    
    def generate_portfolio_report(self, portfolio: MexicanPortfolio) -> Dict[str, Any]:
        """Generate comprehensive portfolio report"""
        
        return {
            'portfolio_summary': {
                'id': portfolio.id,
                'name': portfolio.name,
                'total_value_mxn': f"${portfolio.total_value:,.2f}",
                'created_at': portfolio.created_at.isoformat(),
            },
            'performance_metrics': {
                'expected_annual_return': f"{portfolio.expected_return:.2f}%",
                'portfolio_volatility': f"{portfolio.portfolio_volatility:.2f}%",
                'sharpe_ratio': f"{portfolio.sharpe_ratio:.3f}",
                'diversification_score': f"{portfolio.diversification_score:.2f}",
            },
            'regional_allocation': {
                region.value: f"{allocation * 100:.2f}%"
                for region, allocation in portfolio.regional_allocation.items()
            },
            'asset_class_allocation': {
                asset_class.value: f"{allocation * 100:.2f}%"
                for asset_class, allocation in portfolio.asset_class_allocation.items()
            },
            'guadalajara_focus': {
                'tech_ecosystem_allocation': f"{portfolio.guadalajara_tech_allocation * 100:.2f}%",
                'innovation_exposure': f"{portfolio.innovation_exposure:.2f}",
                'regional_economic_score': f"{portfolio.regional_economic_score:.2f}",
            },
            'sustainability': {
                'esg_score': f"{portfolio.esg_score:.2f}",
                'innovation_exposure': f"{portfolio.innovation_exposure:.2f}",
            },
            'asset_details': [
                {
                    'name': asset.name,
                    'ticker': asset.ticker,
                    'asset_class': asset.asset_class.value,
                    'region': asset.region.value,
                    'expected_return': f"{asset.expected_return:.2f}%",
                    'innovation_score': f"{asset.innovation_score:.2f}",
                }
                for asset in portfolio.assets
            ]
        }


async def main():
    """Demonstration of Mexican Markets Portfolio Allocator"""
    
    print("🇲🇽 Mexican Markets Value Creation Portfolio Allocator")
    print("=" * 70)
    print()
    
    allocator = MexicanMarketsAllocator()
    
    # Initialize economic indicators
    print("📊 Initializing Regional Economic Indicators...")
    indicators = await allocator.initialize_economic_indicators()
    
    print(f"✓ Loaded {len(indicators)} regional indicators")
    for region, indicator in indicators.items():
        print(f"  • {region.value}: GDP Growth {indicator.gdp_growth_rate}%, "
              f"Tech Score {indicator.tech_ecosystem_score:.2f}, "
              f"Startup Growth {indicator.startup_growth_rate}%")
    print()
    
    # Initialize Guadalajara ecosystem
    print("🚀 Initializing Guadalajara Tech Ecosystem...")
    ecosystem = await allocator.initialize_guadalajara_ecosystem()
    print(f"✓ Guadalajara Ecosystem: {ecosystem.tech_companies_count} tech companies, "
          f"{ecosystem.startups_count} startups, ${ecosystem.venture_capital_invested}M VC invested")
    print(f"  • Ecosystem Maturity: {ecosystem.ecosystem_maturity:.2f}")
    print(f"  • Innovation Output: {ecosystem.innovation_output_score:.2f}")
    print()
    
    # Build asset universe
    print("💼 Building Mexican Asset Universe...")
    assets = await allocator.build_asset_universe()
    print(f"✓ Loaded {len(assets)} Mexican market assets")
    print()
    
    # Optimize portfolios with different risk profiles
    risk_profiles = ["conservative", "moderate", "aggressive"]
    
    for risk_profile in risk_profiles:
        print(f"\n{'=' * 70}")
        print(f"🎯 Optimizing {risk_profile.upper()} Portfolio")
        print(f"{'=' * 70}\n")
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,  # 1 million MXN
            risk_tolerance=risk_profile,
            guadalajara_focus=True
        )
        
        report = allocator.generate_portfolio_report(portfolio)
        
        print(f"Portfolio: {report['portfolio_summary']['name']}")
        print(f"Total Value: {report['portfolio_summary']['total_value_mxn']} MXN")
        print()
        
        print("Performance Metrics:")
        for metric, value in report['performance_metrics'].items():
            print(f"  • {metric.replace('_', ' ').title()}: {value}")
        print()
        
        print("Regional Allocation:")
        for region, allocation in report['regional_allocation'].items():
            print(f"  • {region.replace('_', ' ').title()}: {allocation}")
        print()
        
        print("Asset Class Allocation:")
        for asset_class, allocation in report['asset_class_allocation'].items():
            print(f"  • {asset_class.replace('_', ' ').title()}: {allocation}")
        print()
        
        print("Guadalajara Tech Focus:")
        for metric, value in report['guadalajara_focus'].items():
            print(f"  • {metric.replace('_', ' ').title()}: {value}")
        print()
        
        print(f"Selected {len(portfolio.assets)} assets for optimal diversification")
    
    print(f"\n{'=' * 70}")
    print("✓ Mexican Markets Portfolio Optimization Complete")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    asyncio.run(main())
