"""
SIMPLE BUTTON TEST - COM7
Run this to see if button presses are being sent from Arduino
Tests button reading and verifies game start trigger
"""

import serial
import time
import json

PORT = "COM7"
BAUD = 9600

print("="*60)
print("🎮 BUTTON TEST - COM7")
print("="*60)
print(f"\nConnecting to {PORT}...")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"✅ Connected to {PORT}")
    print("\nWaiting 2 seconds for Arduino to initialize...")
    time.sleep(2)
    
    # Read any initialization messages
    if ser.in_waiting > 0:
        init_msg = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"Arduino says: {init_msg}")
    
    print("\n" + "="*60)
    print("🎯 LISTENING FOR BUTTON PRESSES...")
    print("="*60)
    print("\n📋 Instructions:")
    print("  1. Press the button on your Arduino (pin 9)")
    print("  2. Watch for button events below")
    print("  3. Verify JSON format is correct")
    print("  4. Press CTRL+C to stop")
    print("\n" + "="*60 + "\n")
    
    button_press_count = 0
    button_release_count = 0
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] RAW: {line}")
                
                # Try to parse as JSON
                try:
                    data = json.loads(line)
                    if "button" in data:
                        button_state = data["button"]
                        if button_state == "pressed":
                            button_press_count += 1
                            print(f"           ✅ BUTTON PRESSED (Count: {button_press_count})")
                            print(f"           🎮 This should START THE GAME!")
                        elif button_state == "released":
                            button_release_count += 1
                            print(f"           ⚪ Button released (Count: {button_release_count})")
                    elif "status" in data:
                        print(f"           ℹ️  Status: {data['status']}")
                except json.JSONDecodeError:
                    print(f"           ⚠️  Not valid JSON (will try plain text parsing)")
                
                print()  # Empty line for readability
        
        time.sleep(0.01)
        
except serial.SerialException as e:
    print(f"\nERROR: Could not open {PORT}")
    print(f"Details: {e}")
    print("\nTroubleshooting:")
    print("1. Is Arduino connected to COM7?")
    print("2. Close Arduino IDE Serial Monitor")
    print("3. Is another program using COM7?")
    
except KeyboardInterrupt:
    print("\n\nTest stopped")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Port closed")
