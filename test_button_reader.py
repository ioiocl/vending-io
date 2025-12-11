"""
SIMPLE BUTTON TEST READER for COM7
This script reads button presses from Arduino on COM7

Usage:
1. Upload test_button_arduino.ino to your Arduino
2. Close Arduino IDE Serial Monitor
3. Run this script: python test_button_reader.py
4. Press the button and watch for messages
"""

import serial
import time

# Configuration
PORT = "COM7"
BAUD_RATE = 9600

def test_button():
    print("=" * 60)
    print("BUTTON TEST - Reading from COM7")
    print("=" * 60)
    
    try:
        # Open serial connection
        print(f"\nConnecting to {PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        
        # Wait for Arduino to initialize
        print("Waiting for Arduino to initialize (2 seconds)...")
        time.sleep(2)
        
        print("\n✅ Connected successfully!")
        print("=" * 60)
        print("Press the button on your Arduino...")
        print("Press CTRL+C to quit")
        print("=" * 60)
        print()
        
        # Read loop
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"📨 Received: {line}")
                    
                    # Highlight button presses
                    if "PRESSED" in line.upper():
                        print("🎮 ✅ BUTTON DETECTED!")
                        print()
            
            time.sleep(0.01)  # Small delay
    
    except serial.SerialException as e:
        print(f"\n❌ ERROR: Could not open {PORT}")
        print(f"Error details: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Arduino is connected to COM7 (Device Manager)")
        print("2. Close Arduino IDE Serial Monitor")
        print("3. Make sure no other program is using COM7")
        print("4. Try unplugging and replugging the Arduino")
    
    except KeyboardInterrupt:
        print("\n\n✅ Test stopped by user")
    
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed")

if __name__ == "__main__":
    test_button()
