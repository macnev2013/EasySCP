#!/usr/bin/env python3
"""EasySCP - Modern SSH Client with GUI

Entry point optimized for PyInstaller.
"""

if __name__ == "__main__":
    import sys
    import os
    
    # When running from PyInstaller bundle, the path is already set up
    if not getattr(sys, 'frozen', False):
        # Running in normal Python environment
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(script_dir, 'src')
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
    
    from easyscp.core.app import EasySCPApp
    
    app = EasySCPApp()
    app.run()