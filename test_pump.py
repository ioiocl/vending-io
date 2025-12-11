"""
Standalone Pump Test
Tests the pump controller on COM4 directly
"""
import serial
import time

PUMP_PORT = "COM4"
BAUD_RATE = 9600

def read_responses(ser, wait_time=0.5):
    """Read all available responses from serial"""
    time.sleep(wait_time)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line:
            print(f"   📥 {line}")

def test_pump():
    print("="*60)
    print("💨 PUMP TEST - COM4")
    print("="*60)
    
    try:
        # Open serial connection
        print(f"\n📡 Opening {PUMP_PORT}...")
        ser = serial.Serial(PUMP_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        # Read any startup messages
        read_responses(ser, 0.5)
        
        print("✅ Connected to pump controller")
        
        # Test 0: Quick TEST command (Arduino handles full cycle)
        print("\n" + "-"*40)
        print("TEST 0: ARDUINO TEST COMMAND")
        print("-"*40)
        print("This sends 'TEST' - Arduino will do activate(3s)->deactivate")
        input("Press ENTER to send TEST command...")
        
        ser.write(b"TEST\n")
        ser.flush()
        print("📤 Sent: TEST")
        
        # Read responses for 6 seconds
        for i in range(12):
            read_responses(ser, 0.5)
        
        # Test 1: Manual Activate pump
        print("\n" + "-"*40)
        print("TEST 1: MANUAL ACTIVATE PUMP")
        print("-"*40)
        input("Press ENTER to activate pump...")
        
        ser.write(b"ACTIVATE_PUMP\n")
        ser.flush()
        print("📤 Sent: ACTIVATE_PUMP")
        
        read_responses(ser, 0.5)
        
        # Wait and observe
        print("\n⏳ Pump should be running... waiting 5 seconds")
        for i in range(5):
            print(f"   {5-i}...")
            time.sleep(1)
            read_responses(ser, 0.1)
        
        # Test 2: Deactivate pump
        print("\n" + "-"*40)
        print("TEST 2: MANUAL DEACTIVATE PUMP")
        print("-"*40)
        input("Press ENTER to deactivate pump...")
        
        ser.write(b"DEACTIVATE_PUMP\n")
        ser.flush()
        print("📤 Sent: DEACTIVATE_PUMP")
        
        read_responses(ser, 1.5)
        
        print("\n" + "="*60)
        print("✅ PUMP TEST COMPLETE")
        print("="*60)
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"\n❌ Serial Error: {e}")
        print("   Make sure:")
        print("   - Arduino is connected to COM4")
        print("   - stage_2.ino is uploaded")
        print("   - No other program is using COM4")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled")
        if 'ser' in locals() and ser.is_open:
            # Try to deactivate before closing
            try:
                ser.write(b"DEACTIVATE_PUMP\n")
                time.sleep(1)
            except:
                pass
            ser.close()

if __name__ == "__main__":
    test_pump()
