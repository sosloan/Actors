#!/usr/bin/env python3
"""
🛡️ HARPER HENRY GUARDRAILS
Behavioral guardrails for ethical, cultural, and festival-aware portfolio management

"Where financial optimization meets cultural and ethical responsibility"
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from core.config_loader import HarperHenryGuardrailsConfig

logger = logging.getLogger(__name__)


@dataclass
class Asset:
    """Represents an asset in the portfolio"""
    id: str
    name: str
    weight: float
    is_cultural: bool = False
    is_festival_aligned: bool = False
    is_ethical: bool = True
    social_risk: float = 0.0
    sector: Optional[str] = None
    region: Optional[str] = None


@dataclass
class Portfolio:
    """Represents a portfolio of assets"""
    id: str
    name: str
    assets: List[Asset] = field(default_factory=list)
    total_value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailViolation:
    """Represents a guardrail violation"""
    rule: str
    severity: str  # 'warning' or 'error'
    message: str
    current_value: float
    required_value: float
    timestamp: datetime = field(default_factory=datetime.now)


class HarperHenryGuardrails:
    """
    Enforces ethical, cultural, and behavioral limits in portfolio management
    
    Features:
    - Ethical Investment: Avoids high-risk, socially harmful investments
    - Cultural Alignment: Ensures minimum exposure to local/regional cultural assets
    - Max Social Risk: Limits speculative trades impacting communities
    - Festival Tilt: Dynamically favors sectors linked to local festivals/events
    - Min Cultural Weight: Guarantees baseline investment in culturally aligned assets
    """
    
    def __init__(self, config: HarperHenryGuardrailsConfig):
        """
        Initialize Harper Henry Guardrails
        
        Args:
            config: Guardrails configuration
        """
        self.ethical = config.ethical_investment
        self.max_social_risk = config.max_social_risk
        self.min_cultural_weight = config.cultural_alignment_min
        self.festival_tilt_enabled = config.festival_tilt_enabled
        self.min_cultural_weight_threshold = config.min_cultural_weight
        self.enforce_on_portfolio = config.enforce_on_portfolio
        
        self.violations: List[GuardrailViolation] = []
        
        logger.info(
            f"Harper Henry Guardrails initialized: "
            f"ethical={self.ethical}, "
            f"max_social_risk={self.max_social_risk}, "
            f"min_cultural_weight={self.min_cultural_weight}"
        )
    
    def enforce(self, portfolio: Portfolio, festival_tilt_factor: float = 1.0) -> Portfolio:
        """
        Enforce guardrails on portfolio
        
        Args:
            portfolio: Portfolio to enforce guardrails on
            festival_tilt_factor: Tilt factor for festival-aligned assets
            
        Returns:
            Modified portfolio with guardrails enforced
        """
        self.violations = []
        
        if not self.enforce_on_portfolio:
            logger.info("Guardrail enforcement disabled")
            return portfolio
        
        # 1. Check and enforce ethical investment constraints
        if self.ethical:
            portfolio = self._enforce_ethical_investment(portfolio)
        
        # 2. Check and enforce social risk limits
        portfolio = self._enforce_social_risk_limits(portfolio)
        
        # 3. Enforce minimum cultural weight
        portfolio = self._enforce_minimum_cultural_weight(portfolio)
        
        # 4. Apply festival tilt if enabled
        if self.festival_tilt_enabled and festival_tilt_factor > 1.0:
            portfolio = self._apply_festival_tilt(portfolio, festival_tilt_factor)
        
        # 5. Normalize weights to ensure they sum to 1.0
        portfolio = self._normalize_portfolio_weights(portfolio)
        
        # Log violations
        if self.violations:
            logger.warning(f"Guardrails found {len(self.violations)} violations")
            for violation in self.violations:
                logger.warning(f"  {violation.rule}: {violation.message}")
        
        return portfolio
    
    def _enforce_ethical_investment(self, portfolio: Portfolio) -> Portfolio:
        """Enforce ethical investment constraints"""
        unethical_assets = [asset for asset in portfolio.assets if not asset.is_ethical]
        
        if unethical_assets:
            logger.warning(f"Found {len(unethical_assets)} unethical assets")
            
            for asset in unethical_assets:
                self.violations.append(GuardrailViolation(
                    rule="ethical_investment",
                    severity="error",
                    message=f"Asset {asset.name} violates ethical investment constraints",
                    current_value=0.0,
                    required_value=1.0
                ))
                
                # Remove weight from unethical assets
                asset.weight = 0.0
        
        return portfolio
    
    def _enforce_social_risk_limits(self, portfolio: Portfolio) -> Portfolio:
        """Enforce maximum social risk limits"""
        for asset in portfolio.assets:
            if asset.social_risk > self.max_social_risk:
                logger.warning(
                    f"Asset {asset.name} exceeds max social risk: "
                    f"{asset.social_risk:.3f} > {self.max_social_risk:.3f}"
                )
                
                self.violations.append(GuardrailViolation(
                    rule="max_social_risk",
                    severity="warning",
                    message=f"Asset {asset.name} exceeds max social risk",
                    current_value=asset.social_risk,
                    required_value=self.max_social_risk
                ))
                
                # Reduce weight proportionally to risk excess
                risk_excess = (asset.social_risk - self.max_social_risk) / asset.social_risk
                reduction_factor = 1.0 - min(risk_excess, 0.5)  # Max 50% reduction
                asset.weight *= reduction_factor
        
        return portfolio
    
    def _enforce_minimum_cultural_weight(self, portfolio: Portfolio) -> Portfolio:
        """Enforce minimum cultural weight constraint"""
        total_weight = sum(asset.weight for asset in portfolio.assets)
        
        if total_weight < 1e-6:
            logger.warning("Portfolio has zero total weight")
            return portfolio
        
        cultural_weight = sum(asset.weight for asset in portfolio.assets if asset.is_cultural)
        cultural_weight_ratio = cultural_weight / total_weight
        
        if cultural_weight_ratio < self.min_cultural_weight:
            logger.info(
                f"Enforcing minimum cultural weight: "
                f"{cultural_weight_ratio:.3f} < {self.min_cultural_weight:.3f}"
            )
            
            self.violations.append(GuardrailViolation(
                rule="min_cultural_weight",
                severity="warning",
                message="Portfolio below minimum cultural weight",
                current_value=cultural_weight_ratio,
                required_value=self.min_cultural_weight
            ))
            
            # Calculate adjustment needed
            adjustment = self.min_cultural_weight * total_weight - cultural_weight
            
            # Get cultural assets
            cultural_assets = [a for a in portfolio.assets if a.is_cultural]
            
            if cultural_assets:
                # Increase cultural allocation proportionally
                adjustment_per_asset = adjustment / len(cultural_assets)
                
                for asset in cultural_assets:
                    asset.weight += adjustment_per_asset
                
                # Reduce non-cultural assets proportionally
                non_cultural_assets = [a for a in portfolio.assets if not a.is_cultural]
                if non_cultural_assets:
                    total_non_cultural = sum(a.weight for a in non_cultural_assets)
                    if total_non_cultural > adjustment:
                        for asset in non_cultural_assets:
                            reduction_ratio = adjustment / total_non_cultural
                            asset.weight *= (1.0 - reduction_ratio)
            else:
                logger.warning("No cultural assets available to enforce minimum weight")
        
        return portfolio
    
    def _apply_festival_tilt(self, portfolio: Portfolio, tilt_factor: float) -> Portfolio:
        """Apply festival tilt to festival-aligned assets"""
        logger.info(f"Applying festival tilt factor: {tilt_factor:.2f}")
        
        for asset in portfolio.assets:
            if asset.is_festival_aligned:
                original_weight = asset.weight
                asset.weight *= tilt_factor
                logger.debug(
                    f"Festival tilt applied to {asset.name}: "
                    f"{original_weight:.4f} -> {asset.weight:.4f}"
                )
        
        return portfolio
    
    def _normalize_portfolio_weights(self, portfolio: Portfolio) -> Portfolio:
        """Normalize portfolio weights to sum to 1.0"""
        total_weight = sum(asset.weight for asset in portfolio.assets)
        
        if total_weight < 1e-6:
            logger.warning("Portfolio has zero total weight, cannot normalize")
            return portfolio
        
        if abs(total_weight - 1.0) > 1e-3:
            logger.debug(f"Normalizing portfolio weights: total={total_weight:.4f}")
            
            for asset in portfolio.assets:
                asset.weight /= total_weight
        
        return portfolio
    
    def get_violations(self) -> List[GuardrailViolation]:
        """Get list of guardrail violations"""
        return self.violations.copy()
    
    def check_compliance(self, portfolio: Portfolio) -> Dict[str, Any]:
        """
        Check portfolio compliance without enforcing changes
        
        Args:
            portfolio: Portfolio to check
            
        Returns:
            Compliance report dictionary
        """
        total_weight = sum(asset.weight for asset in portfolio.assets)
        cultural_weight = sum(asset.weight for asset in portfolio.assets if asset.is_cultural)
        
        cultural_ratio = cultural_weight / max(total_weight, 1e-6)
        
        # Check ethical compliance
        unethical_count = sum(1 for a in portfolio.assets if not a.is_ethical)
        ethical_compliant = unethical_count == 0
        
        # Check social risk
        high_risk_assets = [a for a in portfolio.assets if a.social_risk > self.max_social_risk]
        social_risk_compliant = len(high_risk_assets) == 0
        
        # Check cultural weight
        cultural_weight_compliant = cultural_ratio >= self.min_cultural_weight
        
        return {
            'ethical_compliant': ethical_compliant,
            'social_risk_compliant': social_risk_compliant,
            'cultural_weight_compliant': cultural_weight_compliant,
            'overall_compliant': all([
                ethical_compliant,
                social_risk_compliant,
                cultural_weight_compliant
            ]),
            'cultural_weight_ratio': cultural_ratio,
            'cultural_weight_target': self.min_cultural_weight,
            'unethical_asset_count': unethical_count,
            'high_risk_asset_count': len(high_risk_assets),
            'timestamp': datetime.now().isoformat()
        }
