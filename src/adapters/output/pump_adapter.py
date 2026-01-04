"""
Pump Output Adapter
Controls suction pump via Arduino serial commands (COM4)
Receives activation signals from Stage 1 Arduino via Python bridge
"""
import logging
import serial
import serial.tools.list_ports
import time
import threading
import json
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class PumpAdapter:
    """
    Output adapter for Arduino pump controller (Stage 2)
    Receives pump commands from Stage 1 via serial and forwards to pump Arduino
    Supports configurable suction strength (0=max, 90=off)
    """
    
    def __init__(self, port: str = "COM4", baud_rate: int = 9600, suction_level: int = 60):
        """
        Initialize pump adapter
        
        Args:
            port: Serial port for pump Arduino (default COM4)
            baud_rate: Baud rate (default 9600)
            suction_level: Suction strength 0-90 (0=max, 60=medium, 90=off)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.suction_level = suction_level
        self.serial_connection: Optional[serial.Serial] = None
        self._initialized = False
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Callback for pump deactivation complete
        self._deactivation_callback: Optional[Callable] = None
        
        logger.info(f"Pump Adapter initialized on {port} @ {baud_rate} baud, suction level: {suction_level}")
    
    def initialize(self) -> bool:
        """
        Initialize pump controller
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open serial connection
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Read initialization message
            if self.serial_connection.in_waiting > 0:
                msg = self.serial_connection.readline().decode('utf-8').strip()
                logger.info(f"Pump controller: {msg}")
            
            self._initialized = True
            self._running = True
            
            # Start read thread
            self._read_thread = threading.Thread(target=self._read_serial, daemon=True)
            self._read_thread.start()
            
            logger.info(f"Pump adapter initialized on {self.port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Failed to open pump serial port {self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error initializing pump adapter: {e}")
            return False
    
    def _read_serial(self):
        """Background thread to read serial responses from pump Arduino"""
        while self._running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        logger.info(f"[PUMP] {line}")
                        print(f"🔧 [PUMP] {line}")
                        try:
                            data = json.loads(line)
                            status = data.get('status', '')
                            if status:
                                print(f"   Pump status: {status}")
                                
                                # Trigger callback when pump deactivation is complete
                                if status == 'pump_inactive':
                                    logger.info(f"Pump inactive detected. Callback registered: {self._deactivation_callback is not None}")
                                    print(f"\n🔔 Pump deactivation complete! Callback: {self._deactivation_callback is not None}")
                                    if self._deactivation_callback:
                                        logger.info("Triggering printer callback...")
                                        print("📞 Calling printer callback...")
                                        try:
                                            self._deactivation_callback()
                                            print("✅ Callback executed successfully")
                                        except Exception as e:
                                            logger.error(f"Error in deactivation callback: {e}")
                                            print(f"❌ Callback error: {e}")
                                    else:
                                        logger.warning("No deactivation callback registered!")
                                        print("⚠️  No callback registered - printer won't trigger")
                        except json.JSONDecodeError:
                            pass
                time.sleep(0.01)
            except Exception as e:
                if self._running:
                    logger.error(f"Error reading pump serial: {e}")
                break
    
    def stop(self):
        """Stop pump controller"""
        logger.info("Stopping pump adapter...")
        self._running = False
        
        # Ensure pump is deactivated
        if self._initialized:
            self.deactivate_pump()
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        self._initialized = False
        logger.info("Pump adapter stopped")
    
    def activate_pump(self, suction_level: Optional[int] = None) -> bool:
        """
        Activate suction pump with configurable strength
        
        Args:
            suction_level: Optional suction strength 0-90 (0=max, 90=off)
                          If None, uses the default level set in __init__
        
        Returns:
            True if command sent successfully
        """
        if not self._initialized:
            logger.warning("Pump adapter not initialized")
            print("⚠️  Pump adapter not initialized!")
            return False
        
        # Use provided level or default
        level = suction_level if suction_level is not None else self.suction_level
        
        # Validate level
        if level < 0 or level > 90:
            logger.error(f"Invalid suction level: {level}. Must be 0-90")
            print(f"❌ Invalid suction level: {level}")
            return False
        
        try:
            print("\n" + "="*60)
            print(f"💨 ACTIVATING SUCTION PUMP (Suction Level: {level})")
            print(f"   0=Max, 60=Medium, 90=Off")
            print("="*60)
            
            # Send command with suction level
            command = f"ACTIVATE_PUMP:{level}\n"
            self.serial_connection.write(command.encode())
            self.serial_connection.flush()
            logger.info(f"Pump activation command sent with suction level {level}")
            print(f"📤 Sent: ACTIVATE_PUMP:{level} to COM4")
            return True
        except Exception as e:
            logger.error(f"Error activating pump: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def deactivate_pump(self) -> bool:
        """
        Deactivate suction pump (release object)
        
        Returns:
            True if command sent successfully
        """
        if not self._initialized:
            logger.warning("Pump adapter not initialized")
            return False
        
        try:
            print("\n" + "="*60)
            print("🔓 DEACTIVATING PUMP (RELEASING)")
            print("="*60)
            
            self.serial_connection.write(b"DEACTIVATE_PUMP\n")
            self.serial_connection.flush()
            logger.info("Pump deactivation command sent")
            print("📤 Sent: DEACTIVATE_PUMP to COM4")
            return True
        except Exception as e:
            logger.error(f"Error deactivating pump: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def set_suction_level(self, level: int) -> bool:
        """
        Set the default suction level for future activations
        
        Args:
            level: Suction strength 0-90 (0=max, 90=off)
        
        Returns:
            True if command sent successfully
        """
        if level < 0 or level > 90:
            logger.error(f"Invalid suction level: {level}. Must be 0-90")
            return False
        
        if not self._initialized:
            logger.warning("Pump adapter not initialized")
            return False
        
        try:
            command = f"SET_SUCTION:{level}\n"
            self.serial_connection.write(command.encode())
            self.serial_connection.flush()
            self.suction_level = level
            logger.info(f"Suction level set to {level}")
            print(f"🔧 Suction level set to {level}")
            return True
        except Exception as e:
            logger.error(f"Error setting suction level: {e}")
            return False
    
    def register_deactivation_callback(self, callback: Callable):
        """Register callback to be called when pump deactivation is complete"""
        self._deactivation_callback = callback
        logger.info("Pump deactivation callback registered")
    
    def reset(self) -> bool:
        """Reset pump to initial state"""
        if not self._initialized:
            return False
        
        try:
            self.serial_connection.write(b"RESET\n")
            self.serial_connection.flush()
            logger.info("Pump reset command sent")
            return True
        except Exception as e:
            logger.error(f"Error resetting pump: {e}")
            return False
    
    def get_output_info(self) -> dict:
        """Get pump adapter information"""
        return {
            'type': 'Pump Controller',
            'port': self.port,
            'baud_rate': self.baud_rate,
            'suction_level': self.suction_level,
            'status': 'initialized' if self._initialized else 'not initialized',
            'connected': self.serial_connection.is_open if self.serial_connection else False
        }
