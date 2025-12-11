"""
Web Visualizer Adapter
Real-time visualization of sensor data with pulse effects
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime
import json
import asyncio
from pathlib import Path

try:
    from flask import Flask, render_template, jsonify
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Run: pip install flask flask-socketio")

from src.core.ports.output_port import VisualizationOutputPort
from src.core.domain.events import SoundEvent, ProximityEvent

logger = logging.getLogger(__name__)


class WebVisualizerAdapter(VisualizationOutputPort):
    """
    Web-based visualizer for sensor data
    Shows real-time pulses and allows joystick navigation
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """
        Initialize web visualizer
        
        Args:
            host: Host address
            port: Port number
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required. Install: pip install flask flask-socketio")
        
        self.host = host
        self.port = port
        self.app = Flask(__name__, 
                        template_folder=str(Path(__file__).parent.parent.parent.parent / "web" / "templates"),
                        static_folder=str(Path(__file__).parent.parent.parent.parent / "web" / "static"))
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self._running = False
        self._history: List[Dict] = []
        self._max_history = 100
        
        # Game event callbacks
        self.game_start_callback = None
        self.game_over_callback = None
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Web Visualizer initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('visualizer.html')
        
        @self.app.route('/game')
        def game():
            return render_template('game_visualizer.html')
        
        @self.app.route('/api/status')
        def status():
            return jsonify({
                'running': self._running,
                'history_count': len(self._history)
            })
        
        @self.app.route('/api/history')
        def history():
            return jsonify(self._history[-50:])  # Last 50 events
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info("Client connected to visualizer")
            emit('connected', {'status': 'ok'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("Client disconnected from visualizer")
        
        @self.socketio.on('joystick_input')
        def handle_joystick(data):
            """Handle joystick input from web client"""
            logger.debug(f"Joystick input: {data}")
            # Emit to all clients
            self.socketio.emit('joystick_event', data)
        
        @self.socketio.on('hand_raised')
        def handle_hand_raised(data):
            """Handle right hand raised event from webcam"""
            logger.info(f"Right hand raised detected: {data}")
            # Emit collectible spawn event
            self.socketio.emit('spawn_collectible', {
                'x': data.get('x', 0.5),
                'y': data.get('y', 0.5),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('hand_raised_left')
        def handle_hand_raised_left(data):
            """Handle left hand raised event from webcam"""
            logger.info(f"Left hand raised detected: {data}")
            # Emit enemy spawn event
            self.socketio.emit('spawn_enemy', {
                'x': data.get('x', 0.5),
                'y': data.get('y', 0.5),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('game_started')
        def handle_game_started(data):
            """Handle game start event"""
            logger.info(f"Game started: {data}")
            # Store game start callback if registered
            if hasattr(self, 'game_start_callback') and self.game_start_callback:
                self.game_start_callback(data)
        
        @self.socketio.on('game_over')
        def handle_game_over(data):
            """Handle game over event with final score"""
            logger.info(f"Game over - Score: {data.get('score', 0)}")
            # Store game over callback if registered
            if hasattr(self, 'game_over_callback') and self.game_over_callback:
                self.game_over_callback(data)
    
    def initialize(self) -> bool:
        """Initialize the visualizer"""
        try:
            self._running = True
            logger.info("Web Visualizer initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize visualizer: {e}")
            return False
    
    def stop(self):
        """Stop the visualizer"""
        self._running = False
        logger.info("Web Visualizer stopped")
    
    def visualize_proximity(self, proximity_event: ProximityEvent):
        """
        Visualize proximity event with pulse effect
        
        Args:
            proximity_event: Proximity event to visualize
        """
        if not self._running:
            return
        
        # Create visualization data
        data = {
            'type': 'proximity',
            'distance': proximity_event.distance,
            'sensor_id': proximity_event.sensor_id,
            'timestamp': datetime.now().isoformat(),
            'pulse_intensity': self._calculate_pulse_intensity(proximity_event.distance)
        }
        
        # Add to history
        self._history.append(data)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # Emit to web clients
        try:
            self.socketio.emit('proximity_pulse', data)
            logger.debug(f"Emitted proximity pulse: {proximity_event.distance}cm")
        except Exception as e:
            logger.error(f"Error emitting proximity pulse: {e}")
    
    def visualize_sound(self, sound_event: SoundEvent):
        """
        Visualize sound event
        
        Args:
            sound_event: Sound event to visualize
        """
        if not self._running:
            return
        
        data = {
            'type': 'sound',
            'frequency': sound_event.frequency,
            'duration': sound_event.duration,
            'amplitude': sound_event.amplitude,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to history
        self._history.append(data)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # Emit to web clients
        try:
            self.socketio.emit('sound_event', data)
            logger.debug(f"Emitted sound event: {sound_event.frequency}Hz")
        except Exception as e:
            logger.error(f"Error emitting sound event: {e}")
    
    def _calculate_pulse_intensity(self, distance: float) -> float:
        """
        Calculate pulse intensity based on distance
        Closer = stronger pulse
        
        Args:
            distance: Distance in cm
        
        Returns:
            Intensity from 0.0 to 1.0
        """
        if distance <= 0:
            return 0.0
        
        # Inverse relationship: closer = stronger
        max_distance = 50.0
        intensity = 1.0 - (min(distance, max_distance) / max_distance)
        return max(0.0, min(1.0, intensity))
    
    def run(self):
        """Run the web server (blocking)"""
        logger.info(f"Starting Web Visualizer on http://{self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=False, allow_unsafe_werkzeug=True)
    
    def register_game_callbacks(self, game_start_callback=None, game_over_callback=None):
        """
        Register callbacks for game events
        
        Args:
            game_start_callback: Called when game starts
            game_over_callback: Called when game ends with score
        """
        self.game_start_callback = game_start_callback
        self.game_over_callback = game_over_callback
        logger.info("Game callbacks registered")
    
    def get_output_info(self) -> dict:
        """Get visualizer information"""
        return {
            'type': 'Web Visualizer',
            'host': self.host,
            'port': self.port,
            'url': f'http://{self.host}:{self.port}',
            'status': 'running' if self._running else 'stopped',
            'history_count': len(self._history)
        }
