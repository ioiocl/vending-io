"""
Servo Output Adapter
Controls servo motors via Arduino serial commands (Stage 1 on COM7)
Bridges pump commands to Stage 2 Arduino (COM4)
"""
import logging
import serial
import serial.tools.list_ports
import time
import threading
import json
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ServoAdapter:
    """
    Output adapter for Arduino servo controller (Stage 1)
    Sends commands to control servo motors and bridges pump signals
    """
    
    def __init__(self, port: str = "COM7", baud_rate: int = 9600, auto_detect: bool = False):
        """
        Initialize servo adapter
        
        Args:
            port: Serial port for Stage 1 Arduino (default COM7)
            baud_rate: Baud rate (default 9600)
            auto_detect: Auto-detect Arduino port
        """
        self.port = port
        self.baud_rate = baud_rate
        self.auto_detect = auto_detect
        self.serial_connection: Optional[serial.Serial] = None
        self._initialized = False
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Pump adapter reference (set externally)
        self.pump_adapter = None
        
        # Thermal printer adapter reference (set externally)
        self.printer_adapter = None

        self._last_game_receipt = None
        self._receipt_printed = False
        
        # Callbacks for status updates
        self._status_callback: Optional[Callable] = None
        self._button_callback: Optional[Callable] = None
        self._invite_callback: Optional[Callable] = None
        self._relay_callback: Optional[Callable] = None
        
        logger.info(f"Servo Adapter initialized on {port} @ {baud_rate} baud")

    def set_last_game_receipt(self, score: int, ascii_line: str, poem: str):
        self._last_game_receipt = {
            'score': score,
            'ascii_line': ascii_line,
            'poem': poem
        }
        self._receipt_printed = False

    def _print_receipt_once(self) -> bool:
        if self._receipt_printed:
            logger.info("Receipt already printed for this game - skipping")
            return True

        if not self.printer_adapter:
            logger.warning("No printer adapter available")
            return False

        if self._last_game_receipt:
            ok = self.printer_adapter.print_thank_you(
                score=self._last_game_receipt.get('score'),
                ascii_line=self._last_game_receipt.get('ascii_line'),
                poem=self._last_game_receipt.get('poem')
            )
        else:
            ok = self.printer_adapter.print_thank_you()

        if ok:
            self._receipt_printed = True
        return ok
    
    def initialize(self) -> bool:
        """
        Initialize servo controller
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Auto-detect port if enabled
            if self.auto_detect:
                detected_port = self._auto_detect_port()
                if detected_port:
                    self.port = detected_port
                    logger.info(f"Auto-detected servo Arduino on {self.port}")
            
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
                logger.info(f"Servo controller: {msg}")
            
            self._initialized = True
            self._running = True
            
            # Start background thread to read serial messages
            self._read_thread = threading.Thread(target=self._read_serial, daemon=True)
            self._read_thread.start()
            
            logger.info(f"Servo adapter initialized on {self.port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Failed to open servo serial port {self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error initializing servo adapter: {e}")
            return False
    
    def set_pump_adapter(self, pump_adapter):
        """Set the pump adapter for bridging pump commands"""
        self.pump_adapter = pump_adapter
        logger.info("Pump adapter linked to servo adapter")
        
        # Register callback for when pump deactivation is complete
        if self.pump_adapter:
            logger.info(f"Registering callback: {self._on_pump_deactivation_complete}")
            print(f"\n🔗 Registering printer callback with pump adapter...")
            self.pump_adapter.register_deactivation_callback(self._on_pump_deactivation_complete)
            logger.info("Pump deactivation callback registered successfully")
            print("✅ Callback registered!")
    
    def set_printer_adapter(self, printer_adapter):
        """Set the thermal printer adapter for printing thank you messages"""
        self.printer_adapter = printer_adapter
        logger.info("Thermal printer adapter linked to servo adapter")
    
    def _on_pump_deactivation_complete(self):
        """Called when pump has finished deactivating (releasing object)"""
        if self._receipt_printed:
            logger.info("Pump deactivation callback received but receipt already printed - skipping")
            return

        logger.info("\n" + "="*60)
        logger.info("CALLBACK TRIGGERED: Pump deactivation complete - triggering printer")
        logger.info("="*60)
        print("\n" + "="*60)
        print("🖨️  PUMP RELEASED - PRINTING THANK YOU MESSAGE")
        print("="*60)
        
        if self.printer_adapter:
            logger.info(f"Printer adapter found: {self.printer_adapter}")
            print(f"🖨️  Printer adapter: {self.printer_adapter.get_printer_info()}")
            print("📝 Starting print job...")
            result = self._print_receipt_once()
            if result:
                print("✅ Print job completed!")
            else:
                print("❌ Print job failed!")
        else:
            logger.warning("No printer adapter available")
            print("⚠️  No printer adapter available")
    
    def register_status_callback(self, callback: Callable):
        """Register callback for status updates from Arduino"""
        self._status_callback = callback
    
    def register_button_callback(self, callback: Callable):
        """Register callback for button events from Arduino"""
        self._button_callback = callback
    
    def register_invite_callback(self, callback: Callable):
        """Register callback for proximity invite events from Arduino"""
        self._invite_callback = callback
    
    def register_relay_callback(self, callback: Callable):
        """Register callback for relay status events from Arduino"""
        self._relay_callback = callback
    
    def _read_serial(self):
        """Background thread to read serial messages from Stage 1 Arduino"""
        while self._running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        self._process_serial_message(line)
                time.sleep(0.01)
            except Exception as e:
                if self._running:
                    logger.error(f"Error reading servo serial: {e}")
                break
    
    def _process_serial_message(self, message: str):
        """Process incoming serial message from Stage 1 Arduino"""
        logger.info(f"[STAGE1] {message}")
        print(f"🤖 [STAGE1] {message}")
        
        try:
            data = json.loads(message)
            
            # Handle pump activation requests
            action = data.get('action', '')
            if action == 'activate_pump':
                print("\n" + "="*60)
                print("💨 STAGE 1 REQUESTING PUMP ACTIVATION!")
                print("="*60)
                if self.pump_adapter:
                    print(f"   Pump adapter found: {self.pump_adapter}")
                    print(f"   Pump initialized: {self.pump_adapter._initialized}")
                    result = self.pump_adapter.activate_pump()
                    print(f"   Activation result: {'✅ Success' if result else '❌ Failed'}")
                else:
                    logger.warning("No pump adapter connected!")
                    print("⚠️  No pump adapter connected to servo adapter!")
                    print("   Check if pump was initialized and linked properly")
            
            elif action == 'deactivate_pump':
                print("\n" + "="*60)
                print("🔓 STAGE 1 REQUESTING PUMP DEACTIVATION!")
                print("="*60)
                if self.pump_adapter:
                    result = self.pump_adapter.deactivate_pump()
                    print(f"   Deactivation command sent: {'✅ Success' if result else '❌ Failed'}")
                    print("   Waiting for pump to finish releasing...")
                    # Note: Printer will be triggered by callback when pump confirms deactivation
                else:
                    logger.warning("No pump adapter connected!")
                    print("⚠️  No pump adapter connected!")
            
            # Handle button press
            button = data.get('button', '')
            if button == 'pressed':
                print("\n" + "="*60)
                print("🔘 BUTTON PRESSED ON STAGE 1!")
                print("="*60)
                if self._button_callback:
                    self._button_callback({'button': 'pressed'})
            
            # Handle status updates
            status = data.get('status', '')
            if status:
                print(f"   Status: {status}")
                if self._status_callback:
                    self._status_callback({'status': status})
                
                # Special handling for game_initiated
                if status == 'game_initiated':
                    print("\n" + "="*60)
                    print("🎮 GAME INITIATED - SG90 dance complete!")
                    print("   Waiting for game result...")
                    print("="*60)
                
                # Special handling for sequence_complete (WIN finished)
                if status == 'sequence_complete':
                    if self._receipt_printed:
                        logger.info("sequence_complete received but receipt already printed - skipping")
                        return
                    print("\n" + "="*60)
                    print("🏆 WIN SEQUENCE COMPLETE!")
                    print("🖨️  PRINTING THANK YOU MESSAGE...")
                    print("="*60)
                    
                    # Trigger printer when win sequence is complete
                    if self.printer_adapter:
                        result = self._print_receipt_once()
                        if result:
                            print("✅ Print job completed!")
                        else:
                            print("❌ Print job failed!")
                    else:
                        print("⚠️  No printer adapter available")
            
            # Handle proximity invite messages
            invite = data.get('invite', None)
            if invite is not None:
                if invite:
                    print(f"👋 Proximity detected - Showing invite: {invite}")
                else:
                    print("👋 User moved away - Hiding invite")
                if self._invite_callback:
                    self._invite_callback({'invite': invite})
            
            # Handle relay status
            relay = data.get('relay', '')
            if relay:
                print(f"🔌 Relay status: {relay}")
                if self._relay_callback:
                    self._relay_callback({'relay': relay})
        
        except json.JSONDecodeError:
            # Not JSON, just log it
            pass
    
    def stop(self):
        """Stop servo controller"""
        logger.info("Stopping servo adapter...")
        self._running = False
        
        # Stop all motors
        if self._initialized:
            self.stop_motors()
            self.reset_sequence()
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        self._initialized = False
        logger.info("Servo adapter stopped")
    
    def activate_left_motor(self):
        """
        Activate left motor (servo1 only)
        Servo1 moves, Servo2 stays neutral for 5 seconds
        """
        if not self._initialized:
            logger.warning("Servo adapter not initialized")
            print("⚠️  Servo adapter not initialized!")
            return False
        
        try:
            self.serial_connection.write(b"LEFT_MOTOR\n")
            logger.info("Left motor activated")
            print("📤 Sent command: LEFT_MOTOR to COM4")
            return True
        except Exception as e:
            logger.error(f"Error activating left motor: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def activate_right_motor(self):
        """
        Activate right motor (servo2 only)
        Servo1 stays neutral, Servo2 moves for 5 seconds
        """
        if not self._initialized:
            logger.warning("Servo adapter not initialized")
            print("⚠️  Servo adapter not initialized!")
            return False
        
        try:
            self.serial_connection.write(b"RIGHT_MOTOR\n")
            logger.info("Right motor activated")
            print("📤 Sent command: RIGHT_MOTOR to COM4")
            return True
        except Exception as e:
            logger.error(f"Error activating right motor: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def stop_motors(self):
        """Stop all motors immediately"""
        if not self._initialized:
            return False
        
        try:
            self.serial_connection.write(b"STOP\n")
            logger.info("Motors stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping motors: {e}")
            return False
    
    def activate_motor_by_score(self, score: int):
        """
        Activate motor based on game score
        
        Args:
            score: Game score
                < 10: User lost - send LOSE command
                >= 10: User won - send WIN command to trigger full sequence
        """
        print("\n" + "="*60)
        print(f"🤖 GAME RESULT - SCORE: {score}")
        print("="*60)
        
        if not self._initialized:
            logger.error("Servo adapter not initialized! Cannot send command.")
            print("❌ ERROR: Servo adapter not initialized!")
            return False
        
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("Serial connection not open! Cannot send command.")
            print("❌ ERROR: Serial connection not open!")
            return False
        
        if score < 10:
            print(f"😢 Score {score} < 10: USER LOST")
            logger.info(f"Score {score} < 10: Sending LOSE command")
            try:
                self.serial_connection.write(b"LOSE\n")
                self.serial_connection.flush()
                print("📤 Sent: LOSE to Stage 1")
                return True
            except Exception as e:
                logger.error(f"Failed to send LOSE command: {e}")
                print(f"❌ Error sending LOSE: {e}")
                return False
        else:
            print(f"🏆 Score {score} >= 10: USER WON!")
            print("   Triggering full win sequence:")
            print("   → 360° servo dance")
            print("   → Arm pick down")
            print("   → Suction pump activation")
            print("   → Arm lift with object")
            print("   → Release")
            logger.info(f"Score {score} >= 10: Sending WIN command to Stage 1")
            try:
                self.serial_connection.write(b"WIN\n")
                self.serial_connection.flush()
                print("📤 Sent: WIN to Stage 1")
                return True
            except Exception as e:
                logger.error(f"Failed to send WIN command: {e}")
                print(f"❌ Error sending WIN: {e}")
                return False
    
    def reset_sequence(self):
        """Reset Stage 1 Arduino to idle state"""
        if not self._initialized:
            return False
        
        try:
            self.serial_connection.write(b"RESET\n")
            self.serial_connection.flush()
            logger.info("Reset command sent to Stage 1")
            print("📤 Sent: RESET to Stage 1")
            return True
        except Exception as e:
            logger.error(f"Error sending reset: {e}")
            return False
    
    def _gate_sequence(self):
        """
        Gate sequence for winning:
        1. Move servo1 one direction for 5 seconds (open gate)
        2. Stop for 2 seconds (gate stays open)
        3. Move servo1 opposite direction for 5 seconds (close gate)
        """
        if not self._initialized:
            logger.warning("Servo adapter not initialized for gate sequence")
            return False
        
        try:
            print("\n" + "="*60)
            print("🚪 GATE SEQUENCE STARTED - USER WON!")
            print("="*60)
            
            # Delegate timing to Arduino for smooth movement on continuous-rotation servo
            print("\n▶️  Running gate sequence on Arduino (5s left slow, 2s stop, 5s right slow)...")
            logger.info("Gate sequence: Delegating to Arduino via GATE_SEQUENCE")
            self.serial_connection.write(b"GATE_SEQUENCE\n")
            return True
            
        except Exception as e:
            logger.error(f"Error in gate sequence: {e}")
            print(f"❌ Gate sequence error: {e}")
            return False
    
    def _auto_detect_port(self) -> Optional[str]:
        """
        Auto-detect Arduino port
        
        Returns:
            Port name if found, None otherwise
        """
        logger.info("Auto-detecting servo Arduino port...")
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            logger.debug(f"Found port: {port.device} - {port.description}")
            
            # Look for Arduino-like devices
            if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'usb serial']):
                # Prefer COM3 for servo controller
                if port.device == "COM3":
                    logger.info(f"Servo Arduino found on COM3")
                    return port.device
        
        # If COM3 not found, return first Arduino-like device
        for port in ports:
            if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'usb serial']):
                logger.info(f"Potential servo Arduino found: {port.device}")
                return port.device
        
        logger.warning("No servo Arduino port auto-detected")
        return None
    
    def get_output_info(self) -> dict:
        """Get servo adapter information"""
        return {
            'type': 'Servo Controller',
            'port': self.port,
            'baud_rate': self.baud_rate,
            'status': 'initialized' if self._initialized else 'not initialized',
            'connected': self.serial_connection.is_open if self.serial_connection else False
        }
