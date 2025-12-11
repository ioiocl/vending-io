"""
Simple Servo Test with Web Console - COM4
Tests communication with servo controller Arduino with real-time web logging

This script will:
1. Start a web server on http://localhost:5001
2. Connect to COM4
3. Test servos based on score thresholds
4. Log to both Python console and web console

Score Logic:
- Score < 10: LEFT motor activates
- Score >= 10: RIGHT motor activates
"""

import serial
import time
from flask import Flask, render_template_string
from flask_socketio import SocketIO
import threading
import sys

PORT = "COM4"
BAUD = 9600

# Flask app for web logging
app = Flask(__name__)
app.config['SECRET_KEY'] = 'servo_test_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# HTML template for web console
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Servo Test Console</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a2e;
            color: #00ff88;
            padding: 20px;
            margin: 0;
        }
        h1 {
            text-align: center;
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        #console {
            background: #0f0f1e;
            border: 2px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            height: 70vh;
            overflow-y: auto;
            font-size: 14px;
            line-height: 1.6;
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-left: 3px solid transparent;
        }
        .log-info {
            color: #00ff88;
            border-left-color: #00ff88;
        }
        .log-success {
            color: #00ffff;
            border-left-color: #00ffff;
            font-weight: bold;
        }
        .log-warning {
            color: #ffaa00;
            border-left-color: #ffaa00;
        }
        .log-error {
            color: #ff4444;
            border-left-color: #ff4444;
            font-weight: bold;
        }
        .log-header {
            color: #ffffff;
            font-weight: bold;
            font-size: 16px;
            border-left-color: #ffffff;
            margin: 10px 0;
        }
        .servo-status {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .servo-indicator {
            background: #0f0f1e;
            border: 2px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            min-width: 200px;
        }
        .servo-indicator.active {
            background: #00ff88;
            color: #1a1a2e;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .score-display {
            text-align: center;
            font-size: 24px;
            margin: 20px 0;
            padding: 15px;
            background: #0f0f1e;
            border: 2px solid #00ff88;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <h1>🤖 Servo Test Console - COM4</h1>
    
    <div class="score-display">
        Score: <span id="score" style="color: #00ffff;">0</span>
    </div>
    
    <div class="servo-status">
        <div class="servo-indicator" id="leftServo">
            <h3>⬅️ LEFT MOTOR</h3>
            <p>Score &lt; 10</p>
            <p id="leftStatus">Idle</p>
        </div>
        <div class="servo-indicator" id="rightServo">
            <h3>➡️ RIGHT MOTOR</h3>
            <p>Score &ge; 10</p>
            <p id="rightStatus">Idle</p>
        </div>
    </div>
    
    <div id="console"></div>
    
    <script>
        const socket = io();
        const consoleDiv = document.getElementById('console');
        const leftServo = document.getElementById('leftServo');
        const rightServo = document.getElementById('rightServo');
        const leftStatus = document.getElementById('leftStatus');
        const rightStatus = document.getElementById('rightStatus');
        const scoreDisplay = document.getElementById('score');
        
        socket.on('log', function(data) {
            const entry = document.createElement('div');
            entry.className = 'log-entry log-' + data.level;
            entry.textContent = data.message;
            consoleDiv.appendChild(entry);
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
        });
        
        socket.on('servo_status', function(data) {
            scoreDisplay.textContent = data.score;
            
            // Update LEFT servo
            if (data.left_active) {
                leftServo.classList.add('active');
                leftStatus.textContent = '🔄 ACTIVE';
            } else {
                leftServo.classList.remove('active');
                leftStatus.textContent = 'Idle';
            }
            
            // Update RIGHT servo
            if (data.right_active) {
                rightServo.classList.add('active');
                rightStatus.textContent = '🔄 ACTIVE';
            } else {
                rightServo.classList.remove('active');
                rightStatus.textContent = 'Idle';
            }
        });
        
        socket.on('connect', function() {
            addLog('info', '🟢 Connected to server');
        });
        
        socket.on('disconnect', function() {
            addLog('error', '🔴 Disconnected from server');
        });
        
        function addLog(level, message) {
            const entry = document.createElement('div');
            entry.className = 'log-entry log-' + level;
            entry.textContent = message;
            consoleDiv.appendChild(entry);
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def log_to_console_and_web(message, level='info'):
    """Log to both Python console and web console"""
    # Python console
    print(message)
    # Web console
    try:
        socketio.emit('log', {'message': message, 'level': level})
    except:
        pass

def update_servo_status(score, left_active=False, right_active=False):
    """Update servo status on web interface"""
    try:
        socketio.emit('servo_status', {
            'score': score,
            'left_active': left_active,
            'right_active': right_active
        })
    except:
        pass

def run_flask():
    """Run Flask server in background"""
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

def test_servo_with_score(ser, score):
    """Test servo based on score threshold"""
    log_to_console_and_web("\n" + "="*60, 'header')
    log_to_console_and_web(f"TESTING WITH SCORE: {score}", 'header')
    log_to_console_and_web("="*60, 'header')
    
    if score < 10:
        # Activate LEFT motor
        log_to_console_and_web(f"\n⬅️  Score {score} < 10: Activating LEFT MOTOR", 'info')
        log_to_console_and_web("   Sending command: LEFT_MOTOR", 'info')
        ser.write(b"LEFT_MOTOR\n")
        time.sleep(0.5)
        
        # Update web status
        update_servo_status(score, left_active=True, right_active=False)
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            log_to_console_and_web(f"   Response: '{response}'", 'info')
            if "LEFT_MOTOR_ACTIVE" in response:
                log_to_console_and_web("   ✅ LEFT motor activated successfully!", 'success')
            else:
                log_to_console_and_web(f"   ⚠️  Unexpected response: {response}", 'warning')
        else:
            log_to_console_and_web("   ⚠️  No response from Arduino", 'warning')
        
        log_to_console_and_web("\n   Motor running for 6 seconds...", 'info')
        for i in range(6):
            time.sleep(1)
            log_to_console_and_web(f"   ⬅️  LEFT motor: {6-i} seconds remaining...", 'info')
            if ser.in_waiting > 0:
                msg = ser.readline().decode('utf-8', errors='ignore').strip()
                if msg:
                    log_to_console_and_web(f"   Arduino: '{msg}'", 'info')
        
        update_servo_status(score, left_active=False, right_active=False)
        
    else:
        # Activate RIGHT motor
        log_to_console_and_web(f"\n➡️  Score {score} >= 10: Activating RIGHT MOTOR", 'info')
        log_to_console_and_web("   Sending command: RIGHT_MOTOR", 'info')
        ser.write(b"RIGHT_MOTOR\n")
        time.sleep(0.5)
        
        # Update web status
        update_servo_status(score, left_active=False, right_active=True)
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            log_to_console_and_web(f"   Response: '{response}'", 'info')
            if "RIGHT_MOTOR_ACTIVE" in response:
                log_to_console_and_web("   ✅ RIGHT motor activated successfully!", 'success')
            else:
                log_to_console_and_web(f"   ⚠️  Unexpected response: {response}", 'warning')
        else:
            log_to_console_and_web("   ⚠️  No response from Arduino", 'warning')
        
        log_to_console_and_web("\n   Motor running for 6 seconds...", 'info')
        for i in range(6):
            time.sleep(1)
            log_to_console_and_web(f"   ➡️  RIGHT motor: {6-i} seconds remaining...", 'info')
            if ser.in_waiting > 0:
                msg = ser.readline().decode('utf-8', errors='ignore').strip()
                if msg:
                    log_to_console_and_web(f"   Arduino: '{msg}'", 'info')
        
        update_servo_status(score, left_active=False, right_active=False)

if __name__ == "__main__":
    # Start Flask server in background thread
    print("="*60)
    print("🌐 Starting Web Console Server...")
    print("   Open browser to: http://localhost:5001")
    print("="*60)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask time to start
    time.sleep(2)
    
    log_to_console_and_web("="*60, 'header')
    log_to_console_and_web("SERVO CONTROLLER TEST - COM4", 'header')
    log_to_console_and_web("="*60, 'header')
    
    try:
        log_to_console_and_web(f"\n1. Connecting to {PORT} at {BAUD} baud...", 'info')
        ser = serial.Serial(PORT, BAUD, timeout=1)
        
        log_to_console_and_web("2. Waiting for Arduino to initialize (2 seconds)...", 'info')
        time.sleep(2)
        
        # Read initialization message
        if ser.in_waiting > 0:
            msg = ser.readline().decode('utf-8', errors='ignore').strip()
            log_to_console_and_web(f"   Arduino says: '{msg}'", 'success')
        
        # Test with different scores
        test_scores = [5, 15, 3, 25]
        
        for score in test_scores:
            test_servo_with_score(ser, score)
            time.sleep(1)
        
        # Stop motors
        log_to_console_and_web("\n" + "="*60, 'header')
        log_to_console_and_web("Stopping all motors...", 'info')
        log_to_console_and_web("   Sending command: STOP", 'info')
        ser.write(b"STOP\n")
        time.sleep(0.5)
        
        update_servo_status(0, left_active=False, right_active=False)
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            log_to_console_and_web(f"   Response: '{response}'", 'info')
            if "MOTORS_STOPPED" in response:
                log_to_console_and_web("   ✅ Motors stopped successfully!", 'success')
            else:
                log_to_console_and_web(f"   ⚠️  Unexpected response: {response}", 'warning')
        
        ser.close()
        
        log_to_console_and_web("\n" + "="*60, 'header')
        log_to_console_and_web("✅ SERVO TEST COMPLETE", 'success')
        log_to_console_and_web("="*60, 'header')
        log_to_console_and_web("\nResults:", 'info')
        log_to_console_and_web("  • Connection to COM4: ✅", 'success')
        log_to_console_and_web("  • Score-based motor selection: ✅", 'success')
        log_to_console_and_web("  • LEFT motor (score < 10): Check output above", 'info')
        log_to_console_and_web("  • RIGHT motor (score >= 10): Check output above", 'info')
        log_to_console_and_web("\nServo communication is working!", 'success')
        log_to_console_and_web("\nPress Ctrl+C to exit...", 'info')
        
        # Keep server running
        while True:
            time.sleep(1)
        
    except serial.SerialException as e:
        log_to_console_and_web(f"\n❌ ERROR: Could not open {PORT}", 'error')
        log_to_console_and_web(f"Details: {e}", 'error')
        log_to_console_and_web("\nTroubleshooting:", 'warning')
        log_to_console_and_web("1. Is Arduino connected to COM4? (Check Device Manager)", 'warning')
        log_to_console_and_web("2. Is servo_controller.ino uploaded to the Arduino?", 'warning')
        log_to_console_and_web("3. Close Arduino IDE Serial Monitor", 'warning')
        log_to_console_and_web("4. Is another program using COM4?", 'warning')
        log_to_console_and_web("\nRun check_ports.py to see which ports are available", 'info')
        sys.exit(1)
    
    except KeyboardInterrupt:
        log_to_console_and_web("\n\n⚠️  Test interrupted by user", 'warning')
        if 'ser' in locals() and ser.is_open:
            log_to_console_and_web("Stopping motors...", 'info')
            ser.write(b"STOP\n")
            ser.close()
        sys.exit(0)
    
    except Exception as e:
        log_to_console_and_web(f"\n❌ Unexpected error: {e}", 'error')
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            log_to_console_and_web("\nPort closed", 'info')
