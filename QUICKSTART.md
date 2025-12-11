# Quick Start Guide

Get Music-IO running in 5 minutes!

## Step 1: Install Python Dependencies

```bash
cd Music-IOpip install -r requirements.txt

```

**Note**: If PyAudio installation fails, see platform-specific instructions in README.md

## Step 2: Set Up Arduino

### Hardware Wiring

Connect HC-SR04 sensor to Arduino:

```
HC-SR04    →    Arduino
VCC        →    5V
GND        →    GND
TRIG       →    Pin 9
ECHO       →    Pin 10
```

### Upload Code

1. Open Arduino IDE
2. Open `arduino/proximity_sensor/proximity_sensor.ino`
3. Select your board: **Tools > Board > Arduino Uno**
4. Select port: **Tools > Port > COM3** (or your port)
5. Click **Upload** (→)

### Verify Arduino

1. Open Serial Monitor: **Tools > Serial Monitor**
2. Set baud rate to **9600**
3. You should see: `{"distance": XX.X}`
4. Move your hand to see values change

## Step 3: Run Music-IO

```bash
cd src
python -m app.main
```

You should see:
```
============================================================
Music Machine is RUNNING!
Move your hand near the proximity sensor to create music
============================================================
```

## Step 4: Make Music!

Move your hand near the sensor:
- **Close (0-10cm)**: High pitched sound
- **Medium (10-30cm)**: Mid pitched sound  
- **Far (30-50cm)**: Low pitched sound
- **Very far (>50cm)**: No sound

## Troubleshooting

### "No serial port available"
- Check USB cable connection
- Try different USB port
- Install CH340 drivers (for clone boards)

### "Failed to initialize audio"
- Check system audio settings
- Close other audio applications
- Try reinstalling PyAudio

### No sound but no errors
- Check system volume
- Test audio with: `app.test_audio()`
- Verify audio device in output info

## Next Steps

- Read `README.md` for detailed documentation
- Read `ARCHITECTURE.md` to understand the design
- Modify `state_machine.py` to change sound mapping
- Add new adapters for different inputs/outputs

## Quick Test

Test without Arduino:

```python
from src.app.application import MusicMachineApplication
from src.core.domain.events import ProximityEvent

app = MusicMachineApplication()
app.output_adapter.initialize()

# Test audio
app.test_audio()

# Simulate proximity event
event = ProximityEvent(distance=15.0)
sound = app.state_machine.handle_proximity_event(event)
app.output_adapter.play_sound(sound)
```

## Common Commands

```bash
# Run application
python -m app.main

# Run with debug logging
python -m app.main --log-level DEBUG

# Check Arduino connection
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

Happy music making! 🎵
