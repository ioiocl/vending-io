"""
Local Audio Output Adapter
Plays sound locally using PyAudio and NumPy
"""
import numpy as np
import pyaudio
import threading
import logging
from typing import Optional
import queue

from core.ports.output_port import AudioOutputPort
from core.domain.events import SoundEvent

logger = logging.getLogger(__name__)


class LocalAudioAdapter(AudioOutputPort):
    """
    Adapter for local audio output
    Uses PyAudio to generate and play tones
    """
    
    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        """
        Initialize local audio adapter
        
        Args:
            sample_rate: Audio sample rate in Hz (default 44100)
            channels: Number of audio channels (1=mono, 2=stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.pyaudio_instance: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self._master_volume = 0.7
        self._initialized = False
        self._sound_queue = queue.Queue()
        self._playback_thread: Optional[threading.Thread] = None
        self._running = False
        
    def initialize(self) -> bool:
        """Initialize PyAudio"""
        try:
            logger.info("Initializing local audio output")
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024
            )
            
            self._initialized = True
            self._running = True
            
            # Start playback thread
            self._playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self._playback_thread.start()
            
            logger.info("Local audio output initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            self._initialized = False
            return False
    
    def play_sound(self, sound_event: SoundEvent) -> bool:
        """
        Play a sound based on the sound event
        Generates a sine wave tone
        """
        if not self._initialized:
            logger.error("Audio not initialized")
            return False
        
        try:
            logger.debug(f"Playing sound: {sound_event.frequency}Hz for {sound_event.duration}s")
            
            # Add to queue for playback
            self._sound_queue.put(sound_event)
            return True
            
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
            return False
    
    def _playback_loop(self):
        """Background thread for playing sounds"""
        logger.info("Audio playback loop started")
        
        while self._running:
            try:
                # Get sound event from queue (with timeout)
                sound_event = self._sound_queue.get(timeout=0.1)
                self._generate_and_play(sound_event)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in playback loop: {e}")
    
    def _generate_and_play(self, sound_event: SoundEvent):
        """Generate and play a tone"""
        try:
            # Calculate number of samples
            num_samples = int(self.sample_rate * sound_event.duration)
            
            # Generate time array
            t = np.linspace(0, sound_event.duration, num_samples, False)
            
            # Generate sine wave
            frequency = sound_event.frequency
            amplitude = sound_event.amplitude * self._master_volume
            
            # Create tone with envelope to avoid clicks
            tone = amplitude * np.sin(2 * np.pi * frequency * t)
            
            # Apply fade in/out envelope to prevent clicks
            fade_samples = int(self.sample_rate * 0.01)  # 10ms fade
            if num_samples > fade_samples * 2:
                # Fade in
                fade_in = np.linspace(0, 1, fade_samples)
                tone[:fade_samples] *= fade_in
                
                # Fade out
                fade_out = np.linspace(1, 0, fade_samples)
                tone[-fade_samples:] *= fade_out
            
            # Convert to float32
            audio_data = tone.astype(np.float32)
            
            # Play audio
            if self.stream and self.stream.is_active():
                self.stream.write(audio_data.tobytes())
                
        except Exception as e:
            logger.error(f"Error generating/playing tone: {e}")
    
    def stop(self):
        """Stop audio output"""
        logger.info("Stopping local audio output")
        self._running = False
        
        if self._playback_thread:
            self._playback_thread.join(timeout=2)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        
        self._initialized = False
        logger.info("Local audio output stopped")
    
    def is_available(self) -> bool:
        """Check if audio is available"""
        return self._initialized and self.stream is not None and self.stream.is_active()
    
    def get_output_info(self) -> dict:
        """Get audio output information"""
        info = {
            "type": "Local Audio Output",
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "master_volume": self._master_volume,
            "status": "initialized" if self._initialized else "not initialized",
            "available": self.is_available()
        }
        
        if self.pyaudio_instance:
            try:
                default_output = self.pyaudio_instance.get_default_output_device_info()
                info["device"] = default_output.get('name', 'Unknown')
            except:
                info["device"] = "Unknown"
        
        return info
    
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self._master_volume = max(0.0, min(1.0, volume))
        logger.info(f"Master volume set to {self._master_volume}")
    
    def get_volume(self) -> float:
        """Get current master volume"""
        return self._master_volume
    
    def test_sound(self, frequency: float = 440.0, duration: float = 0.5):
        """Play a test sound (A4 note by default)"""
        test_event = SoundEvent(frequency=frequency, duration=duration, amplitude=0.5)
        return self.play_sound(test_event)
