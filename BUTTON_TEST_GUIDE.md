# Button Test Guide - COM7 Arduino

## What I Fixed

### 1. **Button Adapter** (`src/adapters/input/button_adapter.py`)
- ✅ Now accepts **plain text** format like `"BUTTON PRESSED!"`
- ✅ Previously only accepted JSON format `{"button": "pressed"}`
- ✅ Works with your current Arduino code

### 2. **Application Handler** (`src/app/application.py`)
- ✅ Added **verbose logging** to show every step of button detection
- ✅ Logs appear in Python console when button is pressed
- ✅ Sends WebSocket event `game_start_trigger` to frontend

### 3. **Web Visualizer** (`web/templates/game_visualizer.html`)
- ✅ Added **WebSocket listener** for `game_start_trigger` event
- ✅ Shows visual feedback when button is pressed
- ✅ Starts the game automatically
- ✅ Displays alert and console logs

---

## How to Test

### Step 1: Make sure your Arduino code is uploaded to COM7

Your current Arduino code (test version):
```cpp
const int buttonPin = 9;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.println("Button Test Ready!");
  Serial.println("Press the button...");
}

void loop() {
  int buttonState = digitalRead(buttonPin);
  if (buttonState == LOW) {
    Serial.println("BUTTON PRESSED!");
    delay(500);
  }
  delay(50);
}
```

✅ This code is now **fully compatible** with the button adapter!

---

### Step 2: Run the application

```powershell
& "C:\Users\Andres Vasquez\AppData\Local\Programs\Python\Python311\python.exe" run_with_visualizer.py
```

---

### Step 3: What to expect when you press the button

#### **In Python Console:**
```
============================================================
[BUTTON EVENT] Event received: ButtonEvent(...)
============================================================

Button state: pressed

============================================================
🎮 BUTTON PRESSED - STARTING GAME!
============================================================

Sending game start signal to web visualizer...
✅ Game start signal sent!
```

#### **In Web Browser** (http://127.0.0.1:5000/game):
- 🟢 Connection status changes to "🎮 BUTTON PRESSED - GAME STARTING!"
- 🎨 Canvas border flashes **yellow** then back to green
- 🚨 Alert popup: "🎮 GAME STARTED! Press button detected!"
- 📊 Browser console logs: "🎮 BUTTON PRESSED ON ARDUINO! Starting game..."
- ✅ Game starts!

---

## Troubleshooting

### ❌ "No logs appear when I press button"

**Check:**
1. Is COM7 free? (Close Arduino IDE Serial Monitor)
2. Is the Arduino code uploaded correctly?
3. Is the button wired to **pin 9** and **GND**?

**Test with:**
```powershell
& "C:\Users\Andres Vasquez\AppData\Local\Programs\Python\Python311\python.exe" simple_button_test.py
```

If this shows `RECEIVED: BUTTON PRESSED!` then Arduino is working.

---

### ❌ "Logs appear in Python but game doesn't start in browser"

**Check:**
1. Is the browser open to `http://127.0.0.1:5000/game`?
2. Open browser console (F12) - do you see WebSocket errors?
3. Check connection status indicator in top-left of game page

---

### ❌ "Permission Error on COM7"

Something else is using COM7. Close:
- Arduino IDE Serial Monitor
- Any other Python scripts
- Serial terminal programs

---

## Current Configuration

- **Button Arduino**: COM7 (9600 baud)
- **Servo Controller**: COM4 (DISABLED for testing)
- **Button Pin**: 9 (with internal pullup)
- **Button Format**: Plain text `"BUTTON PRESSED!"` ✅

---

## Next Steps

Once button detection is working:

1. **Optional**: Upload the JSON version (`arduino/button_controller/button_controller.ino`) for cleaner data format
2. **Enable servo**: Change `enable_servo=False` to `enable_servo=True` in `run_with_visualizer.py`
3. **Test game over**: Play the game and check if servo activates based on score

---

## Quick Reference

**Test button only:**
```powershell
& "C:\Users\Andres Vasquez\AppData\Local\Programs\Python\Python311\python.exe" simple_button_test.py
```

**Check COM ports:**
```powershell
& "C:\Users\Andres Vasquez\AppData\Local\Programs\Python\Python311\python.exe" check_ports.py
```

**Run full application:**
```powershell
& "C:\Users\Andres Vasquez\AppData\Local\Programs\Python\Python311\python.exe" run_with_visualizer.py
```

---

## Summary

✅ Button adapter now handles your Arduino's plain text format
✅ Verbose logging shows every step in Python console
✅ WebSocket listener added to frontend for game start
✅ Visual feedback when button is pressed
✅ Game starts automatically when button is detected

**Try it now!** Press your button and watch the logs! 🎮
