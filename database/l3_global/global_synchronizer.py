"""
L3: Global Synchronization - Redis/Redict Command Bus

This module provides global lockstep synchronization for multiplayer
using Redis as a low-latency key-value store and command sequencer.

Key Features:
- Command bus for player input sequencing
- Global tick ID stamping
- Lockstep command execution
- Multiplayer synchronization

Target Latency: 20-50ms
"""

from typing import Optional, List, Dict, Any
import json
import time

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..config import L3Config


class Command:
    """Player command with metadata"""
    
    def __init__(
        self,
        command_id: str,
        player_id: str,
        tick_id: int,
        command_type: str,
        payload: Dict[str, Any]
    ):
        self.command_id = command_id
        self.player_id = player_id
        self.tick_id = tick_id
        self.command_type = command_type
        self.payload = payload
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'command_id': self.command_id,
            'player_id': self.player_id,
            'tick_id': self.tick_id,
            'command_type': self.command_type,
            'payload': self.payload,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Command':
        """Create from dictionary"""
        cmd = cls(
            command_id=data['command_id'],
            player_id=data['player_id'],
            tick_id=data['tick_id'],
            command_type=data['command_type'],
            payload=data['payload']
        )
        cmd.timestamp = data.get('timestamp', time.time())
        return cmd


class GlobalSynchronizer:
    """
    L3 Global Synchronizer - Multiplayer lockstep coordination.
    
    Uses Redis as a command bus to sequence player inputs and ensure
    all clients execute commands in the same deterministic order.
    """
    
    def __init__(self, config: Optional[L3Config] = None):
        """Initialize global synchronizer"""
        self.config = config or L3Config()
        self.client = None
        self.connected = False
        
        if REDIS_AVAILABLE:
            self._connect()
        else:
            print("Warning: Redis not available. Multiplayer features disabled.")
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True,
                socket_timeout=self.config.command_timeout_ms / 1000.0
            )
            
            # Test connection
            self.client.ping()
            self.connected = True
            
            # Initialize tick sequence if needed
            if not self.client.exists(self.config.tick_sequence_key):
                self.client.set(self.config.tick_sequence_key, 0)
            
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            self.connected = False
    
    def get_current_tick(self) -> int:
        """Get current global tick ID"""
        if not self.connected:
            return 0
        
        try:
            tick = self.client.get(self.config.tick_sequence_key)
            return int(tick) if tick else 0
        except Exception as e:
            print(f"Error getting tick: {e}")
            return 0
    
    def advance_tick(self) -> int:
        """
        Advance global tick and return new tick ID.
        
        Returns:
            New tick ID
        """
        if not self.connected:
            return 0
        
        try:
            new_tick = self.client.incr(self.config.tick_sequence_key)
            return int(new_tick)
        except Exception as e:
            print(f"Error advancing tick: {e}")
            return 0
    
    def submit_command(
        self,
        player_id: str,
        command_type: str,
        payload: Dict[str, Any],
        target_tick: Optional[int] = None
    ) -> Optional[str]:
        """
        Submit player command for execution.
        
        Args:
            player_id: Player identifier
            command_type: Type of command (e.g., 'move', 'attack')
            payload: Command payload
            target_tick: Optional target tick (defaults to next tick)
        
        Returns:
            Command ID or None if failed
        """
        if not self.connected:
            return None
        
        try:
            # Get target tick
            if target_tick is None:
                target_tick = self.get_current_tick() + 1
            
            # Generate command ID
            command_id = f"{player_id}:{target_tick}:{int(time.time() * 1000)}"
            
            # Create command
            command = Command(
                command_id=command_id,
                player_id=player_id,
                tick_id=target_tick,
                command_type=command_type,
                payload=payload
            )
            
            # Store in Redis sorted set (sorted by tick_id)
            key = f"commands:tick:{target_tick}"
            self.client.zadd(
                key,
                {json.dumps(command.to_dict()): time.time()}
            )
            
            # Set expiration (commands expire after execution)
            self.client.expire(key, 60)  # 60 seconds
            
            # Add to player's command history
            player_key = f"commands:player:{player_id}"
            self.client.lpush(player_key, json.dumps(command.to_dict()))
            self.client.ltrim(player_key, 0, 99)  # Keep last 100 commands
            
            return command_id
            
        except Exception as e:
            print(f"Error submitting command: {e}")
            return None
    
    def get_commands_for_tick(self, tick_id: int) -> List[Command]:
        """
        Get all commands for a specific tick.
        
        Args:
            tick_id: Tick to retrieve commands for
        
        Returns:
            List of commands for the tick
        """
        if not self.connected:
            return []
        
        try:
            key = f"commands:tick:{tick_id}"
            
            # Get all commands from sorted set
            commands_json = self.client.zrange(key, 0, -1)
            
            # Parse commands
            commands = []
            for cmd_json in commands_json:
                cmd_data = json.loads(cmd_json)
                commands.append(Command.from_dict(cmd_data))
            
            return commands
            
        except Exception as e:
            print(f"Error getting commands: {e}")
            return []
    
    def lock_tick(self, tick_id: int, timeout_ms: int = 100) -> bool:
        """
        Lock tick for execution (prevents new commands).
        
        Args:
            tick_id: Tick to lock
            timeout_ms: Lock timeout in milliseconds
        
        Returns:
            True if lock acquired
        """
        if not self.connected:
            return False
        
        try:
            lock_key = f"lock:tick:{tick_id}"
            
            # Try to acquire lock with NX (only if not exists)
            acquired = self.client.set(
                lock_key,
                "locked",
                nx=True,
                px=timeout_ms
            )
            
            return bool(acquired)
            
        except Exception as e:
            print(f"Error locking tick: {e}")
            return False
    
    def unlock_tick(self, tick_id: int):
        """Unlock tick"""
        if not self.connected:
            return
        
        try:
            lock_key = f"lock:tick:{tick_id}"
            self.client.delete(lock_key)
        except Exception as e:
            print(f"Error unlocking tick: {e}")
    
    def is_tick_locked(self, tick_id: int) -> bool:
        """Check if tick is locked"""
        if not self.connected:
            return False
        
        try:
            lock_key = f"lock:tick:{tick_id}"
            return bool(self.client.exists(lock_key))
        except Exception as e:
            print(f"Error checking lock: {e}")
            return False
    
    def get_player_commands(self, player_id: str, limit: int = 10) -> List[Command]:
        """Get recent commands from player"""
        if not self.connected:
            return []
        
        try:
            player_key = f"commands:player:{player_id}"
            commands_json = self.client.lrange(player_key, 0, limit - 1)
            
            commands = []
            for cmd_json in commands_json:
                cmd_data = json.loads(cmd_json)
                commands.append(Command.from_dict(cmd_data))
            
            return commands
            
        except Exception as e:
            print(f"Error getting player commands: {e}")
            return []
    
    def clear_tick_commands(self, tick_id: int):
        """Clear commands for a tick (after execution)"""
        if not self.connected:
            return
        
        try:
            key = f"commands:tick:{tick_id}"
            self.client.delete(key)
        except Exception as e:
            print(f"Error clearing tick commands: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get synchronizer statistics"""
        if not self.connected:
            return {'connected': False}
        
        try:
            info = self.client.info('stats')
            return {
                'connected': True,
                'current_tick': self.get_current_tick(),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'connected': True, 'error': str(e)}
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.connected = False
    
    def __del__(self):
        """Cleanup"""
        self.close()
