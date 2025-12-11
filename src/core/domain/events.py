"""
Domain Events for the Music Machine
These represent things that happen in the system
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EventType(Enum):
    """Types of events in the system"""
    PROXIMITY_DETECTED = "proximity_detected"
    SOUND_TRIGGERED = "sound_triggered"
    STATE_CHANGED = "state_changed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class DomainEvent:
    """Base class for all domain events"""
    event_type: EventType
    timestamp: datetime
    data: dict
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ProximityEvent(DomainEvent):
    """Event triggered when proximity sensor detects something"""
    distance: float  # Distance in centimeters
    sensor_id: str
    
    def __init__(self, distance: float, sensor_id: str = "default"):
        super().__init__(
            event_type=EventType.PROXIMITY_DETECTED,
            timestamp=datetime.now(),
            data={"distance": distance, "sensor_id": sensor_id}
        )
        self.distance = distance
        self.sensor_id = sensor_id


@dataclass
class SoundEvent(DomainEvent):
    """Event for sound generation"""
    frequency: float  # Frequency in Hz
    duration: float   # Duration in seconds
    amplitude: float  # Volume 0.0 to 1.0
    
    def __init__(self, frequency: float, duration: float, amplitude: float = 0.5):
        super().__init__(
            event_type=EventType.SOUND_TRIGGERED,
            timestamp=datetime.now(),
            data={"frequency": frequency, "duration": duration, "amplitude": amplitude}
        )
        self.frequency = frequency
        self.duration = duration
        self.amplitude = amplitude


@dataclass
class StateChangeEvent(DomainEvent):
    """Event when state machine changes state"""
    from_state: str
    to_state: str
    reason: Optional[str] = None
    
    def __init__(self, from_state: str, to_state: str, reason: Optional[str] = None):
        super().__init__(
            event_type=EventType.STATE_CHANGED,
            timestamp=datetime.now(),
            data={"from_state": from_state, "to_state": to_state, "reason": reason}
        )
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
