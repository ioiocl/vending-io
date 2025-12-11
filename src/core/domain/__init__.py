"""
Core Domain - Business Logic and State Machine
This is the center of the hexagonal architecture
"""
from .events import (
    DomainEvent,
    EventType,
    ProximityEvent,
    SoundEvent,
    StateChangeEvent
)
from .state_machine import MusicStateMachine, MusicState, StateContext
from .orchestrator import SoundOrchestrator, SoundTrack

__all__ = [
    'DomainEvent',
    'EventType',
    'ProximityEvent',
    'SoundEvent',
    'StateChangeEvent',
    'MusicStateMachine',
    'MusicState',
    'StateContext',
    'SoundOrchestrator',
    'SoundTrack',
]
