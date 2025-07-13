"""Configuration management for EasySCP - Database backed."""

from .db_config import db_config, DatabaseConfig

# For backward compatibility, export the database config as 'config'
config = db_config

# Also export the class for type hints
Config = DatabaseConfig

__all__ = ['config', 'Config']