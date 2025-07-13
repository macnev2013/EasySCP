"""Build configuration for PyInstaller - Run this before building."""

import os
import shutil

def prepare_build():
    """Prepare the source code for building."""
    # Create a temporary build directory
    build_src = "build_src"
    if os.path.exists(build_src):
        shutil.rmtree(build_src)
    
    # Copy all source files to build directory, flattening the structure
    shutil.copytree("src", build_src)
    
    # Create a new main.py in the root that imports directly
    with open("main_build.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import sys
import os

# For PyInstaller, add the bundled directory to path
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    application_path = os.path.dirname(sys.executable)
else:
    # Running in normal Python environment
    application_path = os.path.dirname(os.path.abspath(__file__))

# Import and run the app
from easyscp.core.app import main

if __name__ == "__main__":
    main()
""")
    
    print("Build preparation complete!")
    print("Now run: pyinstaller --onefile --windowed --name EasySCP main_build.py")

if __name__ == "__main__":
    prepare_build()