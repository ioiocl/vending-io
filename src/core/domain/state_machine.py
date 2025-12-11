"""
State Machine Orchestrator - Core of the Music Machine
This is the heart of the hexagonal architecture
"""
from enum import Enum
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass, field
import logging

from .events import ProximityEvent, SoundEvent, StateChangeEvent, DomainEvent

logger = logging.getLogger(__name__)


class MusicState(Enum):
    """States of the music machine"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    PLAYING = "playing"
    ERROR = "error"


@dataclass
class StateContext:
    """Context information for state transitions"""
    current_state: MusicState
    last_proximity: Optional[float] = None
    last_sound_frequency: Optional[float] = None
    event_history: List[DomainEvent] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class MusicStateMachine:
    """
    State Machine Orchestrator
    Coordinates the flow of events and state transitions
    """
    
    def __init__(self):
        self.context = StateContext(current_state=MusicState.IDLE)
        self._state_handlers: Dict[MusicState, Callable] = {
            MusicState.IDLE: self._handle_idle,
            MusicState.LISTENING: self._handle_listening,
            MusicState.PROCESSING: self._handle_processing,
            MusicState.PLAYING: self._handle_playing,
            MusicState.ERROR: self._handle_error,
        }
        self._event_listeners: List[Callable[[DomainEvent], None]] = []
        logger.info("Music State Machine initialized")
    
    def register_event_listener(self, listener: Callable[[DomainEvent], None]):
        """Register a listener for domain events"""
        self._event_listeners.append(listener)
    
    def _emit_event(self, event: DomainEvent):
        """Emit an event to all listeners"""
        self.context.event_history.append(event)
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
    
    def transition_to(self, new_state: MusicState, reason: Optional[str] = None):
        """Transition to a new state"""
        old_state = self.context.current_state
        if old_state != new_state:
            logger.info(f"State transition: {old_state.value} -> {new_state.value}")
            self.context.current_state = new_state
            event = StateChangeEvent(old_state.value, new_state.value, reason)
            self._emit_event(event)
    
    def handle_proximity_event(self, proximity_event: ProximityEvent) -> Optional[SoundEvent]:
        """
        Main entry point for proximity events
        Returns a SoundEvent if sound should be generated
        """
        logger.info(f"Handling proximity event: {proximity_event.distance}cm")
        self.context.last_proximity = proximity_event.distance
        self._emit_event(proximity_event)
        
        # Transition to listening if idle
        if self.context.current_state == MusicState.IDLE:
            self.transition_to(MusicState.LISTENING, "Proximity detected")
        
        # Process the event
        return self._process_proximity(proximity_event)
    
    def _process_proximity(self, proximity_event: ProximityEvent) -> Optional[SoundEvent]:
        """
        Core business logic: Convert proximity to sound
        Distance mapping: 
        - Close (0-10cm): High frequency (800-1200 Hz)
        - Medium (10-30cm): Mid frequency (400-800 Hz)
        - Far (30-50cm): Low frequency (200-400 Hz)
        - Very far (>50cm): No sound
        """
        distance = proximity_event.distance
        
        if distance > 50:
            self.transition_to(MusicState.IDLE, "Distance too far")
            return None
        
        self.transition_to(MusicState.PROCESSING, "Converting distance to sound")
        
        # Map distance to frequency (inverse relationship)
        # Closer = higher frequency
        if distance <= 10:
            frequency = 1200 - (distance * 40)  # 1200-800 Hz
            amplitude = 0.8
        elif distance <= 30:
            frequency = 800 - ((distance - 10) * 20)  # 800-400 Hz
            amplitude = 0.6
        else:  # 30-50cm
            frequency = 400 - ((distance - 30) * 10)  # 400-200 Hz
            amplitude = 0.4
        
        # Duration based on distance (closer = shorter, more urgent)
        duration = 0.1 + (distance / 100)  # 0.1 to 0.6 seconds
        
        sound_event = SoundEvent(
            frequency=max(200, min(1200, frequency)),
            duration=duration,
            amplitude=amplitude
        )
        
        self.context.last_sound_frequency = sound_event.frequency
        self._emit_event(sound_event)
        
        self.transition_to(MusicState.PLAYING, "Sound generated")
        
        return sound_event
    
    def _handle_idle(self):
        """Handle idle state"""
        pass
    
    def _handle_listening(self):
        """Handle listening state"""
        pass
    
    def _handle_processing(self):
        """Handle processing state"""
        pass
    
    def _handle_playing(self):
        """Handle playing state"""
        # After playing, return to listening
        self.transition_to(MusicState.LISTENING, "Ready for next input")
    
    def _handle_error(self):
        """Handle error state"""
        logger.error("State machine in error state")
        # Could implement recovery logic here
    
    def get_state(self) -> MusicState:
        """Get current state"""
        return self.context.current_state
    
    def get_context(self) -> StateContext:
        """Get current context"""
        return self.context
    
    def reset(self):
        """Reset the state machine"""
        logger.info("Resetting state machine")
        self.transition_to(MusicState.IDLE, "Manual reset")
        self.context.last_proximity = None
        self.context.last_sound_frequency = None
        self.context.metadata.clear()
