"""
Test if button on COM7 triggers game start
This simulates what the main application does
"""

import serial
import time
import json

PORT = "COM7"
BAUD_RATE = 9600

def test_game_button():
    print("=" * 60)
    print("GAME BUTTON TEST - COM7")
    print("=" * 60)
    
    try:
        print(f"\nConnecting to {PORT}...")
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        
        print("Waiting for Arduino (2 seconds)...")
        time.sleep(2)
        
        print("\n✅ Connected!")
        print("=" * 60)
        print("Press the Arduino button to trigger game start...")
        print("Press CTRL+C to quit")
        print("=" * 60)
        print()
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    print(f"📨 Raw: {line}")
                    
                    try:
                        # Try to parse as JSON
                        data = json.loads(line)
                        print(f"📦 JSON: {data}")
                        
                        # Check for button press
                        if "button" in data:
                            button_state = data["button"]
                            print(f"🎮 Button state: {button_state}")
                            
                            if button_state == "pressed":
                                print("=" * 60)
                                print("🚀 GAME START TRIGGERED!")
                                print("=" * 60)
                                print()
                    
                    except json.JSONDecodeError:
                        print(f"⚠️  Not JSON format")
                    
                    print()
            
            time.sleep(0.01)
    
    except serial.SerialException as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure:")
        print("1. Arduino is on COM7")
        print("2. Correct sketch is uploaded")
        print("3. Arduino IDE Serial Monitor is closed")
    
    except KeyboardInterrupt:
        print("\n\n✅ Test stopped")
    
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Port closed")

if __name__ == "__main__":
    test_game_button()
