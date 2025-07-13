"""Main application class for EasySCP."""

import customtkinter as ctk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..ui import MainWindow
from ..utils.config import config
from ..utils.logger import logger

class EasySCPApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        # Set appearance (default to light mode)
        ctk.set_appearance_mode(config.get("appearance.theme", "light"))
        ctk.set_default_color_theme(config.get("appearance.color_scheme", "blue"))
        
        # Create root window
        self.root = ctk.CTk()
        
        # Set window properties
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main window
        self.main_window = MainWindow(self.root)
        
        logger.info("EasySCP application initialized")
        
    def run(self) -> None:
        """Run the application."""
        logger.info("Starting EasySCP application")
        self.root.mainloop()
        
    def on_closing(self) -> None:
        """Handle window closing."""
        logger.info("Closing EasySCP application")
        
        # Close all connections
        if hasattr(self.main_window, 'connection_manager'):
            self.main_window.connection_manager.close_all_connections()
            
        # Config is automatically saved to database
        
        # Destroy window
        self.root.destroy()


def main():
    """Main entry point for the application."""
    app = EasySCPApp()
    app.run()


if __name__ == "__main__":
    main()