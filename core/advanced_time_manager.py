#!/usr/bin/env python3
"""
⏰ Advanced Time Manager for ACTORS System
Comprehensive time management, scheduling, and temporal analytics
"""

import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
# import schedule  # Optional dependency
# import pytz  # Optional dependency
# from croniter import croniter  # Optional dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeEventType(Enum):
    SCHEDULED_TASK = "scheduled_task"
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"
    EARNINGS_ANNOUNCEMENT = "earnings_announcement"
    FED_MEETING = "fed_meeting"
    DATA_REFRESH = "data_refresh"
    ML_MODEL_RETRAIN = "ml_model_retrain"
    PORTFOLIO_REBALANCE = "portfolio_rebalance"
    RISK_CHECK = "risk_check"
    AUDIO_PROCESSING = "audio_processing"
    EMBEDDING_UPDATE = "embedding_update"
    SYSTEM_MAINTENANCE = "system_maintenance"

class TimeZone(Enum):
    UTC = "UTC"
    EST = "US/Eastern"
    PST = "US/Pacific"
    GMT = "Europe/London"
    JST = "Asia/Tokyo"
    CET = "Europe/Paris"

class ScheduleFrequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM_CRON = "custom_cron"
    MARKET_HOURS = "market_hours"
    BUSINESS_HOURS = "business_hours"

@dataclass
class TimeEvent:
    """Represents a time-based event"""
    id: str
    name: str
    event_type: TimeEventType
    scheduled_time: datetime
    timezone: TimeZone
    frequency: ScheduleFrequency
    cron_expression: Optional[str] = None
    callback_function: Optional[str] = None
    parameters: Dict[str, Any] = None
    priority: int = 5  # 1-10, higher = more urgent
    is_active: bool = True
    is_recurring: bool = False
    max_executions: Optional[int] = None
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class TimeExecution:
    """Represents an execution of a time event"""
    event_id: str
    execution_time: datetime
    duration_ms: float
    status: str  # "success", "failed", "timeout"
    result: Any = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class TimeAnalytics:
    """Time-based analytics and metrics"""
    total_events: int
    active_events: int
    completed_executions: int
    failed_executions: int
    average_execution_time_ms: float
    events_by_type: Dict[str, int]
    events_by_frequency: Dict[str, int]
    execution_success_rate: float
    last_updated: datetime

class MarketHoursManager:
    """Manages market hours and trading schedules"""
    
    def __init__(self):
        self.market_schedules = {
            'NYSE': {
                'timezone': TimeZone.EST,
                'open': '09:30',
                'close': '16:00',
                'days': [0, 1, 2, 3, 4]  # Monday to Friday
            },
            'NASDAQ': {
                'timezone': TimeZone.EST,
                'open': '09:30',
                'close': '16:00',
                'days': [0, 1, 2, 3, 4]
            },
            'CRYPTO': {
                'timezone': TimeZone.UTC,
                'open': '00:00',
                'close': '23:59',
                'days': [0, 1, 2, 3, 4, 5, 6]  # 24/7
            },
            'FOREX': {
                'timezone': TimeZone.UTC,
                'open': '00:00',
                'close': '23:59',
                'days': [0, 1, 2, 3, 4, 5, 6]  # 24/7
            }
        }
    
    def is_market_open(self, market: str = 'NYSE', timezone: TimeZone = TimeZone.EST) -> bool:
        """Check if market is currently open"""
        if market not in self.market_schedules:
            return False
        
        schedule = self.market_schedules[market]
        now = datetime.now()
        
        # Check if it's a trading day
        if now.weekday() not in schedule['days']:
            return False
        
        # Check if it's within trading hours
        current_time = now.time()
        open_time = datetime.strptime(schedule['open'], '%H:%M').time()
        close_time = datetime.strptime(schedule['close'], '%H:%M').time()
        
        return open_time <= current_time <= close_time
    
    def get_next_market_open(self, market: str = 'NYSE') -> datetime:
        """Get next market opening time"""
        if market not in self.market_schedules:
            return None
        
        schedule = self.market_schedules[market]
        now = datetime.now()
        
        # Find next trading day
        days_ahead = 0
        while days_ahead < 7:  # Look ahead max 7 days
            check_date = now + timedelta(days=days_ahead)
            if check_date.weekday() in schedule['days']:
                # Found a trading day, set market open time
                open_time = datetime.strptime(schedule['open'], '%H:%M').time()
                next_open = datetime.combine(check_date.date(), open_time)
                
                # If it's today and market is already open, get next day
                if days_ahead == 0 and self.is_market_open(market):
                    days_ahead += 1
                    continue
                
                return next_open
            days_ahead += 1
        
        return None
    
    def get_next_market_close(self, market: str = 'NYSE') -> datetime:
        """Get next market closing time"""
        if market not in self.market_schedules:
            return None
        
        schedule = self.market_schedules[market]
        now = datetime.now()
        
        # If market is open, get today's close
        if self.is_market_open(market):
            close_time = datetime.strptime(schedule['close'], '%H:%M').time()
            today_close = datetime.combine(now.date(), close_time)
            return today_close
        
        # Otherwise, get next trading day's close
        days_ahead = 1
        while days_ahead < 7:
            check_date = now + timedelta(days=days_ahead)
            if check_date.weekday() in schedule['days']:
                close_time = datetime.strptime(schedule['close'], '%H:%M').time()
                next_close = datetime.combine(check_date.date(), close_time)
                return next_close
            days_ahead += 1
        
        return None

class AdvancedTimeManager:
    """Advanced time management and scheduling system"""
    
    def __init__(self):
        self.events: Dict[str, TimeEvent] = {}
        self.executions: List[TimeExecution] = []
        self.market_hours = MarketHoursManager()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.is_running = False
        self.scheduler_thread = None
        self.callback_registry: Dict[str, Callable] = {}
        self.analytics = TimeAnalytics(
            total_events=0,
            active_events=0,
            completed_executions=0,
            failed_executions=0,
            average_execution_time_ms=0.0,
            events_by_type={},
            events_by_frequency={},
            execution_success_rate=0.0,
            last_updated=datetime.now()
        )
        
        # Register default callbacks
        self._register_default_callbacks()
    
    def _register_default_callbacks(self):
        """Register default callback functions"""
        self.callback_registry.update({
            'market_open_handler': self._handle_market_open,
            'market_close_handler': self._handle_market_close,
            'data_refresh_handler': self._handle_data_refresh,
            'ml_retrain_handler': self._handle_ml_retrain,
            'portfolio_rebalance_handler': self._handle_portfolio_rebalance,
            'risk_check_handler': self._handle_risk_check,
            'audio_processing_handler': self._handle_audio_processing,
            'embedding_update_handler': self._handle_embedding_update,
            'system_maintenance_handler': self._handle_system_maintenance
        })
    
    async def initialize(self):
        """Initialize the time manager"""
        logger.info("⏰ Initializing Advanced Time Manager...")
        
        # Load existing events (in production, this would load from database)
        await self._load_events()
        
        # Start the scheduler
        self.start_scheduler()
        
        logger.info("✅ Advanced Time Manager initialized successfully")
    
    async def _load_events(self):
        """Load events from storage (placeholder for database integration)"""
        # In production, this would load from a database
        # For now, we'll create some default events
        default_events = [
            {
                'id': 'market_open_nyse',
                'name': 'NYSE Market Open',
                'event_type': TimeEventType.MARKET_OPEN,
                'scheduled_time': datetime.now() + timedelta(hours=1),
                'timezone': TimeZone.EST,
                'frequency': ScheduleFrequency.DAILY,
                'callback_function': 'market_open_handler',
                'priority': 8,
                'is_recurring': True
            },
            {
                'id': 'market_close_nyse',
                'name': 'NYSE Market Close',
                'event_type': TimeEventType.MARKET_CLOSE,
                'scheduled_time': datetime.now() + timedelta(hours=8),
                'timezone': TimeZone.EST,
                'frequency': ScheduleFrequency.DAILY,
                'callback_function': 'market_close_handler',
                'priority': 8,
                'is_recurring': True
            },
            {
                'id': 'data_refresh_hourly',
                'name': 'Hourly Data Refresh',
                'event_type': TimeEventType.DATA_REFRESH,
                'scheduled_time': datetime.now() + timedelta(minutes=5),
                'timezone': TimeZone.UTC,
                'frequency': ScheduleFrequency.CUSTOM_CRON,
                'cron_expression': '0 * * * *',  # Every hour
                'callback_function': 'data_refresh_handler',
                'priority': 6,
                'is_recurring': True
            }
        ]
        
        for event_data in default_events:
            event = TimeEvent(
                **event_data,
                parameters={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.events[event.id] = event
        
        self._update_analytics()
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("🔄 Time scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("⏹️ Time scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check for events that need to be executed
                for event in self.events.values():
                    if not event.is_active:
                        continue
                    
                    if event.next_execution and current_time >= event.next_execution:
                        # Execute the event
                        asyncio.run(self._execute_event(event))
                
                # Update next execution times for recurring events
                self._update_recurring_events()
                
                # Sleep for a short interval
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Scheduler loop error: {e}")
                time.sleep(5)
    
    async def _execute_event(self, event: TimeEvent):
        """Execute a time event"""
        start_time = time.time()
        execution = TimeExecution(
            event_id=event.id,
            execution_time=datetime.now(),
            duration_ms=0.0,
            status="running",
            metadata={}
        )
        
        try:
            logger.info(f"⏰ Executing event: {event.name}")
            
            # Get callback function
            callback = self.callback_registry.get(event.callback_function)
            if not callback:
                raise ValueError(f"Callback function '{event.callback_function}' not found")
            
            # Execute callback
            if asyncio.iscoroutinefunction(callback):
                result = await callback(event, event.parameters or {})
            else:
                result = callback(event, event.parameters or {})
            
            # Update execution
            execution.duration_ms = (time.time() - start_time) * 1000
            execution.status = "success"
            execution.result = result
            
            # Update event
            event.execution_count += 1
            event.last_execution = datetime.now()
            
            logger.info(f"✅ Event executed successfully: {event.name} ({execution.duration_ms:.2f}ms)")
            
        except Exception as e:
            execution.duration_ms = (time.time() - start_time) * 1000
            execution.status = "failed"
            execution.error_message = str(e)
            
            logger.error(f"❌ Event execution failed: {event.name} - {e}")
        
        # Store execution
        self.executions.append(execution)
        
        # Update analytics
        self._update_analytics()
    
    def _update_recurring_events(self):
        """Update next execution times for recurring events"""
        current_time = datetime.now()
        
        for event in self.events.values():
            if not event.is_active or not event.is_recurring:
                continue
            
            # Check if we need to update next execution time
            if not event.next_execution or current_time >= event.next_execution:
                event.next_execution = self._calculate_next_execution(event)
    
    def _calculate_next_execution(self, event: TimeEvent) -> Optional[datetime]:
        """Calculate next execution time for an event"""
        if not event.is_recurring:
            return None
        
        current_time = datetime.now()
        
        if event.frequency == ScheduleFrequency.DAILY:
            return current_time + timedelta(days=1)
        elif event.frequency == ScheduleFrequency.WEEKLY:
            return current_time + timedelta(weeks=1)
        elif event.frequency == ScheduleFrequency.MONTHLY:
            return current_time + timedelta(days=30)
        elif event.frequency == ScheduleFrequency.CUSTOM_CRON:
            if event.cron_expression:
                # Simple cron-like parsing for common patterns
                try:
                    # For now, just return a simple interval
                    # In production, you'd use a proper cron parser
                    if event.cron_expression == '0 * * * *':  # Every hour
                        return current_time + timedelta(hours=1)
                    elif event.cron_expression == '0 */2 * * *':  # Every 2 hours
                        return current_time + timedelta(hours=2)
                    elif event.cron_expression == '0 */4 * * *':  # Every 4 hours
                        return current_time + timedelta(hours=4)
                    else:
                        return current_time + timedelta(hours=1)  # Default to hourly
                except Exception as e:
                    logger.error(f"❌ Invalid cron expression: {event.cron_expression} - {e}")
                    return None
        elif event.frequency == ScheduleFrequency.MARKET_HOURS:
            # Schedule for next market open
            return self.market_hours.get_next_market_open()
        
        return None
    
    # Default callback handlers
    async def _handle_market_open(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle market open event"""
        logger.info("📈 Market opened - activating trading systems")
        return {"status": "market_opened", "timestamp": datetime.now().isoformat()}
    
    async def _handle_market_close(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle market close event"""
        logger.info("📉 Market closed - deactivating trading systems")
        return {"status": "market_closed", "timestamp": datetime.now().isoformat()}
    
    async def _handle_data_refresh(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle data refresh event"""
        logger.info("🔄 Refreshing market data")
        return {"status": "data_refreshed", "timestamp": datetime.now().isoformat()}
    
    async def _handle_ml_retrain(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle ML model retraining event"""
        logger.info("🤖 Retraining ML models")
        return {"status": "models_retrained", "timestamp": datetime.now().isoformat()}
    
    async def _handle_portfolio_rebalance(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle portfolio rebalancing event"""
        logger.info("⚖️ Rebalancing portfolio")
        return {"status": "portfolio_rebalanced", "timestamp": datetime.now().isoformat()}
    
    async def _handle_risk_check(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle risk check event"""
        logger.info("⚠️ Performing risk assessment")
        return {"status": "risk_checked", "timestamp": datetime.now().isoformat()}
    
    async def _handle_audio_processing(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle audio processing event"""
        logger.info("🎤 Processing audio for trading signals")
        return {"status": "audio_processed", "timestamp": datetime.now().isoformat()}
    
    async def _handle_embedding_update(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle embedding update event"""
        logger.info("📚 Updating embeddings")
        return {"status": "embeddings_updated", "timestamp": datetime.now().isoformat()}
    
    async def _handle_system_maintenance(self, event: TimeEvent, parameters: Dict[str, Any]):
        """Handle system maintenance event"""
        logger.info("🔧 Performing system maintenance")
        return {"status": "maintenance_completed", "timestamp": datetime.now().isoformat()}
    
    # Public API methods
    async def create_event(self, event_data: Dict[str, Any]) -> TimeEvent:
        """Create a new time event"""
        event_id = event_data.get('id', f"event_{int(time.time())}")
        
        if event_id in self.events:
            raise ValueError(f"Event with ID '{event_id}' already exists")
        
        event = TimeEvent(
            id=event_id,
            name=event_data.get('name', 'Unnamed Event'),
            event_type=TimeEventType(event_data.get('event_type', 'scheduled_task')),
            scheduled_time=event_data.get('scheduled_time', datetime.now()),
            timezone=TimeZone(event_data.get('timezone', 'UTC')),
            frequency=ScheduleFrequency(event_data.get('frequency', 'once')),
            cron_expression=event_data.get('cron_expression'),
            callback_function=event_data.get('callback_function'),
            parameters=event_data.get('parameters', {}),
            priority=event_data.get('priority', 5),
            is_active=event_data.get('is_active', True),
            is_recurring=event_data.get('is_recurring', False),
            max_executions=event_data.get('max_executions'),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Calculate next execution time
        if event.is_recurring:
            event.next_execution = self._calculate_next_execution(event)
        else:
            event.next_execution = event.scheduled_time
        
        self.events[event_id] = event
        self._update_analytics()
        
        logger.info(f"✅ Created event: {event.name} (ID: {event_id})")
        return event
    
    async def update_event(self, event_id: str, updates: Dict[str, Any]) -> TimeEvent:
        """Update an existing time event"""
        if event_id not in self.events:
            raise ValueError(f"Event with ID '{event_id}' not found")
        
        event = self.events[event_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        event.updated_at = datetime.now()
        
        # Recalculate next execution time
        if event.is_recurring:
            event.next_execution = self._calculate_next_execution(event)
        
        self._update_analytics()
        
        logger.info(f"✅ Updated event: {event.name} (ID: {event_id})")
        return event
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete a time event"""
        if event_id not in self.events:
            return False
        
        del self.events[event_id]
        self._update_analytics()
        
        logger.info(f"✅ Deleted event: {event_id}")
        return True
    
    def get_event(self, event_id: str) -> Optional[TimeEvent]:
        """Get a time event by ID"""
        return self.events.get(event_id)
    
    def get_events(self, filters: Dict[str, Any] = None) -> List[TimeEvent]:
        """Get events with optional filters"""
        events = list(self.events.values())
        
        if not filters:
            return events
        
        # Apply filters
        filtered_events = []
        for event in events:
            match = True
            
            for key, value in filters.items():
                if hasattr(event, key):
                    if getattr(event, key) != value:
                        match = False
                        break
            
            if match:
                filtered_events.append(event)
        
        return filtered_events
    
    def get_upcoming_events(self, limit: int = 10) -> List[TimeEvent]:
        """Get upcoming events sorted by execution time"""
        upcoming = []
        current_time = datetime.now()
        
        for event in self.events.values():
            if event.is_active and event.next_execution and event.next_execution > current_time:
                upcoming.append(event)
        
        # Sort by next execution time
        upcoming.sort(key=lambda x: x.next_execution)
        
        return upcoming[:limit]
    
    def get_execution_history(self, event_id: str = None, limit: int = 100) -> List[TimeExecution]:
        """Get execution history"""
        executions = self.executions
        
        if event_id:
            executions = [e for e in executions if e.event_id == event_id]
        
        # Sort by execution time (most recent first)
        executions.sort(key=lambda x: x.execution_time, reverse=True)
        
        return executions[:limit]
    
    def _update_analytics(self):
        """Update analytics data"""
        total_events = len(self.events)
        active_events = len([e for e in self.events.values() if e.is_active])
        
        completed_executions = len([e for e in self.executions if e.status == "success"])
        failed_executions = len([e for e in self.executions if e.status == "failed"])
        total_executions = completed_executions + failed_executions
        
        average_execution_time = 0.0
        if self.executions:
            total_time = sum(e.duration_ms for e in self.executions)
            average_execution_time = total_time / len(self.executions)
        
        # Count events by type
        events_by_type = defaultdict(int)
        for event in self.events.values():
            events_by_type[event.event_type.value] += 1
        
        # Count events by frequency
        events_by_frequency = defaultdict(int)
        for event in self.events.values():
            events_by_frequency[event.frequency.value] += 1
        
        execution_success_rate = 0.0
        if total_executions > 0:
            execution_success_rate = completed_executions / total_executions
        
        self.analytics = TimeAnalytics(
            total_events=total_events,
            active_events=active_events,
            completed_executions=completed_executions,
            failed_executions=failed_executions,
            average_execution_time_ms=average_execution_time,
            events_by_type=dict(events_by_type),
            events_by_frequency=dict(events_by_frequency),
            execution_success_rate=execution_success_rate,
            last_updated=datetime.now()
        )
    
    def get_analytics(self) -> TimeAnalytics:
        """Get current analytics"""
        self._update_analytics()
        return self.analytics
    
    def register_callback(self, name: str, callback: Callable):
        """Register a custom callback function"""
        self.callback_registry[name] = callback
        logger.info(f"✅ Registered callback: {name}")
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        markets = ['NYSE', 'NASDAQ', 'CRYPTO', 'FOREX']
        status = {}
        
        for market in markets:
            is_open = self.market_hours.is_market_open(market)
            next_open = self.market_hours.get_next_market_open(market)
            next_close = self.market_hours.get_next_market_close(market)
            
            status[market] = {
                'is_open': is_open,
                'next_open': next_open.isoformat() if next_open else None,
                'next_close': next_close.isoformat() if next_close else None
            }
        
        return status

# Example usage and testing
async def main():
    """Example usage of Advanced Time Manager"""
    
    # Initialize time manager
    time_manager = AdvancedTimeManager()
    await time_manager.initialize()
    
    print("⏰ Advanced Time Manager Demo")
    print("=" * 50)
    
    # Get current analytics
    analytics = time_manager.get_analytics()
    print(f"📊 Analytics:")
    print(f"   • Total Events: {analytics.total_events}")
    print(f"   • Active Events: {analytics.active_events}")
    print(f"   • Success Rate: {analytics.execution_success_rate:.2%}")
    print(f"   • Avg Execution Time: {analytics.average_execution_time_ms:.2f}ms")
    
    # Get market status
    market_status = time_manager.get_market_status()
    print(f"\n📈 Market Status:")
    for market, status in market_status.items():
        print(f"   • {market}: {'🟢 Open' if status['is_open'] else '🔴 Closed'}")
        if status['next_open']:
            print(f"     Next Open: {status['next_open']}")
        if status['next_close']:
            print(f"     Next Close: {status['next_close']}")
    
    # Get upcoming events
    upcoming = time_manager.get_upcoming_events(limit=5)
    print(f"\n⏰ Upcoming Events ({len(upcoming)}):")
    for event in upcoming:
        print(f"   • {event.name} ({event.event_type.value})")
        print(f"     Next: {event.next_execution}")
        print(f"     Priority: {event.priority}/10")
    
    # Create a new event
    new_event_data = {
        'name': 'Test Event',
        'event_type': 'scheduled_task',
        'scheduled_time': datetime.now() + timedelta(minutes=2),
        'timezone': 'UTC',
        'frequency': 'once',
        'callback_function': 'data_refresh_handler',
        'priority': 7
    }
    
    try:
        new_event = await time_manager.create_event(new_event_data)
        print(f"\n✅ Created new event: {new_event.name}")
        print(f"   ID: {new_event.id}")
        print(f"   Scheduled: {new_event.scheduled_time}")
    except Exception as e:
        print(f"❌ Failed to create event: {e}")
    
    # Get execution history
    history = time_manager.get_execution_history(limit=5)
    print(f"\n📋 Recent Executions ({len(history)}):")
    for execution in history:
        print(f"   • {execution.event_id}: {execution.status}")
        print(f"     Time: {execution.execution_time}")
        print(f"     Duration: {execution.duration_ms:.2f}ms")
    
    # Stop the scheduler
    time_manager.stop_scheduler()
    print(f"\n⏹️ Time manager stopped")

if __name__ == "__main__":
    asyncio.run(main())
