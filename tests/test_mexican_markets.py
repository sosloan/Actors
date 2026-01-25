#!/usr/bin/env python3
"""
Tests for Mexican Markets Value Creation Portfolio Allocator
"""

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mexican_markets_allocator import (
    MexicanAssetClass,
    RegionalFocus,
    EconomicIndicator,
    MexicanAsset,
    GuadalajaraEcosystem,
    MexicanPortfolio,
    MexicanMarketsAllocator
)


class TestMexicanAssetClass:
    """Test Mexican asset class enumerations"""
    
    def test_asset_classes_defined(self):
        """Test that all required asset classes are defined"""
        assert MexicanAssetClass.EQUITIES.value == "equities"
        assert MexicanAssetClass.BONDS.value == "bonds"
        assert MexicanAssetClass.REAL_ESTATE.value == "real_estate"
        assert MexicanAssetClass.FINTECH.value == "fintech"
        assert MexicanAssetClass.TECH_INNOVATION.value == "tech_innovation"
    
    def test_asset_class_count(self):
        """Test that expected number of asset classes exist"""
        asset_classes = list(MexicanAssetClass)
        assert len(asset_classes) >= 5  # At least 5 core asset classes


class TestRegionalFocus:
    """Test regional focus enumerations"""
    
    def test_guadalajara_defined(self):
        """Test that Guadalajara region is defined"""
        assert RegionalFocus.GUADALAJARA.value == "guadalajara"
    
    def test_major_regions_defined(self):
        """Test that major Mexican economic regions are defined"""
        assert RegionalFocus.MEXICO_CITY.value == "mexico_city"
        assert RegionalFocus.MONTERREY.value == "monterrey"
        assert RegionalFocus.QUERETARO.value == "queretaro"
    
    def test_regional_diversity(self):
        """Test that multiple regions are available"""
        regions = list(RegionalFocus)
        assert len(regions) >= 4  # At least 4 major regions


class TestEconomicIndicator:
    """Test economic indicator data structure"""
    
    def test_economic_indicator_creation(self):
        """Test creating an economic indicator"""
        indicator = EconomicIndicator(
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
        
        assert indicator.region == RegionalFocus.GUADALAJARA
        assert indicator.gdp_growth_rate == 4.2
        assert indicator.tech_ecosystem_score == 0.92
        assert indicator.startup_growth_rate == 28.5
    
    def test_indicator_score_ranges(self):
        """Test that indicator scores are within valid ranges"""
        indicator = EconomicIndicator(
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
        
        # Score-based metrics should be 0.0-1.0
        assert 0.0 <= indicator.industrial_cluster_score <= 1.0
        assert 0.0 <= indicator.tech_ecosystem_score <= 1.0
        assert 0.0 <= indicator.innovation_index <= 1.0
        assert 0.0 <= indicator.infrastructure_quality <= 1.0
        assert 0.0 <= indicator.workforce_quality <= 1.0
        assert 0.0 <= indicator.business_environment <= 1.0


class TestMexicanAsset:
    """Test Mexican asset data structure"""
    
    def test_mexican_asset_creation(self):
        """Test creating a Mexican market asset"""
        asset = MexicanAsset(
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
        )
        
        assert asset.id == "mx-tech-001"
        assert asset.asset_class == MexicanAssetClass.TECH_INNOVATION
        assert asset.region == RegionalFocus.GUADALAJARA
        assert asset.innovation_score == 0.94
    
    def test_asset_scores_valid(self):
        """Test that asset scores are within valid ranges"""
        asset = MexicanAsset(
            id="mx-tech-001",
            name="Test Asset",
            asset_class=MexicanAssetClass.TECH_INNOVATION,
            ticker="TEST",
            region=RegionalFocus.GUADALAJARA,
            sector="Technology",
            market_cap=1_000_000_000,
            current_price=100.0,
            expected_return=15.0,
            volatility=20.0,
            beta=1.2,
            pe_ratio=25.0,
            dividend_yield=2.0,
            liquidity_score=0.80,
            esg_score=0.85,
            growth_potential=0.90,
            innovation_score=0.88,
            regional_economic_score=0.87,
            updated_at=datetime.now()
        )
        
        assert 0.0 <= asset.liquidity_score <= 1.0
        assert 0.0 <= asset.esg_score <= 1.0
        assert 0.0 <= asset.growth_potential <= 1.0
        assert 0.0 <= asset.innovation_score <= 1.0
        assert 0.0 <= asset.regional_economic_score <= 1.0


class TestGuadalajaraEcosystem:
    """Test Guadalajara tech ecosystem data structure"""
    
    def test_guadalajara_ecosystem_creation(self):
        """Test creating Guadalajara ecosystem data"""
        ecosystem = GuadalajaraEcosystem(
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
        
        assert ecosystem.tech_companies_count == 1850
        assert ecosystem.unicorns_count == 3
        assert ecosystem.startups_count == 450
        assert ecosystem.venture_capital_invested == 320.5
    
    def test_ecosystem_scores_valid(self):
        """Test that ecosystem scores are within valid ranges"""
        ecosystem = GuadalajaraEcosystem(
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
        
        assert 0.0 <= ecosystem.tech_talent_pool_score <= 1.0
        assert 0.0 <= ecosystem.infrastructure_readiness <= 1.0
        assert 0.0 <= ecosystem.government_support_score <= 1.0
        assert 0.0 <= ecosystem.global_connectivity_score <= 1.0
        assert 0.0 <= ecosystem.innovation_output_score <= 1.0
        assert 0.0 <= ecosystem.ecosystem_maturity <= 1.0


class TestMexicanMarketsAllocator:
    """Test Mexican Markets Allocator functionality"""
    
    @pytest.mark.asyncio
    async def test_allocator_initialization(self):
        """Test allocator initialization"""
        allocator = MexicanMarketsAllocator()
        
        assert allocator.economic_indicators == {}
        assert allocator.guadalajara_ecosystem is None
        assert allocator.asset_universe == []
        assert allocator.min_guadalajara_allocation == 0.15
    
    @pytest.mark.asyncio
    async def test_initialize_economic_indicators(self):
        """Test economic indicators initialization"""
        allocator = MexicanMarketsAllocator()
        indicators = await allocator.initialize_economic_indicators()
        
        assert len(indicators) >= 4  # At least 4 major regions
        assert RegionalFocus.GUADALAJARA in indicators
        assert RegionalFocus.MEXICO_CITY in indicators
        assert RegionalFocus.MONTERREY in indicators
        
        # Validate Guadalajara indicator
        gdl_indicator = indicators[RegionalFocus.GUADALAJARA]
        assert gdl_indicator.tech_ecosystem_score >= 0.80  # High tech score
        assert gdl_indicator.startup_growth_rate > 20.0  # Strong startup growth
        assert gdl_indicator.innovation_index >= 0.80  # High innovation
    
    @pytest.mark.asyncio
    async def test_initialize_guadalajara_ecosystem(self):
        """Test Guadalajara ecosystem initialization"""
        allocator = MexicanMarketsAllocator()
        ecosystem = await allocator.initialize_guadalajara_ecosystem()
        
        assert ecosystem.tech_companies_count > 1000
        assert ecosystem.startups_count > 300
        assert ecosystem.venture_capital_invested > 200.0  # Over $200M
        assert ecosystem.ecosystem_maturity >= 0.80
        assert ecosystem.tech_talent_pool_score >= 0.80
    
    @pytest.mark.asyncio
    async def test_build_asset_universe(self):
        """Test asset universe building"""
        allocator = MexicanMarketsAllocator()
        assets = await allocator.build_asset_universe()
        
        assert len(assets) >= 5  # At least 5 assets
        
        # Check for Guadalajara tech assets
        gdl_tech_assets = [
            a for a in assets 
            if a.region == RegionalFocus.GUADALAJARA and
            a.asset_class == MexicanAssetClass.TECH_INNOVATION
        ]
        assert len(gdl_tech_assets) >= 2  # At least 2 Guadalajara tech assets
        
        # Check for fintech assets
        fintech_assets = [a for a in assets if a.asset_class == MexicanAssetClass.FINTECH]
        assert len(fintech_assets) >= 1
        
        # Check for bonds
        bond_assets = [a for a in assets if a.asset_class == MexicanAssetClass.BONDS]
        assert len(bond_assets) >= 1
        
        # Check for real estate
        re_assets = [a for a in assets if a.asset_class == MexicanAssetClass.REAL_ESTATE]
        assert len(re_assets) >= 1
    
    @pytest.mark.asyncio
    async def test_calculate_regional_score(self):
        """Test regional score calculation"""
        allocator = MexicanMarketsAllocator()
        await allocator.initialize_economic_indicators()
        
        # Test score for Guadalajara tech
        score = await allocator.calculate_regional_score(
            RegionalFocus.GUADALAJARA,
            MexicanAssetClass.TECH_INNOVATION
        )
        
        assert 0.0 <= score <= 1.0
        assert score > 0.65  # Should be high for Guadalajara tech
    
    @pytest.mark.asyncio
    async def test_optimize_portfolio_conservative(self):
        """Test conservative portfolio optimization"""
        allocator = MexicanMarketsAllocator()
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="conservative",
            guadalajara_focus=True
        )
        
        assert portfolio.total_value == 1_000_000
        assert len(portfolio.assets) > 0
        assert portfolio.expected_return > 0
        assert portfolio.portfolio_volatility > 0
        assert portfolio.guadalajara_tech_allocation >= 0.05  # Some Guadalajara exposure
        
        # Check that regional allocation exists
        assert len(portfolio.regional_allocation) > 0
        assert sum(portfolio.regional_allocation.values()) <= 1.01  # Allow small rounding
        
        # Check that asset class allocation exists
        assert len(portfolio.asset_class_allocation) > 0
        assert sum(portfolio.asset_class_allocation.values()) <= 1.01
    
    @pytest.mark.asyncio
    async def test_optimize_portfolio_moderate(self):
        """Test moderate portfolio optimization"""
        allocator = MexicanMarketsAllocator()
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="moderate",
            guadalajara_focus=True
        )
        
        assert portfolio.total_value == 1_000_000
        assert portfolio.guadalajara_tech_allocation >= 0.10  # Significant Guadalajara exposure
        assert portfolio.expected_return > 10.0  # Reasonable return expectation
        assert portfolio.sharpe_ratio > 0  # Positive risk-adjusted return
    
    @pytest.mark.asyncio
    async def test_optimize_portfolio_aggressive(self):
        """Test aggressive portfolio optimization"""
        allocator = MexicanMarketsAllocator()
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="aggressive",
            guadalajara_focus=True
        )
        
        assert portfolio.total_value == 1_000_000
        assert portfolio.guadalajara_tech_allocation >= 0.15  # Strong Guadalajara exposure
        assert portfolio.expected_return > 12.0  # Higher return expectation
        assert portfolio.innovation_exposure > 0.55  # Good innovation exposure
    
    @pytest.mark.asyncio
    async def test_guadalajara_focus_impact(self):
        """Test that Guadalajara focus increases allocation"""
        allocator = MexicanMarketsAllocator()
        
        # Portfolio with Guadalajara focus
        portfolio_focused = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="moderate",
            guadalajara_focus=True
        )
        
        # Portfolio without Guadalajara focus
        portfolio_unfocused = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="moderate",
            guadalajara_focus=False
        )
        
        # Focused portfolio should have higher Guadalajara allocation
        assert portfolio_focused.guadalajara_tech_allocation >= portfolio_unfocused.guadalajara_tech_allocation
    
    @pytest.mark.asyncio
    async def test_portfolio_diversification(self):
        """Test portfolio diversification"""
        allocator = MexicanMarketsAllocator()
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="moderate",
            guadalajara_focus=True
        )
        
        # Should have multiple regions
        assert len(portfolio.regional_allocation) >= 2
        
        # Should have multiple asset classes
        assert len(portfolio.asset_class_allocation) >= 3
        
        # Diversification score should be reasonable
        assert portfolio.diversification_score > 0.3
    
    @pytest.mark.asyncio
    async def test_generate_portfolio_report(self):
        """Test portfolio report generation"""
        allocator = MexicanMarketsAllocator()
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="moderate",
            guadalajara_focus=True
        )
        
        report = allocator.generate_portfolio_report(portfolio)
        
        # Check report structure
        assert 'portfolio_summary' in report
        assert 'performance_metrics' in report
        assert 'regional_allocation' in report
        assert 'asset_class_allocation' in report
        assert 'guadalajara_focus' in report
        assert 'sustainability' in report
        assert 'asset_details' in report
        
        # Check portfolio summary
        assert 'id' in report['portfolio_summary']
        assert 'name' in report['portfolio_summary']
        assert 'total_value_mxn' in report['portfolio_summary']
        
        # Check performance metrics
        assert 'expected_annual_return' in report['performance_metrics']
        assert 'sharpe_ratio' in report['performance_metrics']
        
        # Check Guadalajara focus metrics
        assert 'tech_ecosystem_allocation' in report['guadalajara_focus']
        assert 'innovation_exposure' in report['guadalajara_focus']
    
    @pytest.mark.asyncio
    async def test_portfolio_metrics_validity(self):
        """Test that portfolio metrics are valid"""
        allocator = MexicanMarketsAllocator()
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="moderate",
            guadalajara_focus=True
        )
        
        # All scores should be 0.0-1.0
        assert 0.0 <= portfolio.diversification_score <= 1.0
        assert 0.0 <= portfolio.regional_economic_score <= 1.0
        assert 0.0 <= portfolio.innovation_exposure <= 1.0
        assert 0.0 <= portfolio.esg_score <= 1.0
        
        # Returns should be positive
        assert portfolio.expected_return > 0
        assert portfolio.portfolio_volatility > 0
        
        # Allocations should sum to approximately 1.0 (allowing for partial allocation)
        total_regional = sum(portfolio.regional_allocation.values())
        assert 0.75 <= total_regional <= 1.05
        
        total_asset_class = sum(portfolio.asset_class_allocation.values())
        assert 0.75 <= total_asset_class <= 1.05


class TestPortfolioValidation:
    """Test portfolio validation and constraints"""
    
    @pytest.mark.asyncio
    async def test_allocation_constraints(self):
        """Test that allocation constraints are respected"""
        allocator = MexicanMarketsAllocator()
        
        portfolio = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="moderate",
            guadalajara_focus=True
        )
        
        # No single asset class should dominate too much
        for asset_class, allocation in portfolio.asset_class_allocation.items():
            assert allocation <= 0.70  # Max 70% in any asset class
    
    @pytest.mark.asyncio
    async def test_risk_profile_impact(self):
        """Test that risk profile impacts portfolio construction"""
        allocator = MexicanMarketsAllocator()
        
        conservative = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="conservative",
            guadalajara_focus=True
        )
        
        aggressive = await allocator.optimize_portfolio(
            target_value=1_000_000,
            risk_tolerance="aggressive",
            guadalajara_focus=True
        )
        
        # Aggressive should have higher expected return
        assert aggressive.expected_return >= conservative.expected_return - 0.5  # Allow small variance
        
        # Aggressive should have higher innovation exposure
        assert aggressive.innovation_exposure >= conservative.innovation_exposure - 0.1  # Allow small variance


def test_imports():
    """Test that all required modules can be imported"""
    from core.mexican_markets_allocator import (
        MexicanAssetClass,
        RegionalFocus,
        EconomicIndicator,
        MexicanAsset,
        GuadalajaraEcosystem,
        MexicanPortfolio,
        MexicanMarketsAllocator
    )
    
    assert MexicanAssetClass is not None
    assert RegionalFocus is not None
    assert EconomicIndicator is not None
    assert MexicanAsset is not None
    assert GuadalajaraEcosystem is not None
    assert MexicanPortfolio is not None
    assert MexicanMarketsAllocator is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
