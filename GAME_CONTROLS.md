# Game Controls & System Overview

## Quick Start

1. **Upload Arduino Code**
   - Upload `arduino/servo_controller/servo_controller.ino` to Arduino MEGA (COM3)
   - Upload `arduino/button_controller/button_controller.ino` to Arduino (COM4)

2. **Run Application**
   ```bash
   python run_with_visualizer.py
   ```

3. **Open Game**
   - Browser: `http://127.0.0.1:5000/game`

4. **Play**
   - Press physical button to start
   - Use keyboard/joystick to play
   - Servos activate when game ends

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MUSIC-IO GAME SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Arduino 2 (COM4)          Python App          Arduino 1    │
│  ┌──────────────┐         ┌──────────┐        (COM3)        │
│  │   BUTTON     │────────▶│  Button  │      ┌──────────┐   │
│  │ Controller   │  JSON   │ Adapter  │      │  Servo   │   │
│  └──────────────┘         └────┬─────┘      │Controller│   │
│                                │             └────▲─────┘   │
│                                ▼                  │         │
│                          ┌──────────┐             │         │
│                          │   Game   │             │         │
│  Web Browser             │  Logic   │             │         │
│  ┌──────────────┐        └────┬─────┘             │         │
│  │  Game UI     │◀────────────┤                   │         │
│  │  Visualizer  │             │                   │         │
│  └──────┬───────┘             │                   │         │
│         │                     │                   │         │
│         └─────────────────────┴───────────────────┘         │
│              WebSocket (game over + score)                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Game Controls

### Physical Controls
- **Button (Arduino COM4)**: Start/Restart game

### Keyboard Controls
- **Arrow Keys**: Move player left/right
- **Space**: Jump
- **W/A/S/D**: Alternative movement

### USB Joystick (Auto-detected)
- **Left Stick**: Move player
- **Button 0**: Jump

## Game Mechanics

### Objective
Survive for 60 seconds while jumping over pulses and avoiding enemies.

### Scoring
- **Jump over pulse**: +10 points (x combo multiplier)
- **Collect item**: +5 points
- **Kill enemy**: +25 points
- **Combo**: Increases with consecutive jumps

### Game Over Conditions
- **Death**: Hit by pulse or enemy
- **Victory**: Survive 60 seconds

## Servo Motor Behavior

### When Game Ends

**Score < 10 points:**
- LEFT motor activates
- Servo1 rotates LEFT (60°)
- Servo2 rotates RIGHT (120°)
- Duration: 5 seconds
- Then stops

**Score >= 10 points:**
- RIGHT motor activates
- Servo1 rotates RIGHT (120°)
- Servo2 rotates LEFT (60°)
- Duration: 5 seconds
- Then stops

### Motor Pattern Visualization

```
Score < 10 (LEFT MOTOR):
  Servo1: ←←← (LEFT)
  Servo2: →→→ (RIGHT)
  
Score >= 10 (RIGHT MOTOR):
  Servo1: →→→ (RIGHT)
  Servo2: ←←← (LEFT)
```

## Event Flow

### Game Start Flow
```
1. Player presses button (Arduino COM4)
   ↓
2. Button sends JSON: {"button": "pressed"}
   ↓
3. Python receives event
   ↓
4. Python emits 'game_start_trigger' to web
   ↓
5. Web browser restarts game
```

### Game Over Flow
```
1. Player dies or wins in browser
   ↓
2. Browser emits 'game_over' with score
   ↓
3. Python receives event with score
   ↓
4. Python checks score:
   - If score < 10: Send "LEFT_MOTOR" to COM3
   - If score >= 10: Send "RIGHT_MOTOR" to COM3
   ↓
5. Arduino activates servos for 5 seconds
   ↓
6. Arduino sends "MOTOR_COMPLETE"
   ↓
7. Servos stop
```

## Serial Communication

### Arduino 1 (COM3) - Servo Controller

**Commands (Python → Arduino):**
```
LEFT_MOTOR\n   → Activate left motor pattern
RIGHT_MOTOR\n  → Activate right motor pattern
STOP\n         → Stop all motors
```

**Responses (Arduino → Python):**
```
Servo Controller Ready
LEFT_MOTOR_ACTIVE
RIGHT_MOTOR_ACTIVE
MOTORS_STOPPED
MOTOR_COMPLETE
```

### Arduino 2 (COM4) - Button Controller

**Data (Arduino → Python):**
```json
{"status": "ready"}
{"button": "pressed"}
{"button": "released"}
```

## Web Interface

### Main Dashboard
- URL: `http://127.0.0.1:5000`
- Shows real-time sensor data
- Pulse visualization

### Game Interface
- URL: `http://127.0.0.1:5000/game`
- Full game with score tracking
- Real-time updates via WebSocket

## Customization

### Change Score Threshold

Edit `src/adapters/output/servo_adapter.py`:
```python
def activate_motor_by_score(self, score: int):
    if score < 10:  # Change this number
        return self.activate_left_motor()
    else:
        return self.activate_right_motor()
```

### Change Motor Duration

Edit `arduino/servo_controller/servo_controller.ino`:
```cpp
unsigned long motorDuration = 5000;  // milliseconds
```

### Change Motor Speed

Edit `arduino/servo_controller/servo_controller.ino`:
```cpp
int power = 30;  // 0-90 (higher = faster)
```

## Troubleshooting

### Button doesn't start game
1. Check Arduino COM4 is connected
2. Check Serial Monitor shows button presses
3. Verify Python app is running
4. Check browser console for WebSocket connection

### Servos don't activate
1. Check Arduino COM3 is connected
2. Verify servos are powered
3. Test manually in Serial Monitor: send `LEFT_MOTOR`
4. Check Python logs for servo commands

### Game doesn't respond
1. Check browser console for errors
2. Verify WebSocket connection (green dot)
3. Refresh browser page
4. Restart Python app

## File Reference

### Arduino Code
- `arduino/servo_controller/servo_controller.ino` - Servo control (COM3)
- `arduino/button_controller/button_controller.ino` - Button input (COM4)

### Python Adapters
- `src/adapters/input/button_adapter.py` - Button input handler
- `src/adapters/output/servo_adapter.py` - Servo control handler
- `src/app/application.py` - Main application logic

### Web Interface
- `web/templates/game_visualizer.html` - Game UI
- `src/adapters/output/web_visualizer_adapter.py` - WebSocket server

## Tips

- **Test Arduinos separately** before running full system
- **Use Serial Monitor** to debug communication
- **Check COM ports** in Device Manager if connection fails
- **External power** may be needed for servos
- **Calibrate servos** if they don't stop at neutral

## Summary

1. **Button press** → Starts game
2. **Play game** → Earn score
3. **Game over** → Servo activates based on score
4. **Score < 10** → LEFT motor
5. **Score >= 10** → RIGHT motor

Enjoy! 🎮🤖🎵
