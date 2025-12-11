"""
Adapters - Implementations of ports
These connect the core domain to the outside world
"""
from adapters.input.arduino_adapter import ArduinoAdapter
from adapters.output.local_audio_adapter import LocalAudioAdapter

__all__ = [
    'ArduinoAdapter',
    'LocalAudioAdapter',
]
