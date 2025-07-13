#!/usr/bin/env python3
"""EasySCP - Modern SSH Client with GUI

A feature-rich SSH client with file management and terminal capabilities.
"""

import sys
import os

# Get the absolute path to the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add src to Python path
src_path = os.path.join(script_dir, 'src')
sys.path.insert(0, src_path)

from easyscp import EasySCPApp

def main():
    """Main entry point."""
    app = EasySCPApp()
    app.run()

if __name__ == "__main__":
    main()