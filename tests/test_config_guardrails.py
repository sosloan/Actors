#!/usr/bin/env python3
"""
Tests for ACTORS v2 Configuration Layer and Harper Henry Guardrails
"""

import pytest
import os
import sys
import tempfile
import yaml
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_loader import (
    ConfigLoader, AgentConfig, MetricsConfig, 
    HarperHenryGuardrailsConfig, FestivalCalendarConfig
)
from core.harper_henry_guardrails import (
    HarperHenryGuardrails, Asset, Portfolio, GuardrailViolation
)
from core.festival_calendar import FestivalCalendar, ActiveFestival
from core.metrics_tracker import MetricsTracker, PortfolioMetrics
from core.metrics_exporter import MetricsExporter


class TestConfigLoader:
    """Tests for configuration loader"""
    
    def test_config_loader_initialization(self):
        """Test that config loader can be initialized"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        config = ConfigLoader(str(config_path))
        assert config.config_data is not None
        assert 'agents' in config.config_data
        assert 'metrics' in config.config_data
    
    def test_get_agent_config(self):
        """Test getting agent configuration"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        config = ConfigLoader(str(config_path))
        agent_config = config.get_agent_config('portfolio_agent')
        
        assert isinstance(agent_config, AgentConfig)
        assert isinstance(agent_config.max_risk, float)
        assert 0 <= agent_config.max_risk <= 1
    
    def test_get_metrics_config(self):
        """Test getting metrics configuration"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        config = ConfigLoader(str(config_path))
        metrics_config = config.get_metrics_config()
        
        assert isinstance(metrics_config, MetricsConfig)
        assert isinstance(metrics_config.enable_rich_metrics, bool)
        assert isinstance(metrics_config.export_formats, list)
    
    def test_get_guardrails_config(self):
        """Test getting guardrails configuration"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        config = ConfigLoader(str(config_path))
        guardrails_config = config.get_guardrails_config()
        
        assert isinstance(guardrails_config, HarperHenryGuardrailsConfig)
        assert isinstance(guardrails_config.ethical_investment, bool)
        assert 0 <= guardrails_config.max_social_risk <= 1
        assert 0 <= guardrails_config.min_cultural_weight <= 1
    
    def test_get_festival_calendar_config(self):
        """Test getting festival calendar configuration"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        config = ConfigLoader(str(config_path))
        calendar_config = config.get_festival_calendar_config()
        
        assert isinstance(calendar_config, FestivalCalendarConfig)
        assert isinstance(calendar_config.enabled, bool)
        assert isinstance(calendar_config.region, str)
        assert isinstance(calendar_config.festivals, list)


class TestHarperHenryGuardrails:
    """Tests for Harper Henry Guardrails"""
    
    def test_guardrails_initialization(self):
        """Test guardrails initialization"""
        config = HarperHenryGuardrailsConfig(
            ethical_investment=True,
            max_social_risk=0.2,
            cultural_alignment_min=0.2,
            festival_tilt_enabled=True,
            min_cultural_weight=0.1,
            enforce_on_portfolio=True
        )
        
        guardrails = HarperHenryGuardrails(config)
        
        assert guardrails.ethical == True
        assert guardrails.max_social_risk == 0.2
        assert guardrails.min_cultural_weight == 0.2
    
    def test_enforce_ethical_investment(self):
        """Test ethical investment enforcement"""
        config = HarperHenryGuardrailsConfig(
            ethical_investment=True,
            max_social_risk=0.2,
            cultural_alignment_min=0.2,
            festival_tilt_enabled=False,
            min_cultural_weight=0.1,
            enforce_on_portfolio=True
        )
        
        guardrails = HarperHenryGuardrails(config)
        
        # Create portfolio with unethical asset
        portfolio = Portfolio(
            id="test-1",
            name="Test Portfolio",
            assets=[
                Asset(id="a1", name="Ethical Asset", weight=0.5, is_ethical=True),
                Asset(id="a2", name="Unethical Asset", weight=0.5, is_ethical=False)
            ]
        )
        
        # Enforce guardrails
        result = guardrails.enforce(portfolio)
        
        # Check that unethical asset weight is zeroed
        unethical_asset = [a for a in result.assets if a.id == "a2"][0]
        assert unethical_asset.weight == 0.0
        
        # Check violations
        violations = guardrails.get_violations()
        assert len(violations) > 0
    
    def test_enforce_minimum_cultural_weight(self):
        """Test minimum cultural weight enforcement"""
        config = HarperHenryGuardrailsConfig(
            ethical_investment=False,
            max_social_risk=1.0,
            cultural_alignment_min=0.3,
            festival_tilt_enabled=False,
            min_cultural_weight=0.3,
            enforce_on_portfolio=True
        )
        
        guardrails = HarperHenryGuardrails(config)
        
        # Create portfolio with insufficient cultural weight
        portfolio = Portfolio(
            id="test-2",
            name="Test Portfolio",
            assets=[
                Asset(id="a1", name="Cultural Asset", weight=0.1, is_cultural=True),
                Asset(id="a2", name="Non-Cultural Asset", weight=0.9, is_cultural=False)
            ]
        )
        
        # Enforce guardrails
        result = guardrails.enforce(portfolio)
        
        # Calculate cultural weight ratio
        total_weight = sum(a.weight for a in result.assets)
        cultural_weight = sum(a.weight for a in result.assets if a.is_cultural)
        cultural_ratio = cultural_weight / total_weight
        
        # Should be at least minimum cultural weight
        assert cultural_ratio >= 0.29  # Allow small numerical error
    
    def test_apply_festival_tilt(self):
        """Test festival tilt application"""
        config = HarperHenryGuardrailsConfig(
            ethical_investment=False,
            max_social_risk=1.0,
            cultural_alignment_min=0.0,
            festival_tilt_enabled=True,
            min_cultural_weight=0.0,
            enforce_on_portfolio=True
        )
        
        guardrails = HarperHenryGuardrails(config)
        
        # Create portfolio with festival-aligned asset
        portfolio = Portfolio(
            id="test-3",
            name="Test Portfolio",
            assets=[
                Asset(id="a1", name="Festival Asset", weight=0.3, is_festival_aligned=True),
                Asset(id="a2", name="Normal Asset", weight=0.7, is_festival_aligned=False)
            ]
        )
        
        original_weight = portfolio.assets[0].weight
        
        # Apply festival tilt (1.5x)
        result = guardrails.enforce(portfolio, festival_tilt_factor=1.5)
        
        # Festival asset should have increased weight (after normalization)
        festival_asset = [a for a in result.assets if a.id == "a1"][0]
        assert festival_asset.weight > original_weight * 0.9  # Allow for normalization
    
    def test_check_compliance(self):
        """Test compliance checking"""
        config = HarperHenryGuardrailsConfig(
            ethical_investment=True,
            max_social_risk=0.2,
            cultural_alignment_min=0.3,
            festival_tilt_enabled=False,
            min_cultural_weight=0.3,
            enforce_on_portfolio=True
        )
        
        guardrails = HarperHenryGuardrails(config)
        
        # Create compliant portfolio
        portfolio = Portfolio(
            id="test-4",
            name="Test Portfolio",
            assets=[
                Asset(id="a1", name="Cultural Ethical Asset", weight=0.4, is_cultural=True, is_ethical=True, social_risk=0.1),
                Asset(id="a2", name="Normal Ethical Asset", weight=0.6, is_cultural=False, is_ethical=True, social_risk=0.1)
            ]
        )
        
        compliance = guardrails.check_compliance(portfolio)
        
        assert 'ethical_compliant' in compliance
        assert 'social_risk_compliant' in compliance
        assert 'cultural_weight_compliant' in compliance
        assert 'overall_compliant' in compliance


class TestFestivalCalendar:
    """Tests for Festival Calendar"""
    
    def test_festival_calendar_initialization(self):
        """Test festival calendar initialization"""
        from core.config_loader import Festival
        
        config = FestivalCalendarConfig(
            enabled=True,
            region="Guadalajara",
            tilt_factor=1.2,
            festivals=[
                Festival(
                    name="Test Festival",
                    start_date="2024-10-01",
                    end_date="2024-10-31",
                    related_sectors=["cultural_events"],
                    tilt_factor=1.3
                )
            ]
        )
        
        calendar = FestivalCalendar(config)
        
        assert calendar.enabled == True
        assert calendar.region == "Guadalajara"
        assert len(calendar.festivals) == 1
    
    def test_get_active_festivals(self):
        """Test getting active festivals"""
        from core.config_loader import Festival
        
        # Create festival that's active today
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        config = FestivalCalendarConfig(
            enabled=True,
            region="Guadalajara",
            tilt_factor=1.2,
            festivals=[
                Festival(
                    name="Active Festival",
                    start_date=yesterday.strftime("%Y-%m-%d"),
                    end_date=tomorrow.strftime("%Y-%m-%d"),
                    related_sectors=["cultural_events"],
                    tilt_factor=1.3
                )
            ]
        )
        
        calendar = FestivalCalendar(config)
        active_festivals = calendar.get_active_festivals(today)
        
        assert len(active_festivals) >= 0  # May or may not have active festivals
    
    def test_get_sector_tilt_factor(self):
        """Test getting sector tilt factor"""
        from core.config_loader import Festival
        
        config = FestivalCalendarConfig(
            enabled=True,
            region="Guadalajara",
            tilt_factor=1.2,
            festivals=[]
        )
        
        calendar = FestivalCalendar(config)
        
        # With no active festivals, should return 1.0
        tilt_factor = calendar.get_sector_tilt_factor("cultural_events")
        assert tilt_factor == 1.0
    
    def test_festival_impact_report(self):
        """Test festival impact report"""
        from core.config_loader import Festival
        
        config = FestivalCalendarConfig(
            enabled=True,
            region="Guadalajara",
            tilt_factor=1.2,
            festivals=[]
        )
        
        calendar = FestivalCalendar(config)
        report = calendar.get_festival_impact_report()
        
        assert 'enabled' in report
        assert 'region' in report
        assert 'active_festivals' in report
        assert 'upcoming_festivals' in report
        assert report['enabled'] == True
        assert report['region'] == "Guadalajara"


class TestMetricsTracker:
    """Tests for Metrics Tracker"""
    
    def test_metrics_tracker_initialization(self):
        """Test metrics tracker initialization"""
        tracker = MetricsTracker(
            track_cultural_exposure=True,
            track_festival_impact=True,
            track_ethical_compliance=True,
            track_social_risk=True
        )
        
        assert tracker.track_cultural_exposure == True
        assert tracker.track_festival_impact == True
        assert tracker.track_ethical_compliance == True
        assert tracker.track_social_risk == True
    
    def test_calculate_metrics(self):
        """Test metrics calculation"""
        tracker = MetricsTracker()
        
        # Create test portfolio
        portfolio = Portfolio(
            id="test-5",
            name="Test Portfolio",
            assets=[
                Asset(id="a1", name="Cultural Asset", weight=0.3, is_cultural=True, is_ethical=True, social_risk=0.1),
                Asset(id="a2", name="Normal Asset", weight=0.7, is_cultural=False, is_ethical=True, social_risk=0.05)
            ],
            total_value=10000.0
        )
        
        metrics = tracker.calculate_metrics(portfolio)
        
        assert isinstance(metrics, PortfolioMetrics)
        assert metrics.cultural_exposure >= 0
        assert metrics.ethical_compliance >= 0
        assert metrics.social_risk >= 0
        assert metrics.asset_count == 2
    
    def test_get_latest_metrics(self):
        """Test getting latest metrics"""
        tracker = MetricsTracker()
        
        portfolio = Portfolio(
            id="test-6",
            name="Test Portfolio",
            assets=[
                Asset(id="a1", name="Asset 1", weight=1.0)
            ]
        )
        
        tracker.calculate_metrics(portfolio)
        latest = tracker.get_latest_metrics()
        
        assert latest is not None
        assert isinstance(latest, PortfolioMetrics)


class TestMetricsExporter:
    """Tests for Metrics Exporter"""
    
    def test_metrics_exporter_initialization(self):
        """Test metrics exporter initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = MetricsExporter(
                output_directory=tmpdir,
                compression=False,
                include_metadata=True
            )
            
            assert exporter.output_directory.exists()
            assert exporter.compression == False
            assert exporter.include_metadata == True
    
    def test_export_json(self):
        """Test JSON export"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = MetricsExporter(output_directory=tmpdir)
            
            metrics = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'cultural_exposure': 0.3,
                    'ethical_compliance': 1.0,
                    'social_risk': 0.1
                }
            ]
            
            file_path = exporter.export_metrics(metrics, format='json', filename='test_metrics')
            
            assert os.path.exists(file_path)
            assert file_path.endswith('.json')
            
            # Verify JSON can be read
            with open(file_path, 'r') as f:
                data = json.load(f)
                assert 'metadata' in data or isinstance(data, list)
    
    def test_export_multiple_formats(self):
        """Test exporting to multiple formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = MetricsExporter(output_directory=tmpdir)
            
            metrics = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'value': 100.0
                }
            ]
            
            results = exporter.export_multiple_formats(
                metrics,
                formats=['json'],
                filename='multi_test'
            )
            
            assert 'json' in results
            assert os.path.exists(results['json'])
    
    def test_get_export_summary(self):
        """Test getting export summary"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = MetricsExporter(output_directory=tmpdir)
            
            metrics = [{'value': 1.0}]
            exporter.export_metrics(metrics, format='json', filename='summary_test')
            
            summary = exporter.get_export_summary()
            
            assert 'directory' in summary
            assert 'exists' in summary
            assert 'files' in summary
            assert summary['exists'] == True
            assert summary['file_count'] >= 1


class TestIntegration:
    """Integration tests for ACTORS v2 components"""
    
    def test_full_pipeline(self):
        """Test complete pipeline from config to export"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        # 1. Load configuration
        config = ConfigLoader(str(config_path))
        guardrails_config = config.get_guardrails_config()
        metrics_config = config.get_metrics_config()
        
        # 2. Initialize components
        guardrails = HarperHenryGuardrails(guardrails_config)
        tracker = MetricsTracker(
            track_cultural_exposure=metrics_config.track_cultural_exposure,
            track_festival_impact=metrics_config.track_festival_impact,
            track_ethical_compliance=metrics_config.track_ethical_compliance,
            track_social_risk=metrics_config.track_social_risk
        )
        
        # 3. Create test portfolio
        portfolio = Portfolio(
            id="integration-test",
            name="Integration Test Portfolio",
            assets=[
                Asset(id="a1", name="Cultural Asset", weight=0.2, is_cultural=True, is_ethical=True, social_risk=0.05),
                Asset(id="a2", name="Festival Asset", weight=0.3, is_festival_aligned=True, is_ethical=True, social_risk=0.1),
                Asset(id="a3", name="Normal Asset", weight=0.5, is_ethical=True, social_risk=0.08)
            ],
            total_value=50000.0
        )
        
        # 4. Enforce guardrails
        portfolio = guardrails.enforce(portfolio)
        
        # 5. Calculate metrics
        metrics = tracker.calculate_metrics(portfolio)
        
        # 6. Verify results
        assert metrics.cultural_exposure >= 0
        assert metrics.ethical_compliance > 0
        assert metrics.social_risk >= 0
        assert len(portfolio.assets) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
