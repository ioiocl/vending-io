"""
Arduino Input Adapter
Connects to Arduino via serial port and receives proximity sensor data
"""
import serial
import serial.tools.list_ports
import threading
import time
import logging
from typing import Callable, Optional
import json

from core.ports.input_port import SensorInputPort
from core.domain.events import ProximityEvent

logger = logging.getLogger(__name__)


class ArduinoAdapter(SensorInputPort):
    """
    Adapter for Arduino proximity sensor input
    Communicates via serial port (USB)
    """
    
    def __init__(self, port: Optional[str] = "COM3", baud_rate: int = 9600, auto_detect: bool = False):
        """
        Initialize Arduino adapter
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baud_rate: Serial communication speed (default 9600)
            auto_detect: Automatically detect Arduino port if True
        """
        self.port = port
        self.baud_rate = baud_rate
        self.auto_detect = auto_detect
        self.serial_connection: Optional[serial.Serial] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[ProximityEvent], None]] = None
        self.sensor_id = "arduino_proximity_01"
        
    def _find_arduino_port(self) -> Optional[str]:
        """Auto-detect Arduino port"""
        logger.info("Searching for Arduino...")
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Look for common Arduino identifiers
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB Serial' in port.description:
                logger.info(f"Found potential Arduino at {port.device}: {port.description}")
                return port.device
        
        # If no Arduino found, return first available port
        if ports:
            logger.warning(f"No Arduino detected, using first available port: {ports[0].device}")
            return ports[0].device
        
        return None
    
    def start(self):
        """Start listening for Arduino data"""
        if self._running:
            logger.warning("Arduino adapter already running")
            return
        
        # Determine port
        if self.auto_detect and not self.port:
            self.port = self._find_arduino_port()
        
        if not self.port:
            logger.error("No serial port available")
            raise RuntimeError("Cannot find Arduino port")
        
        try:
            # Open serial connection
            logger.info(f"Connecting to Arduino on {self.port} at {self.baud_rate} baud")
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            
            # Wait for Arduino to reset (Arduino resets on serial connection)
            time.sleep(2)
            
            # Clear any initial garbage data
            self.serial_connection.reset_input_buffer()
            
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            
            logger.info("Arduino adapter started successfully")
            
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            raise
    
    def stop(self):
        """Stop listening for Arduino data"""
        logger.info("Stopping Arduino adapter")
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=2)
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        logger.info("Arduino adapter stopped")
    
    def is_running(self) -> bool:
        """Check if adapter is running"""
        return self._running
    
    def register_callback(self, callback: Callable[[ProximityEvent], None]):
        """Register callback for proximity events"""
        self._callback = callback
        logger.info("Callback registered for Arduino adapter")
    
    def _read_loop(self):
        """Main loop for reading serial data"""
        logger.info("Arduino read loop started")
        
        while self._running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    # Read line from Arduino
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line:
                        self._process_data(line)
                
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except serial.SerialException as e:
                logger.error(f"Serial communication error: {e}")
                self._running = False
            except Exception as e:
                logger.error(f"Error in read loop: {e}")
    
    def _process_data(self, data: str):
        """
        Process incoming data from Arduino
        Expected format: JSON {"distance": 25.5} or plain number "25.5"
        """
        try:
            # Try JSON format first
            try:
                parsed = json.loads(data)
                distance = float(parsed.get('distance', 0))
            except (json.JSONDecodeError, ValueError):
                # Fall back to plain number
                distance = float(data)
            
            if distance > 0:
                logger.debug(f"Received distance: {distance}cm")
                
                # Create proximity event
                event = ProximityEvent(distance=distance, sensor_id=self.sensor_id)
                
                # Call registered callback
                if self._callback:
                    self._callback(event)
                    
        except ValueError as e:
            logger.warning(f"Invalid data received: {data} - {e}")
        except Exception as e:
            logger.error(f"Error processing data: {e}")
    
    def get_sensor_info(self) -> dict:
        """Get sensor information"""
        return {
            "type": "Arduino Proximity Sensor",
            "sensor_id": self.sensor_id,
            "port": self.port,
            "baud_rate": self.baud_rate,
            "status": "running" if self._running else "stopped",
            "connection": "connected" if (self.serial_connection and self.serial_connection.is_open) else "disconnected"
        }
    
    def calibrate(self) -> bool:
        """
        Calibrate sensor (placeholder for future implementation)
        Could send calibration command to Arduino
        """
        logger.info("Calibration not implemented yet")
        return True
    
    def send_command(self, command: str):
        """Send a command to Arduino (for future use)"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(f"{command}\n".encode('utf-8'))
            logger.debug(f"Sent command to Arduino: {command}")
