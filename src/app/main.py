"""
Main Entry Point for Music-IO
Hexagonal Architecture Music Machine
"""
import logging
import sys
import time
import signal
from pathlib import Path
import os

# Add src to path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Change to src directory for relative imports
os.chdir(src_path)

from app.application import MusicMachineApplication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('music_machine.log')
    ]
)

logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\nShutdown signal received...")
    sys.exit(0)


def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Music-IO - Hexagonal Architecture Music Machine")
    logger.info("=" * 60)
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    app = None
    
    try:
        # Create and start application with Stage 1 (COM7) and Stage 2 (COM4)
        app = MusicMachineApplication(
            enable_servo=True,   # Stage 1 - COM7 (SG90, 360° servo, arm)
            enable_pump=True     # Stage 2 - COM4 (suction pump)
        )
        app.start()
        
        # Keep running
        logger.info("Press Ctrl+C to stop")
        
        while app.is_running():
            time.sleep(1)
            
            # Optionally print status periodically
            # status = app.get_status()
            # logger.debug(f"Status: {status}")
        
    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
    finally:
        if app:
            app.stop()
        logger.info("Application terminated")


if __name__ == "__main__":
    main()
