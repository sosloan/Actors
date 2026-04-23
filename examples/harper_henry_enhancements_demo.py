#!/usr/bin/env python3
"""
🎭 Harper Henry Harmony Enhancements Demo
Showcasing new features:
- Config layer
- Behavioral guardrails
- Festival-aware tilt
- Cultural-weight constraint
- Export functionality
- Richer metrics
"""

import asyncio
import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.harper_henry_harmony import (
    HarmonyConfig,
    HarperHenryBehavioralGuardrails,
    HarperHenryHarmony
)

# Get temporary directory in a cross-platform way
EXPORT_DIR = Path(tempfile.gettempdir()) / "harper_henry_exports"


async def demo_basic_optimization():
    """Demo 1: Basic optimization with default config"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 1: Basic Optimization with Default Config")
    print("=" * 80)
    
    engine = HarperHenryHarmony()
    
    portfolio_data = {
        "destinations": ["Tokyo", "Kyoto", "Osaka"],
        "duration_days": 14,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.9,
            "cultural_immersion": 0.85,
            "traditional_practices": 0.8
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    print(f"\n📊 Optimization Results:")
    print(f"   • Total Value Created: {result.total_value_created:.2f}")
    print(f"   • Optimization Score: {result.optimization_score:.1%}")
    print(f"   • Harmony Achieved: {'✅ YES' if result.harmony_achieved else '❌ NO'}")
    print(f"   • Optimization Time: {result.optimization_time:.2f}s")
    
    print(f"\n🎨 Cultural Metrics:")
    print(f"   • Cultural Immersion: {result.cultural_immersion_score:.1%}")
    print(f"   • Language Learning: {result.language_learning_score:.1%}")
    print(f"   • Traditional Knowledge: {result.traditional_knowledge_score:.1%}")
    print(f"   • Artistic Expression: {result.artistic_expression_score:.1%}")


async def demo_custom_config():
    """Demo 2: Custom configuration with stricter thresholds"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 2: Custom Configuration with Stricter Thresholds")
    print("=" * 80)
    
    # Custom config with higher standards
    config = HarmonyConfig(
        min_cultural_weight=0.75,  # Higher than default 0.6
        min_harmony_score=0.95,     # Higher than default 0.9
        festival_boost_factor=0.3,  # Stronger festival boost
        min_artistic_expression=0.8
    )
    
    guardrails = HarperHenryBehavioralGuardrails(
        enforce_cultural_weight=True,
        enforce_harmony_minimums=True,
        enforce_artistic_balance=True
    )
    
    engine = HarperHenryHarmony(config=config, guardrails=guardrails)
    
    portfolio_data = {
        "destinations": ["New Delhi", "Jaipur", "Agra"],
        "duration_days": 10,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.95,
            "cultural_immersion": 0.9
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    print(f"\n📋 Config Settings:")
    print(f"   • Min Cultural Weight: {config.min_cultural_weight:.1%}")
    print(f"   • Min Harmony Score: {config.min_harmony_score:.1%}")
    print(f"   • Festival Boost Factor: {config.festival_boost_factor:.1%}")
    
    print(f"\n🛡️ Guardrails Status:")
    if result.guardrails_status:
        print(f"   • All Passed: {'✅ YES' if result.guardrails_status['all_guardrails_passed'] else '❌ NO'}")
        print(f"   • Checks Performed: {len(result.guardrails_status['checks_performed'])}")
        print(f"   • Violations: {len(result.guardrails_status.get('violations', []))}")
        print(f"   • Warnings: {len(result.guardrails_status.get('warnings', []))}")


async def demo_festival_detection():
    """Demo 3: Festival-aware tilt during cultural festivals"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 3: Festival-Aware Tilt - Cherry Blossom Season in Japan")
    print("=" * 80)
    
    engine = HarperHenryHarmony()
    
    # Portfolio during Cherry Blossom festival (April in Japan)
    portfolio_data = {
        "destinations": ["Tokyo, Japan", "Kyoto, Japan"],
        "start_date": "2024-04-01",  # Cherry Blossom season
        "duration_days": 14,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.9,
            "cultural_immersion": 0.9
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    print(f"\n🎊 Festival Detection:")
    if result.festival_metrics:
        print(f"   • Festival Detected: {'✅ YES' if result.festival_metrics['festivals_detected'] else '❌ NO'}")
        if result.festival_metrics.get('festivals'):
            for festival in result.festival_metrics['festivals']:
                print(f"   • Festival: {festival['name']} ({festival['type']})")
        print(f"   • Total Boost Applied: {result.festival_metrics.get('total_boost_applied', 0):.2f}")
        print(f"   • Average Cultural Weight: {result.festival_metrics.get('average_cultural_weight', 0):.1%}")
        print(f"   • Festival Cultural Weight: {result.festival_metrics.get('festival_cultural_weight', 0):.1%}")


async def demo_cultural_weight_validation():
    """Demo 4: Cultural-weight constraint validation"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 4: Cultural-Weight Constraint Validation")
    print("=" * 80)
    
    config = HarmonyConfig(
        min_cultural_weight=0.7  # Higher threshold
    )
    
    engine = HarperHenryHarmony(config=config)
    
    portfolio_data = {
        "destinations": ["Bali, Indonesia"],
        "duration_days": 7,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.9
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    print(f"\n⚖️ Cultural Weight Validation:")
    if result.cultural_weight_validation:
        cv = result.cultural_weight_validation
        print(f"   • Constraint Met: {'✅ YES' if cv['constraint_met'] else '❌ NO'}")
        print(f"   • Total Harmony Types: {cv['total_types']}")
        print(f"   • Passed: {cv['passed_count']}")
        print(f"   • Violations: {cv['violations_count']}")
        print(f"   • Average Cultural Weight: {cv['average_cultural_weight']:.1%}")
        print(f"   • Minimum Required: {config.min_cultural_weight:.1%}")


async def demo_export_functionality():
    """Demo 5: Export functionality (JSON and CSV)"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 5: Export Functionality")
    print("=" * 80)
    
    engine = HarperHenryHarmony()
    
    portfolio_data = {
        "destinations": ["Paris", "Lyon"],
        "duration_days": 10,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.88
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    # Create output directory
    EXPORT_DIR.mkdir(exist_ok=True)
    
    # Export to JSON
    json_file = EXPORT_DIR / f"harmony_result_{int(datetime.now().timestamp())}.json"
    result.export_to_file(json_file, format="json")
    print(f"\n📄 Exported to JSON: {json_file}")
    print(f"   • File size: {json_file.stat().st_size} bytes")
    
    # Export to CSV
    csv_file = EXPORT_DIR / f"harmony_summary_{int(datetime.now().timestamp())}.csv"
    result.export_to_file(csv_file, format="csv")
    print(f"\n📊 Exported to CSV: {csv_file}")
    print(f"   • File size: {csv_file.stat().st_size} bytes")
    
    # Show JSON preview (first 500 chars)
    json_str = result.to_json(pretty=True)
    print(f"\n📋 JSON Preview (first 500 chars):")
    print(json_str[:500] + "...")
    
    # Show export metadata
    if result.export_metadata:
        print(f"\n📦 Export Metadata:")
        print(f"   • Total Harmony Types: {result.export_metadata.get('total_harmony_types')}")
        print(f"   • Total Builders: {result.export_metadata.get('total_harmony_builders')}")
        print(f"   • Total BIG Builders: {result.export_metadata.get('total_big_builders')}")


async def demo_richer_metrics():
    """Demo 6: Richer metrics and optimization history"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 6: Richer Metrics and Optimization History")
    print("=" * 80)
    
    config = HarmonyConfig(
        enable_rich_metrics=True,
        track_optimization_history=True
    )
    
    engine = HarperHenryHarmony(config=config)
    
    portfolio_data = {
        "destinations": ["Bangkok, Thailand"],
        "start_date": "2024-04-13",  # Songkran festival
        "duration_days": 7,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.92,
            "cultural_immersion": 0.88
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    print(f"\n📈 Rich Metrics:")
    print(f"   • Cultural Immersion: {result.cultural_immersion_score:.1%}")
    print(f"   • Language Learning: {result.language_learning_score:.1%}")
    print(f"   • Community Building: {result.community_building_score:.1%}")
    print(f"   • Traditional Knowledge: {result.traditional_knowledge_score:.1%}")
    print(f"   • Homestay Value: {result.homestay_value_score:.1%}")
    print(f"   • FIRE Optimization: {result.fire_optimization_score:.1%}")
    
    print(f"\n🎨 Artistic Metrics:")
    print(f"   • Artistic Expression: {result.artistic_expression_score:.1%}")
    print(f"   • Creative Collaboration: {result.creative_collaboration_score:.1%}")
    print(f"   • Cultural Artistry: {result.cultural_artistry_score:.1%}")
    print(f"   • Traditional Crafts: {result.traditional_crafts_score:.1%}")
    print(f"   • Performance Arts: {result.performance_arts_score:.1%}")
    print(f"   • Visual Arts: {result.visual_arts_score:.1%}")
    print(f"   • Musical Harmony: {result.musical_harmony_score:.1%}")
    print(f"   • Literary Arts: {result.literary_arts_score:.1%}")
    
    print(f"\n📜 Optimization History:")
    if result.optimization_history:
        for i, entry in enumerate(result.optimization_history, 1):
            print(f"   {i}. Timestamp: {entry['timestamp']}")
            print(f"      - Score: {entry['optimization_score']:.1%}")
            print(f"      - Value: {entry['total_value_created']:.2f}")
            print(f"      - Harmony: {'✅' if entry['harmony_achieved'] else '❌'}")
            print(f"      - Guardrails: {'✅' if entry['guardrails_passed'] else '❌'}")


async def demo_all_features():
    """Demo 7: All features combined"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 7: All Features Combined - Diwali in India")
    print("=" * 80)
    
    # Custom config with all features enabled
    config = HarmonyConfig(
        min_cultural_weight=0.7,
        min_harmony_score=0.92,
        festival_boost_factor=0.25,
        festival_cultural_multiplier=1.3,
        enable_rich_metrics=True,
        track_optimization_history=True,
        export_format="json",
        export_pretty_print=True
    )
    
    guardrails = HarperHenryBehavioralGuardrails(
        enforce_cultural_weight=True,
        enforce_harmony_minimums=True,
        enforce_sustainability=True,
        enforce_artistic_balance=True,
        allow_festival_override=True
    )
    
    engine = HarperHenryHarmony(config=config, guardrails=guardrails)
    
    # Portfolio during Diwali
    portfolio_data = {
        "destinations": ["New Delhi, India", "Jaipur, India", "Varanasi, India"],
        "start_date": "2024-10-25",  # Diwali season
        "duration_days": 14,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.95,
            "cultural_immersion": 0.92,
            "traditional_practices": 0.9,
            "artistic_expression": 0.88
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    print(f"\n🎊 Festival & Cultural Features:")
    if result.festival_metrics and result.festival_metrics['festivals_detected']:
        print(f"   ✨ Festival Detected: {result.festival_metrics['festivals'][0]['name']}")
        print(f"   🎯 Festival Boost: {result.festival_metrics['total_boost_applied']:.2f}")
        print(f"   🌟 Festival Cultural Weight: {result.festival_metrics['festival_cultural_weight']:.1%}")
    
    print(f"\n🛡️ Guardrails & Validation:")
    if result.guardrails_status:
        print(f"   ✅ All Guardrails: {'PASSED' if result.guardrails_status['all_guardrails_passed'] else 'FAILED'}")
        print(f"   🔍 Checks: {', '.join(result.guardrails_status['checks_performed'])}")
    
    if result.cultural_weight_validation:
        print(f"   ⚖️ Cultural Weight: {'VALID' if result.cultural_weight_validation['constraint_met'] else 'INVALID'}")
        print(f"   📊 Average: {result.cultural_weight_validation['average_cultural_weight']:.1%}")
    
    print(f"\n📈 Performance Metrics:")
    print(f"   • Optimization Score: {result.optimization_score:.1%}")
    print(f"   • Total Value: {result.total_value_created:.2f}")
    print(f"   • Harmony Achieved: {'✅ YES' if result.harmony_achieved else '❌ NO'}")
    print(f"   • Processing Time: {result.optimization_time:.2f}s")
    
    print(f"\n🎨 Top 3 Cultural Scores:")
    scores = [
        ("Cultural Immersion", result.cultural_immersion_score),
        ("Traditional Knowledge", result.traditional_knowledge_score),
        ("Artistic Expression", result.artistic_expression_score),
        ("Traditional Crafts", result.traditional_crafts_score),
        ("Cultural Artistry", result.cultural_artistry_score)
    ]
    top_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:3]
    for i, (name, score) in enumerate(top_scores, 1):
        print(f"   {i}. {name}: {score:.1%}")
    
    # Export the result
    EXPORT_DIR.mkdir(exist_ok=True)
    result_file = EXPORT_DIR / "diwali_harmony_complete.json"
    result.export_to_file(result_file, format="json")
    print(f"\n💾 Exported complete results to: {result_file}")


async def main():
    """Run all demos"""
    print("\n" + "🎭" * 40)
    print("HARPER HENRY HARMONY - ENHANCEMENTS DEMO")
    print("🎭" * 40)
    
    await demo_basic_optimization()
    await demo_custom_config()
    await demo_festival_detection()
    await demo_cultural_weight_validation()
    await demo_export_functionality()
    await demo_richer_metrics()
    await demo_all_features()
    
    print("\n" + "=" * 80)
    print("✅ All demos completed successfully!")
    print("=" * 80)
    print(f"\n📁 Check {EXPORT_DIR} for exported files\n")


if __name__ == "__main__":
    asyncio.run(main())
