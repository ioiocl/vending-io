"""
Application Layer - Orchestrates the hexagonal architecture
This is where all the pieces come together
"""
import logging
from typing import Optional

from src.adapters.input.arduino_adapter import ArduinoAdapter
from src.adapters.input.button_adapter import ButtonAdapter
from src.adapters.output.local_audio_adapter import LocalAudioAdapter
from src.adapters.output.servo_adapter import ServoAdapter
from src.adapters.output.pump_adapter import PumpAdapter
from src.adapters.output.thermal_printer_adapter_win import ThermalPrinterAdapter
from src.core.domain import SoundOrchestrator, ProximityEvent, SoundEvent
from src.core.ports import InputPort, OutputPort

try:
    from src.adapters.output.web_visualizer_adapter import WebVisualizerAdapter
    WEB_VISUALIZER_AVAILABLE = True
except ImportError:
    WEB_VISUALIZER_AVAILABLE = False

logger = logging.getLogger(__name__)


class MusicMachineApplication:
    """
    Main application that wires together the hexagonal architecture
    
    Architecture:
    - Core: Sound Orchestrator (coordinates multiple sounds)
    - Ports: Interfaces (contracts)
    - Adapters: Implementations (Arduino input, local audio output)
    """
    
    def __init__(
        self,
        input_adapter: Optional[InputPort] = None,
        output_adapter: Optional[OutputPort] = None,
        enable_visualizer: bool = False,
        enable_button: bool = False,
        enable_servo: bool = False,
        enable_pump: bool = False,
        enable_printer: bool = False,
        printer_port: Optional[str] = None
    ):
        """
        Initialize the application
        
        Args:
            input_adapter: Input adapter (defaults to ArduinoAdapter)
            output_adapter: Output adapter (defaults to LocalAudioAdapter)
            enable_visualizer: Enable web visualizer
            enable_button: Enable button controller (COM7)
            enable_servo: Enable servo controller - Stage 1 (COM7)
            enable_pump: Enable pump controller - Stage 2 (COM4)
            enable_printer: Enable thermal printer (Windows printer API)
            printer_port: Windows printer name (e.g., 'Generic / Text Only'). If None, auto-detect USB printer
        """
        logger.info("Initializing Music Machine Application with Orchestrator")
        
        # Core domain - Sound Orchestrator
        self.orchestrator = SoundOrchestrator(max_simultaneous_sounds=8)
        
        # Adapters (dependency injection)
        # No proximity sensor - only button and servo
        self.input_adapter = input_adapter  # Optional, can be None
        self.output_adapter = output_adapter or LocalAudioAdapter()
        
        # Button adapter (optional) - DISABLED when using Stage 1 servo adapter
        # Stage 1 Arduino handles button internally and sends events via serial
        self.button_adapter = None
        if enable_button and not enable_servo:
            # Only enable separate button adapter if servo is not enabled
            self.button_adapter = ButtonAdapter(port="COM7", auto_detect=True)
            logger.info("Button adapter enabled (preferred port COM7, auto-detect ON)")
        elif enable_button and enable_servo:
            logger.info("Button adapter SKIPPED - Stage 1 servo adapter handles button on COM7")
        
        # Servo adapter (Stage 1 - COM7) - handles button, SG90, 360° servo, arm
        self.servo_adapter = None
        if enable_servo:
            self.servo_adapter = ServoAdapter(port="COM7", auto_detect=False)
            logger.info("Servo adapter (Stage 1) enabled on COM7")
        
        # Pump adapter (Stage 2 - COM4)
        self.pump_adapter = None
        if enable_pump:
            self.pump_adapter = PumpAdapter(port="COM4")
            logger.info("Pump adapter (Stage 2) enabled on COM4")
        
        # Thermal printer adapter (Windows printer API)
        self.printer_adapter = None
        if enable_printer:
            # Use Windows printer name instead of COM port
            self.printer_adapter = ThermalPrinterAdapter(
                printer_name=printer_port  # printer_port now means Windows printer name
            )
            if printer_port:
                logger.info(f"Thermal printer adapter enabled (printer: {printer_port})")
            else:
                logger.info("Thermal printer adapter enabled (auto-detect USB printer)")
        
        # Web visualizer (optional)
        self.visualizer = None
        if enable_visualizer and WEB_VISUALIZER_AVAILABLE:
            self.visualizer = WebVisualizerAdapter()
            logger.info("Web visualizer enabled")
        
        # Register event listeners
        self.orchestrator.register_event_listener(self._handle_domain_event)
        
        # Game state
        self._game_active = False
        self._game_score = 0
        
        self._running = False
        
    def start(self):
        """Start the music machine"""
        logger.info("=" * 60)
        logger.info("Starting Music Machine")
        logger.info("=" * 60)
        
        try:
            # Initialize output first
            logger.info("Initializing audio output...")
            if not self.output_adapter.initialize():
                raise RuntimeError("Failed to initialize audio output")
            
            logger.info(f"Audio output info: {self.output_adapter.get_output_info()}")
            
            # Initialize thermal printer adapter if enabled
            # IMPORTANT: Initialize printer BEFORE pump to avoid COM port conflicts
            if self.printer_adapter:
                logger.info("Initializing thermal printer...")
                print("🖨️  Initializing thermal printer...")
                if not self.printer_adapter.initialize():
                    logger.warning("Failed to initialize thermal printer")
                    print("⚠️  Failed to initialize thermal printer (will continue without it)")
                else:
                    logger.info(f"Printer info: {self.printer_adapter.get_printer_info()}")
                    print(f"✅ Thermal printer initialized: {self.printer_adapter.get_printer_info()}")
                
                # Small delay to ensure printer port is fully released
                import time
                time.sleep(0.5)
            
            # Initialize pump adapter if enabled (Stage 2 - COM4)
            pump_initialized = False
            if self.pump_adapter:
                logger.info("Initializing pump controller (Stage 2 - COM4)...")
                print("💨 Initializing pump controller on COM4...")
                if not self.pump_adapter.initialize():
                    logger.warning("Failed to initialize pump controller")
                    print("⚠️  Failed to initialize pump controller on COM4")
                else:
                    pump_initialized = True
                    logger.info(f"Pump info: {self.pump_adapter.get_output_info()}")
                    print(f"✅ Pump controller initialized: {self.pump_adapter.get_output_info()}")
            
            # Initialize servo adapter if enabled (Stage 1 - COM7)
            if self.servo_adapter:
                logger.info("Initializing servo controller (Stage 1 - COM7)...")
                print("🤖 Initializing servo controller on COM7...")
                if not self.servo_adapter.initialize():
                    logger.warning("Failed to initialize servo controller")
                    print("⚠️  Failed to initialize servo controller on COM7")
                else:
                    logger.info(f"Servo info: {self.servo_adapter.get_output_info()}")
                    print(f"✅ Servo controller initialized: {self.servo_adapter.get_output_info()}")
                
                # Link pump adapter to servo adapter for bridging (even if servo had issues)
                if self.pump_adapter and pump_initialized:
                    self.servo_adapter.set_pump_adapter(self.pump_adapter)
                    logger.info("Pump adapter linked to servo adapter for command bridging")
                    print("🔗 Pump adapter linked to servo adapter")
                elif self.pump_adapter:
                    print("⚠️  Pump adapter NOT linked (pump not initialized)")
                
                # Link thermal printer adapter to servo adapter
                if self.printer_adapter:
                    self.servo_adapter.set_printer_adapter(self.printer_adapter)
                    logger.info("Thermal printer adapter linked to servo adapter")
                    print("🔗 Thermal printer adapter linked to servo adapter")
                
                # Register button callback from Stage 1 Arduino
                self.servo_adapter.register_button_callback(self._handle_stage1_button)
                logger.info("Button callback registered with servo adapter")
                
                # Register invite callback for proximity sensor
                self.servo_adapter.register_invite_callback(self._handle_proximity_invite)
                logger.info("Proximity invite callback registered with servo adapter")
            
            # Start proximity sensor input adapter if provided
            if self.input_adapter:
                logger.info("Starting proximity sensor input adapter...")
                self.input_adapter.register_callback(self._handle_input_event)
                self.input_adapter.start()
                logger.info(f"Input adapter info: {self.input_adapter.get_sensor_info()}")
            
            # Start button adapter if enabled
            if self.button_adapter:
                logger.info("Starting button controller...")
                logger.info(f"[APP] Registering button callback: {self._handle_button_event}")
                self.button_adapter.register_callback(self._handle_button_event)
                logger.info("[APP] Button callback registered successfully")
                self.button_adapter.start()
                logger.info(f"Button info: {self.button_adapter.get_sensor_info()}")
            
            # Register game callbacks with visualizer
            if self.visualizer:
                self.visualizer.register_game_callbacks(
                    game_start_callback=self._handle_game_start,
                    game_over_callback=self._handle_game_over
                )
            
            self._running = True
            
            logger.info("=" * 60)
            logger.info("Music Machine with Game Controls is RUNNING!")
            if self.input_adapter:
                logger.info("Proximity sensor: Move your hand near sensor to create music")
            if self.button_adapter:
                logger.info("Button controller: Press button to start game")
            if self.servo_adapter:
                logger.info("Stage 1 (COM7): Servo controller - SG90 dance, 360° servo, robotic arm")
            if self.pump_adapter:
                logger.info("Stage 2 (COM4): Pump controller - Suction pump and valve")
            if self.printer_adapter:
                logger.info(f"Thermal Printer ({self.printer_adapter.printer_name}): Thank you message printing")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the music machine"""
        logger.info("Stopping Music Machine...")
        
        self._running = False
        
        try:
            if self.input_adapter:
                self.input_adapter.stop()
        except Exception as e:
            logger.error(f"Error stopping input adapter: {e}")
        
        try:
            if self.button_adapter:
                self.button_adapter.stop()
        except Exception as e:
            logger.error(f"Error stopping button adapter: {e}")
        
        try:
            if self.output_adapter:
                self.output_adapter.stop()
        except Exception as e:
            logger.error(f"Error stopping output adapter: {e}")
        
        try:
            if self.servo_adapter:
                self.servo_adapter.stop()
        except Exception as e:
            logger.error(f"Error stopping servo adapter: {e}")
        
        try:
            if self.pump_adapter:
                self.pump_adapter.stop()
        except Exception as e:
            logger.error(f"Error stopping pump adapter: {e}")
        
        try:
            if self.printer_adapter:
                self.printer_adapter.stop()
        except Exception as e:
            logger.error(f"Error stopping printer adapter: {e}")
        
        logger.info("Music Machine stopped")
    
    def is_running(self) -> bool:
        """Check if application is running"""
        return self._running
    
    def _handle_input_event(self, proximity_event: ProximityEvent):
        """
        Handle input events from the input adapter
        This is the entry point from the outside world into the core domain
        """
        logger.debug(f"Input event received: {proximity_event.distance}cm")
        
        # Visualize proximity event
        if self.visualizer:
            self.visualizer.visualize_proximity(proximity_event)
        
        # Pass event to orchestrator (core domain)
        # Orchestrator processes and returns all active sounds for mixing
        sound_events = self.orchestrator.process_proximity_event(
            proximity_event,
            source_id="arduino_proximity"
        )
        
        # Play all orchestrated sounds
        for sound_event in sound_events:
            self._play_sound(sound_event)
    
    def _handle_domain_event(self, event):
        """
        Handle domain events from the orchestrator
        This is for logging, monitoring, or triggering side effects
        """
        logger.debug(f"Domain event: {event.event_type.value}")
        
        # Could add more sophisticated event handling here
        # For example: logging to database, sending to monitoring system, etc.
    
    def _play_sound(self, sound_event: SoundEvent):
        """Play sound through output adapter"""
        try:
            # Visualize sound event
            if self.visualizer:
                self.visualizer.visualize_sound(sound_event)
            
            success = self.output_adapter.play_sound(sound_event)
            if not success:
                logger.warning("Failed to play sound")
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
    
    def get_status(self) -> dict:
        """Get application status"""
        return {
            "running": self._running,
            "orchestrator": self.orchestrator.get_status(),
            "input": self.input_adapter.get_sensor_info() if hasattr(self.input_adapter, 'get_sensor_info') else {},
            "output": self.output_adapter.get_output_info() if hasattr(self.output_adapter, 'get_output_info') else {},
        }
    
    def _handle_button_event(self, button_event):
        """
        Handle button press events
        Button press starts the game
        """
        from src.adapters.input.button_adapter import ButtonEvent
        
        logger.info(f"[BUTTON EVENT] Received event: {button_event}")
        print(f"\n{'='*60}")
        print(f"[BUTTON EVENT] Event received: {button_event}")
        print(f"{'='*60}\n")
        
        if isinstance(button_event, ButtonEvent):
            logger.info(f"[BUTTON EVENT] Event is ButtonEvent, state: {button_event.button_state}")
            print(f"Button state: {button_event.button_state}")
            
            if button_event.button_state == "pressed":
                logger.info("🎮 Button pressed - Starting game!")
                print("\n" + "="*60)
                print("🎮 BUTTON PRESSED - STARTING GAME!")
                print("="*60 + "\n")
                self._game_active = True
                self._game_score = 0
                
                # Emit game start to web visualizer
                if self.visualizer:
                    logger.info("[BUTTON EVENT] Emitting game_start_trigger to web visualizer")
                    print("Sending game start signal to web visualizer...")
                    self.visualizer.socketio.emit('game_start_trigger', {
                        'timestamp': button_event.timestamp.isoformat()
                    })
                    print("✅ Game start signal sent!")
                else:
                    logger.warning("[BUTTON EVENT] No visualizer available to send game start")
            else:
                logger.info(f"[BUTTON EVENT] Button state is '{button_event.button_state}', not 'pressed'")
        else:
            logger.warning(f"[BUTTON EVENT] Event is not ButtonEvent, type: {type(button_event)}")
    
    def _handle_stage1_button(self, data):
        """
        Handle button press from Stage 1 Arduino (via servo adapter)
        This is called when the physical button on Stage 1 is pressed
        """
        button = data.get('button', '')
        if button == 'pressed':
            logger.info("🔘 Physical button pressed on Stage 1 Arduino")
            print("\n" + "="*60)
            print("🔘 PHYSICAL BUTTON PRESSED - Stage 1 will do SG90 dance")
            print("="*60)
            self._game_active = True
            self._game_score = 0
            
            # Emit game start to web visualizer
            if self.visualizer:
                logger.info("Emitting game_start_trigger to web visualizer")
                self.visualizer.socketio.emit('game_start_trigger', {
                    'source': 'physical_button'
                })
    
    def _handle_proximity_invite(self, data):
        """
        Handle proximity invite from Stage 1 Arduino (via servo adapter)
        Shows/hides "Ven a Jugar" text on web visualizer when user is within 50cm
        """
        invite = data.get('invite', '')
        if invite:
            logger.info(f"👋 Proximity invite: {invite}")
            print(f"👋 Showing invite text: {invite}")
        else:
            logger.info("👋 Hiding proximity invite")
            print("👋 Hiding invite text")
        
        # Emit invite event to web visualizer
        if self.visualizer:
            self.visualizer.socketio.emit('proximity_invite', {
                'invite': invite
            })
    
    def _handle_game_start(self, data):
        """
        Handle game start event from web visualizer
        """
        logger.info("🎮 Game started from web interface")
        self._game_active = True
        self._game_score = 0
    
    def _handle_game_over(self, data):
        """
        Handle game over event from web visualizer
        Activates servo based on final score
        """
        score = data.get('score', 0)
        logger.info(f"🏁 Game over! Final score: {score}")
        print("\n" + "="*60)
        print(f"🏁 GAME OVER - Final Score: {score}")
        print("="*60)
        
        self._game_active = False
        self._game_score = score
        
        # Activate servo based on score
        if self.servo_adapter:
            logger.info(f"Activating servo motor based on score: {score}")
            print(f"📤 Sending score {score} to servo adapter...")
            result = self.servo_adapter.activate_motor_by_score(score)
            print(f"   Result: {'✅ Success' if result else '❌ Failed'}")
        else:
            logger.warning("No servo adapter available!")
            print("⚠️  WARNING: No servo adapter available!")
    
    def test_audio(self):
        """Test audio output with a simple tone"""
        logger.info("Testing audio output...")
        if hasattr(self.output_adapter, 'test_sound'):
            self.output_adapter.test_sound()
        else:
            # Fallback test
            test_event = SoundEvent(frequency=440.0, duration=0.5, amplitude=0.5)
            self.output_adapter.play_sound(test_event)
