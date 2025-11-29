#!/opt/homebrew/bin/python3.11
"""
integra App - macOS Launcher
uses Homebrew Python 3.11 which provides stable Qt6 support on macOS
"""

import os
import sys
from pathlib import Path

# get app directory and set up paths
app_dir = Path(__file__).parent.absolute()
src_dir = app_dir / "src"

# set up Python path
sys.path.insert(0, str(src_dir))
os.environ["PYTHONPATH"] = str(src_dir)

# change to app directory
os.chdir(app_dir)

# import and run
if __name__ == "__main__":
    from main import main
    main()