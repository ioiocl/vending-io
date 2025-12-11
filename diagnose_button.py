"""
BUTTON DIAGNOSTIC TOOL
This script helps diagnose why button presses aren't being detected

Steps:
1. Lists all available COM ports
2. Tests connection to COM7
3. Reads raw serial data from COM7
4. Shows what the button adapter would see
"""

import serial
import serial.tools.list_ports
import time
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def list_ports():
    """List all available COM ports"""
    print("\n" + "="*60)
    print("📋 AVAILABLE COM PORTS")
    print("="*60)
    
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("❌ No COM ports found!")
        return []
    
    for port in ports:
        print(f"\n🔌 {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
    
    return [port.device for port in ports]

def test_port(port_name, duration=10):
    """Test reading from a specific port"""
    print("\n" + "="*60)
    print(f"🔍 TESTING {port_name}")
    print("="*60)
    
    try:
        print(f"\nConnecting to {port_name} at 9600 baud...")
        ser = serial.Serial(port_name, 9600, timeout=1)
        
        print("Waiting for Arduino to initialize (2 seconds)...")
        time.sleep(2)
        
        print(f"\n✅ Connected to {port_name}")
        print("="*60)
        print("📡 LISTENING FOR DATA...")
        print("Press the button on your Arduino")
        print(f"Will listen for {duration} seconds")
        print("="*60)
        print()
        
        start_time = time.time()
        line_count = 0
        
        while time.time() - start_time < duration:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        line_count += 1
                        print(f"[{line_count}] 📨 {line}")
                        
                        # Check for button-related keywords
                        if any(keyword in line.lower() for keyword in ['button', 'pressed', 'released']):
                            print("     ⭐ BUTTON EVENT DETECTED!")
                except Exception as e:
                    print(f"     ⚠️  Error decoding: {e}")
            
            time.sleep(0.01)
        
        ser.close()
        
        print("\n" + "="*60)
        if line_count == 0:
            print("❌ NO DATA RECEIVED")
            print("\nPossible issues:")
            print("  1. Arduino not programmed with button code")
            print("  2. Wrong COM port")
            print("  3. Arduino not powered/connected")
            print("  4. Baud rate mismatch")
        else:
            print(f"✅ Received {line_count} lines of data")
        print("="*60)
        
        return line_count > 0
        
    except serial.SerialException as e:
        print(f"\n❌ ERROR: Could not open {port_name}")
        print(f"Details: {e}")
        print("\nPossible issues:")
        print("  1. Port is already in use by another program")
        print("  2. Arduino is not connected to this port")
        print("  3. Permission denied (try running as admin)")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    print("="*60)
    print("🔧 BUTTON DIAGNOSTIC TOOL")
    print("="*60)
    
    # Step 1: List all ports
    available_ports = list_ports()
    
    if not available_ports:
        print("\n❌ No COM ports found. Is your Arduino connected?")
        return
    
    # Step 2: Test COM7 specifically
    if "COM7" in available_ports:
        print("\n✅ COM7 is available")
        test_port("COM7", duration=15)
    else:
        print("\n❌ COM7 not found in available ports!")
        print("\nAvailable ports:", ", ".join(available_ports))
        
        # Offer to test another port
        if available_ports:
            print(f"\nWould you like to test {available_ports[0]}? (y/n)")
            # For now, just test the first available port automatically
            print(f"\nTesting {available_ports[0]} instead...")
            test_port(available_ports[0], duration=15)
    
    print("\n" + "="*60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
