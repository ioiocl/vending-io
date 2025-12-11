"""
Game Events - Domain events for game mechanics
"""
from dataclasses import dataclass
from datetime import datetime
from .events import DomainEvent, EventType


@dataclass
class CollectibleSpawnEvent(DomainEvent):
    """Event when a collectible item spawns"""
    position_x: float
    position_y: float
    item_type: str
    value: int
    
    def __post_init__(self):
        if not hasattr(self, 'event_type'):
            self.event_type = EventType.STATE_CHANGE
        if not hasattr(self, 'timestamp'):
            self.timestamp = datetime.now()


@dataclass
class CollectibleCollectedEvent(DomainEvent):
    """Event when player collects an item"""
    item_id: str
    item_type: str
    value: int
    player_score: int
    
    def __post_init__(self):
        if not hasattr(self, 'event_type'):
            self.event_type = EventType.STATE_CHANGE
        if not hasattr(self, 'timestamp'):
            self.timestamp = datetime.now()


@dataclass
class HandGestureEvent(DomainEvent):
    """Event when hand gesture is detected"""
    gesture_type: str  # 'hand_raised', 'hand_lowered', etc.
    hand_position: tuple  # (x, y) normalized
    confidence: float
    
    def __post_init__(self):
        if not hasattr(self, 'event_type'):
            self.event_type = EventType.PROXIMITY
        if not hasattr(self, 'timestamp'):
            self.timestamp = datetime.now()
