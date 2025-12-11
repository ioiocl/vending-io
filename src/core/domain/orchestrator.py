"""
Sound Orchestrator - Coordinates and synchronizes multiple sounds
This is the conductor of the music machine
"""
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import threading
import logging

from .events import SoundEvent, ProximityEvent, DomainEvent
from .state_machine import MusicStateMachine

logger = logging.getLogger(__name__)


@dataclass
class SoundTrack:
    """Represents an active sound track"""
    sound_event: SoundEvent
    start_time: datetime
    track_id: str
    priority: int = 0
    source: str = "unknown"  # Which input generated this sound
    
    def is_expired(self) -> bool:
        """Check if the sound has finished playing"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed >= self.sound_event.duration


class SoundOrchestrator:
    """
    Sound Orchestrator - The conductor of the music machine
    
    Responsibilities:
    - Manage multiple simultaneous sounds
    - Coordinate multiple input sources (sensors, MIDI, etc.)
    - Apply musical patterns and rules
    - Prioritize and mix sounds
    - Temporal synchronization
    
    This is the CORE of the hexagonal architecture
    """
    
    def __init__(self, max_simultaneous_sounds: int = 8):
        """
        Initialize the orchestrator
        
        Args:
            max_simultaneous_sounds: Maximum number of sounds playing at once
        """
        self.max_simultaneous_sounds = max_simultaneous_sounds
        self.active_tracks: Dict[str, SoundTrack] = {}
        self._lock = threading.Lock()
        
        # State machines for different input sources
        self.state_machines: Dict[str, MusicStateMachine] = {
            "default": MusicStateMachine()
        }
        
        # Configuration
        self.master_volume = 1.0
        self.mix_mode = "additive"  # "additive", "priority", "layered"
        self.tempo_bpm: Optional[int] = None
        
        # Event listeners
        self._event_listeners: List[Callable[[DomainEvent], None]] = []
        
        logger.info("Sound Orchestrator initialized")
    
    def register_event_listener(self, listener: Callable[[DomainEvent], None]):
        """Register a listener for orchestrator events"""
        self._event_listeners.append(listener)
    
    def _emit_event(self, event: DomainEvent):
        """Emit an event to all listeners"""
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
    
    def register_input_source(self, source_id: str):
        """
        Register a new input source (sensor, MIDI, etc.)
        Each source gets its own state machine
        
        Args:
            source_id: Unique identifier for the input source
        """
        if source_id not in self.state_machines:
            self.state_machines[source_id] = MusicStateMachine()
            logger.info(f"Registered input source: {source_id}")
    
    def process_proximity_event(
        self, 
        proximity_event: ProximityEvent,
        source_id: str = "default"
    ) -> List[SoundEvent]:
        """
        Process a proximity event and generate orchestrated sounds
        
        Args:
            proximity_event: Proximity event from sensor
            source_id: Which input source generated this event
        
        Returns:
            List of sound events to play (mixed)
        """
        logger.debug(f"Orchestrator processing proximity: {proximity_event.distance}cm from {source_id}")
        
        # Get or create state machine for this source
        if source_id not in self.state_machines:
            self.register_input_source(source_id)
        
        state_machine = self.state_machines[source_id]
        
        # Generate sound from state machine
        sound_event = state_machine.handle_proximity_event(proximity_event)
        
        if sound_event:
            # Add to orchestrator
            track_id = f"{source_id}_{datetime.now().timestamp()}"
            self.add_sound(sound_event, track_id, priority=5, source=source_id)
        
        # Clean up expired tracks
        self._cleanup_expired_tracks()
        
        # Return all active sounds for mixing
        return self.get_active_sounds()
    
    def add_sound(
        self, 
        sound_event: SoundEvent, 
        track_id: str, 
        priority: int = 0,
        source: str = "unknown"
    ) -> bool:
        """
        Add a sound to the orchestrator
        
        Args:
            sound_event: Sound event to play
            track_id: Unique identifier for this track
            priority: Priority level (higher = more important)
            source: Which input source generated this sound
        
        Returns:
            True if sound was added successfully
        """
        with self._lock:
            # Check if we're at capacity
            if len(self.active_tracks) >= self.max_simultaneous_sounds:
                if not self._make_room_for_priority(priority):
                    logger.warning(f"Cannot add sound {track_id}: orchestrator at capacity")
                    return False
            
            # Create track
            track = SoundTrack(
                sound_event=sound_event,
                start_time=datetime.now(),
                track_id=track_id,
                priority=priority,
                source=source
            )
            
            self.active_tracks[track_id] = track
            logger.debug(f"Added sound track: {track_id} ({sound_event.frequency}Hz, priority={priority})")
            return True
    
    def _make_room_for_priority(self, new_priority: int) -> bool:
        """
        Make room for a higher priority sound by removing lower priority ones
        
        Args:
            new_priority: Priority of the new sound
        
        Returns:
            True if room was made
        """
        if not self.active_tracks:
            return False
        
        # Find lowest priority track
        lowest_priority_track = min(
            self.active_tracks.values(),
            key=lambda t: t.priority
        )
        
        # Only remove if new sound has higher priority
        if lowest_priority_track.priority < new_priority:
            logger.debug(f"Removing lower priority track: {lowest_priority_track.track_id}")
            del self.active_tracks[lowest_priority_track.track_id]
            return True
        
        return False
    
    def remove_sound(self, track_id: str):
        """Remove a sound from the orchestrator"""
        with self._lock:
            if track_id in self.active_tracks:
                del self.active_tracks[track_id]
                logger.debug(f"Removed sound track: {track_id}")
    
    def _cleanup_expired_tracks(self):
        """Remove tracks that have finished playing"""
        with self._lock:
            expired_tracks = [
                track_id for track_id, track in self.active_tracks.items()
                if track.is_expired()
            ]
            
            for track_id in expired_tracks:
                del self.active_tracks[track_id]
                logger.debug(f"Cleaned up expired track: {track_id}")
    
    def get_active_sounds(self) -> List[SoundEvent]:
        """
        Get all currently active sounds for mixing
        
        Returns:
            List of SoundEvents to play simultaneously
        """
        with self._lock:
            sounds = [track.sound_event for track in self.active_tracks.values()]
            
            # Apply mixing rules based on mode
            if self.mix_mode == "priority":
                # Only return highest priority sound
                if self.active_tracks:
                    highest_priority_track = max(
                        self.active_tracks.values(),
                        key=lambda t: t.priority
                    )
                    return [highest_priority_track.sound_event]
                return []
            
            elif self.mix_mode == "additive":
                # Return all sounds (will be mixed additively)
                return sounds
            
            elif self.mix_mode == "layered":
                # Return sounds with volume adjustment for layering
                for sound in sounds:
                    # Reduce volume when multiple sounds playing
                    sound.amplitude *= (1.0 / max(1, len(sounds)))
                return sounds
            
            return sounds
    
    def clear_all(self):
        """Stop all sounds"""
        with self._lock:
            count = len(self.active_tracks)
            self.active_tracks.clear()
            logger.info(f"Cleared all sounds ({count} tracks)")
    
    def set_mix_mode(self, mode: str):
        """
        Set the mixing mode
        
        Args:
            mode: "additive", "priority", or "layered"
        """
        if mode in ["additive", "priority", "layered"]:
            self.mix_mode = mode
            logger.info(f"Mix mode set to: {mode}")
        else:
            logger.warning(f"Invalid mix mode: {mode}")
    
    def set_tempo(self, bpm: int):
        """
        Set the tempo for synchronization
        
        Args:
            bpm: Beats per minute
        """
        self.tempo_bpm = bpm
        logger.info(f"Tempo set to: {bpm} BPM")
    
    def get_status(self) -> dict:
        """Get orchestrator status"""
        with self._lock:
            return {
                "active_tracks": len(self.active_tracks),
                "max_tracks": self.max_simultaneous_sounds,
                "mix_mode": self.mix_mode,
                "tempo_bpm": self.tempo_bpm,
                "master_volume": self.master_volume,
                "input_sources": list(self.state_machines.keys()),
                "tracks": [
                    {
                        "track_id": track.track_id,
                        "frequency": track.sound_event.frequency,
                        "priority": track.priority,
                        "source": track.source,
                        "age_seconds": (datetime.now() - track.start_time).total_seconds()
                    }
                    for track in self.active_tracks.values()
                ]
            }
    
    def apply_harmony(self, base_frequency: float) -> List[SoundEvent]:
        """
        Generate harmonic sounds based on a base frequency
        
        Args:
            base_frequency: Base frequency in Hz
        
        Returns:
            List of harmonic sound events
        """
        # Generate major triad (1, 5/4, 3/2)
        harmonics = [
            base_frequency,           # Root
            base_frequency * 5/4,     # Major third
            base_frequency * 3/2,     # Perfect fifth
        ]
        
        sound_events = []
        for i, freq in enumerate(harmonics):
            sound_event = SoundEvent(
                frequency=freq,
                duration=0.5,
                amplitude=0.3 / (i + 1)  # Reduce volume for higher harmonics
            )
            sound_events.append(sound_event)
            
            # Add to orchestrator
            track_id = f"harmony_{i}_{datetime.now().timestamp()}"
            self.add_sound(sound_event, track_id, priority=3, source="harmony_generator")
        
        logger.info(f"Generated harmony for {base_frequency}Hz")
        return sound_events
    
    def reset(self):
        """Reset the orchestrator"""
        logger.info("Resetting orchestrator")
        self.clear_all()
        for state_machine in self.state_machines.values():
            state_machine.reset()
