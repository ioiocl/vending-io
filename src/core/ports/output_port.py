"""
Output Port - Interface for all output adapters
This defines the contract that all output adapters must follow
"""
from abc import ABC, abstractmethod
from ..domain.events import SoundEvent


class OutputPort(ABC):
    """
    Abstract base class for output adapters
    Any output destination (local audio, Ableton, SuperCollider, visual server, etc.)
    must implement this interface
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the output system"""
        pass
    
    @abstractmethod
    def play_sound(self, sound_event: SoundEvent) -> bool:
        """
        Play a sound based on the sound event
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def stop(self):
        """Stop all sound output"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the output system is available and ready"""
        pass
    
    @abstractmethod
    def get_output_info(self) -> dict:
        """Get information about the output system"""
        pass


class AudioOutputPort(OutputPort):
    """
    Specialized output port for audio
    """
    
    @abstractmethod
    def set_volume(self, volume: float):
        """Set the master volume (0.0 to 1.0)"""
        pass
    
    @abstractmethod
    def get_volume(self) -> float:
        """Get the current master volume"""
        pass


class VisualizationOutputPort(ABC):
    """
    Port for visualization output
    Used for web visualizers, dashboards, etc.
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the visualization system"""
        pass
    
    @abstractmethod
    def visualize_proximity(self, proximity_event):
        """Visualize a proximity event"""
        pass
    
    @abstractmethod
    def visualize_sound(self, sound_event: SoundEvent):
        """Visualize a sound event"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the visualization"""
        pass
    
    @abstractmethod
    def get_output_info(self) -> dict:
        """Get information about the visualization system"""
        pass
