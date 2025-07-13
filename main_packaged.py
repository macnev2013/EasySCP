#!/usr/bin/env python3
"""EasySCP - Modern SSH Client with GUI

A feature-rich SSH client with file management and terminal capabilities.
This version is optimized for PyInstaller packaging.
"""

import sys
import os

def main():
    """Main entry point."""
    # Import here to ensure proper packaging
    from src.easyscp import EasySCPApp
    app = EasySCPApp()
    app.run()

if __name__ == "__main__":
    main()