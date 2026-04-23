"""
F' Component Pattern - Database as Specialized Component

This module implements NASA's F´ (F Prime) component pattern for the database,
treating it as a specialized component with input/output ports for complete
isolation from simulation logic.

Key Features:
- Component-based architecture
- Input/output port abstraction
- Isolation from simulation logic
- Event-driven communication
- Health monitoring

Reference: NASA's F´ Flight Software Framework
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any, List, Tuple
from dataclasses import dataclass
import time


class PortType(Enum):
    """Port type enumeration"""
    INPUT = "input"
    OUTPUT = "output"
    COMMAND = "command"
    TELEMETRY = "telemetry"


class ComponentHealth(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class Port:
    """Component port definition"""
    name: str
    port_type: PortType
    data_type: str
    handler: Optional[Callable] = None


@dataclass
class Event:
    """Component event"""
    event_id: str
    event_type: str
    timestamp: float
    data: Dict[str, Any]
    severity: str = "INFO"


@dataclass(frozen=True)
class EsportsMetadata:
    """Structured esports metadata for the F´ database component layer."""
    domain: str
    genre: str
    subsystem: str
    match_phase: str
    responsibilities: Tuple[str, ...]
    integration_points: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to a serializable dictionary."""
        return {
            "domain": self.domain,
            "genre": self.genre,
            "subsystem": self.subsystem,
            "match_phase": self.match_phase,
            "responsibilities": list(self.responsibilities),
            "integration_points": list(self.integration_points),
        }


ESPORTS_METADATA = EsportsMetadata(
    domain="esports",
    genre="real_time_strategy",
    subsystem="deterministic_match_persistence",
    match_phase="live_match_operations",
    responsibilities=(
        "snapshot storage for rollback and replay",
        "player command synchronization",
        "telemetry emission for observers and operators",
        "component health monitoring for tournament reliability",
    ),
    integration_points=(
        "snapshot_in",
        "command_in",
        "snapshot_out",
        "telemetry_out",
        "cmd_response",
    ),
)


def get_esports_metadata() -> Dict[str, Any]:
    """Return module-level esports metadata."""
    return ESPORTS_METADATA.to_dict()


class FPrimeComponent:
    """
    F´ Component - Base class for database components.
    
    Implements the NASA F´ component pattern with:
    - Input/Output ports
    - Command handlers
    - Telemetry generation
    - Event logging
    - Health monitoring
    """
    
    def __init__(self, component_id: str, component_name: str):
        """
        Initialize F´ component.
        
        Args:
            component_id: Unique component identifier
            component_name: Human-readable component name
        """
        self.component_id = component_id
        self.component_name = component_name
        self.health = ComponentHealth.HEALTHY
        
        # Port registry
        self.ports: Dict[str, Port] = {}
        
        # Event log
        self.events: List[Event] = []
        
        # Telemetry data
        self.telemetry: Dict[str, Any] = {}
        
        # Component state
        self.initialized = False
        self.running = False
    
    def register_port(self, port: Port):
        """Register a component port"""
        if port.name in self.ports:
            raise ValueError(f"Port '{port.name}' already registered")
        
        self.ports[port.name] = port
        self._log_event("PORT_REGISTERED", {"port_name": port.name, "port_type": port.port_type.value})
    
    def connect_port(self, port_name: str, handler: Callable):
        """Connect handler to port"""
        if port_name not in self.ports:
            raise ValueError(f"Port '{port_name}' not found")
        
        self.ports[port_name].handler = handler
        self._log_event("PORT_CONNECTED", {"port_name": port_name})
    
    def send_to_port(self, port_name: str, data: Any):
        """Send data to output port"""
        if port_name not in self.ports:
            raise ValueError(f"Port '{port_name}' not found")
        
        port = self.ports[port_name]
        
        if port.port_type != PortType.OUTPUT:
            raise ValueError(f"Port '{port_name}' is not an output port")
        
        if port.handler:
            try:
                port.handler(data)
            except Exception as e:
                self._log_event("PORT_ERROR", {
                    "port_name": port_name,
                    "error": str(e)
                }, severity="ERROR")
    
    def receive_from_port(self, port_name: str, data: Any):
        """Receive data from input port"""
        if port_name not in self.ports:
            raise ValueError(f"Port '{port_name}' not found")
        
        port = self.ports[port_name]
        
        if port.port_type != PortType.INPUT:
            raise ValueError(f"Port '{port_name}' is not an input port")
        
        if port.handler:
            try:
                port.handler(data)
            except Exception as e:
                self._log_event("PORT_ERROR", {
                    "port_name": port_name,
                    "error": str(e)
                }, severity="ERROR")
    
    def _log_event(self, event_type: str, data: Dict[str, Any], severity: str = "INFO"):
        """Log component event"""
        event = Event(
            event_id=f"{self.component_id}:{event_type}:{int(time.time() * 1000)}",
            event_type=event_type,
            timestamp=time.time(),
            data=data,
            severity=severity
        )
        self.events.append(event)
        
        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
    
    def update_telemetry(self, key: str, value: Any):
        """Update telemetry value"""
        self.telemetry[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def get_telemetry(self) -> Dict[str, Any]:
        """Get current telemetry"""
        return self.telemetry.copy()
    
    def get_health(self) -> ComponentHealth:
        """Get component health status"""
        return self.health

    def get_esports_metadata(self) -> Dict[str, Any]:
        """Get esports metadata enriched with component runtime details."""
        metadata = get_esports_metadata().copy()
        metadata.update({
            "component_id": self.component_id,
            "component_name": self.component_name,
            "health": self.health.value,
            "ports": {
                name: {
                    "port_type": port.port_type.value,
                    "data_type": port.data_type,
                }
                for name, port in self.ports.items()
            },
        })
        return metadata
    
    def set_health(self, health: ComponentHealth):
        """Set component health status"""
        old_health = self.health
        self.health = health
        
        if old_health != health:
            self._log_event("HEALTH_CHANGED", {
                "old_health": old_health.value,
                "new_health": health.value
            }, severity="WARNING" if health != ComponentHealth.HEALTHY else "INFO")
    
    def initialize(self) -> bool:
        """Initialize component"""
        try:
            self._on_initialize()
            self.initialized = True
            self._log_event("COMPONENT_INITIALIZED", {})
            return True
        except Exception as e:
            self._log_event("INITIALIZATION_FAILED", {"error": str(e)}, severity="ERROR")
            self.set_health(ComponentHealth.FAILED)
            return False
    
    def start(self) -> bool:
        """Start component"""
        if not self.initialized:
            raise RuntimeError("Component not initialized")
        
        try:
            self._on_start()
            self.running = True
            self._log_event("COMPONENT_STARTED", {})
            return True
        except Exception as e:
            self._log_event("START_FAILED", {"error": str(e)}, severity="ERROR")
            self.set_health(ComponentHealth.FAILED)
            return False
    
    def stop(self) -> bool:
        """Stop component"""
        try:
            self._on_stop()
            self.running = False
            self._log_event("COMPONENT_STOPPED", {})
            return True
        except Exception as e:
            self._log_event("STOP_FAILED", {"error": str(e)}, severity="ERROR")
            return False
    
    def _on_initialize(self):
        """Override in subclass"""
        pass
    
    def _on_start(self):
        """Override in subclass"""
        pass
    
    def _on_stop(self):
        """Override in subclass"""
        pass


class DatabaseComponent(FPrimeComponent):
    """
    Database Component - F´ component wrapping the database layers.
    
    Provides ports for:
    - Snapshot storage (input)
    - Snapshot retrieval (output)
    - Telemetry export (output)
    - Command synchronization (input/output)
    """
    
    def __init__(self, component_id: str = "DB_COMP"):
        """Initialize database component"""
        super().__init__(component_id, "Database Component")
        
        # Register ports
        self._register_ports()
    
    def _register_ports(self):
        """Register component ports"""
        # Input ports
        self.register_port(Port(
            name="snapshot_in",
            port_type=PortType.INPUT,
            data_type="SnapshotData"
        ))
        
        self.register_port(Port(
            name="command_in",
            port_type=PortType.INPUT,
            data_type="Command"
        ))
        
        # Output ports
        self.register_port(Port(
            name="snapshot_out",
            port_type=PortType.OUTPUT,
            data_type="SnapshotData"
        ))
        
        self.register_port(Port(
            name="telemetry_out",
            port_type=PortType.OUTPUT,
            data_type="TelemetryData"
        ))
        
        # Command port
        self.register_port(Port(
            name="cmd_response",
            port_type=PortType.COMMAND,
            data_type="CommandResponse"
        ))
    
    def _on_initialize(self):
        """Initialize database layers"""
        self.update_telemetry("initialization_time", time.time())
    
    def _on_start(self):
        """Start database component"""
        self.update_telemetry("start_time", time.time())
    
    def _on_stop(self):
        """Stop database component"""
        self.update_telemetry("stop_time", time.time())
