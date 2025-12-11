"""
Test Thermal Printer Integration
Tests the printer adapter in the context of the application
"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from adapters.output.thermal_printer_adapter import ThermalPrinterAdapter

def main():
    print("="*60)
    print("🖨️  Thermal Printer Integration Test")
    print("="*60)
    
    # Create printer adapter
    print("\n1. Creating thermal printer adapter...")
    printer = ThermalPrinterAdapter(auto_detect=True)
    
    # Initialize
    print("\n2. Initializing printer...")
    if not printer.initialize():
        print("❌ Failed to initialize printer")
        print("\nTroubleshooting:")
        print("  • Make sure thermal printer is connected via USB")
        print("  • Check that printer is powered on")
        print("  • Verify printer appears in Device Manager")
        return
    
    print(f"✅ Printer initialized: {printer.get_printer_info()}")
    
    # Print thank you message
    print("\n3. Printing thank you message...")
    input("Press ENTER to print...")
    
    if printer.print_thank_you():
        print("\n✅ SUCCESS! Check your printer for the thank you message.")
    else:
        print("\n❌ Failed to print message")
    
    # Cleanup
    printer.stop()
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

if __name__ == "__main__":
    main()
