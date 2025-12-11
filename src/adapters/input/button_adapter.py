"""
Button Input Adapter
Reads button press events from Arduino via serial port
"""
import logging
import serial
import serial.tools.list_ports
import json
import threading
import time
from typing import Callable, Optional

from src.core.ports.input_port import InputPort
from src.core.domain.events import DomainEvent, EventType
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ButtonEvent(DomainEvent):
    """Event when button is pressed or released"""
    button_state: str  # "pressed" or "released"
    
    def __init__(self, button_state: str):
        super().__init__(
            event_type=EventType.STATE_CHANGED,
            timestamp=datetime.now(),
            data={"button_state": button_state}
        )
        self.button_state = button_state


class ButtonAdapter(InputPort):
    """
    Input adapter for Arduino button controller
    Reads button events from serial port and emits ButtonEvent
    """
    
    def __init__(self, port: str = "COM4", baud_rate: int = 9600, auto_detect: bool = False):
        """
        Initialize button adapter
        
        Args:
            port: Serial port (e.g., "COM4")
            baud_rate: Baud rate (default 9600)
            auto_detect: Auto-detect Arduino port
        """
        self.port = port
        self.baud_rate = baud_rate
        self.auto_detect = auto_detect
        self.serial_connection: Optional[serial.Serial] = None
        self.callback: Optional[Callable] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        logger.info(f"Button Adapter initialized on {port} @ {baud_rate} baud")
    
    def start(self):
        """Start reading button events"""
        try:
            # Auto-detect port if enabled
            if self.auto_detect:
                detected_port = self._auto_detect_port()
                if detected_port:
                    self.port = detected_port
                    logger.info(f"Auto-detected button Arduino on {self.port}")
            
            # Open serial connection
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            logger.info(f"Button Arduino serial connection opened on {self.port} @ {self.baud_rate} baud")
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Start reading thread
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            
            logger.info(f"Button adapter started on {self.port}")
            
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {self.port}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error starting button adapter: {e}")
            raise
    
    def stop(self):
        """Stop reading button events"""
        logger.info("Stopping button adapter...")
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=2)
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        logger.info("Button adapter stopped")
    
    def is_running(self) -> bool:
        """Check if button adapter is running"""
        return self._running
    
    def register_callback(self, callback: Callable[[ButtonEvent], None]):
        """
        Register callback for button events
        
        Args:
            callback: Function to call when button event occurs
        """
        self.callback = callback
        logger.info(f"[ButtonAdapter] Callback registered: {callback}")
        logger.info(f"[ButtonAdapter] Callback is now: {self.callback}")
    
    def _read_loop(self):
        """Main reading loop (runs in separate thread)"""
        logger.info("Button reading loop started")
        
        while self._running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line:
                        logger.info(f"[ButtonAdapter] Raw serial line: {line}")
                        self._process_line(line)
                
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except serial.SerialException as e:
                logger.error(f"Serial error: {e}")
                break
            except Exception as e:
                logger.error(f"Error in button reading loop: {e}")
                time.sleep(0.1)
        
        logger.info("Button reading loop stopped")
    
    def _process_line(self, line: str):
        """
        Process a line from serial port
        
        Args:
            line: JSON string from Arduino
        """
        try:
            # First, try JSON
            data = json.loads(line)
            
            # Check for button event
            if "button" in data:
                button_state = data["button"]
                logger.info(f"Button state received from Arduino (JSON): {button_state}")
                
                # Create and emit event
                event = ButtonEvent(button_state=button_state)
                
                if self.callback:
                    self.callback(event)
                return
            
        except json.JSONDecodeError:
            # Fallback: plain text format
            normalized = line.strip().lower()
            
            # Handle various plain text formats
            if "pressed" in normalized or "button" in normalized:
                logger.info(f"Button PRESSED detected from Arduino (plain text): {line}")
                event = ButtonEvent(button_state="pressed")
                if self.callback:
                    logger.info(f"[ButtonAdapter] Calling callback with event: {event}")
                    self.callback(event)
                    logger.info(f"[ButtonAdapter] Callback executed successfully")
                else:
                    logger.warning(f"[ButtonAdapter] No callback registered! Cannot send button event.")
            elif "released" in normalized:
                logger.info(f"Button RELEASED detected from Arduino (plain text): {line}")
                event = ButtonEvent(button_state="released")
                if self.callback:
                    self.callback(event)
            else:
                logger.debug(f"Non-button line: {line}")
        except Exception as e:
            logger.error(f"Error processing button data: {e}")
    
    def _auto_detect_port(self) -> Optional[str]:
        """
        Auto-detect Arduino port
        
        Returns:
            Port name if found, None otherwise
        """
        logger.info("Auto-detecting button Arduino port...")
        ports = serial.tools.list_ports.comports()
        
        # First, check if COM7 is available (preferred button port)
        for port in ports:
            if port.device == "COM7":
                if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'usb serial']):
                    logger.info(f"Button Arduino found on preferred port COM7")
                    return port.device
        
        # If COM7 not found, look for other Arduino devices (skip servo ports)
        for port in ports:
            logger.debug(f"Found port: {port.device} - {port.description}")
            
            # Look for Arduino-like devices
            if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'usb serial']):
                # Skip COM3 and COM4 (servo controller ports)
                if port.device not in ["COM3", "COM4"]:
                    logger.info(f"Potential button Arduino found: {port.device}")
                    return port.device
        
        logger.warning("No button Arduino port auto-detected")
        return None
    
    def get_sensor_info(self) -> dict:
        """Get button adapter information"""
        return {
            'type': 'Button Controller',
            'port': self.port,
            'baud_rate': self.baud_rate,
            'status': 'running' if self._running else 'stopped',
            'connected': self.serial_connection.is_open if self.serial_connection else False
        }
