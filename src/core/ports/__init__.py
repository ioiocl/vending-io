"""
Ports - Interfaces for adapters
These define the contracts between the core domain and the outside world
"""
from .input_port import InputPort, SensorInputPort
from .output_port import OutputPort, AudioOutputPort

__all__ = [
    'InputPort',
    'SensorInputPort',
    'OutputPort',
    'AudioOutputPort',
]
