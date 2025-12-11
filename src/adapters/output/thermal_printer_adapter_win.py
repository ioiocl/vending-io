"""
Thermal Printer Output Adapter (Windows)
Prints thank you messages via Windows printer API
Uses the same method as test_printer_simple.py
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import win32print for Windows printing
try:
    import win32print
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("win32print not available - install with: pip install pywin32")


class ThermalPrinterAdapter:
    """
    Output adapter for thermal printer using Windows printing API
    Prints thank you messages after game completion
    """
    
    def __init__(self, printer_name: Optional[str] = None):
        """
        Initialize thermal printer adapter
        
        Args:
            printer_name: Windows printer name. If None, will auto-detect USB printer
        """
        self.printer_name = printer_name
        self._initialized = False
        
        logger.info(f"Thermal Printer Adapter initialized (printer: {printer_name or 'auto-detect'})")
    
    def initialize(self) -> bool:
        """
        Initialize thermal printer
        
        Returns:
            True if successful, False otherwise
        """
        if not WIN32_AVAILABLE:
            logger.error("win32print not available - cannot use Windows printer")
            print("❌ win32print not installed. Run: pip install pywin32")
            return False
        
        try:
            # Auto-detect printer if not specified
            if not self.printer_name:
                self.printer_name = self._find_usb_printer()
                if not self.printer_name:
                    logger.warning("Could not find USB thermal printer, using default")
                    self.printer_name = win32print.GetDefaultPrinter()
            
            # Test that printer exists
            try:
                hprinter = win32print.OpenPrinter(self.printer_name)
                win32print.ClosePrinter(hprinter)
                self._initialized = True
                logger.info(f"Thermal printer initialized: {self.printer_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to open printer '{self.printer_name}': {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error initializing thermal printer: {e}")
            return False
    
    def _find_usb_printer(self) -> Optional[str]:
        """
        Find USB thermal printer
        
        Returns:
            Printer name if found, None otherwise
        """
        try:
            # Get all printers and their ports
            printers = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
                None, 2  # Level 2 gives us port info
            )
            
            logger.info("Searching for USB thermal printer...")
            
            # First try: Look for USB port
            for printer in printers:
                name = printer['pPrinterName']
                port = printer.get('pPortName', 'Unknown')
                logger.info(f"Found printer: {name} -> Port: {port}")
                
                # Check if this printer is on a USB port
                if 'USB' in port.upper() or '0001' in port:
                    logger.info(f"Auto-detected USB printer: {name}")
                    return name
            
            # Second try: Look for thermal/POS printer by name
            for printer in printers:
                name = printer['pPrinterName'].lower()
                if any(keyword in name for keyword in ['generic', 'pos', 'thermal', 'receipt', 'usb']):
                    logger.info(f"Auto-detected thermal printer by name: {printer['pPrinterName']}")
                    return printer['pPrinterName']
            
            logger.warning("No USB thermal printer found")
            return None
            
        except Exception as e:
            logger.error(f"Error during printer detection: {e}")
            return None
    
    def print_thank_you(self) -> bool:
        """
        Print thank you message using Windows printer API
        
        Returns:
            True if successful, False otherwise
        """
        if not WIN32_AVAILABLE:
            logger.error("win32print not available")
            print("❌ win32print not installed")
            return False
        
        if not self._initialized:
            logger.warning("Thermal printer not initialized, attempting to initialize now...")
            print("⚠️  Printer not initialized, trying to initialize...")
            if not self.initialize():
                logger.error("Failed to initialize printer for printing")
                print("❌ Failed to initialize printer")
                return False
            print("✅ Printer initialized successfully!")
        
        try:
            logger.info("Printing thank you message...")
            print("\n" + "="*60)
            print("🖨️  PRINTING THANK YOU MESSAGE")
            print("="*60)
            
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
            hprinter = win32print.OpenPrinter(self.printer_name)
            try:
                job = win32print.StartDocPrinter(hprinter, 1, ("IOIO Thank You", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, bytes(data))
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                
                logger.info("Thank you message printed successfully!")
                print("✅ Thank you message printed!")
                return True
            finally:
                win32print.ClosePrinter(hprinter)
            
        except Exception as e:
            logger.error(f"Error printing thank you message: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def stop(self):
        """Stop thermal printer adapter"""
        logger.info("Stopping thermal printer adapter...")
        self._initialized = False
        logger.info("Thermal printer adapter stopped")
    
    def get_printer_info(self) -> dict:
        """Get printer adapter information"""
        return {
            'type': 'Thermal Printer (Windows)',
            'printer_name': self.printer_name,
            'status': 'initialized' if self._initialized else 'not initialized'
        }
