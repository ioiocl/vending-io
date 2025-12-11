# Troubleshooting Guide

Common issues and solutions for Music-IO.

## Installation Issues

### PyAudio Installation Fails

**Windows:**
```bash
# Error: Microsoft Visual C++ required
# Solution: Use pipwin
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
# Error: portaudio.h not found
# Solution: Install system dependencies
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
# Error: portaudio not found
# Solution: Install via Homebrew
brew install portaudio
pip install pyaudio
```

### PySerial Installation Issues

```bash
# If pip install fails
pip install --upgrade pip
pip install pyserial
```

## Arduino Issues

### Arduino Not Detected

**Check USB Connection:**
```bash
# List available serial ports
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

**Windows:**
- Check Device Manager → Ports (COM & LPT)
- Install CH340 driver if using clone board
- Try different USB port
- Use USB 2.0 port (not 3.0)

**Linux:**
```bash
# Check permissions
ls -l /dev/ttyUSB0
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

**macOS:**
```bash
# List ports
ls /dev/tty.*
# Should see something like /dev/tty.usbserial-*
```

### Arduino Upload Fails

1. **Wrong board selected:**
   - Tools → Board → Select your Arduino model

2. **Wrong port selected:**
   - Tools → Port → Select correct COM port

3. **Board in use:**
   - Close Serial Monitor
   - Close Music-IO application
   - Try upload again

4. **Bootloader issue:**
   - Press reset button on Arduino
   - Immediately click Upload

### Sensor Not Working

**Check Wiring:**
```
HC-SR04    Arduino    Check
VCC    →   5V         Red wire, power LED should light
GND    →   GND        Black wire
TRIG   →   Pin 9      Signal wire
ECHO   →   Pin 10     Signal wire
```

**Test Sensor:**
1. Open Serial Monitor (Tools → Serial Monitor)
2. Set baud rate to 9600
3. Should see: `{"distance": XX.X}`
4. Move hand to see values change

**Common Issues:**
- Loose connections → Re-seat wires
- Wrong pins → Double-check pin numbers
- Damaged sensor → Try different sensor
- Interference → Keep away from other electronics

### Erratic Sensor Readings

**Causes:**
- Soft materials (fabric, foam) absorb ultrasound
- Angled surfaces reflect sound away
- Multiple sensors interfering
- Electrical noise

**Solutions:**
- Point sensor at flat, hard surface
- Keep sensor perpendicular to surface
- Increase smoothing samples in Arduino code
- Add capacitor (100µF) across VCC/GND

## Audio Issues

### No Audio Output

**Check System Audio:**
1. Test system audio with other application
2. Check volume is not muted
3. Check correct output device selected

**Test PyAudio:**
```python
import pyaudio
p = pyaudio.PyAudio()
print(p.get_default_output_device_info())
```

**Check Audio Adapter:**
```python
from src.adapters.output.local_audio_adapter import LocalAudioAdapter

adapter = LocalAudioAdapter()
adapter.initialize()
print(adapter.get_output_info())
adapter.test_sound()  # Should hear 440Hz tone
```

### Audio Crackling/Distortion

**Causes:**
- Buffer underrun
- CPU overload
- Sample rate mismatch

**Solutions:**
```python
# Increase buffer size
LocalAudioAdapter(sample_rate=44100)

# Lower sample rate
LocalAudioAdapter(sample_rate=22050)

# Reduce volume
adapter.set_volume(0.5)
```

### Audio Latency

**Reduce latency:**
```python
# Smaller buffer (may cause crackling)
# Edit local_audio_adapter.py
frames_per_buffer=512  # Default is 1024
```

## Application Issues

### "No serial port available"

**Cause:** Arduino not connected or not detected

**Solutions:**
1. Check USB cable connection
2. Install Arduino drivers
3. Manually specify port:
   ```python
   from src.adapters.input.arduino_adapter import ArduinoAdapter
   adapter = ArduinoAdapter(port="COM3", auto_detect=False)
   ```

### "Failed to initialize audio"

**Cause:** Audio device not available

**Solutions:**
1. Close other audio applications
2. Check audio device permissions
3. Restart audio service (Linux):
   ```bash
   pulseaudio --kill
   pulseaudio --start
   ```

### Application Hangs on Start

**Cause:** Waiting for Arduino connection

**Debug:**
```bash
# Run with debug logging
cd src
python -c "import logging; logging.basicConfig(level=logging.DEBUG); from app.main import main; main()"
```

**Solutions:**
1. Check Arduino is connected and running
2. Check correct port specified
3. Increase connection timeout

### No Sound Generated

**Debug Steps:**

1. **Check if events are received:**
   ```python
   # Add logging to state_machine.py
   logger.setLevel(logging.DEBUG)
   ```

2. **Test state machine directly:**
   ```python
   from src.core.domain import MusicStateMachine, ProximityEvent
   
   sm = MusicStateMachine()
   event = ProximityEvent(distance=15.0)
   sound = sm.handle_proximity_event(event)
   print(f"Sound: {sound.frequency}Hz, {sound.duration}s")
   ```

3. **Test audio adapter directly:**
   ```python
   from src.adapters.output.local_audio_adapter import LocalAudioAdapter
   from src.core.domain.events import SoundEvent
   
   adapter = LocalAudioAdapter()
   adapter.initialize()
   sound = SoundEvent(frequency=440, duration=0.5, amplitude=0.5)
   adapter.play_sound(sound)
   ```

## Performance Issues

### High CPU Usage

**Causes:**
- Too frequent sensor readings
- Audio buffer too small
- Logging too verbose

**Solutions:**
1. Increase Arduino measurement interval:
   ```cpp
   // In proximity_sensor.ino
   const int MEASUREMENT_INTERVAL = 100;  // Increase from 50
   ```

2. Reduce logging:
   ```python
   logging.basicConfig(level=logging.INFO)  # Change from DEBUG
   ```

3. Increase audio buffer:
   ```python
   frames_per_buffer=2048  # Increase from 1024
   ```

### Memory Leak

**Check event history:**
```python
# In state_machine.py, limit event history
if len(self.context.event_history) > 100:
    self.context.event_history = self.context.event_history[-100:]
```

## Development Issues

### Import Errors

**Cause:** Python path not set correctly

**Solution:**
```bash
# Always run from src directory
cd src
python -m app.main

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/Music-IO/src"
```

### Module Not Found

**Check installation:**
```bash
pip list | grep -E "pyaudio|pyserial|numpy"
```

**Reinstall if needed:**
```bash
pip install -r requirements.txt --force-reinstall
```

## Testing Issues

### Can't Test Without Hardware

**Use mock adapters:**
```python
from src.app.application import MusicMachineApplication
from src.core.domain.events import ProximityEvent

class MockInputAdapter:
    def start(self): pass
    def stop(self): pass
    def register_callback(self, callback):
        self.callback = callback
    def simulate(self, distance):
        event = ProximityEvent(distance=distance)
        self.callback(event)

class MockOutputAdapter:
    def initialize(self): return True
    def play_sound(self, sound_event):
        print(f"Mock: {sound_event.frequency}Hz")
        return True
    def stop(self): pass

# Test without hardware
app = MusicMachineApplication(
    input_adapter=MockInputAdapter(),
    output_adapter=MockOutputAdapter()
)
```

## Getting Help

### Enable Debug Logging

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check Logs

```bash
# View log file
cat music_machine.log

# Watch logs in real-time
tail -f music_machine.log
```

### System Information

```python
import sys
import platform
print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")

import pyaudio
p = pyaudio.PyAudio()
print(f"PyAudio version: {pyaudio.__version__}")
print(f"Audio devices: {p.get_device_count()}")

import serial
print(f"PySerial version: {serial.__version__}")
```

## Still Having Issues?

1. **Check all connections** - Hardware first
2. **Test components individually** - Isolate the problem
3. **Read the logs** - They contain valuable information
4. **Try the mock adapters** - Rule out hardware issues
5. **Check the documentation** - README.md and ARCHITECTURE.md

## Common Error Messages

### "CreateFile: El sistema no puede encontrar la ruta especificada"
- **Cause:** Serial port doesn't exist
- **Solution:** Check Arduino connection and port name

### "OSError: [Errno -9996] Invalid output device"
- **Cause:** Audio device not available
- **Solution:** Check audio settings, restart audio service

### "serial.serialutil.SerialException: could not open port"
- **Cause:** Port already in use or no permission
- **Solution:** Close other programs using port, check permissions

### "ImportError: No module named 'pyaudio'"
- **Cause:** PyAudio not installed
- **Solution:** Follow PyAudio installation instructions above

---

**Most issues are related to hardware connections or driver installation. Always check the basics first!**
