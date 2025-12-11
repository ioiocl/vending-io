"""
Simple test for USB thermal printer at Port_#0001.Hub_#0001
"""

def get_printer_by_port():
    """Find printer connected to USB Port_#0001.Hub_#0001"""
    try:
        import win32print
        import winreg
        
        # Get all printers and their ports
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
            None, 2  # Level 2 gives us port info
        )
        
        print("Searching for printer at Port_#0001.Hub_#0001...")
        print("\nAvailable printers and ports:")
        
        for printer in printers:
            name = printer['pPrinterName']
            port = printer.get('pPortName', 'Unknown')
            print(f"  - {name} -> Port: {port}")
            
            # Check if this printer is on the USB port we want
            if 'USB' in port.upper() or '0001' in port:
                return name
        
        # Fallback: look for generic/POS printer
        for printer in printers:
            name = printer['pPrinterName'].lower()
            if 'generic' in name or 'pos' in name or 'thermal' in name or 'receipt' in name or 'usb' in name:
                return printer['pPrinterName']
        
        return None
    except Exception as e:
        print(f"Error finding printer: {e}")
        return None


def print_with_windows():
    """Print using Windows printer with raw ESC/POS commands"""
    try:
        import win32print
        
        # Try to find printer by USB port
        printer_name = get_printer_by_port()
        
        if not printer_name:
            # Fallback to default printer
            printer_name = win32print.GetDefaultPrinter()
            print(f"\n⚠️  Could not find USB printer, using default: {printer_name}")
        else:
            print(f"\n📠 Found printer: {printer_name}")
        
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
        
        # Open printer and send raw data
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            job = win32print.StartDocPrinter(hprinter, 1, ("IOIO Test", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, bytes(data))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            print("✅ Message sent to printer!")
            return True
        finally:
            win32print.ClosePrinter(hprinter)
            
    except ImportError:
        print("❌ pywin32 not installed. Run: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("="*50)
    print("🖨️  USB Thermal Printer Test")
    print("="*50)
    print("\nPrinting: 'Gracias por jugar con nosotros, atentamente IOIO'\n")
    print_with_windows()
