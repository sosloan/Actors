#!/usr/bin/env python3
"""
🔥 DeFi Market Integration API
RESTful API for Traditional + DeFi market portfolio diversification
"""

import asyncio
import functools
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "core"))

from defi_market_integration import (
    DeFiMarketIntegrationEngine,
    TraditionalAsset, TraditionalAssetClass,
    DeFiProtocol, DeFiProtocolType,
    TraditionalMarketData, DeFiMarketData,
    RiskTier,
    build_sample_traditional_assets,
    build_sample_defi_protocols,
    build_sample_market_data,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

integration_engine: Optional[DeFiMarketIntegrationEngine] = None


def initialize_engine() -> bool:
    global integration_engine
    try:
        integration_engine = DeFiMarketIntegrationEngine()
        logger.info("✅ DeFi Market Integration Engine initialized")
        return True
    except Exception as exc:
        logger.error("❌ Failed to initialize engine: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def async_route(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


def _parse_traditional_assets(data: List[Dict[str, Any]]) -> List[TraditionalAsset]:
    assets = []
    for item in data:
        assets.append(TraditionalAsset(
            symbol=item["symbol"],
            name=item.get("name", item["symbol"]),
            asset_class=TraditionalAssetClass(item.get("asset_class", "equity")),
            current_price=float(item.get("current_price", 0.0)),
            quantity=float(item.get("quantity", 0.0)),
            market_value=float(item.get("market_value", 0.0)),
            expected_annual_return=float(item.get("expected_annual_return", 0.08)),
            volatility=float(item.get("volatility", 0.15)),
            dividend_yield=float(item.get("dividend_yield", 0.0)),
            liquidity_score=float(item.get("liquidity_score", 0.90)),
            beta=float(item.get("beta", 1.0)),
            correlation_to_market=float(item.get("correlation_to_market", 0.7)),
        ))
    return assets


def _parse_defi_protocols(data: List[Dict[str, Any]]) -> List[DeFiProtocol]:
    protocols = []
    for item in data:
        protocols.append(DeFiProtocol(
            protocol_id=item["protocol_id"],
            protocol_name=item.get("protocol_name", item["protocol_id"]),
            protocol_type=DeFiProtocolType(item.get("protocol_type", "lending")),
            blockchain=item.get("blockchain", "ethereum"),
            token_symbol=item.get("token_symbol", ""),
            tvl_usd=float(item.get("tvl_usd", 0.0)),
            current_apy=float(item.get("current_apy", 0.0)),
            position_value_usd=float(item.get("position_value_usd", 0.0)),
            smart_contract_risk=float(item.get("smart_contract_risk", 0.20)),
            audit_score=float(item.get("audit_score", 0.80)),
            liquidity_depth=float(item.get("liquidity_depth", 1_000_000.0)),
            gas_cost_usd=float(item.get("gas_cost_usd", 20.0)),
            impermanent_loss_risk=float(item.get("impermanent_loss_risk", 0.0)),
        ))
    return protocols


def _parse_trad_market(data: Dict[str, Any]) -> TraditionalMarketData:
    return TraditionalMarketData(
        market_index=float(data.get("market_index", 4500.0)),
        market_trend=data.get("market_trend", "bull"),
        vix=float(data.get("vix", 18.0)),
        risk_free_rate=float(data.get("risk_free_rate", 0.045)),
        inflation_rate=float(data.get("inflation_rate", 0.03)),
        fed_rate=float(data.get("fed_rate", 0.055)),
    )


def _parse_defi_market(data: Dict[str, Any]) -> DeFiMarketData:
    return DeFiMarketData(
        total_defi_tvl=float(data.get("total_defi_tvl", 85_000_000_000.0)),
        average_defi_apy=float(data.get("average_defi_apy", 0.085)),
        gas_price_gwei=float(data.get("gas_price_gwei", 25.0)),
        btc_dominance=float(data.get("btc_dominance", 0.48)),
        defi_fear_greed_index=float(data.get("defi_fear_greed_index", 60.0)),
        cross_chain_bridge_volume=float(data.get("cross_chain_bridge_volume", 500_000_000.0)),
    )


def _serialize_result(result) -> Dict[str, Any]:
    """Convert IntegratedPortfolioResult to a JSON-serialisable dict."""
    def _alloc(a):
        return {
            "traditional_weight": a.traditional_weight,
            "defi_weight": a.defi_weight,
            "equity_weight": a.equity_weight,
            "fixed_income_weight": a.fixed_income_weight,
            "commodity_weight": a.commodity_weight,
            "real_estate_weight": a.real_estate_weight,
            "cash_equivalent_weight": a.cash_equivalent_weight,
            "yield_farming_weight": a.yield_farming_weight,
            "liquidity_pool_weight": a.liquidity_pool_weight,
            "staking_weight": a.staking_weight,
            "lending_weight": a.lending_weight,
        }

    r = result.risk_metrics
    d = result.diversification_score
    return {
        "portfolio_id": result.portfolio_id,
        "timestamp": result.timestamp.isoformat(),
        "next_review": result.next_review.isoformat(),
        "estimated_annual_yield": result.estimated_annual_yield,
        "rebalance_signal": result.rebalance_signal.value,
        "optimization_notes": result.optimization_notes,
        "current_allocation": _alloc(result.current_allocation),
        "target_allocation": _alloc(result.target_allocation),
        "risk_metrics": {
            "total_portfolio_value": r.total_portfolio_value,
            "portfolio_volatility": r.portfolio_volatility,
            "sharpe_ratio": r.sharpe_ratio,
            "max_drawdown_estimate": r.max_drawdown_estimate,
            "var_95": r.var_95,
            "traditional_risk_contribution": r.traditional_risk_contribution,
            "defi_risk_contribution": r.defi_risk_contribution,
            "smart_contract_risk_score": r.smart_contract_risk_score,
            "liquidity_risk_score": r.liquidity_risk_score,
            "correlation_trad_defi": r.correlation_trad_defi,
            "risk_tier": r.risk_tier.value,
        },
        "diversification_score": {
            "overall_score": d.overall_score,
            "cross_market_score": d.cross_market_score,
            "within_traditional_score": d.within_traditional_score,
            "within_defi_score": d.within_defi_score,
            "asset_count": d.asset_count,
            "effective_asset_count": d.effective_asset_count,
            "market_type_count": d.market_type_count,
        },
        "traditional_assets": [
            {
                "symbol": a.symbol,
                "name": a.name,
                "asset_class": a.asset_class.value,
                "market_value": a.market_value,
                "expected_annual_return": a.expected_annual_return,
                "volatility": a.volatility,
            }
            for a in result.traditional_assets
        ],
        "defi_protocols": [
            {
                "protocol_id": p.protocol_id,
                "protocol_name": p.protocol_name,
                "protocol_type": p.protocol_type.value,
                "blockchain": p.blockchain,
                "current_apy": p.current_apy,
                "position_value_usd": p.position_value_usd,
                "smart_contract_risk": p.smart_contract_risk,
            }
            for p in result.defi_protocols
        ],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy" if integration_engine is not None else "degraded",
        "service": "DeFi Market Integration API",
        "timestamp": time.time(),
        "engine_initialized": integration_engine is not None,
    })


@app.route("/api/defi/status", methods=["GET"])
def get_status():
    latest = integration_engine.get_latest() if integration_engine else None
    history_count = len(integration_engine.get_history(100)) if integration_engine else 0
    return jsonify({
        "engine_initialized": integration_engine is not None,
        "portfolios_analyzed": history_count,
        "latest_portfolio_id": latest.portfolio_id if latest else None,
        "latest_timestamp": latest.timestamp.isoformat() if latest else None,
    })


async def _analyze(body: Dict[str, Any]):
    if integration_engine is None:
        return jsonify({"error": "Engine not initialized"}), 503

    try:
        trad_assets = _parse_traditional_assets(body.get("traditional_assets", []))
        defi_protocols = _parse_defi_protocols(body.get("defi_protocols", []))

        trad_market = _parse_trad_market(body.get("traditional_market_data", {}))
        defi_market = _parse_defi_market(body.get("defi_market_data", {}))

        risk_tier_raw = body.get("preferred_risk_tier")
        preferred_tier = RiskTier(risk_tier_raw) if risk_tier_raw else None

        result = await integration_engine.analyze_portfolio(
            trad_assets, defi_protocols, trad_market, defi_market, preferred_tier
        )
        return jsonify(_serialize_result(result))
    except (ValueError, KeyError) as exc:
        logger.warning("Bad request: %s", exc)
        return jsonify({"error": "Invalid request parameters"}), 400
    except Exception as exc:
        logger.error("Analysis error: %s", exc)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/defi/analyze", methods=["POST"])
@async_route
async def analyze_portfolio():
    """
    Analyze a combined traditional + DeFi portfolio.

    Body (JSON):
        traditional_assets  – list of TraditionalAsset dicts
        defi_protocols      – list of DeFiProtocol dicts
        traditional_market_data – optional market snapshot
        defi_market_data        – optional DeFi market snapshot
        preferred_risk_tier     – optional: "conservative"|"moderate"|"aggressive"
    """
    return await _analyze(request.get_json(force=True) or {})


@app.route("/api/defi/demo", methods=["POST"])
@async_route
async def run_demo():
    """Run a full demo analysis with built-in sample data."""
    if integration_engine is None:
        return jsonify({"error": "Engine not initialized"}), 503
    try:
        trad_assets = build_sample_traditional_assets()
        defi_protocols = build_sample_defi_protocols()
        trad_data, defi_data = build_sample_market_data()
        result = await integration_engine.analyze_portfolio(
            trad_assets, defi_protocols, trad_data, defi_data
        )
        return jsonify({
            "demo": True,
            "result": _serialize_result(result),
        })
    except Exception as exc:
        logger.error("Demo error: %s", exc)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/defi/history", methods=["GET"])
def get_history():
    """Return recent portfolio analyses."""
    if integration_engine is None:
        return jsonify({"error": "Engine not initialized"}), 503
    limit = min(int(request.args.get("limit", 10)), 100)
    history = integration_engine.get_history(limit)
    return jsonify({
        "count": len(history),
        "portfolios": [_serialize_result(r) for r in history],
    })


@app.route("/api/defi/allocation/recommend", methods=["POST"])
@async_route
async def recommend_allocation():
    """
    Quick allocation recommendation given a risk tier.

    Body (JSON):
        risk_tier   – "conservative" | "moderate" | "aggressive"
        total_value – total portfolio value in USD
    """
    if integration_engine is None:
        return jsonify({"error": "Engine not initialized"}), 503

    body = request.get_json(force=True) or {}
    try:
        tier = RiskTier(body.get("risk_tier", "moderate"))
        total_value = float(body.get("total_value", 100_000.0))

        # Build minimal synthetic positions so the allocator has weights
        trad_value = total_value * 0.60
        defi_value = total_value * 0.40
        trad_assets = [TraditionalAsset(
            symbol="_PLACEHOLDER", name="Placeholder",
            asset_class=TraditionalAssetClass.EQUITY,
            current_price=1.0, quantity=trad_value, market_value=trad_value,
            expected_annual_return=0.08, volatility=0.15, dividend_yield=0.01,
            liquidity_score=0.95, beta=1.0, correlation_to_market=0.9,
        )]
        defi_protocols = [DeFiProtocol(
            protocol_id="_placeholder", protocol_name="Placeholder",
            protocol_type=DeFiProtocolType.LENDING,
            blockchain="ethereum", token_symbol="USDC",
            tvl_usd=1_000_000_000.0, current_apy=0.05,
            position_value_usd=defi_value,
            smart_contract_risk=0.15, audit_score=0.90,
            liquidity_depth=500_000_000.0, gas_cost_usd=15.0,
            impermanent_loss_risk=0.0,
        )]
        trad_data, defi_data = build_sample_market_data()

        result = await integration_engine.analyze_portfolio(
            trad_assets, defi_protocols, trad_data, defi_data, tier
        )

        return jsonify({
            "risk_tier": tier.value,
            "total_value": total_value,
            "target_allocation": {
                "traditional_weight": result.target_allocation.traditional_weight,
                "defi_weight": result.target_allocation.defi_weight,
                "traditional_breakdown": {
                    "equity": result.target_allocation.equity_weight,
                    "fixed_income": result.target_allocation.fixed_income_weight,
                    "commodity": result.target_allocation.commodity_weight,
                    "real_estate": result.target_allocation.real_estate_weight,
                    "cash_equivalent": result.target_allocation.cash_equivalent_weight,
                },
                "defi_breakdown": {
                    "staking": result.target_allocation.staking_weight,
                    "lending": result.target_allocation.lending_weight,
                    "liquidity_pool": result.target_allocation.liquidity_pool_weight,
                    "yield_farming": result.target_allocation.yield_farming_weight,
                },
            },
        })
    except (ValueError, KeyError) as exc:
        return jsonify({"error": "Invalid request parameters"}), 400
    except Exception as exc:
        logger.error("Allocation recommendation error: %s", exc)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🔥 Starting DeFi Market Integration API Server…")
    if not initialize_engine():
        print("❌ Engine initialization failed; some features may be unavailable.")

    print("✅ Engine ready")
    print("📊 Endpoints:")
    print("  GET  /health                        – Health check")
    print("  GET  /api/defi/status               – Engine status")
    print("  POST /api/defi/analyze              – Analyze portfolio")
    print("  POST /api/defi/demo                 – Demo analysis")
    print("  GET  /api/defi/history              – Portfolio history")
    print("  POST /api/defi/allocation/recommend – Allocation recommendation")

    app.run(host="0.0.0.0", port=5005, debug=os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true"))
