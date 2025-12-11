"""
Quick script to find the thermal printer COM port
"""
import serial.tools.list_ports

print("="*60)
print("🔍 Scanning for COM ports...")
print("="*60)

ports = serial.tools.list_ports.comports()

if not ports:
    print("\n❌ No COM ports found!")
else:
    print(f"\n✅ Found {len(ports)} COM port(s):\n")
    
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
        
        # Check if it might be a printer
        desc_lower = port.description.lower()
        if any(keyword in desc_lower for keyword in ['printer', 'thermal', 'pos', 'usb-serial', 'ch340', 'cp210', 'ftdi']):
            print(f"   ⭐ POSSIBLE PRINTER!")
        
        # Check if it's Arduino
        if port.device in ['COM4', 'COM7']:
            print(f"   🤖 Arduino port (excluded from printer detection)")
        
        print()

print("="*60)
print("\n💡 Tips:")
print("  • Thermal printers often show as 'USB-Serial' or 'CH340'")
print("  • COM4 and COM7 are your Arduino ports (excluded)")
print("  • If you see your printer, note the COM port number")
print("\n" + "="*60)
