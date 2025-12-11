# Arduino Setup Guide - Dual Controller System

This guide explains how to set up the two Arduino controllers for the Music-IO game system.

## Overview

The system uses **two Arduino boards**:

1. **Arduino MEGA (COM3)** - Servo Controller
   - Controls two 360° continuous rotation servos
   - Activates based on game score
   
2. **Arduino (COM4)** - Button Controller
   - Reads button press to start game
   - Simple joystick button input

## Hardware Requirements

### Arduino 1 - Servo Controller (COM3)
- Arduino MEGA (or Uno)
- 2x 360° Continuous Rotation Servos
- USB cable
- Power supply (if servos draw too much current)

### Arduino 2 - Button Controller (COM4)
- Arduino (any model)
- 1x Push button or Joystick with SW pin
- USB cable

## Wiring Diagrams

### Arduino 1 - Servo Controller (COM3)

```
Servo 1:
  Signal → Pin 9
  VCC    → 5V (or external power)
  GND    → GND

Servo 2:
  Signal → Pin 10
  VCC    → 5V (or external power)
  GND    → GND
```

**Important:** If servos draw too much current, use an external 5V power supply for the servos (connect GND to Arduino GND).

### Arduino 2 - Button Controller (COM4)

```
Button/Joystick:
  SW Pin → Pin 9
  VCC    → 5V
  GND    → GND
```

The button uses `INPUT_PULLUP`, so it's active LOW (pressed = LOW).

## Upload Arduino Code

### Step 1: Upload Servo Controller Code

1. Open Arduino IDE
2. Open `arduino/servo_controller/servo_controller.ino`
3. Select board: **Tools > Board > Arduino Mega** (or Uno)
4. Select port: **Tools > Port > COM3**
5. Click **Upload** (→)
6. Open Serial Monitor (9600 baud) - should see "Servo Controller Ready"

### Step 2: Upload Button Controller Code

1. Open Arduino IDE
2. Open `arduino/button_controller/button_controller.ino`
3. Select board: **Tools > Board > Arduino Uno** (or your board)
4. Select port: **Tools > Port > COM4**
5. Click **Upload** (→)
6. Open Serial Monitor (9600 baud) - should see `{"status": "ready"}`
7. Press button - should see `{"button": "pressed"}`

## How It Works

### Game Flow

1. **Start Game**
   - Press physical button on Arduino 2 (COM4)
   - OR click "Play Again" in web interface
   - Game starts in browser

2. **Play Game**
   - Use keyboard/joystick to jump over pulses
   - Collect items for points
   - Avoid enemies

3. **Game Over**
   - When game ends, final score is sent to Python app
   - Python app sends command to Arduino 1 (COM3)
   - **Score < 10**: LEFT motor activates
   - **Score >= 10**: RIGHT motor activates

### Motor Patterns

**LEFT Motor (Score < 10):**
```
Servo1: Rotate LEFT  (90 - 30 = 60°)
Servo2: Rotate RIGHT (90 + 30 = 120°)
Duration: 5 seconds
Then: Stop (return to 90°)
```

**RIGHT Motor (Score >= 10):**
```
Servo1: Rotate RIGHT (90 + 30 = 120°)
Servo2: Rotate LEFT  (90 - 30 = 60°)
Duration: 5 seconds
Then: Stop (return to 90°)
```

## Serial Communication Protocol

### Servo Controller (COM3)

**Commands sent from Python:**
- `LEFT_MOTOR\n` - Activate left motor pattern
- `RIGHT_MOTOR\n` - Activate right motor pattern
- `STOP\n` - Stop all motors immediately

**Responses from Arduino:**
- `Servo Controller Ready` - On startup
- `LEFT_MOTOR_ACTIVE` - Left motor started
- `RIGHT_MOTOR_ACTIVE` - Right motor started
- `MOTORS_STOPPED` - Motors stopped
- `MOTOR_COMPLETE` - 5-second cycle finished

### Button Controller (COM4)

**Data sent from Arduino (JSON):**
- `{"status": "ready"}` - On startup
- `{"button": "pressed"}` - Button pressed
- `{"button": "released"}` - Button released

## Calibration

### Servo Calibration

If your servos don't stop at neutral position:

1. Edit `arduino/servo_controller/servo_controller.ino`
2. Adjust these values:
   ```cpp
   int neutral1 = 90;   // Change to 88-92 if needed
   int neutral2 = 90;   // Change to 88-92 if needed
   int power = 30;      // Speed (higher = faster)
   ```
3. Re-upload code
4. Test in Serial Monitor: send `LEFT_MOTOR` or `RIGHT_MOTOR`

## Troubleshooting

### Servo Controller Issues

**Servos don't move:**
- Check wiring (signal, VCC, GND)
- Check power supply (servos may need external power)
- Test in Serial Monitor: send `LEFT_MOTOR`
- Verify COM3 is correct port

**Servos jitter at neutral:**
- Adjust `neutral1` and `neutral2` values
- May need values like 88, 89, 91, or 92

**Servos run continuously:**
- These are 360° servos, they should stop at 90°
- If using regular servos, they will try to reach position

### Button Controller Issues

**No button events:**
- Check wiring (SW to Pin 9, GND to GND)
- Verify COM4 is correct port
- Test in Serial Monitor - press button

**Button always pressed:**
- Check if button is wired correctly
- May need to change `INPUT_PULLUP` logic

### Port Detection Issues

**Wrong COM ports:**
1. Open Device Manager (Windows)
2. Expand "Ports (COM & LPT)"
3. Note which Arduino is on which port
4. Update port numbers in Python code if needed:
   ```python
   # In run_with_visualizer.py or application.py
   ButtonAdapter(port="COM4")  # Change if needed
   ServoAdapter(port="COM3")   # Change if needed
   ```

## Testing

### Test Servo Controller Manually

1. Open Serial Monitor on COM3 (9600 baud)
2. Type: `LEFT_MOTOR` and press Enter
3. Servos should move for 5 seconds
4. Type: `RIGHT_MOTOR` and press Enter
5. Servos should move in opposite direction
6. Type: `STOP` to stop immediately

### Test Button Controller Manually

1. Open Serial Monitor on COM4 (9600 baud)
2. Press button
3. Should see: `{"button": "pressed"}`
4. Release button
5. Should see: `{"button": "released"}`

### Test Full System

1. Upload both Arduino codes
2. Connect both Arduinos via USB
3. Run: `python run_with_visualizer.py`
4. Open browser: `http://127.0.0.1:5000/game`
5. Press physical button - game should start
6. Play game until game over
7. Servos should activate based on score

## Code Customization

### Change Motor Duration

Edit `arduino/servo_controller/servo_controller.ino`:
```cpp
unsigned long motorDuration = 5000;  // Change to 3000 for 3 seconds
```

### Change Motor Speed

Edit `arduino/servo_controller/servo_controller.ino`:
```cpp
int power = 30;  // Change to 20 (slower) or 40 (faster)
```

### Change Score Threshold

Edit `src/adapters/output/servo_adapter.py`:
```python
def activate_motor_by_score(self, score: int):
    if score < 10:  # Change threshold here
        return self.activate_left_motor()
    else:
        return self.activate_right_motor()
```

## Safety Notes

- **Power Supply:** Servos can draw significant current. Use external power if needed.
- **Mechanical Safety:** Ensure servos are securely mounted and won't cause injury.
- **Heat:** Continuous rotation servos can get warm. Don't run for extended periods.
- **Testing:** Always test with Serial Monitor before connecting to full system.

## Summary

- **Arduino 1 (COM3)**: Servo controller - activates on game over
- **Arduino 2 (COM4)**: Button controller - starts game
- **Score < 10**: Left motor pattern
- **Score >= 10**: Right motor pattern
- **Duration**: 5 seconds per activation

Happy gaming! 🎮🤖
