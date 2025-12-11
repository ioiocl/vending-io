"""
Simple runner script for Music-IO
Run this from the Music-IO root directory
"""
import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import and run
if __name__ == "__main__":
    from app.main import main
    main()
