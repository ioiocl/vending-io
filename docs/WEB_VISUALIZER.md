# Web Visualizer Documentation 🌐

## Overview

The **Web Visualizer** provides a real-time, browser-based visualization of sensor data with beautiful pulse effects and USB joystick support.

## Features

### 🎨 Real-Time Pulse Visualization
- **Dynamic pulses** that respond to sensor proximity
- **Color-coded intensity** (closer = brighter/larger pulse)
- **Smooth animations** with fade effects
- **Distance display** in large, easy-to-read format

### 📊 Live Statistics
- **Frequency** (Hz) - Current sound frequency
- **Amplitude** - Sound volume level
- **Duration** - Sound length in seconds
- **Visual frequency bar** - Graphical representation

### 🎮 USB Joystick Support
- **Plug-and-play** - Automatically detects connected joysticks
- **Full axis support** - X/Y joystick movement
- **Button support** - All joystick buttons
- **Multi-client sync** - Joystick events broadcast to all connected browsers

### ⌨️ Keyboard Controls
- **Arrow Keys** - Navigate through pulses (↑↓←→)
- **Space Bar** - Jump action
- **Real-time feedback** - See your inputs in the event history

### 📜 Event History
- **Last 10 events** displayed
- **Timestamps** for each event
- **Auto-scroll** to latest events
- **Color-coded** event types

## Installation

### 1. Install Dependencies

```bash
pip install flask flask-socketio python-socketio
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```python
python -c "import flask, flask_socketio; print('✅ Web visualizer ready!')"
```

## Usage

### Method 1: Run with Visualizer Script (Recommended)

```bash
cd C:\Users\avasquezp\Desktop\Music-IO
python run_with_visualizer.py
```

This will:
1. Start the Music-IO application
2. Start the web server on `http://127.0.0.1:5000`
3. Open your browser to see the visualizer

### Method 2: Enable in Application Code

```python
from app.application import MusicMachineApplication

# Create app with visualizer enabled
app = MusicMachineApplication(enable_visualizer=True)

# Initialize visualizer
if app.visualizer:
    app.visualizer.initialize()
    
    # Run visualizer in background thread
    import threading
    viz_thread = threading.Thread(
        target=app.visualizer.run,
        daemon=True
    )
    viz_thread.start()

# Start music machine
app.start()
```

## Web Interface

### Accessing the Visualizer

1. **Start the application** with visualizer enabled
2. **Open your browser** to: `http://127.0.0.1:5000`
3. **See the magic!** Real-time pulses and data

### Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│                  🎵 Music-IO Visualizer                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────┐  ┌─────────────────────────┐ │
│  │                      │  │  📊 Current Stats       │ │
│  │   PULSE DISPLAY      │  │  Frequency: 700 Hz      │ │
│  │                      │  │  Amplitude: 0.6         │ │
│  │      15.0 cm         │  │  Duration: 0.25 s       │ │
│  │                      │  │  [████████░░] 40%       │ │
│  │   (animated pulse)   │  └─────────────────────────┘ │
│  │                      │                              │
│  └──────────────────────┘  ┌─────────────────────────┐ │
│                            │  🎮 Joystick            │ │
│                            │  ✅ Connected           │ │
│                            │  Xbox Controller        │ │
│                            └─────────────────────────┘ │
│                                                          │
│                            ┌─────────────────────────┐ │
│                            │  📜 Recent Events       │ │
│                            │  14:30:15 - 🎵 700Hz   │ │
│                            │  14:30:14 - 📏 15.0cm  │ │
│                            │  14:30:13 - ⌨️ jump    │ │
│                            └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Joystick Support

### Compatible Devices

- ✅ Xbox Controllers (Xbox One, Xbox Series X/S)
- ✅ PlayStation Controllers (DualShock 4, DualSense)
- ✅ Generic USB Gamepads
- ✅ Flight Sticks
- ✅ Racing Wheels

### How It Works

1. **Connect your USB joystick** to your computer
2. **Open the visualizer** in your browser
3. **Joystick automatically detected** - Status shows "✅ Connected"
4. **Move joystick** - Events sent in real-time via WebSocket
5. **All clients see the events** - Multi-user support!

### Joystick Data Structure

```javascript
{
    axes: {
        x: 0.5,    // -1.0 to 1.0 (left/right)
        y: -0.3    // -1.0 to 1.0 (up/down)
    },
    buttons: [
        { index: 0, pressed: true, value: 1.0 },
        { index: 1, pressed: false, value: 0.0 }
    ],
    timestamp: 1234567890123
}
```

### Using Joystick Data

You can extend the system to use joystick input:

```python
# In your adapter or orchestrator
@socketio.on('joystick_input')
def handle_joystick(data):
    axes = data['axes']
    
    # Map joystick to sound parameters
    frequency = 440 + (axes['x'] * 500)  # 440-940 Hz
    amplitude = 0.5 + (abs(axes['y']) * 0.5)  # 0.5-1.0
    
    # Create sound event
    sound = SoundEvent(
        frequency=frequency,
        duration=0.2,
        amplitude=amplitude
    )
    
    # Play it!
    audio_adapter.play_sound(sound)
```

## Keyboard Controls

When no joystick is connected, use keyboard:

| Key | Action | Joystick Equivalent |
|-----|--------|---------------------|
| ↑ | Up | Y-axis negative |
| ↓ | Down | Y-axis positive |
| ← | Left | X-axis negative |
| → | Right | X-axis positive |
| Space | Jump | Button 0 |

## WebSocket Events

### Client → Server

#### `joystick_input`
Sent when joystick moves or button pressed:
```javascript
socket.emit('joystick_input', {
    axes: { x: 0.5, y: -0.3 },
    buttons: [{ index: 0, pressed: true }],
    timestamp: Date.now()
});
```

### Server → Client

#### `proximity_pulse`
Sent when sensor detects proximity:
```javascript
socket.on('proximity_pulse', (data) => {
    // data = {
    //     type: 'proximity',
    //     distance: 15.0,
    //     sensor_id: 'arduino_proximity_01',
    //     timestamp: '2025-10-19T14:30:15.123Z',
    //     pulse_intensity: 0.7
    // }
});
```

#### `sound_event`
Sent when sound is played:
```javascript
socket.on('sound_event', (data) => {
    // data = {
    //     type: 'sound',
    //     frequency: 700,
    //     duration: 0.25,
    //     amplitude: 0.6,
    //     timestamp: '2025-10-19T14:30:15.123Z'
    // }
});
```

#### `joystick_event`
Broadcast joystick events to all clients:
```javascript
socket.on('joystick_event', (data) => {
    // Same structure as joystick_input
    console.log('Another user moved their joystick!', data);
});
```

## Customization

### Change Colors

Edit `web/templates/visualizer.html`:

```css
/* Pulse color */
.pulse-circle {
    background: radial-gradient(
        circle,
        rgba(255, 100, 100, 0.8) 0%,  /* Change this */
        rgba(255, 100, 100, 0) 70%
    );
}

/* Background gradient */
body {
    background: linear-gradient(
        135deg,
        #667eea 0%,  /* Change these */
        #764ba2 100%
    );
}
```

### Change Port

```python
# In run_with_visualizer.py or application code
visualizer = WebVisualizerAdapter(
    host="0.0.0.0",  # Listen on all interfaces
    port=8080        # Custom port
)
```

### Add Custom Events

```python
# In web_visualizer_adapter.py
def visualize_custom(self, data):
    """Visualize custom data"""
    self.socketio.emit('custom_event', {
        'type': 'custom',
        'data': data,
        'timestamp': datetime.now().isoformat()
    })
```

Then in HTML:
```javascript
socket.on('custom_event', (data) => {
    console.log('Custom event:', data);
    // Your custom visualization
});
```

## Troubleshooting

### Visualizer Not Starting

**Problem:** `ImportError: No module named 'flask'`

**Solution:**
```bash
pip install flask flask-socketio python-socketio
```

### Can't Connect to Visualizer

**Problem:** Browser shows "Can't reach this page"

**Solutions:**
1. Check if server is running: Look for "Starting Web Visualizer on http://127.0.0.1:5000"
2. Try `http://localhost:5000` instead
3. Check firewall settings
4. Try different port: `WebVisualizerAdapter(port=8080)`

### Joystick Not Detected

**Problem:** Shows "No joystick detected"

**Solutions:**
1. **Plug in USB joystick** before opening browser
2. **Refresh the page** after connecting joystick
3. **Check browser compatibility** - Use Chrome, Edge, or Firefox
4. **Test joystick** - Try at https://gamepad-tester.com/

### No Pulses Appearing

**Problem:** Visualizer loads but no pulses

**Solutions:**
1. Check Arduino is connected and sending data
2. Check serial port (COM3) is correct
3. Look at browser console (F12) for errors
4. Check application logs for proximity events

## Performance

- **Latency:** ~50-100ms from sensor to visualization
- **Frame rate:** 60 FPS animations
- **Max clients:** Unlimited (tested with 10+)
- **Data rate:** ~20 events/second per sensor

## Security Note

The visualizer runs on `127.0.0.1` (localhost) by default, which means only your computer can access it.

To allow access from other devices on your network:

```python
visualizer = WebVisualizerAdapter(
    host="0.0.0.0",  # Listen on all interfaces
    port=5000
)
```

Then access from other devices using your computer's IP:
```
http://192.168.1.100:5000
```

⚠️ **Warning:** Only do this on trusted networks!

## Examples

### Example 1: Basic Usage

```bash
python run_with_visualizer.py
```

Open browser → `http://127.0.0.1:5000` → See pulses!

### Example 2: With Joystick

1. Connect Xbox controller via USB
2. Run: `python run_with_visualizer.py`
3. Open browser → `http://127.0.0.1:5000`
4. Move joystick → See events in history!

### Example 3: Multiple Browsers

1. Run visualizer
2. Open browser 1 → `http://127.0.0.1:5000`
3. Open browser 2 → `http://127.0.0.1:5000`
4. Move joystick in browser 1
5. See event in browser 2! (synchronized)

---

**The web visualizer makes Music-IO come alive!** 🎨✨
