"""
Thermal Printer Output Adapter
Prints thank you messages via Windows printer API
"""
import logging
import serial
import serial.tools.list_ports
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
    Output adapter for thermal printer
    Prints thank you messages after game completion
    """
    
    def __init__(self, port: Optional[str] = None, baud_rate: int = 9600, auto_detect: bool = True, exclude_ports: list = None):
        """
        Initialize thermal printer adapter
        
        Args:
            port: Serial port for printer (e.g., COM3). If None, will auto-detect
            baud_rate: Baud rate (default 9600)
            auto_detect: Auto-detect printer port if port is None
            exclude_ports: List of ports to exclude from auto-detection (e.g., ['COM4', 'COM7'])
        """
        self.port = port
        self.baud_rate = baud_rate
        self.auto_detect = auto_detect
        self.exclude_ports = exclude_ports or []
        self._initialized = False
        
        logger.info(f"Thermal Printer Adapter initialized (port: {port or 'auto-detect'}, exclude: {self.exclude_ports})")
    
    def initialize(self) -> bool:
        """
        Initialize thermal printer
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Auto-detect printer port if needed
            if not self.port and self.auto_detect:
                self.port = self._auto_detect_printer_port()
                if not self.port:
                    logger.warning("Could not auto-detect thermal printer port")
                    return False
            
            # Test connection
            with serial.Serial(self.port, self.baud_rate, timeout=2) as ser:
                logger.info(f"Thermal printer connection test successful on {self.port}")
            
            self._initialized = True
            logger.info(f"Thermal printer initialized on {self.port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Failed to initialize thermal printer on {self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error initializing thermal printer: {e}")
            return False
    
    def _auto_detect_printer_port(self) -> Optional[str]:
        """
        Auto-detect thermal printer COM port
        
        Returns:
            Port name if found, None otherwise
        """
        try:
            ports = serial.tools.list_ports.comports()
            
            logger.info(f"Scanning for thermal printer (excluding: {self.exclude_ports})...")
            
            # Look for common printer keywords
            for port in ports:
                # Skip excluded ports
                if port.device in self.exclude_ports:
                    logger.info(f"Skipping {port.device} (excluded)")
                    continue
                
                desc = port.description.lower()
                if any(keyword in desc for keyword in ['printer', 'thermal', 'pos', 'usb-serial', 'ch340']):
                    logger.info(f"Auto-detected printer on {port.device}: {port.description}")
                    return port.device
            
            logger.warning("No thermal printer found in auto-detection")
            return None
            
        except Exception as e:
            logger.error(f"Error during auto-detection: {e}")
            return None
    
    def print_thank_you(self, score: Optional[int] = None, ascii_line: Optional[str] = None, poem: Optional[str] = None) -> bool:
        """
        Print thank you message
        
        Returns:
            True if successful, False otherwise
        """
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
            
            with serial.Serial(self.port, self.baud_rate, timeout=2) as ser:
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

                if score is not None:
                    ser.write((f'Puntaje: {score}\n').encode('cp437', errors='replace'))
                if ascii_line:
                    ser.write((f'{ascii_line}\n').encode('cp437', errors='replace'))
                if poem:
                    ser.write((f'{poem}\n').encode('cp437', errors='replace'))
                if score is not None or ascii_line or poem:
                    ser.write(b'\n')
                ser.write('Atentamente,\n'.encode('cp437'))
                ser.write(BOLD_ON)
                ser.write(b'IOIO\n')
                ser.write(BOLD_OFF)
                ser.write(b'\n\n\n')
                
                # Cut paper
                ser.write(CUT)
            
            logger.info("Thank you message printed successfully!")
            print("✅ Thank you message printed!")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Serial error while printing: {e}")
            print(f"❌ Printer error: {e}")
            return False
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
            'type': 'Thermal Printer',
            'port': self.port,
            'baud_rate': self.baud_rate,
            'status': 'initialized' if self._initialized else 'not initialized'
        }
