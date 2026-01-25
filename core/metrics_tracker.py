#!/usr/bin/env python3
"""
📊 METRICS TRACKER
Enhanced metrics tracking for cultural, ethical, and festival-aware performance

"Where every metric tells a story of financial and cultural harmony"
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PortfolioMetrics:
    """Comprehensive portfolio metrics"""
    timestamp: datetime
    
    # Traditional financial metrics
    total_value: float
    total_return: float
    sharpe_ratio: float
    volatility: float
    var_95: float
    max_drawdown: float
    
    # Cultural metrics
    cultural_exposure: float
    cultural_asset_count: int
    cultural_diversity_score: float
    
    # Festival metrics
    festival_tilt_impact: float
    festival_aligned_assets: int
    festival_period_active: bool
    
    # Ethical metrics
    ethical_compliance: float
    ethical_asset_percentage: float
    unethical_asset_count: int
    
    # Social risk metrics
    social_risk: float
    high_social_risk_assets: int
    social_impact_score: float
    
    # Portfolio composition
    asset_count: int
    diversification_score: float
    
    # Additional metadata
    region: str = ""
    active_festivals: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time"""
    timestamp: datetime
    metrics: Dict[str, float]
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsTracker:
    """
    Tracks and manages enhanced portfolio metrics
    
    Features:
    - Cultural exposure tracking
    - Festival tilt impact measurement
    - Ethical compliance monitoring
    - Social risk calculation
    - Traditional financial metrics
    - Historical metric storage
    """
    
    def __init__(
        self,
        track_cultural_exposure: bool = True,
        track_festival_impact: bool = True,
        track_ethical_compliance: bool = True,
        track_social_risk: bool = True
    ):
        """
        Initialize metrics tracker
        
        Args:
            track_cultural_exposure: Enable cultural exposure tracking
            track_festival_impact: Enable festival impact tracking
            track_ethical_compliance: Enable ethical compliance tracking
            track_social_risk: Enable social risk tracking
        """
        self.track_cultural_exposure = track_cultural_exposure
        self.track_festival_impact = track_festival_impact
        self.track_ethical_compliance = track_ethical_compliance
        self.track_social_risk = track_social_risk
        
        self.metrics_history: List[PortfolioMetrics] = []
        self.snapshots: List[MetricSnapshot] = []
        
        logger.info(
            f"Metrics Tracker initialized: "
            f"cultural={track_cultural_exposure}, "
            f"festival={track_festival_impact}, "
            f"ethical={track_ethical_compliance}, "
            f"social_risk={track_social_risk}"
        )
    
    def calculate_metrics(
        self,
        portfolio: Any,
        returns: Optional[List[float]] = None,
        festival_context: Optional[Dict[str, Any]] = None
    ) -> PortfolioMetrics:
        """
        Calculate comprehensive portfolio metrics
        
        Args:
            portfolio: Portfolio object to analyze
            returns: Historical returns for calculation
            festival_context: Festival calendar context
            
        Returns:
            PortfolioMetrics object
        """
        timestamp = datetime.now()
        
        # Calculate traditional financial metrics
        total_value = sum(asset.weight * portfolio.total_value for asset in portfolio.assets) if hasattr(portfolio, 'total_value') else sum(asset.weight for asset in portfolio.assets)
        
        total_return = 0.0
        sharpe_ratio = 0.0
        volatility = 0.0
        var_95 = 0.0
        max_drawdown = 0.0
        
        if returns and len(returns) > 0:
            import numpy as np
            
            total_return = sum(returns)
            returns_array = np.array(returns)
            
            if len(returns) > 1:
                volatility = float(np.std(returns_array))
                mean_return = float(np.mean(returns_array))
                
                if volatility > 0:
                    sharpe_ratio = mean_return / volatility
                
                # Calculate VaR (95% confidence)
                sorted_returns = np.sort(returns_array)
                var_index = int(0.05 * len(sorted_returns))
                if var_index < len(sorted_returns):
                    var_95 = -float(sorted_returns[var_index])
                
                # Calculate max drawdown
                cumulative = np.cumprod(1 + returns_array)
                running_max = np.maximum.accumulate(cumulative)
                drawdowns = (cumulative - running_max) / running_max
                max_drawdown = float(abs(np.min(drawdowns)))
        
        # Calculate cultural metrics
        cultural_exposure = 0.0
        cultural_asset_count = 0
        cultural_diversity_score = 0.0
        
        if self.track_cultural_exposure:
            cultural_assets = [a for a in portfolio.assets if getattr(a, 'is_cultural', False)]
            cultural_asset_count = len(cultural_assets)
            
            total_weight = sum(a.weight for a in portfolio.assets)
            if total_weight > 0:
                cultural_weight = sum(a.weight for a in cultural_assets)
                cultural_exposure = cultural_weight / total_weight
            
            # Calculate cultural diversity (entropy-based)
            if cultural_assets:
                import numpy as np
                weights = np.array([a.weight for a in cultural_assets])
                if weights.sum() > 0:
                    weights = weights / weights.sum()
                    cultural_diversity_score = -float(np.sum(weights * np.log(weights + 1e-10)))
        
        # Calculate festival metrics
        festival_tilt_impact = 0.0
        festival_aligned_assets = 0
        festival_period_active = False
        active_festivals = []
        
        if self.track_festival_impact and festival_context:
            festival_period_active = festival_context.get('total_active_festivals', 0) > 0
            active_festivals = [f['name'] for f in festival_context.get('active_festivals', [])]
            
            festival_assets = [a for a in portfolio.assets if getattr(a, 'is_festival_aligned', False)]
            festival_aligned_assets = len(festival_assets)
            
            if festival_assets:
                festival_weight = sum(a.weight for a in festival_assets)
                total_weight = sum(a.weight for a in portfolio.assets)
                if total_weight > 0:
                    festival_tilt_impact = festival_weight / total_weight
        
        # Calculate ethical metrics
        ethical_compliance = 1.0
        ethical_asset_percentage = 1.0
        unethical_asset_count = 0
        
        if self.track_ethical_compliance:
            ethical_assets = [a for a in portfolio.assets if getattr(a, 'is_ethical', True)]
            unethical_asset_count = len(portfolio.assets) - len(ethical_assets)
            
            if portfolio.assets:
                ethical_asset_percentage = len(ethical_assets) / len(portfolio.assets)
                ethical_compliance = ethical_asset_percentage
        
        # Calculate social risk metrics
        social_risk = 0.0
        high_social_risk_assets = 0
        social_impact_score = 0.0
        
        if self.track_social_risk:
            social_risks = [getattr(a, 'social_risk', 0.0) for a in portfolio.assets]
            
            if social_risks:
                import numpy as np
                
                # Weighted average social risk
                weights = [a.weight for a in portfolio.assets]
                total_weight = sum(weights)
                
                if total_weight > 0:
                    social_risk = sum(r * w for r, w in zip(social_risks, weights)) / total_weight
                
                # Count high-risk assets (>0.3)
                high_social_risk_assets = sum(1 for r in social_risks if r > 0.3)
                
                # Calculate social impact score (inverse of social risk)
                social_impact_score = max(0, 1.0 - social_risk)
        
        # Portfolio composition metrics
        asset_count = len(portfolio.assets)
        diversification_score = 0.0
        
        if asset_count > 1:
            import numpy as np
            weights = np.array([a.weight for a in portfolio.assets])
            if weights.sum() > 0:
                weights = weights / weights.sum()
                # Use Herfindahl index for diversification
                herfindahl = float(np.sum(weights ** 2))
                diversification_score = 1.0 - herfindahl
        
        metrics = PortfolioMetrics(
            timestamp=timestamp,
            total_value=total_value,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            volatility=volatility,
            var_95=var_95,
            max_drawdown=max_drawdown,
            cultural_exposure=cultural_exposure,
            cultural_asset_count=cultural_asset_count,
            cultural_diversity_score=cultural_diversity_score,
            festival_tilt_impact=festival_tilt_impact,
            festival_aligned_assets=festival_aligned_assets,
            festival_period_active=festival_period_active,
            ethical_compliance=ethical_compliance,
            ethical_asset_percentage=ethical_asset_percentage,
            unethical_asset_count=unethical_asset_count,
            social_risk=social_risk,
            high_social_risk_assets=high_social_risk_assets,
            social_impact_score=social_impact_score,
            asset_count=asset_count,
            diversification_score=diversification_score,
            region=festival_context.get('region', '') if festival_context else '',
            active_festivals=active_festivals
        )
        
        # Store in history
        self.metrics_history.append(metrics)
        
        logger.info(
            f"Metrics calculated: "
            f"cultural_exposure={cultural_exposure:.2%}, "
            f"ethical_compliance={ethical_compliance:.2%}, "
            f"social_risk={social_risk:.3f}"
        )
        
        return metrics
    
    def get_latest_metrics(self) -> Optional[PortfolioMetrics]:
        """Get most recent metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_history(
        self,
        limit: Optional[int] = None
    ) -> List[PortfolioMetrics]:
        """
        Get metrics history
        
        Args:
            limit: Maximum number of metrics to return (most recent)
            
        Returns:
            List of PortfolioMetrics
        """
        if limit:
            return self.metrics_history[-limit:]
        return self.metrics_history.copy()
    
    def get_metrics_as_dict(self, metrics: PortfolioMetrics) -> Dict[str, Any]:
        """Convert PortfolioMetrics to dictionary"""
        return asdict(metrics)
    
    def create_snapshot(self, metrics: Dict[str, float], tags: Optional[Dict[str, str]] = None) -> MetricSnapshot:
        """
        Create a metric snapshot
        
        Args:
            metrics: Dictionary of metric values
            tags: Optional tags for categorization
            
        Returns:
            MetricSnapshot object
        """
        snapshot = MetricSnapshot(
            timestamp=datetime.now(),
            metrics=metrics,
            tags=tags or {}
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def clear_history(self) -> None:
        """Clear metrics history"""
        self.metrics_history = []
        self.snapshots = []
        logger.info("Metrics history cleared")
