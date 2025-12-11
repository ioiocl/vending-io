"""
Webcam Adapter - Hand detection input
Detects hand gestures using MediaPipe
"""
import logging
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass

try:
    import cv2
    import mediapipe as mp
    WEBCAM_AVAILABLE = True
except ImportError:
    WEBCAM_AVAILABLE = False
    print("Webcam support not available. Install: pip install opencv-python mediapipe")

from src.core.ports.input_port import SensorInputPort
from src.core.domain.events import ProximityEvent

logger = logging.getLogger(__name__)


@dataclass
class HandGesture:
    """Represents a detected hand gesture"""
    hand_raised: bool
    hand_position: tuple  # (x, y) normalized 0-1
    confidence: float
    timestamp: float


class WebcamAdapter(SensorInputPort):
    """
    Webcam adapter for hand detection
    Uses MediaPipe for real-time hand tracking
    """
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize webcam adapter
        
        Args:
            camera_index: Camera device index (0 for default)
        """
        if not WEBCAM_AVAILABLE:
            raise ImportError("OpenCV and MediaPipe required. Install: pip install opencv-python mediapipe")
        
        self.camera_index = camera_index
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = None
        self._running = False
        self._thread = None
        self._callback: Optional[Callable] = None
        
        # Hand detection state
        self.last_hand_raised = False
        self.hand_raise_threshold = 0.3  # Y position threshold (lower = higher in frame)
        
        logger.info(f"Webcam adapter initialized (camera {camera_index})")
    
    def register_callback(self, callback: Callable):
        """Register callback for hand gesture events"""
        self._callback = callback
        logger.info("Callback registered for webcam events")
    
    def start(self):
        """Start webcam capture and hand detection"""
        if self._running:
            logger.warning("Webcam adapter already running")
            return
        
        try:
            # Initialize webcam
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise RuntimeError(f"Could not open camera {self.camera_index}")
            
            # Initialize MediaPipe Hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self._running = True
            
            # Start detection thread
            self._thread = threading.Thread(target=self._detection_loop, daemon=True)
            self._thread.start()
            
            logger.info("Webcam adapter started")
            
        except Exception as e:
            logger.error(f"Failed to start webcam adapter: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop webcam capture"""
        logger.info("Stopping webcam adapter...")
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=2.0)
        
        if self.hands:
            self.hands.close()
        
        if self.cap:
            self.cap.release()
        
        logger.info("Webcam adapter stopped")
    
    def _detection_loop(self):
        """Main detection loop (runs in background thread)"""
        logger.info("Hand detection loop started")
        
        while self._running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from webcam")
                    time.sleep(0.1)
                    continue
                
                # Flip frame horizontally for mirror view
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame with MediaPipe
                results = self.hands.process(rgb_frame)
                
                # Detect hand gestures
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self._process_hand(hand_landmarks)
                else:
                    # No hand detected
                    if self.last_hand_raised:
                        self.last_hand_raised = False
                        logger.debug("Hand lowered")
                
                # Small delay to control frame rate
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(0.1)
        
        logger.info("Hand detection loop ended")
    
    def _process_hand(self, hand_landmarks):
        """
        Process detected hand landmarks
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
        """
        # Get wrist position (landmark 0)
        wrist = hand_landmarks.landmark[0]
        
        # Get middle finger tip (landmark 12)
        middle_finger_tip = hand_landmarks.landmark[12]
        
        # Check if hand is raised (middle finger tip is above wrist)
        hand_raised = middle_finger_tip.y < self.hand_raise_threshold
        
        # Detect hand raise event (transition from down to up)
        if hand_raised and not self.last_hand_raised:
            logger.info("✋ Hand raised detected!")
            
            # Create gesture event
            gesture = HandGesture(
                hand_raised=True,
                hand_position=(middle_finger_tip.x, middle_finger_tip.y),
                confidence=1.0,
                timestamp=time.time()
            )
            
            # Trigger callback
            if self._callback:
                # Convert to ProximityEvent for compatibility
                # Use Y position as "distance" (inverted)
                distance = (1.0 - middle_finger_tip.y) * 50  # 0-50cm range
                
                event = ProximityEvent(
                    distance=distance,
                    sensor_id="webcam_hand",
                    metadata={
                        'hand_position': (middle_finger_tip.x, middle_finger_tip.y),
                        'gesture': 'hand_raised'
                    }
                )
                
                self._callback(event)
        
        self.last_hand_raised = hand_raised
    
    def get_sensor_info(self) -> dict:
        """Get webcam sensor information"""
        return {
            'type': 'Webcam Hand Detection',
            'camera_index': self.camera_index,
            'status': 'running' if self._running else 'stopped',
            'hand_detected': self.last_hand_raised
        }
    
    def is_available(self) -> bool:
        """Check if webcam is available"""
        return WEBCAM_AVAILABLE and self._running
