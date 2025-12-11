"""
Input Port - Interface for all input adapters
This defines the contract that all input adapters must follow
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional
from ..domain.events import ProximityEvent


class InputPort(ABC):
    """
    Abstract base class for input adapters
    Any input source (Arduino, sensors, web APIs, blockchain events, etc.)
    must implement this interface
    """
    
    @abstractmethod
    def start(self):
        """Start listening for input"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop listening for input"""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if the input adapter is running"""
        pass
    
    @abstractmethod
    def register_callback(self, callback: Callable[[ProximityEvent], None]):
        """
        Register a callback to be called when input is received
        The callback receives a ProximityEvent (or other event types in the future)
        """
        pass


class SensorInputPort(InputPort):
    """
    Specialized input port for sensor data
    This can be extended for different sensor types
    """
    
    @abstractmethod
    def get_sensor_info(self) -> dict:
        """Get information about the connected sensor"""
        pass
    
    @abstractmethod
    def calibrate(self) -> bool:
        """Calibrate the sensor if needed"""
        pass
