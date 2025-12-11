"""
Run Music-IO with Web Visualizer
This starts both the music machine and the web visualizer
"""
import sys
import os
from pathlib import Path
import threading
import time
import logging

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to src directory
os.chdir(str(src_path))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from app.application import MusicMachineApplication

def run_visualizer(app):
    """Run the web visualizer in a separate thread"""
    if app.visualizer:
        print("\n" + "="*60)
        print("🌐 Web Visualizer starting...")
        print(f"   Open your browser to: http://127.0.0.1:5000")
        print("="*60 + "\n")
        
        # Give the main app time to start
        time.sleep(2)
        
        # Run visualizer (this is blocking)
        app.visualizer.run()

def main():
    """Main function with visualizer"""
    print("="*60)
    print("🎵 Music-IO with Web Visualizer + Game Controls")
    print("="*60)
    
    # Create application with visualizer, servo (Stage 1), pump (Stage 2), and thermal printer
    # Note: Button is handled by Stage 1 Arduino, not a separate adapter
    app = MusicMachineApplication(
        enable_visualizer=True,
        enable_button=True,   # Button events come from Stage 1 Arduino
        enable_servo=True,    # Stage 1 on COM7 - Button + SG90 + 360° servo + robotic arm
        enable_pump=True,     # Stage 2 on COM4 - Suction pump controller
        enable_printer=True   # Thermal printer - auto-detect port
    )
    
    # Initialize visualizer
    if app.visualizer:
        app.visualizer.initialize()
        
        # Start visualizer in background thread
        viz_thread = threading.Thread(target=run_visualizer, args=(app,), daemon=True)
        viz_thread.start()
    
    # Start the music machine
    try:
        app.start()
        
        print("\n" + "="*60)
        print("✅ Game System is RUNNING with Web Visualizer!")
        print("="*60)
        print("\n📊 Features:")
        print("  • Real-time game visualization")
        print("  • USB Joystick support (plug and play)")
        print("  • Keyboard controls (Arrow keys + Space)")
        print("  • 🎮 Button controller (COM7) - Press to start game")
        print("  • 🤖 Stage 1 (COM7) - SG90 dance, 360° servo, robotic arm")
        print("  • 💨 Stage 2 (COM4) - Suction pump controller")
        print("  • 🖨️  Thermal Printer - Thank you message printing")
        print("\n🎮 Controls:")
        print("  • Arrow Keys: Navigate through pulses")
        print("  • Space: Jump action")
        print("  • USB Joystick: Full support")
        print("  • Physical Button: Start game")
        print("\n🌐 Web Interface:")
        print("  • Dashboard: http://127.0.0.1:5000")
        print("  • 🎮 GAME: http://127.0.0.1:5000/game")
        print("  • Real-time updates via WebSocket")
        print("\n🤖 Game Flow:")
        print("  1. Button press → SG90 dance (game starts)")
        print("  2. Play game in web interface")
        print("  3. Score < 10: LOSE → Reset to idle")
        print("  4. Score >= 10: WIN → Full sequence:")
        print("     → 360° servo dance")
        print("     → Arm picks down")
        print("     → Suction pump activates (COM4)")
        print("     → Arm lifts object")
        print("     → Pump releases object")
        print("     → 🖨️  Print thank you message")
        print("     → Reset to idle")
        print("\n" + "="*60)
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        # Keep running
        while app.is_running():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.stop()
        print("\n✅ Music Machine stopped")

if __name__ == "__main__":
    main()
