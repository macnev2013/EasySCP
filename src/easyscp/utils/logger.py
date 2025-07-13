"""Logging configuration for EasySCP."""

import logging
import os
from datetime import datetime
from typing import Optional

class LoggerSetup:
    """Configure and manage application logging."""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "easyscp") -> logging.Logger:
        """Get or create a logger instance."""
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance
    
    @staticmethod
    def _setup_logger(name: str) -> logging.Logger:
        """Set up the logger with file and console handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Create logs directory
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        log_file = os.path.join(log_dir, f"easyscp_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

# Global logger instance
logger = LoggerSetup.get_logger()