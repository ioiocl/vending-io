"""
Check which COM ports are available and which are in use
"""

import serial.tools.list_ports

print("="*60)
print("COM PORT STATUS CHECK")
print("="*60)

ports = serial.tools.list_ports.comports()

if not ports:
    print("\nNo COM ports found!")
else:
    print(f"\nFound {len(ports)} COM port(s):\n")
    
    for port in ports:
        print(f"Port: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Hardware ID: {port.hwid}")
        
        # Try to open the port
        try:
            import serial
            test = serial.Serial(port.device, 9600, timeout=0.5)
            test.close()
            print(f"  Status: AVAILABLE (not in use)")
        except serial.SerialException as e:
            if "PermissionError" in str(e) or "Acceso denegado" in str(e):
                print(f"  Status: IN USE (locked by another program)")
            else:
                print(f"  Status: ERROR - {e}")
        
        print()

print("="*60)
print("\nTo free up a port:")
print("1. Close Arduino IDE Serial Monitor")
print("2. Stop any running Python scripts")
print("3. Close any serial terminal programs")
print("="*60)
