#!/usr/bin/env python3
"""
🎉 FESTIVAL CALENDAR
Regional festival tracking and portfolio tilt management

"Where cultural celebrations meet strategic portfolio allocation"
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, date
import logging

from core.config_loader import FestivalCalendarConfig, Festival

logger = logging.getLogger(__name__)


@dataclass
class ActiveFestival:
    """Represents an active festival with calculated properties"""
    festival: Festival
    days_remaining: int
    is_active: bool
    sectors_to_tilt: List[str]
    tilt_factor: float


class FestivalCalendar:
    """
    Manages regional festival calendar and provides portfolio tilt guidance
    
    Features:
    - Track regional festivals and cultural events
    - Determine active festivals based on current date
    - Provide sector-specific tilt factors during festivals
    - Support multiple regions and custom festival definitions
    """
    
    def __init__(self, config: FestivalCalendarConfig):
        """
        Initialize festival calendar
        
        Args:
            config: Festival calendar configuration
        """
        self.enabled = config.enabled
        self.region = config.region
        self.default_tilt_factor = config.tilt_factor
        self.festivals = config.festivals
        
        logger.info(
            f"Festival Calendar initialized: "
            f"region={self.region}, "
            f"enabled={self.enabled}, "
            f"festivals={len(self.festivals)}"
        )
    
    def get_active_festivals(self, reference_date: Optional[date] = None) -> List[ActiveFestival]:
        """
        Get list of currently active festivals
        
        Args:
            reference_date: Date to check against (defaults to today)
            
        Returns:
            List of active festivals
        """
        if not self.enabled:
            return []
        
        if reference_date is None:
            reference_date = date.today()
        
        active_festivals = []
        
        for festival in self.festivals:
            # Parse festival dates
            start_date = datetime.strptime(festival.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(festival.end_date, "%Y-%m-%d").date()
            
            # Check if festival is active
            is_active = start_date <= reference_date <= end_date
            
            if is_active:
                days_remaining = (end_date - reference_date).days
                
                active_festival = ActiveFestival(
                    festival=festival,
                    days_remaining=days_remaining,
                    is_active=True,
                    sectors_to_tilt=festival.related_sectors,
                    tilt_factor=festival.tilt_factor
                )
                
                active_festivals.append(active_festival)
                
                logger.info(
                    f"Active festival: {festival.name} "
                    f"(ends in {days_remaining} days, tilt={festival.tilt_factor:.2f})"
                )
        
        return active_festivals
    
    def get_sector_tilt_factor(
        self,
        sector: str,
        reference_date: Optional[date] = None
    ) -> float:
        """
        Get tilt factor for a specific sector based on active festivals
        
        Args:
            sector: Sector to check
            reference_date: Date to check against (defaults to today)
            
        Returns:
            Tilt factor (1.0 if no festival affecting this sector)
        """
        if not self.enabled:
            return 1.0
        
        active_festivals = self.get_active_festivals(reference_date)
        
        # Find maximum tilt factor for this sector
        max_tilt = 1.0
        
        for active_festival in active_festivals:
            if sector in active_festival.sectors_to_tilt:
                max_tilt = max(max_tilt, active_festival.tilt_factor)
        
        return max_tilt
    
    def apply_festival_tilt(
        self,
        portfolio: Any,
        reference_date: Optional[date] = None
    ) -> Any:
        """
        Apply festival tilt to portfolio assets
        
        Args:
            portfolio: Portfolio object with assets
            reference_date: Date to check against (defaults to today)
            
        Returns:
            Modified portfolio with festival tilt applied
        """
        if not self.enabled:
            logger.info("Festival calendar disabled, skipping tilt application")
            return portfolio
        
        active_festivals = self.get_active_festivals(reference_date)
        
        if not active_festivals:
            logger.info("No active festivals, skipping tilt application")
            return portfolio
        
        logger.info(f"Applying festival tilt for {len(active_festivals)} active festivals")
        
        # Build sector tilt map
        sector_tilt_map: Dict[str, float] = {}
        for active_festival in active_festivals:
            for sector in active_festival.sectors_to_tilt:
                # Use maximum tilt factor if multiple festivals affect same sector
                current_tilt = sector_tilt_map.get(sector, 1.0)
                sector_tilt_map[sector] = max(current_tilt, active_festival.tilt_factor)
        
        # Apply tilt to portfolio assets
        for asset in portfolio.assets:
            if hasattr(asset, 'sector') and asset.sector:
                tilt_factor = sector_tilt_map.get(asset.sector, 1.0)
                
                if tilt_factor > 1.0:
                    original_weight = asset.weight
                    asset.weight *= tilt_factor
                    
                    logger.debug(
                        f"Festival tilt applied to {asset.name} ({asset.sector}): "
                        f"{original_weight:.4f} -> {asset.weight:.4f}"
                    )
        
        return portfolio
    
    def get_upcoming_festivals(
        self,
        days_ahead: int = 30,
        reference_date: Optional[date] = None
    ) -> List[Festival]:
        """
        Get upcoming festivals within specified days
        
        Args:
            days_ahead: Number of days to look ahead
            reference_date: Date to check from (defaults to today)
            
        Returns:
            List of upcoming festivals
        """
        if not self.enabled:
            return []
        
        if reference_date is None:
            reference_date = date.today()
        
        upcoming_festivals = []
        
        for festival in self.festivals:
            start_date = datetime.strptime(festival.start_date, "%Y-%m-%d").date()
            
            # Check if festival starts within the specified days
            days_until_start = (start_date - reference_date).days
            
            if 0 < days_until_start <= days_ahead:
                upcoming_festivals.append(festival)
                
                logger.debug(
                    f"Upcoming festival: {festival.name} "
                    f"(starts in {days_until_start} days)"
                )
        
        return upcoming_festivals
    
    def get_festival_impact_report(
        self,
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive festival impact report
        
        Args:
            reference_date: Date to check against (defaults to today)
            
        Returns:
            Festival impact report
        """
        active_festivals = self.get_active_festivals(reference_date)
        upcoming_festivals = self.get_upcoming_festivals(30, reference_date)
        
        # Build sector impact summary
        sector_impacts: Dict[str, float] = {}
        for active_festival in active_festivals:
            for sector in active_festival.sectors_to_tilt:
                current_impact = sector_impacts.get(sector, 1.0)
                sector_impacts[sector] = max(current_impact, active_festival.tilt_factor)
        
        return {
            'enabled': self.enabled,
            'region': self.region,
            'reference_date': reference_date.isoformat() if reference_date else date.today().isoformat(),
            'active_festivals': [
                {
                    'name': af.festival.name,
                    'days_remaining': af.days_remaining,
                    'tilt_factor': af.tilt_factor,
                    'sectors': af.sectors_to_tilt
                }
                for af in active_festivals
            ],
            'upcoming_festivals': [
                {
                    'name': f.name,
                    'start_date': f.start_date,
                    'end_date': f.end_date,
                    'tilt_factor': f.tilt_factor,
                    'sectors': f.related_sectors
                }
                for f in upcoming_festivals
            ],
            'sector_impacts': sector_impacts,
            'total_active_festivals': len(active_festivals),
            'total_upcoming_festivals': len(upcoming_festivals),
            'timestamp': datetime.now().isoformat()
        }
    
    def is_festival_period(self, reference_date: Optional[date] = None) -> bool:
        """
        Check if it's currently a festival period
        
        Args:
            reference_date: Date to check (defaults to today)
            
        Returns:
            True if any festival is active
        """
        if not self.enabled:
            return False
        
        active_festivals = self.get_active_festivals(reference_date)
        return len(active_festivals) > 0
