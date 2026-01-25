#!/usr/bin/env python3
"""
Tests for Harper Henry Harmony enhancements:
- Config layer
- Behavioral guardrails
- Festival-aware tilt
- Cultural-weight constraint
- Export functionality
- Richer metrics
"""

import pytest
import sys
import os
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.harper_henry_harmony import (
    HarmonyConfig,
    HarperHenryBehavioralGuardrails,
    HarperHenryHarmony,
    HarmonyEngine
)


def test_harmony_config_defaults():
    """Test HarmonyConfig default values"""
    config = HarmonyConfig()
    
    assert config.min_cultural_weight == 0.6
    assert config.min_harmony_score == 0.9
    assert config.festival_boost_factor == 0.2
    assert config.festival_cultural_multiplier == 1.25
    assert config.enable_rich_metrics == True
    assert config.export_format == "json"


def test_harmony_config_custom():
    """Test HarmonyConfig with custom values"""
    config = HarmonyConfig(
        min_cultural_weight=0.7,
        min_harmony_score=0.85,
        festival_boost_factor=0.3
    )
    
    assert config.min_cultural_weight == 0.7
    assert config.min_harmony_score == 0.85
    assert config.festival_boost_factor == 0.3


def test_behavioral_guardrails_defaults():
    """Test HarperHenryBehavioralGuardrails default values"""
    guardrails = HarperHenryBehavioralGuardrails()
    
    assert guardrails.enforce_cultural_weight == True
    assert guardrails.enforce_harmony_minimums == True
    assert guardrails.enforce_sustainability == True
    assert guardrails.enforce_artistic_balance == True
    assert guardrails.allow_festival_override == True
    assert guardrails.max_optimization_iterations == 100


def test_harper_henry_initialization():
    """Test HarperHenryHarmony initialization with config and guardrails"""
    config = HarmonyConfig(min_cultural_weight=0.65)
    guardrails = HarperHenryBehavioralGuardrails(enforce_cultural_weight=True)
    
    engine = HarperHenryHarmony(config=config, guardrails=guardrails)
    
    assert engine.config.min_cultural_weight == 0.65
    assert engine.guardrails.enforce_cultural_weight == True
    assert engine.optimization_history == []


def test_harper_henry_default_initialization():
    """Test HarperHenryHarmony initialization with defaults"""
    engine = HarperHenryHarmony()
    
    assert engine.config is not None
    assert engine.guardrails is not None
    assert engine.config.min_cultural_weight == 0.6
    assert engine.guardrails.enforce_cultural_weight == True


@pytest.mark.asyncio
async def test_festival_detection_no_festival():
    """Test festival detection when no festival is present"""
    engine = HarperHenryHarmony()
    
    # Portfolio without matching festival dates
    portfolio_data = {
        "start_date": "2024-06-15",
        "destinations": ["Paris", "London"]
    }
    
    festival_detected, festival_name = engine._detect_festival(portfolio_data)
    
    assert festival_detected == False
    assert festival_name is None


@pytest.mark.asyncio
async def test_festival_detection_diwali():
    """Test festival detection for Diwali"""
    engine = HarperHenryHarmony()
    
    # Portfolio with Diwali timing and Indian destination
    portfolio_data = {
        "start_date": "2024-10-15",
        "destinations": ["New Delhi, India", "Mumbai"]
    }
    
    festival_detected, festival_name = engine._detect_festival(portfolio_data)
    
    assert festival_detected == True
    assert festival_name == "Diwali"


@pytest.mark.asyncio
async def test_festival_detection_chinese_new_year():
    """Test festival detection for Chinese New Year"""
    engine = HarperHenryHarmony()
    
    # Portfolio with Chinese New Year timing and Chinese destination
    portfolio_data = {
        "start_date": "2024-02-10",
        "destinations": ["Beijing, China", "Shanghai"]
    }
    
    festival_detected, festival_name = engine._detect_festival(portfolio_data)
    
    assert festival_detected == True
    assert festival_name == "Chinese New Year"


@pytest.mark.asyncio
async def test_cultural_weight_validation_pass():
    """Test cultural weight validation when all types pass"""
    engine = HarperHenryHarmony()
    
    # Initialize harmony types with sufficient cultural weight
    portfolio_data = {
        "destinations": ["Tokyo", "Kyoto"],
        "duration_days": 14,
        "budget": 0,
        "preferences": {"harmony_seeking": 0.9}
    }
    
    harmony_types = await engine._initialize_harmony_types(portfolio_data)
    validation = engine._validate_cultural_weight_constraint(harmony_types)
    
    assert "constraint_met" in validation
    assert "violations" in validation
    assert "passed" in validation
    assert validation["total_types"] == len(harmony_types)


@pytest.mark.asyncio
async def test_cultural_weight_validation_with_config():
    """Test cultural weight validation with custom config"""
    config = HarmonyConfig(min_cultural_weight=0.5)  # Lower threshold
    engine = HarperHenryHarmony(config=config)
    
    portfolio_data = {
        "destinations": ["Paris"],
        "duration_days": 7,
        "budget": 0,
        "preferences": {"harmony_seeking": 0.8}
    }
    
    harmony_types = await engine._initialize_harmony_types(portfolio_data)
    validation = engine._validate_cultural_weight_constraint(harmony_types)
    
    # With lower threshold, more should pass
    assert validation["total_types"] > 0


@pytest.mark.asyncio
async def test_optimization_with_new_features():
    """Test full optimization with all new features"""
    config = HarmonyConfig(
        min_cultural_weight=0.6,
        enable_rich_metrics=True,
        track_optimization_history=True
    )
    guardrails = HarperHenryBehavioralGuardrails(
        enforce_cultural_weight=True,
        enforce_harmony_minimums=True
    )
    
    engine = HarperHenryHarmony(config=config, guardrails=guardrails)
    
    # Portfolio with festival timing
    portfolio_data = {
        "destinations": ["Tokyo, Japan", "Kyoto"],
        "start_date": "2024-04-01",  # Cherry Blossom season
        "duration_days": 14,
        "budget": 0,
        "preferences": {
            "harmony_seeking": 0.95,
            "cultural_immersion": 0.9,
            "traditional_practices": 0.85
        }
    }
    
    result = await engine.optimize_harmony_portfolio(portfolio_data)
    
    # Verify result has new fields
    assert result.festival_metrics is not None
    assert result.cultural_weight_validation is not None
    assert result.guardrails_status is not None
    assert result.optimization_history is not None
    assert result.export_metadata is not None
    
    # Verify festival detection worked
    assert "festivals_detected" in result.festival_metrics
    
    # Verify guardrails ran
    assert "all_guardrails_passed" in result.guardrails_status
    assert "checks_performed" in result.guardrails_status
    
    # Verify cultural weight validation
    assert "constraint_met" in result.cultural_weight_validation
    
    # Verify export metadata
    assert "config_used" in result.export_metadata
    assert "total_harmony_types" in result.export_metadata


def test_result_to_dict():
    """Test HarperHenryHarmonyResult.to_dict() method"""
    from core.harper_henry_harmony import HarperHenryHarmonyResult
    
    # Create a minimal result for testing
    result = HarperHenryHarmonyResult(
        id="test_123",
        engine_type=HarmonyEngine.HARPER_HENRY_HARMONY,
        total_value_created=10.5,
        optimization_score=0.95,
        harmony_types_used=[],
        harmony_builders=[],
        homestay_builders={},
        homestay_big_builders={},
        homestay_portfolio={},
        final_roi=1.5,
        optimization_time=2.3,
        harmony_achieved=True,
        cultural_immersion_score=0.9,
        language_learning_score=0.85,
        community_building_score=0.88,
        traditional_knowledge_score=0.82,
        homestay_value_score=0.91,
        fire_optimization_score=0.87,
        artistic_expression_score=0.84,
        creative_collaboration_score=0.86,
        cultural_artistry_score=0.89,
        traditional_crafts_score=0.83,
        traditional_crafts_analysis={},
        performance_arts_score=0.81,
        visual_arts_score=0.85,
        musical_harmony_score=0.88,
        literary_arts_score=0.80,
        elite_calculations_analysis={},
        big_builder_power_analysis={},
        created_at=datetime.now(),
        festival_metrics={"festivals_detected": False},
        cultural_weight_validation={"constraint_met": True},
        guardrails_status={"all_guardrails_passed": True},
        optimization_history=[],
        export_metadata={}
    )
    
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert result_dict["id"] == "test_123"
    assert result_dict["optimization_score"] == 0.95
    assert "created_at" in result_dict
    assert isinstance(result_dict["created_at"], str)  # Should be ISO format


def test_result_to_json():
    """Test HarperHenryHarmonyResult.to_json() method"""
    from core.harper_henry_harmony import HarperHenryHarmonyResult
    
    result = HarperHenryHarmonyResult(
        id="test_json",
        engine_type=HarmonyEngine.HARPER_HENRY_HARMONY,
        total_value_created=8.5,
        optimization_score=0.92,
        harmony_types_used=[],
        harmony_builders=[],
        homestay_builders={},
        homestay_big_builders={},
        homestay_portfolio={},
        final_roi=1.3,
        optimization_time=1.8,
        harmony_achieved=True,
        cultural_immersion_score=0.88,
        language_learning_score=0.83,
        community_building_score=0.86,
        traditional_knowledge_score=0.81,
        homestay_value_score=0.89,
        fire_optimization_score=0.85,
        artistic_expression_score=0.82,
        creative_collaboration_score=0.84,
        cultural_artistry_score=0.87,
        traditional_crafts_score=0.81,
        traditional_crafts_analysis={},
        performance_arts_score=0.79,
        visual_arts_score=0.83,
        musical_harmony_score=0.86,
        literary_arts_score=0.78,
        elite_calculations_analysis={},
        big_builder_power_analysis={},
        created_at=datetime.now(),
        festival_metrics={},
        cultural_weight_validation={},
        guardrails_status={},
        optimization_history=[],
        export_metadata={}
    )
    
    json_str = result.to_json(pretty=True)
    
    assert isinstance(json_str, str)
    # Verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["id"] == "test_json"
    assert parsed["optimization_score"] == 0.92


def test_result_export_to_file_json(tmp_path):
    """Test exporting result to JSON file"""
    from core.harper_henry_harmony import HarperHenryHarmonyResult
    
    result = HarperHenryHarmonyResult(
        id="test_export",
        engine_type=HarmonyEngine.HARPER_HENRY_HARMONY,
        total_value_created=9.0,
        optimization_score=0.93,
        harmony_types_used=[],
        harmony_builders=[],
        homestay_builders={},
        homestay_big_builders={},
        homestay_portfolio={},
        final_roi=1.4,
        optimization_time=2.0,
        harmony_achieved=True,
        cultural_immersion_score=0.87,
        language_learning_score=0.84,
        community_building_score=0.85,
        traditional_knowledge_score=0.80,
        homestay_value_score=0.88,
        fire_optimization_score=0.86,
        artistic_expression_score=0.83,
        creative_collaboration_score=0.85,
        cultural_artistry_score=0.88,
        traditional_crafts_score=0.82,
        traditional_crafts_analysis={},
        performance_arts_score=0.80,
        visual_arts_score=0.84,
        musical_harmony_score=0.87,
        literary_arts_score=0.79,
        elite_calculations_analysis={},
        big_builder_power_analysis={},
        created_at=datetime.now(),
        festival_metrics={},
        cultural_weight_validation={},
        guardrails_status={},
        optimization_history=[],
        export_metadata={}
    )
    
    # Export to JSON file
    json_file = tmp_path / "result.json"
    result.export_to_file(json_file, format="json")
    
    # Verify file exists and is valid JSON
    assert json_file.exists()
    with open(json_file) as f:
        data = json.load(f)
        assert data["id"] == "test_export"


def test_result_export_to_file_csv(tmp_path):
    """Test exporting result to CSV file"""
    from core.harper_henry_harmony import HarperHenryHarmonyResult
    
    result = HarperHenryHarmonyResult(
        id="test_csv_export",
        engine_type=HarmonyEngine.HARPER_HENRY_HARMONY,
        total_value_created=9.5,
        optimization_score=0.94,
        harmony_types_used=[],
        harmony_builders=[],
        homestay_builders={},
        homestay_big_builders={},
        homestay_portfolio={},
        final_roi=1.5,
        optimization_time=2.1,
        harmony_achieved=True,
        cultural_immersion_score=0.89,
        language_learning_score=0.85,
        community_building_score=0.87,
        traditional_knowledge_score=0.82,
        homestay_value_score=0.90,
        fire_optimization_score=0.88,
        artistic_expression_score=0.84,
        creative_collaboration_score=0.86,
        cultural_artistry_score=0.89,
        traditional_crafts_score=0.83,
        traditional_crafts_analysis={},
        performance_arts_score=0.81,
        visual_arts_score=0.85,
        musical_harmony_score=0.88,
        literary_arts_score=0.80,
        elite_calculations_analysis={},
        big_builder_power_analysis={},
        created_at=datetime.now(),
        festival_metrics={},
        cultural_weight_validation={},
        guardrails_status={},
        optimization_history=[],
        export_metadata={}
    )
    
    # Export to CSV file
    csv_file = tmp_path / "result.csv"
    result.export_to_file(csv_file, format="csv")
    
    # Verify file exists
    assert csv_file.exists()
    
    # Verify CSV content
    import csv
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) > 0
        assert rows[0] == ['Metric', 'Value']
        assert rows[1][0] == 'ID'
        assert rows[1][1] == 'test_csv_export'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
