#!/usr/bin/env python3
"""
Tests for core/defi_market_integration.py and apis/defi_integration_api.py

Covers:
  - DiversificationCalculator
  - RiskCalculator
  - AllocationOptimizer
  - TraditionalMarketAnalyzer
  - DeFiProtocolAnalyzer
  - DeFiMarketIntegrationEngine (async)
  - Flask API endpoints via test client
"""

import sys
import os
import asyncio
import json
import types
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Path setup – make core/ importable
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(REPO_ROOT, "core"))
sys.path.insert(0, os.path.join(REPO_ROOT, "apis"))

from defi_market_integration import (
    TraditionalAsset, TraditionalAssetClass,
    DeFiProtocol, DeFiProtocolType,
    TraditionalMarketData, DeFiMarketData,
    PortfolioAllocation, RiskTier, RebalanceSignal,
    DiversificationCalculator, RiskCalculator,
    AllocationOptimizer, TraditionalMarketAnalyzer, DeFiProtocolAnalyzer,
    DeFiMarketIntegrationEngine,
    build_sample_traditional_assets,
    build_sample_defi_protocols,
    build_sample_market_data,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def trad_assets():
    return build_sample_traditional_assets()


@pytest.fixture
def defi_protocols():
    return build_sample_defi_protocols()


@pytest.fixture
def market_data():
    return build_sample_market_data()


@pytest.fixture
def trad_market(market_data):
    return market_data[0]


@pytest.fixture
def defi_market(market_data):
    return market_data[1]


@pytest.fixture
def engine():
    return DeFiMarketIntegrationEngine()


# ---------------------------------------------------------------------------
# TraditionalMarketAnalyzer
# ---------------------------------------------------------------------------

class TestTraditionalMarketAnalyzer:
    def test_empty_assets_returns_zeros(self, trad_market):
        analyzer = TraditionalMarketAnalyzer()
        metrics = analyzer.calculate_portfolio_metrics([], trad_market)
        assert metrics["volatility"] == 0.0
        assert metrics["total_value"] == 0.0

    def test_metrics_with_assets(self, trad_assets, trad_market):
        analyzer = TraditionalMarketAnalyzer()
        metrics = analyzer.calculate_portfolio_metrics(trad_assets, trad_market)
        assert metrics["total_value"] > 0
        assert 0.0 < metrics["volatility"] < 1.0
        assert metrics["expected_return"] > 0.0

    def test_liquidity_score_range(self, trad_assets):
        analyzer = TraditionalMarketAnalyzer()
        score = analyzer.assess_liquidity(trad_assets)
        assert 0.0 <= score <= 1.0

    def test_empty_liquidity_returns_one(self):
        analyzer = TraditionalMarketAnalyzer()
        assert analyzer.assess_liquidity([]) == 1.0


# ---------------------------------------------------------------------------
# DeFiProtocolAnalyzer
# ---------------------------------------------------------------------------

class TestDeFiProtocolAnalyzer:
    def test_empty_protocols_returns_zeros(self, defi_market):
        analyzer = DeFiProtocolAnalyzer()
        metrics = analyzer.calculate_portfolio_metrics([], defi_market)
        assert metrics["total_value"] == 0.0
        assert metrics["weighted_apy"] == 0.0

    def test_metrics_with_protocols(self, defi_protocols, defi_market):
        analyzer = DeFiProtocolAnalyzer()
        metrics = analyzer.calculate_portfolio_metrics(defi_protocols, defi_market)
        assert metrics["total_value"] > 0
        assert 0.0 < metrics["weighted_apy"] < 1.0
        assert 0.0 <= metrics["smart_contract_risk"] <= 1.0

    def test_effective_yield_less_than_gross(self, defi_protocols):
        analyzer = DeFiProtocolAnalyzer()
        effective = analyzer.estimate_effective_yield(defi_protocols)
        gross = sum(p.position_value_usd * p.current_apy for p in defi_protocols) / \
                sum(p.position_value_usd for p in defi_protocols)
        assert effective <= gross

    def test_effective_yield_empty(self):
        analyzer = DeFiProtocolAnalyzer()
        assert analyzer.estimate_effective_yield([]) == 0.0


# ---------------------------------------------------------------------------
# DiversificationCalculator
# ---------------------------------------------------------------------------

class TestDiversificationCalculator:
    def test_empty_portfolio(self):
        calc = DiversificationCalculator()
        score = calc.calculate([], [])
        assert score.overall_score == 0.0
        assert score.asset_count == 0

    def test_single_asset(self, trad_assets):
        calc = DiversificationCalculator()
        score = calc.calculate([trad_assets[0]], [])
        assert score.overall_score >= 0.0
        assert score.market_type_count == 1

    def test_mixed_portfolio(self, trad_assets, defi_protocols):
        calc = DiversificationCalculator()
        score = calc.calculate(trad_assets, defi_protocols)
        assert 0.0 <= score.overall_score <= 1.0
        assert score.market_type_count == 2
        assert score.effective_asset_count > 1.0

    def test_cross_market_score_max_at_equal_weights(self):
        calc = DiversificationCalculator()
        # Equal-weight trad and DeFi
        trad = [TraditionalAsset(
            symbol="X", name="X", asset_class=TraditionalAssetClass.EQUITY,
            current_price=100.0, quantity=1.0, market_value=1000.0,
            expected_annual_return=0.10, volatility=0.15, dividend_yield=0.0,
            liquidity_score=0.9, beta=1.0, correlation_to_market=0.8,
        )]
        defi = [DeFiProtocol(
            protocol_id="y", protocol_name="Y", protocol_type=DeFiProtocolType.LENDING,
            blockchain="ethereum", token_symbol="USDC",
            tvl_usd=1e9, current_apy=0.05, position_value_usd=1000.0,
            smart_contract_risk=0.1, audit_score=0.9,
            liquidity_depth=1e8, gas_cost_usd=10.0, impermanent_loss_risk=0.0,
        )]
        score = calc.calculate(trad, defi)
        assert score.cross_market_score == pytest.approx(1.0, abs=0.01)


# ---------------------------------------------------------------------------
# RiskCalculator
# ---------------------------------------------------------------------------

class TestRiskCalculator:
    def test_zero_portfolio(self):
        calc = RiskCalculator()
        trad = {"total_value": 0.0, "volatility": 0.0, "expected_return": 0.0}
        defi = {"total_value": 0.0, "weighted_apy": 0.0, "smart_contract_risk": 0.0, "liquidity_risk": 0.0}
        trad_market = TraditionalMarketData(
            market_index=4500.0, market_trend="bull", vix=18.0,
            risk_free_rate=0.045, inflation_rate=0.03, fed_rate=0.055,
        )
        metrics = calc.calculate(trad, defi, trad_market)
        assert metrics.total_portfolio_value == 0.0

    def test_risk_metrics_with_data(self, trad_assets, defi_protocols, trad_market, defi_market):
        trad_analyzer = TraditionalMarketAnalyzer()
        defi_analyzer = DeFiProtocolAnalyzer()
        trad_m = trad_analyzer.calculate_portfolio_metrics(trad_assets, trad_market)
        defi_m = defi_analyzer.calculate_portfolio_metrics(defi_protocols, defi_market)
        calc = RiskCalculator()
        risk = calc.calculate(trad_m, defi_m, trad_market)
        assert risk.total_portfolio_value > 0
        assert 0.0 < risk.portfolio_volatility < 2.0
        assert risk.var_95 >= 0.0
        assert risk.risk_tier in list(RiskTier)

    def test_sharpe_ratio_is_finite(self, trad_assets, defi_protocols, trad_market, defi_market):
        trad_analyzer = TraditionalMarketAnalyzer()
        defi_analyzer = DeFiProtocolAnalyzer()
        trad_m = trad_analyzer.calculate_portfolio_metrics(trad_assets, trad_market)
        defi_m = defi_analyzer.calculate_portfolio_metrics(defi_protocols, defi_market)
        calc = RiskCalculator()
        risk = calc.calculate(trad_m, defi_m, trad_market)
        assert abs(risk.sharpe_ratio) < 100  # sanity bound


# ---------------------------------------------------------------------------
# AllocationOptimizer
# ---------------------------------------------------------------------------

class TestAllocationOptimizer:
    @pytest.mark.parametrize("tier", list(RiskTier))
    def test_weights_sum_to_one(self, tier):
        optimizer = AllocationOptimizer()
        current = PortfolioAllocation(traditional_weight=0.60, defi_weight=0.40)
        target, signal = optimizer.recommend_allocation(tier, current, {}, {})
        total = target.traditional_weight + target.defi_weight
        assert total == pytest.approx(1.0, abs=1e-4)

    def test_conservative_is_trad_heavy(self):
        optimizer = AllocationOptimizer()
        current = PortfolioAllocation(traditional_weight=0.80, defi_weight=0.20)
        target, _ = optimizer.recommend_allocation(RiskTier.CONSERVATIVE, current, {}, {})
        assert target.traditional_weight >= 0.70

    def test_aggressive_is_defi_friendly(self):
        optimizer = AllocationOptimizer()
        current = PortfolioAllocation(traditional_weight=0.40, defi_weight=0.60)
        target, _ = optimizer.recommend_allocation(RiskTier.AGGRESSIVE, current, {}, {})
        assert target.defi_weight >= 0.40

    def test_hold_signal_when_on_target(self):
        optimizer = AllocationOptimizer()
        # moderate target is 0.60 trad; feed exactly that
        current = PortfolioAllocation(traditional_weight=0.60, defi_weight=0.40)
        _, signal = optimizer.recommend_allocation(RiskTier.MODERATE, current, {}, {})
        assert signal == RebalanceSignal.HOLD

    def test_rebalance_signal_on_large_drift(self):
        optimizer = AllocationOptimizer()
        # large over-allocation to trad
        current = PortfolioAllocation(traditional_weight=0.95, defi_weight=0.05)
        _, signal = optimizer.recommend_allocation(RiskTier.MODERATE, current, {}, {})
        assert signal == RebalanceSignal.REDUCE_TRADITIONAL


# ---------------------------------------------------------------------------
# DeFiMarketIntegrationEngine (async)
# ---------------------------------------------------------------------------

class TestDeFiMarketIntegrationEngine:
    def test_analyze_returns_result(self, engine, trad_assets, defi_protocols, trad_market, defi_market):
        result = asyncio.run(engine.analyze_portfolio(
            trad_assets, defi_protocols, trad_market, defi_market
        ))
        assert result.portfolio_id.startswith("portfolio_")
        assert isinstance(result.timestamp, datetime)
        assert result.risk_metrics.total_portfolio_value > 0

    def test_history_grows(self, engine, trad_assets, defi_protocols, trad_market, defi_market):
        asyncio.run(engine.analyze_portfolio(trad_assets, defi_protocols, trad_market, defi_market))
        asyncio.run(engine.analyze_portfolio(trad_assets, defi_protocols, trad_market, defi_market))
        assert len(engine.get_history()) >= 2

    def test_get_latest(self, engine, trad_assets, defi_protocols, trad_market, defi_market):
        assert engine.get_latest() is None
        r = asyncio.run(engine.analyze_portfolio(trad_assets, defi_protocols, trad_market, defi_market))
        assert engine.get_latest().portfolio_id == r.portfolio_id

    def test_empty_positions(self, engine, trad_market, defi_market):
        result = asyncio.run(engine.analyze_portfolio([], [], trad_market, defi_market))
        assert result.risk_metrics.total_portfolio_value == 0.0

    def test_preferred_risk_tier_respected(self, engine, trad_assets, defi_protocols, trad_market, defi_market):
        result = asyncio.run(engine.analyze_portfolio(
            trad_assets, defi_protocols, trad_market, defi_market,
            preferred_risk_tier=RiskTier.CONSERVATIVE,
        ))
        # Conservative target should have trad weight >= 0.70
        assert result.target_allocation.traditional_weight >= 0.70

    def test_yield_is_positive(self, engine, trad_assets, defi_protocols, trad_market, defi_market):
        result = asyncio.run(engine.analyze_portfolio(
            trad_assets, defi_protocols, trad_market, defi_market
        ))
        assert result.estimated_annual_yield > 0.0

    def test_optimization_notes_populated(self, engine, trad_assets, defi_protocols, trad_market, defi_market):
        result = asyncio.run(engine.analyze_portfolio(
            trad_assets, defi_protocols, trad_market, defi_market
        ))
        assert isinstance(result.optimization_notes, list)
        assert len(result.optimization_notes) >= 1


# ---------------------------------------------------------------------------
# Flask API tests
# ---------------------------------------------------------------------------

# Inject mock flask_cors so import doesn't require the package
_mock_cors = types.ModuleType("flask_cors")
_mock_cors.CORS = MagicMock(return_value=None)
sys.modules.setdefault("flask_cors", _mock_cors)

import defi_integration_api as api_module
from defi_integration_api import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    api_module.integration_engine = DeFiMarketIntegrationEngine()
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def client_no_engine():
    flask_app.config["TESTING"] = True
    api_module.integration_engine = None
    with flask_app.test_client() as c:
        yield c


class TestDeFiIntegrationAPI:
    def test_health_check_healthy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"

    def test_health_check_degraded_when_no_engine(self, client_no_engine):
        resp = client_no_engine.get("/health")
        data = resp.get_json()
        assert data["status"] == "degraded"

    def test_status_endpoint(self, client):
        resp = client.get("/api/defi/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["engine_initialized"] is True

    def test_demo_endpoint(self, client):
        resp = client.post("/api/defi/demo")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["demo"] is True
        assert "result" in data
        assert "portfolio_id" in data["result"]

    def test_demo_returns_503_without_engine(self, client_no_engine):
        resp = client_no_engine.post("/api/defi/demo")
        assert resp.status_code == 503

    def test_analyze_endpoint_with_sample_data(self, client):
        trad_assets = build_sample_traditional_assets()
        defi_protocols = build_sample_defi_protocols()
        trad_data, defi_data = build_sample_market_data()

        payload = {
            "traditional_assets": [
                {
                    "symbol": a.symbol, "name": a.name,
                    "asset_class": a.asset_class.value,
                    "current_price": a.current_price, "quantity": a.quantity,
                    "market_value": a.market_value,
                    "expected_annual_return": a.expected_annual_return,
                    "volatility": a.volatility, "dividend_yield": a.dividend_yield,
                    "liquidity_score": a.liquidity_score, "beta": a.beta,
                    "correlation_to_market": a.correlation_to_market,
                }
                for a in trad_assets
            ],
            "defi_protocols": [
                {
                    "protocol_id": p.protocol_id, "protocol_name": p.protocol_name,
                    "protocol_type": p.protocol_type.value,
                    "blockchain": p.blockchain, "token_symbol": p.token_symbol,
                    "tvl_usd": p.tvl_usd, "current_apy": p.current_apy,
                    "position_value_usd": p.position_value_usd,
                    "smart_contract_risk": p.smart_contract_risk,
                    "audit_score": p.audit_score,
                    "liquidity_depth": p.liquidity_depth,
                    "gas_cost_usd": p.gas_cost_usd,
                    "impermanent_loss_risk": p.impermanent_loss_risk,
                }
                for p in defi_protocols
            ],
        }
        resp = client.post(
            "/api/defi/analyze",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "portfolio_id" in data
        assert data["risk_metrics"]["total_portfolio_value"] > 0

    def test_analyze_empty_payload(self, client):
        resp = client.post(
            "/api/defi/analyze",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 200  # empty positions → valid zero-value portfolio

    def test_analyze_invalid_asset_class(self, client):
        payload = {
            "traditional_assets": [{"symbol": "X", "asset_class": "not_valid_class"}]
        }
        resp = client.post(
            "/api/defi/analyze",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_history_endpoint(self, client):
        # First run a demo to populate history
        client.post("/api/defi/demo")
        resp = client.get("/api/defi/history")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "portfolios" in data
        assert data["count"] >= 1

    def test_allocation_recommend_endpoint(self, client):
        payload = {"risk_tier": "moderate", "total_value": 100000.0}
        resp = client.post(
            "/api/defi/allocation/recommend",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["risk_tier"] == "moderate"
        alloc = data["target_allocation"]
        total = alloc["traditional_weight"] + alloc["defi_weight"]
        assert total == pytest.approx(1.0, abs=1e-3)

    def test_allocation_recommend_invalid_tier(self, client):
        payload = {"risk_tier": "unknown_tier"}
        resp = client.post(
            "/api/defi/allocation/recommend",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_404_handler(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404
