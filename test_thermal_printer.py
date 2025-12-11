"""
Standalone test for USB thermal printer
Prints a thank you message
"""
import sys

# Try different thermal printer libraries
def test_with_escpos():
    """Test using python-escpos library"""
    try:
        # Check if USB library is available first
        try:
            import usb.core
            usb_available = True
        except ImportError:
            print("❌ USB library (pyusb) not installed. Skipping USB method.")
            print("   Install with: pip install pyusb")
            return False
        
        from escpos.printer import Usb
        
        # Common USB thermal printer vendor/product IDs
        # You may need to adjust these for your specific printer
        VENDOR_IDS = [
            (0x0416, 0x5011),  # Common thermal printer
            (0x0483, 0x5720),  # Another common one
            (0x04B8, 0x0202),  # Epson
            (0x0519, 0x0001),  # Star
            (0x0DD4, 0x0205),  # Custom
        ]
        
        printer = None
        for vid, pid in VENDOR_IDS:
            try:
                printer = Usb(vid, pid)
                print(f"✅ Connected to printer with VID:0x{vid:04X} PID:0x{pid:04X}")
                break
            except Exception:
                continue
        
        if printer is None:
            print("❌ Could not find printer with known VIDs. Trying auto-detect...")
            # Try to list USB devices
            devices = usb.core.find(find_all=True)
            print("\nAvailable USB devices:")
            for dev in devices:
                print(f"  VID:0x{dev.idVendor:04X} PID:0x{dev.idProduct:04X}")
            return False
        
        # Print the message
        printer.set(align='center', font='a', bold=True, double_height=True, double_width=True)
        printer.text("\n")
        printer.text("IOIO\n")
        printer.set(align='center', font='a', bold=False, double_height=False, double_width=False)
        printer.text("\n")
        printer.text("Gracias por jugar\n")
        printer.text("con nosotros\n")
        printer.text("\n")
        printer.text("Atentamente,\n")
        printer.set(align='center', font='a', bold=True)
        printer.text("IOIO\n")
        printer.text("\n\n\n")
        printer.cut()
        
        # Properly close the printer
        if printer:
            try:
                printer.close()
            except:
                pass
        
        print("✅ Message printed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Required library not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error with escpos: {e}")
        return False


def test_with_serial():
    """Test using direct serial connection"""
    try:
        import serial
        import serial.tools.list_ports
        
        # List available COM ports
        ports = serial.tools.list_ports.comports()
        print("\nAvailable COM ports:")
        for port in ports:
            print(f"  {port.device}: {port.description}")
        
        # Try common printer ports (adjust as needed)
        printer_port = None
        for port in ports:
            desc = port.description.lower()
            if 'printer' in desc or 'thermal' in desc or 'pos' in desc or 'usb' in desc:
                printer_port = port.device
                break
        
        if not printer_port:
            # Ask user to specify
            print("\n⚠️  No printer auto-detected.")
            printer_port = input("Enter COM port for printer (e.g., COM3): ").strip()
            if not printer_port:
                return False
        
        print(f"\n📠 Trying to connect to {printer_port}...")
        
        # ESC/POS commands
        ESC = b'\x1b'
        GS = b'\x1d'
        
        INIT = ESC + b'@'  # Initialize printer
        CENTER = ESC + b'a\x01'  # Center align
        BOLD_ON = ESC + b'E\x01'
        BOLD_OFF = ESC + b'E\x00'
        DOUBLE_ON = GS + b'!\x11'  # Double height and width
        DOUBLE_OFF = GS + b'!\x00'
        CUT = GS + b'V\x00'  # Full cut
        
        with serial.Serial(printer_port, 9600, timeout=2) as ser:
            # Initialize
            ser.write(INIT)
            
            # Center align
            ser.write(CENTER)
            
            # Big title
            ser.write(DOUBLE_ON)
            ser.write(BOLD_ON)
            ser.write(b'\nIOIO\n')
            ser.write(DOUBLE_OFF)
            ser.write(BOLD_OFF)
            
            # Message
            ser.write(b'\n')
            ser.write('Gracias por jugar\n'.encode('cp437'))
            ser.write('con nosotros\n'.encode('cp437'))
            ser.write(b'\n')
            ser.write('Atentamente,\n'.encode('cp437'))
            ser.write(BOLD_ON)
            ser.write(b'IOIO\n')
            ser.write(BOLD_OFF)
            ser.write(b'\n\n\n')
            
            # Cut paper
            ser.write(CUT)
            
        print("✅ Message printed successfully via serial!")
        return True
        
    except ImportError:
        print("❌ pyserial not installed. Install with: pip install pyserial")
        return False
    except Exception as e:
        print(f"❌ Error with serial: {e}")
        return False


def test_with_win32print():
    """Test using Windows printing API"""
    try:
        import win32print
        import win32ui
        
        # Get default printer
        printer_name = win32print.GetDefaultPrinter()
        print(f"📠 Default printer: {printer_name}")
        
        # List all printers
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        print("\nAvailable printers:")
        for printer in printers:
            print(f"  - {printer[2]}")
        
        # Open printer and send raw data
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            # ESC/POS commands
            ESC = b'\x1b'
            GS = b'\x1d'
            
            INIT = ESC + b'@'
            CENTER = ESC + b'a\x01'
            BOLD_ON = ESC + b'E\x01'
            BOLD_OFF = ESC + b'E\x00'
            DOUBLE_ON = GS + b'!\x11'
            DOUBLE_OFF = GS + b'!\x00'
            CUT = GS + b'V\x00'
            
            # Build the print data
            data = bytearray()
            data.extend(INIT)
            data.extend(CENTER)
            data.extend(DOUBLE_ON)
            data.extend(BOLD_ON)
            data.extend(b'\nIOIO\n')
            data.extend(DOUBLE_OFF)
            data.extend(BOLD_OFF)
            data.extend(b'\n')
            data.extend('Gracias por jugar\n'.encode('cp437'))
            data.extend('con nosotros\n'.encode('cp437'))
            data.extend(b'\n')
            data.extend('Atentamente,\n'.encode('cp437'))
            data.extend(BOLD_ON)
            data.extend(b'IOIO\n')
            data.extend(BOLD_OFF)
            data.extend(b'\n\n\n')
            data.extend(CUT)
            
            # Start print job
            job = win32print.StartDocPrinter(hprinter, 1, ("Test Print", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, bytes(data))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            
            print("✅ Message sent to printer!")
            return True
            
        finally:
            win32print.ClosePrinter(hprinter)
            
    except ImportError:
        print("❌ pywin32 not installed. Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Error with win32print: {e}")
        return False


if __name__ == "__main__":
    print("="*50)
    print("🖨️  USB Thermal Printer Test")
    print("="*50)
    print("\nMessage to print:")
    print("  'Gracias por jugar con nosotros, atentamente IOIO'")
    print("\n" + "="*50)
    
    # Try different methods
    print("\n[Method 1] Trying python-escpos...")
    if test_with_escpos():
        sys.exit(0)
    
    print("\n[Method 2] Trying direct serial connection...")
    if test_with_serial():
        sys.exit(0)
    
    print("\n[Method 3] Trying Windows print API...")
    if test_with_win32print():
        sys.exit(0)
    
    print("\n" + "="*50)
    print("❌ All methods failed. Please check:")
    print("  1. Printer is connected and powered on")
    print("  2. Correct drivers are installed")
    print("  3. Install required library:")
    print("     pip install python-escpos pyserial pywin32")
    print("="*50)
