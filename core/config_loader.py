#!/usr/bin/env python3
"""
🔧 ACTORS Configuration Loader
Loads and validates YAML configuration for ACTORS v2

"Where configuration meets intelligent behavior"
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    enabled: bool = True
    max_risk: float = 0.15
    min_cultural_weight: float = 0.1
    festival_tilt: bool = True
    slippage_limit: float = 0.01
    hedge_enabled: bool = True
    max_protocol_risk: float = 0.2
    gas_optimization: bool = True
    var_confidence: float = 0.95
    stress_testing: bool = True


@dataclass
class MetricsConfig:
    """Configuration for metrics tracking"""
    enable_rich_metrics: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json"])
    export_frequency: str = "daily"
    track_cultural_exposure: bool = True
    track_festival_impact: bool = True
    track_ethical_compliance: bool = True
    track_social_risk: bool = True


@dataclass
class Festival:
    """Festival definition"""
    name: str
    start_date: str
    end_date: str
    related_sectors: List[str]
    tilt_factor: float = 1.2


@dataclass
class FestivalCalendarConfig:
    """Configuration for festival calendar"""
    enabled: bool = True
    region: str = "Guadalajara"
    tilt_factor: float = 1.2
    festivals: List[Festival] = field(default_factory=list)


@dataclass
class HarperHenryGuardrailsConfig:
    """Configuration for Harper Henry guardrails"""
    ethical_investment: bool = True
    max_social_risk: float = 0.2
    cultural_alignment_min: float = 0.2
    festival_tilt_enabled: bool = True
    min_cultural_weight: float = 0.1
    enforce_on_portfolio: bool = True


@dataclass
class PortfolioConfig:
    """Configuration for portfolio management"""
    rebalance_frequency: str = "weekly"
    max_position_size: float = 0.2
    min_position_size: float = 0.01
    diversification_target: int = 10
    cultural_asset_min: float = 0.1
    festival_asset_min: float = 0.05


@dataclass
class ExportSettings:
    """Configuration for export settings"""
    output_directory: str = "exports"
    timestamp_format: str = "%Y%m%d_%H%M%S"
    compression: bool = False
    include_metadata: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging"""
    level: str = "INFO"
    export_logs: bool = True
    log_file: str = "logs/actors.log"
    enable_metrics_logging: bool = True


class ConfigLoader:
    """Loads and manages ACTORS configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to configuration file. If None, uses default config.yaml
        """
        if config_path is None:
            # Default to config.yaml in project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config_data = yaml.safe_load(f)
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration data"""
        required_sections = [
            'agents',
            'metrics',
            'harper_henry_guardrails',
            'festival_calendar',
            'logging'
        ]
        
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"Missing required configuration section: {section}")
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """
        Get configuration for a specific agent
        
        Args:
            agent_name: Name of the agent (e.g., 'portfolio_agent')
            
        Returns:
            AgentConfig object with agent settings
        """
        agents = self.config_data.get('agents', {})
        agent_data = agents.get(agent_name, {})
        
        return AgentConfig(
            enabled=agent_data.get('enabled', True),
            max_risk=agent_data.get('max_risk', 0.15),
            min_cultural_weight=agent_data.get('min_cultural_weight', 0.1),
            festival_tilt=agent_data.get('festival_tilt', True),
            slippage_limit=agent_data.get('slippage_limit', 0.01),
            hedge_enabled=agent_data.get('hedge_enabled', True),
            max_protocol_risk=agent_data.get('max_protocol_risk', 0.2),
            gas_optimization=agent_data.get('gas_optimization', True),
            var_confidence=agent_data.get('var_confidence', 0.95),
            stress_testing=agent_data.get('stress_testing', True)
        )
    
    def get_metrics_config(self) -> MetricsConfig:
        """Get metrics configuration"""
        metrics = self.config_data.get('metrics', {})
        
        return MetricsConfig(
            enable_rich_metrics=metrics.get('enable_rich_metrics', True),
            export_formats=metrics.get('export_formats', ['csv', 'json']),
            export_frequency=metrics.get('export_frequency', 'daily'),
            track_cultural_exposure=metrics.get('track_cultural_exposure', True),
            track_festival_impact=metrics.get('track_festival_impact', True),
            track_ethical_compliance=metrics.get('track_ethical_compliance', True),
            track_social_risk=metrics.get('track_social_risk', True)
        )
    
    def get_guardrails_config(self) -> HarperHenryGuardrailsConfig:
        """Get Harper Henry guardrails configuration"""
        guardrails = self.config_data.get('harper_henry_guardrails', {})
        
        return HarperHenryGuardrailsConfig(
            ethical_investment=guardrails.get('ethical_investment', True),
            max_social_risk=guardrails.get('max_social_risk', 0.2),
            cultural_alignment_min=guardrails.get('cultural_alignment_min', 0.2),
            festival_tilt_enabled=guardrails.get('festival_tilt_enabled', True),
            min_cultural_weight=guardrails.get('min_cultural_weight', 0.1),
            enforce_on_portfolio=guardrails.get('enforce_on_portfolio', True)
        )
    
    def get_festival_calendar_config(self) -> FestivalCalendarConfig:
        """Get festival calendar configuration"""
        calendar = self.config_data.get('festival_calendar', {})
        
        # Parse festivals
        festivals = []
        for fest_data in calendar.get('festivals', []):
            festival = Festival(
                name=fest_data['name'],
                start_date=fest_data['start_date'],
                end_date=fest_data['end_date'],
                related_sectors=fest_data.get('related_sectors', []),
                tilt_factor=fest_data.get('tilt_factor', 1.2)
            )
            festivals.append(festival)
        
        return FestivalCalendarConfig(
            enabled=calendar.get('enabled', True),
            region=calendar.get('region', 'Guadalajara'),
            tilt_factor=calendar.get('tilt_factor', 1.2),
            festivals=festivals
        )
    
    def get_portfolio_config(self) -> PortfolioConfig:
        """Get portfolio configuration"""
        portfolio = self.config_data.get('portfolio', {})
        
        return PortfolioConfig(
            rebalance_frequency=portfolio.get('rebalance_frequency', 'weekly'),
            max_position_size=portfolio.get('max_position_size', 0.2),
            min_position_size=portfolio.get('min_position_size', 0.01),
            diversification_target=portfolio.get('diversification_target', 10),
            cultural_asset_min=portfolio.get('cultural_asset_min', 0.1),
            festival_asset_min=portfolio.get('festival_asset_min', 0.05)
        )
    
    def get_export_settings(self) -> ExportSettings:
        """Get export settings"""
        export = self.config_data.get('export_settings', {})
        
        return ExportSettings(
            output_directory=export.get('output_directory', 'exports'),
            timestamp_format=export.get('timestamp_format', '%Y%m%d_%H%M%S'),
            compression=export.get('compression', False),
            include_metadata=export.get('include_metadata', True)
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        logging = self.config_data.get('logging', {})
        
        return LoggingConfig(
            level=logging.get('level', 'INFO'),
            export_logs=logging.get('export_logs', True),
            log_file=logging.get('log_file', 'logs/actors.log'),
            enable_metrics_logging=logging.get('enable_metrics_logging', True)
        )
    
    def get_raw_config(self) -> Dict[str, Any]:
        """Get raw configuration dictionary"""
        return self.config_data.copy()
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()


# Global configuration instance
_config_instance: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get global configuration instance
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ConfigLoader instance
    """
    global _config_instance
    
    if _config_instance is None or config_path is not None:
        _config_instance = ConfigLoader(config_path)
    
    return _config_instance


def reload_config() -> None:
    """Reload global configuration"""
    global _config_instance
    
    if _config_instance is not None:
        _config_instance.reload()
