# 🎮 Button & Servo Test Guide

## Overview
This guide helps you test the complete flow:
**Button Press (COM7) → Game Start → Game Over → Servo Activation (COM4)**

---

## 🔧 Hardware Setup

### Required Connections:
1. **Button Controller** → COM7 (Arduino with button on pin 9)
2. **Servo Controller** → COM4 (Arduino with 2 servos on pins 9 & 10)

### Verify Connections:
```bash
python check_ports.py
```

---

## 🧪 Test 1: Button Reading (COM7)

### Test the button is sending signals:
```bash
python simple_button_test.py
```

### What to expect:
- ✅ Connection to COM7
- ✅ Arduino initialization message
- ✅ When you press the button:
  ```
  [HH:MM:SS] RAW: {"button": "pressed"}
             ✅ BUTTON PRESSED (Count: 1)
             🎮 This should START THE GAME!
  ```
- ✅ When you release:
  ```
  [HH:MM:SS] RAW: {"button": "released"}
             ⚪ Button released (Count: 1)
  ```

### Troubleshooting:
- **No connection?** Check Arduino is on COM7 in Device Manager
- **No output?** Verify `button_controller.ino` is uploaded to Arduino
- **Wrong format?** Arduino should send JSON: `{"button": "pressed"}`

---

## 🧪 Test 2: Servo Control (COM4)

### Test servos with different scores:
```bash
python test_servo.py
```

### What to expect:
1. **Web console opens** at http://localhost:5001
2. **Tests 4 scores**: 5, 15, 3, 25
3. **Score < 10** (5, 3):
   - ⬅️ LEFT motor (servo1) moves
   - ➡️ RIGHT motor (servo2) stays neutral
4. **Score ≥ 10** (15, 25):
   - ⬅️ LEFT motor (servo1) stays neutral
   - ➡️ RIGHT motor (servo2) moves

### Visual Indicators:
- **Python Console**: Detailed logs with timestamps
- **Web Console**: Real-time updates with color-coded logs
- **Servo Indicators**: Pulse animation when active

### Troubleshooting:
- **Both motors moving?** Re-upload `servo_controller.ino` to Arduino
- **No movement?** Check servo power supply
- **Wrong motor?** Verify servo connections (pin 9 = LEFT, pin 10 = RIGHT)

---

## 🎮 Test 3: Full Game Integration

### Run the complete system:
```bash
python run_with_visualizer.py
```

### What to expect:
1. **System starts** with both COM7 (button) and COM4 (servo)
2. **Open browser** to http://127.0.0.1:5000/game
3. **Press physical button** on COM7 Arduino
4. **Game starts** in browser
5. **Play the game** (survive 60 seconds or get killed)
6. **Game ends** → Servo activates based on final score

### Complete Flow:
```
Button Press (COM7)
    ↓
Game Starts (Web Browser)
    ↓
Play Game (Arrow keys / Joystick)
    ↓
Game Over (Death or Victory)
    ↓
Servo Activates (COM4)
    ├─ Score < 10  → LEFT motor moves
    └─ Score ≥ 10  → RIGHT motor moves
```

### Python Console Logs:
```
🎮 BUTTON PRESSED - STARTING GAME!
✅ Game started by Arduino button!
...
🏁 Game over! Final score: 15
Activating servo motor based on score: 15
➡️  Score 15 >= 10: Activating RIGHT motor
✅ RIGHT motor activated successfully!
```

### Troubleshooting:
- **Button doesn't start game?** Check Python console for button events
- **Servo doesn't activate?** Verify `enable_servo=True` in `run_with_visualizer.py`
- **Wrong servo moves?** Check score threshold logic (< 10 vs ≥ 10)

---

## 📊 Score-Based Servo Logic

### Arduino Code (`servo_controller.ino`):
```cpp
// LEFT_MOTOR command:
servo1.write(neutral1 - power);  // LEFT motor moves
servo2.write(neutral2);          // RIGHT motor NEUTRAL (not moving)

// RIGHT_MOTOR command:
servo1.write(neutral1);          // LEFT motor NEUTRAL (not moving)
servo2.write(neutral2 + power);  // RIGHT motor moves
```

### Python Code (`servo_adapter.py`):
```python
def activate_motor_by_score(self, score: int):
    if score < 10:
        return self.activate_left_motor()  # servo1 moves
    else:
        return self.activate_right_motor()  # servo2 moves
```

---

## 🎯 Quick Reference

| Component | Port | Function |
|-----------|------|----------|
| Button Controller | COM7 | Starts game when pressed |
| Servo Controller | COM4 | Activates based on score |
| Servo 1 (LEFT) | Pin 9 | Moves when score < 10 |
| Servo 2 (RIGHT) | Pin 10 | Moves when score ≥ 10 |

---

## ✅ Success Checklist

- [ ] Button test shows JSON format: `{"button": "pressed"}`
- [ ] Servo test moves only ONE motor at a time
- [ ] Score < 10 activates LEFT motor only
- [ ] Score ≥ 10 activates RIGHT motor only
- [ ] Button press starts game in browser
- [ ] Game over triggers servo activation
- [ ] Python console shows all events clearly
- [ ] Web console (port 5001) shows servo status

---

## 🆘 Common Issues

### Issue: Both servos moving
**Solution:** Re-upload `servo_controller.ino` - code was updated to move only one servo

### Issue: Button not detected
**Solution:** 
1. Check COM7 in Device Manager
2. Close Arduino IDE Serial Monitor
3. Verify `button_controller.ino` is uploaded

### Issue: Servo not activating after game
**Solution:** 
1. Ensure `enable_servo=True` in `run_with_visualizer.py`
2. Check COM4 connection
3. Verify servo power supply

### Issue: Wrong servo activates
**Solution:** Check score value - threshold is 10 (< 10 = LEFT, ≥ 10 = RIGHT)

---

## 📝 Notes

- Servos run for **5 seconds** then automatically stop
- Button uses **debouncing** (50ms) to prevent false triggers
- Game requires **60 seconds survival** for victory
- Web visualizer runs on **port 5000**
- Servo test console runs on **port 5001**
