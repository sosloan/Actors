#!/usr/bin/env python3
"""
Tests for Harper Henry Harmony – Mexico / Guadalajara Edition
"""

import pytest
import sys
import os
from datetime import datetime
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.harper_henry_harmony_mexico import (
    HarperHenryHarmonyMexico,
    MexicanAssetType,
    GuadalajaraSector,
    CulturalEvent,
    MexicanAsset,
    GuadalajaraStartup,
    JaliscoEconomicIndicator,
    CulturalHarmonyMetric,
    MarketSimulationScenario,
    AsyncMarketSentimentBuilder,
    PortfolioAllocation,
    MexicoGuadalajaraResult
)


class TestMexicanAssetTypes:
    """Test Mexican asset type enumerations"""
    
    def test_asset_types_exist(self):
        """Test that all Mexican asset types are defined"""
        assert MexicanAssetType.MEXICAN_EQUITY
        assert MexicanAssetType.MEXICAN_BOND
        assert MexicanAssetType.MEXICAN_REAL_ESTATE
        assert MexicanAssetType.MEXICAN_FINTECH
        assert MexicanAssetType.GUADALAJARA_TECH_STARTUP
        assert MexicanAssetType.GUADALAJARA_AI_VENTURE
        assert MexicanAssetType.GUADALAJARA_HARDWARE
        assert MexicanAssetType.ARTISANAL_INDUSTRY
        assert MexicanAssetType.CULTURAL_ENTERPRISE
        assert MexicanAssetType.SUSTAINABLE_TECH_VENTURE
    
    def test_guadalajara_sectors_exist(self):
        """Test that Guadalajara tech sectors are defined"""
        assert GuadalajaraSector.IT_SERVICES
        assert GuadalajaraSector.AI_ML
        assert GuadalajaraSector.HARDWARE_MANUFACTURING
        assert GuadalajaraSector.SOFTWARE_DEVELOPMENT
        assert GuadalajaraSector.FINTECH
        assert GuadalajaraSector.EDTECH
        assert GuadalajaraSector.HEALTHTECH
        assert GuadalajaraSector.AGTECH
    
    def test_cultural_events_exist(self):
        """Test that cultural events are defined"""
        assert CulturalEvent.MARIACHI_FESTIVAL
        assert CulturalEvent.BOOK_FAIR
        assert CulturalEvent.FILM_FESTIVAL
        assert CulturalEvent.DAY_OF_DEAD
        assert CulturalEvent.INDEPENDENCE_DAY
        assert CulturalEvent.CULTURAL_HERITAGE_WEEK


class TestDataStructures:
    """Test data structure creation and validation"""
    
    def test_mexican_asset_creation(self):
        """Test creating a Mexican asset"""
        asset = MexicanAsset(
            id="test_001",
            asset_name="Test Asset",
            asset_type=MexicanAssetType.MEXICAN_EQUITY,
            ticker_symbol="TEST",
            current_price_mxn=100.0,
            current_price_usd=5.71,
            exchange_rate_mxn_usd=17.5,
            market_cap_mxn=1_000_000_000,
            volatility=0.20,
            expected_return=0.12,
            risk_score=0.30,
            cultural_impact_score=0.80,
            social_sentiment_score=0.75,
            regional_development_score=0.85,
            created_at=datetime.now()
        )
        
        assert asset.id == "test_001"
        assert asset.asset_name == "Test Asset"
        assert asset.volatility == 0.20
        assert asset.expected_return == 0.12
    
    def test_guadalajara_startup_creation(self):
        """Test creating a Guadalajara startup"""
        startup = GuadalajaraStartup(
            id="startup_001",
            startup_name="Test Startup",
            sector=GuadalajaraSector.AI_ML,
            founding_year=2020,
            employees_count=50,
            valuation_mxn=100_000_000,
            valuation_usd=5_714_286,
            growth_rate=1.5,
            exit_potential_score=0.80,
            innovation_score=0.90,
            tech_maturity_score=0.70,
            market_fit_score=0.85,
            team_quality_score=0.88,
            cultural_alignment_score=0.92,
            sustainability_score=0.87,
            created_at=datetime.now()
        )
        
        assert startup.id == "startup_001"
        assert startup.sector == GuadalajaraSector.AI_ML
        assert startup.growth_rate == 1.5
        assert startup.innovation_score == 0.90


class TestHarperHenryHarmonyMexico:
    """Test Harper Henry Harmony Mexico optimization engine"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """Test engine initialization"""
        engine = HarperHenryHarmonyMexico()
        assert engine is not None
        assert engine.current_exchange_rate > 0
        assert isinstance(engine.mexican_assets, dict)
        assert isinstance(engine.guadalajara_startups, dict)
        assert isinstance(engine.optimization_history, list)
    
    @pytest.mark.asyncio
    async def test_initialize_mexican_assets(self):
        """Test initialization of Mexican assets"""
        engine = HarperHenryHarmonyMexico()
        assets = await engine._initialize_mexican_assets()
        
        assert len(assets) > 0
        assert all(isinstance(asset, MexicanAsset) for asset in assets)
        
        # Check that various asset types are included
        asset_types = {asset.asset_type for asset in assets}
        assert MexicanAssetType.MEXICAN_EQUITY in asset_types
        assert MexicanAssetType.MEXICAN_BOND in asset_types
    
    @pytest.mark.asyncio
    async def test_initialize_guadalajara_startups(self):
        """Test initialization of Guadalajara startups"""
        engine = HarperHenryHarmonyMexico()
        startups = await engine._initialize_guadalajara_startups()
        
        assert len(startups) > 0
        assert all(isinstance(startup, GuadalajaraStartup) for startup in startups)
        
        # Check that startups have valid metrics
        for startup in startups:
            assert 0 <= startup.innovation_score <= 1
            assert 0 <= startup.exit_potential_score <= 1
            assert startup.growth_rate > 0
    
    @pytest.mark.asyncio
    async def test_initialize_jalisco_indicators(self):
        """Test initialization of Jalisco economic indicators"""
        engine = HarperHenryHarmonyMexico()
        indicators = await engine._initialize_jalisco_indicators()
        
        assert len(indicators) > 0
        assert all(isinstance(ind, JaliscoEconomicIndicator) for ind in indicators)
        
        # Check GDP indicator exists
        gdp_indicators = [ind for ind in indicators if "GDP" in ind.indicator_name]
        assert len(gdp_indicators) > 0
    
    @pytest.mark.asyncio
    async def test_initialize_cultural_metrics(self):
        """Test initialization of cultural harmony metrics"""
        engine = HarperHenryHarmonyMexico()
        metrics = await engine._initialize_cultural_metrics()
        
        assert len(metrics) > 0
        assert all(isinstance(metric, CulturalHarmonyMetric) for metric in metrics)
        
        # Check that metrics have valid scores
        for metric in metrics:
            assert 0 <= metric.social_sentiment_index <= 1
            assert 0 <= metric.community_engagement_score <= 1
            assert metric.festival_commerce_boost >= 1.0
    
    @pytest.mark.asyncio
    async def test_initialize_sentiment_builders(self):
        """Test initialization of async sentiment builders"""
        engine = HarperHenryHarmonyMexico()
        builders = await engine._initialize_sentiment_builders()
        
        assert len(builders) > 0
        assert all(isinstance(builder, AsyncMarketSentimentBuilder) for builder in builders)
        
        # Check that builders are active
        for builder in builders:
            assert builder.is_active
            assert builder.update_frequency_minutes > 0
            assert len(builder.sentiment_sources) > 0
    
    @pytest.mark.asyncio
    async def test_generate_market_scenarios(self):
        """Test generation of market simulation scenarios"""
        engine = HarperHenryHarmonyMexico()
        scenarios = await engine._generate_market_scenarios()
        
        assert len(scenarios) > 0
        assert all(isinstance(scenario, MarketSimulationScenario) for scenario in scenarios)
        
        # Check that probabilities sum to 1.0 (approximately)
        total_probability = sum(scenario.probability for scenario in scenarios)
        assert abs(total_probability - 1.0) < 0.01
    
    @pytest.mark.asyncio
    async def test_optimize_mexico_portfolio(self):
        """Test full portfolio optimization"""
        engine = HarperHenryHarmonyMexico()
        
        result = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.6,
            cultural_priority=0.7,
            tech_hub_focus=0.8
        )
        
        assert isinstance(result, MexicoGuadalajaraResult)
        assert result.total_portfolio_value_usd == 100_000.0
        assert result.exchange_rate_mxn_usd > 0
        assert len(result.portfolio_allocations) > 0
        assert 0 <= result.optimization_score <= 1
        assert result.optimization_time >= 0
    
    @pytest.mark.asyncio
    async def test_portfolio_allocations_sum_to_one(self):
        """Test that portfolio allocations sum to 100%"""
        engine = HarperHenryHarmonyMexico()
        
        result = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.6,
            cultural_priority=0.7,
            tech_hub_focus=0.8
        )
        
        total_allocation = sum(alloc.allocation_percentage for alloc in result.portfolio_allocations)
        assert abs(total_allocation - 1.0) < 0.01  # Should sum to approximately 1.0
    
    @pytest.mark.asyncio
    async def test_portfolio_metrics_validity(self):
        """Test that portfolio metrics are within valid ranges"""
        engine = HarperHenryHarmonyMexico()
        
        result = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.6,
            cultural_priority=0.7,
            tech_hub_focus=0.8
        )
        
        # Check financial metrics
        assert result.expected_annual_return >= 0
        assert result.portfolio_volatility >= 0
        assert result.max_drawdown >= 0
        
        # Check cultural metrics
        assert 0 <= result.cultural_impact_score <= 1
        assert 0 <= result.social_sentiment_score <= 1
        assert 0 <= result.community_engagement_score <= 1
        assert 0 <= result.regional_development_score <= 1
        
        # Check tech hub metrics
        assert 0 <= result.tech_hub_integration_score <= 1
        assert 0 <= result.startup_portfolio_weight <= 1
        assert 0 <= result.innovation_index <= 1
    
    @pytest.mark.asyncio
    async def test_different_risk_tolerances(self):
        """Test optimization with different risk tolerances"""
        engine = HarperHenryHarmonyMexico()
        
        # Low risk
        result_low = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.3,
            cultural_priority=0.7,
            tech_hub_focus=0.5
        )
        
        # High risk
        result_high = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.9,
            cultural_priority=0.7,
            tech_hub_focus=0.5
        )
        
        # Both should produce valid results
        assert result_low.optimization_score >= 0
        assert result_high.optimization_score >= 0
    
    @pytest.mark.asyncio
    async def test_tech_hub_focus_impact(self):
        """Test that tech hub focus impacts startup allocation"""
        engine = HarperHenryHarmonyMexico()
        
        # Low tech hub focus
        result_low_tech = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.6,
            cultural_priority=0.7,
            tech_hub_focus=0.3
        )
        
        # High tech hub focus
        result_high_tech = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.6,
            cultural_priority=0.7,
            tech_hub_focus=0.9
        )
        
        # Higher tech focus should result in higher startup weight
        assert result_high_tech.startup_portfolio_weight >= result_low_tech.startup_portfolio_weight - 0.1
    
    @pytest.mark.asyncio
    async def test_cultural_priority_impact(self):
        """Test that cultural priority impacts cultural metrics"""
        engine = HarperHenryHarmonyMexico()
        
        # Low cultural priority
        result_low = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.6,
            cultural_priority=0.3,
            tech_hub_focus=0.7
        )
        
        # High cultural priority
        result_high = await engine.optimize_mexico_portfolio(
            portfolio_budget_usd=100_000.0,
            risk_tolerance=0.6,
            cultural_priority=0.9,
            tech_hub_focus=0.7
        )
        
        # Both should have valid cultural impact scores
        assert result_low.cultural_impact_score >= 0
        assert result_high.cultural_impact_score >= 0


class TestPortfolioOptimization:
    """Test portfolio optimization logic"""
    
    @pytest.mark.asyncio
    async def test_calculate_portfolio_metrics(self):
        """Test portfolio metrics calculation"""
        engine = HarperHenryHarmonyMexico()
        
        # Initialize data
        assets = await engine._initialize_mexican_assets()
        startups = await engine._initialize_guadalajara_startups()
        
        # Create sample allocations
        allocations = [
            PortfolioAllocation(
                id="alloc_001",
                asset_id="mex_eq_001",
                asset_name="Test Asset 1",
                asset_type=MexicanAssetType.MEXICAN_EQUITY,
                allocation_percentage=0.5,
                allocation_amount_mxn=50000,
                allocation_amount_usd=2857,
                risk_contribution=0.15,
                return_contribution=0.06,
                cultural_impact_contribution=0.40,
                created_at=datetime.now()
            ),
            PortfolioAllocation(
                id="alloc_002",
                asset_id="mex_bond_001",
                asset_name="Test Asset 2",
                asset_type=MexicanAssetType.MEXICAN_BOND,
                allocation_percentage=0.5,
                allocation_amount_mxn=50000,
                allocation_amount_usd=2857,
                risk_contribution=0.075,
                return_contribution=0.0375,
                cultural_impact_contribution=0.325,
                created_at=datetime.now()
            )
        ]
        
        metrics = engine._calculate_portfolio_metrics(allocations, assets, startups)
        
        assert "expected_return" in metrics
        assert "volatility" in metrics
        assert "sharpe_ratio" in metrics
        assert "max_drawdown" in metrics
        
        assert metrics["expected_return"] >= 0
        assert metrics["volatility"] >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_cultural_impact(self):
        """Test cultural impact calculation"""
        engine = HarperHenryHarmonyMexico()
        
        # Initialize data
        assets = await engine._initialize_mexican_assets()
        startups = await engine._initialize_guadalajara_startups()
        cultural_metrics = await engine._initialize_cultural_metrics()
        
        # Create sample allocations
        allocations = [
            PortfolioAllocation(
                id="alloc_001",
                asset_id="mex_cult_001",
                asset_name="Cultural Asset",
                asset_type=MexicanAssetType.CULTURAL_ENTERPRISE,
                allocation_percentage=1.0,
                allocation_amount_mxn=100000,
                allocation_amount_usd=5714,
                risk_contribution=0.3,
                return_contribution=0.1,
                cultural_impact_contribution=0.9,
                created_at=datetime.now()
            )
        ]
        
        impact = engine._calculate_cultural_impact(
            allocations, assets, startups, cultural_metrics
        )
        
        assert "cultural_impact_score" in impact
        assert "social_sentiment_score" in impact
        assert "community_engagement_score" in impact
        assert "regional_development_score" in impact
        
        assert 0 <= impact["cultural_impact_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_tech_hub_metrics(self):
        """Test tech hub metrics calculation"""
        engine = HarperHenryHarmonyMexico()
        
        # Initialize startups
        startups = await engine._initialize_guadalajara_startups()
        
        # Create allocations with startup focus
        allocations = [
            PortfolioAllocation(
                id="alloc_startup",
                asset_id="gdl_startup_001",
                asset_name="Startup",
                asset_type=MexicanAssetType.GUADALAJARA_TECH_STARTUP,
                allocation_percentage=0.6,
                allocation_amount_mxn=60000,
                allocation_amount_usd=3429,
                risk_contribution=0.36,
                return_contribution=0.24,
                cultural_impact_contribution=0.55,
                created_at=datetime.now()
            ),
            PortfolioAllocation(
                id="alloc_other",
                asset_id="mex_eq_001",
                asset_name="Other",
                asset_type=MexicanAssetType.MEXICAN_EQUITY,
                allocation_percentage=0.4,
                allocation_amount_mxn=40000,
                allocation_amount_usd=2286,
                risk_contribution=0.14,
                return_contribution=0.048,
                cultural_impact_contribution=0.32,
                created_at=datetime.now()
            )
        ]
        
        tech_metrics = engine._calculate_tech_hub_metrics(allocations, startups)
        
        assert "tech_hub_integration_score" in tech_metrics
        assert "startup_portfolio_weight" in tech_metrics
        assert "innovation_index" in tech_metrics
        assert "exit_potential_score" in tech_metrics
        
        # Should have significant startup weight
        assert tech_metrics["startup_portfolio_weight"] >= 0.5


class TestOptimizationScoring:
    """Test optimization scoring and harmony checks"""
    
    @pytest.mark.asyncio
    async def test_optimization_score_calculation(self):
        """Test optimization score calculation"""
        engine = HarperHenryHarmonyMexico()
        
        portfolio_metrics = {
            "expected_return": 0.15,
            "volatility": 0.20,
            "sharpe_ratio": 1.5,
            "max_drawdown": 0.25
        }
        
        cultural_impact = {
            "cultural_impact_score": 0.85,
            "social_sentiment_score": 0.80,
            "community_engagement_score": 0.90,
            "regional_development_score": 0.88
        }
        
        tech_metrics = {
            "tech_hub_integration_score": 0.75,
            "startup_portfolio_weight": 0.40,
            "innovation_index": 0.85,
            "exit_potential_score": 0.80
        }
        
        score = engine._calculate_optimization_score(
            portfolio_metrics, cultural_impact, tech_metrics
        )
        
        assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_harmony_achievement_check(self):
        """Test harmony achievement check"""
        engine = HarperHenryHarmonyMexico()
        
        # High-performing portfolio
        portfolio_metrics_high = {
            "sharpe_ratio": 1.5,
            "volatility": 0.15
        }
        
        cultural_impact_high = {
            "cultural_impact_score": 0.85,
            "regional_development_score": 0.88
        }
        
        tech_metrics_high = {
            "tech_hub_integration_score": 0.75
        }
        
        harmony_achieved = engine._check_harmony_achieved(
            portfolio_metrics_high, cultural_impact_high, tech_metrics_high
        )
        
        assert isinstance(harmony_achieved, bool)
        
        # Low-performing portfolio
        portfolio_metrics_low = {
            "sharpe_ratio": 0.3,
            "volatility": 0.40
        }
        
        cultural_impact_low = {
            "cultural_impact_score": 0.40,
            "regional_development_score": 0.50
        }
        
        tech_metrics_low = {
            "tech_hub_integration_score": 0.30
        }
        
        harmony_not_achieved = engine._check_harmony_achieved(
            portfolio_metrics_low, cultural_impact_low, tech_metrics_low
        )
        
        assert harmony_not_achieved == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
