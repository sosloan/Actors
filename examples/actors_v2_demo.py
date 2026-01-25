#!/usr/bin/env python3
"""
🎯 ACTORS v2 Demo
Demonstrates Configuration Layer, Harper Henry Guardrails, and Festival-Aware Portfolio Management

"Where financial optimization meets cultural harmony"
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_loader import get_config
from core.harper_henry_guardrails import HarperHenryGuardrails, Asset, Portfolio
from core.festival_calendar import FestivalCalendar
from core.metrics_tracker import MetricsTracker
from core.metrics_exporter import MetricsExporter


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def main():
    """Run ACTORS v2 demonstration"""
    
    print_section("🚀 ACTORS v2 Configuration Layer & Harper Henry Guardrails Demo")
    
    # 1. Load Configuration
    print_section("1️⃣  Loading Configuration")
    
    config_path = Path(__file__).parent.parent / "config.yaml"
    config = get_config(str(config_path))
    
    print(f"✅ Configuration loaded from: {config_path}")
    print(f"   • Agents configured: portfolio, execution, defi, risk")
    print(f"   • Metrics tracking: Enhanced")
    print(f"   • Export formats: {', '.join(config.get_metrics_config().export_formats)}")
    
    # 2. Initialize Harper Henry Guardrails
    print_section("2️⃣  Initializing Harper Henry Guardrails")
    
    guardrails_config = config.get_guardrails_config()
    guardrails = HarperHenryGuardrails(guardrails_config)
    
    print(f"✅ Guardrails initialized:")
    print(f"   • Ethical investment: {guardrails.ethical}")
    print(f"   • Max social risk: {guardrails.max_social_risk:.1%}")
    print(f"   • Min cultural weight: {guardrails.min_cultural_weight:.1%}")
    print(f"   • Festival tilt enabled: {guardrails.festival_tilt_enabled}")
    
    # 3. Initialize Festival Calendar
    print_section("3️⃣  Initializing Festival Calendar")
    
    calendar_config = config.get_festival_calendar_config()
    calendar = FestivalCalendar(calendar_config)
    
    print(f"✅ Festival calendar initialized:")
    print(f"   • Region: {calendar.region}")
    print(f"   • Festivals tracked: {len(calendar.festivals)}")
    
    # Check for active festivals
    active_festivals = calendar.get_active_festivals()
    if active_festivals:
        print(f"   • Active festivals: {len(active_festivals)}")
        for af in active_festivals:
            print(f"     - {af.festival.name} (tilt: {af.tilt_factor:.2f}x)")
    else:
        print(f"   • No active festivals at this time")
    
    # Check upcoming festivals
    upcoming = calendar.get_upcoming_festivals(days_ahead=90)
    if upcoming:
        print(f"   • Upcoming festivals (next 90 days): {len(upcoming)}")
        for fest in upcoming[:3]:  # Show first 3
            print(f"     - {fest.name} ({fest.start_date})")
    
    # 4. Create Sample Portfolio
    print_section("4️⃣  Creating Sample Portfolio")
    
    portfolio = Portfolio(
        id="demo-portfolio-001",
        name="Cultural Harmony Portfolio",
        assets=[
            # Cultural assets
            Asset(
                id="asset-1",
                name="Guadalajara Cultural Exchange Fund",
                weight=0.15,
                is_cultural=True,
                is_festival_aligned=True,
                is_ethical=True,
                social_risk=0.05,
                sector="cultural_events",
                region="Guadalajara"
            ),
            Asset(
                id="asset-2",
                name="Traditional Artisan Cooperative",
                weight=0.10,
                is_cultural=True,
                is_festival_aligned=True,
                is_ethical=True,
                social_risk=0.08,
                sector="artisan_crafts",
                region="Guadalajara"
            ),
            
            # Festival-aligned assets
            Asset(
                id="asset-3",
                name="Local Music & Arts Fund",
                weight=0.15,
                is_cultural=True,
                is_festival_aligned=True,
                is_ethical=True,
                social_risk=0.06,
                sector="local_music",
                region="Guadalajara"
            ),
            
            # Ethical tech assets
            Asset(
                id="asset-4",
                name="Green Technology Fund",
                weight=0.25,
                is_cultural=False,
                is_festival_aligned=False,
                is_ethical=True,
                social_risk=0.12,
                sector="technology",
                region="Global"
            ),
            
            # Traditional investment
            Asset(
                id="asset-5",
                name="Sustainable Agriculture ETF",
                weight=0.20,
                is_cultural=False,
                is_festival_aligned=False,
                is_ethical=True,
                social_risk=0.09,
                sector="agriculture",
                region="North America"
            ),
            
            # High-risk speculative asset (should be flagged)
            Asset(
                id="asset-6",
                name="Speculative Derivatives",
                weight=0.15,
                is_cultural=False,
                is_festival_aligned=False,
                is_ethical=True,
                social_risk=0.25,  # High social risk
                sector="derivatives",
                region="Global"
            )
        ],
        total_value=100000.0
    )
    
    print(f"✅ Portfolio created:")
    print(f"   • Portfolio ID: {portfolio.id}")
    print(f"   • Total assets: {len(portfolio.assets)}")
    print(f"   • Total value: ${portfolio.total_value:,.2f}")
    
    # Show initial composition
    cultural_count = sum(1 for a in portfolio.assets if a.is_cultural)
    festival_count = sum(1 for a in portfolio.assets if a.is_festival_aligned)
    cultural_weight = sum(a.weight for a in portfolio.assets if a.is_cultural)
    
    print(f"   • Cultural assets: {cultural_count} ({cultural_weight:.1%} of portfolio)")
    print(f"   • Festival-aligned: {festival_count}")
    
    # 5. Check Compliance Before Enforcement
    print_section("5️⃣  Checking Compliance (Before Enforcement)")
    
    compliance_before = guardrails.check_compliance(portfolio)
    
    print(f"Compliance Status:")
    print(f"   • Ethical compliant: {'✅' if compliance_before['ethical_compliant'] else '❌'}")
    print(f"   • Social risk compliant: {'✅' if compliance_before['social_risk_compliant'] else '❌'}")
    print(f"   • Cultural weight compliant: {'✅' if compliance_before['cultural_weight_compliant'] else '❌'}")
    print(f"   • Overall compliant: {'✅' if compliance_before['overall_compliant'] else '❌'}")
    print(f"\nMetrics:")
    print(f"   • Cultural weight: {compliance_before['cultural_weight_ratio']:.1%}")
    print(f"   • Target: {compliance_before['cultural_weight_target']:.1%}")
    print(f"   • High-risk assets: {compliance_before['high_risk_asset_count']}")
    
    # 6. Apply Guardrails
    print_section("6️⃣  Applying Harper Henry Guardrails")
    
    # Get festival tilt factor
    festival_tilt = 1.0
    if calendar.is_festival_period():
        active = calendar.get_active_festivals()[0]
        festival_tilt = active.tilt_factor
        print(f"🎉 Festival period active! Applying {festival_tilt:.2f}x tilt")
    
    # Enforce guardrails
    portfolio_adjusted = guardrails.enforce(portfolio, festival_tilt_factor=festival_tilt)
    
    violations = guardrails.get_violations()
    if violations:
        print(f"\n⚠️  Guardrail violations detected and corrected:")
        for v in violations:
            print(f"   • {v.rule}: {v.message}")
            print(f"     Current: {v.current_value:.3f} | Required: {v.required_value:.3f}")
    else:
        print(f"✅ No guardrail violations detected")
    
    # Show adjusted weights
    print(f"\n📊 Portfolio adjustments:")
    cultural_weight_after = sum(a.weight for a in portfolio_adjusted.assets if a.is_cultural)
    print(f"   • Cultural weight: {cultural_weight:.1%} → {cultural_weight_after:.1%}")
    
    # 7. Calculate Metrics
    print_section("7️⃣  Calculating Enhanced Metrics")
    
    metrics_config = config.get_metrics_config()
    tracker = MetricsTracker(
        track_cultural_exposure=metrics_config.track_cultural_exposure,
        track_festival_impact=metrics_config.track_festival_impact,
        track_ethical_compliance=metrics_config.track_ethical_compliance,
        track_social_risk=metrics_config.track_social_risk
    )
    
    # Get festival context for metrics
    festival_context = calendar.get_festival_impact_report()
    
    # Calculate metrics with sample returns
    sample_returns = [0.02, -0.01, 0.03, 0.01, -0.02, 0.04, 0.02]
    metrics = tracker.calculate_metrics(
        portfolio_adjusted,
        returns=sample_returns,
        festival_context=festival_context
    )
    
    print(f"✅ Metrics calculated:")
    print(f"\n📈 Financial Metrics:")
    print(f"   • Total value: ${metrics.total_value:,.2f}")
    print(f"   • Total return: {metrics.total_return:.2%}")
    print(f"   • Sharpe ratio: {metrics.sharpe_ratio:.3f}")
    print(f"   • Volatility: {metrics.volatility:.2%}")
    print(f"   • VaR (95%): {metrics.var_95:.2%}")
    
    print(f"\n🎭 Cultural Metrics:")
    print(f"   • Cultural exposure: {metrics.cultural_exposure:.1%}")
    print(f"   • Cultural assets: {metrics.cultural_asset_count}")
    print(f"   • Cultural diversity: {metrics.cultural_diversity_score:.3f}")
    
    print(f"\n🎉 Festival Metrics:")
    print(f"   • Festival period active: {'Yes' if metrics.festival_period_active else 'No'}")
    print(f"   • Festival tilt impact: {metrics.festival_tilt_impact:.1%}")
    print(f"   • Festival-aligned assets: {metrics.festival_aligned_assets}")
    
    print(f"\n✅ Ethical Metrics:")
    print(f"   • Ethical compliance: {metrics.ethical_compliance:.1%}")
    print(f"   • Ethical assets: {metrics.ethical_asset_percentage:.1%}")
    print(f"   • Unethical assets: {metrics.unethical_asset_count}")
    
    print(f"\n⚖️  Social Impact Metrics:")
    print(f"   • Social risk: {metrics.social_risk:.3f}")
    print(f"   • High-risk assets: {metrics.high_social_risk_assets}")
    print(f"   • Social impact score: {metrics.social_impact_score:.3f}")
    
    print(f"\n📊 Portfolio Metrics:")
    print(f"   • Total assets: {metrics.asset_count}")
    print(f"   • Diversification: {metrics.diversification_score:.3f}")
    
    # 8. Export Metrics
    print_section("8️⃣  Exporting Metrics")
    
    export_settings = config.get_export_settings()
    exporter = MetricsExporter(
        output_directory=export_settings.output_directory,
        timestamp_format=export_settings.timestamp_format,
        compression=export_settings.compression,
        include_metadata=export_settings.include_metadata
    )
    
    # Export to multiple formats
    export_results = exporter.export_portfolio_metrics(
        metrics,
        formats=metrics_config.export_formats
    )
    
    print(f"✅ Metrics exported:")
    for format, path in export_results.items():
        if not path.startswith("ERROR"):
            print(f"   • {format.upper()}: {path}")
        else:
            print(f"   • {format.upper()}: {path}")
    
    # 9. Summary
    print_section("✨ Summary")
    
    print("ACTORS v2 successfully demonstrated:")
    print("  ✅ Configuration layer with YAML support")
    print("  ✅ Harper Henry behavioral guardrails")
    print("  ✅ Festival-aware portfolio tilt")
    print("  ✅ Enhanced cultural and ethical metrics")
    print("  ✅ Multi-format metric exports")
    print("  ✅ Minimum cultural weight enforcement")
    print("  ✅ Social risk monitoring")
    
    print(f"\n🎯 Final Portfolio Status:")
    compliance_after = guardrails.check_compliance(portfolio_adjusted)
    print(f"   • Overall Compliance: {'✅ PASSED' if compliance_after['overall_compliant'] else '❌ FAILED'}")
    print(f"   • Cultural Exposure: {metrics.cultural_exposure:.1%}")
    print(f"   • Ethical Compliance: {metrics.ethical_compliance:.1%}")
    print(f"   • Social Impact Score: {metrics.social_impact_score:.3f}")
    
    print(f"\n{'=' * 80}")
    print("🚀 ACTORS v2 Demo Complete!")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
