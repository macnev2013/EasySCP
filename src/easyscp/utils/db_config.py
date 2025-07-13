"""Database-based configuration management for EasySCP."""

import json
from typing import Any, Dict, Optional, Union
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..storage.database import get_db_manager
from ..storage.db_models import Setting
from ..utils.logger import logger


class DatabaseConfig:
    """Manage application configuration using database."""
    
    DEFAULT_SETTINGS = {
        "appearance": {
            "theme": "dark",
            "color_scheme": "blue"
        },
        "connection": {
            "default_port": 22,
            "timeout": 30,
            "keepalive_interval": 60
        },
        "file_manager": {
            "show_hidden_files": False,
            "default_download_path": str(Path.home() / "Downloads")
        },
        "terminal": {
            "font_family": "Consolas",
            "font_size": 11,
            "buffer_size": 10000
        }
    }
    
    def __init__(self):
        """Initialize database configuration."""
        self._cache: Dict[str, Any] = {}
        self._initialize_defaults()
        self._load_cache()
        
    def _initialize_defaults(self) -> None:
        """Initialize default settings in database if not present."""
        with get_db_manager().get_session() as session:
            for category, settings in self.DEFAULT_SETTINGS.items():
                for key, value in settings.items():
                    self._ensure_setting(session, category, key, value)
                    
    def _ensure_setting(self, session: Session, category: str, key: str, default_value: Any) -> None:
        """Ensure a setting exists in database."""
        # Check if setting exists
        existing = session.query(Setting).filter_by(
            category=category,
            key=key
        ).first()
        
        if not existing:
            # Determine value type
            value_type = self._get_value_type(default_value)
            
            # Convert value to string for storage
            if value_type == 'json':
                value_str = json.dumps(default_value)
            else:
                value_str = str(default_value)
                
            # Create new setting
            setting = Setting(
                category=category,
                key=key,
                value=value_str,
                value_type=value_type
            )
            session.add(setting)
            
            try:
                session.flush()
                logger.info(f"Created default setting: {category}.{key}")
            except IntegrityError:
                # Setting was created by another process
                session.rollback()
                
    def _get_value_type(self, value: Any) -> str:
        """Determine the type of a value."""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        else:
            return 'json'
            
    def _load_cache(self) -> None:
        """Load all settings into cache."""
        with get_db_manager().get_session() as session:
            settings = session.query(Setting).all()
            
            self._cache.clear()
            for setting in settings:
                cache_key = f"{setting.category}.{setting.key}"
                self._cache[cache_key] = self._parse_value(setting.value, setting.value_type)
                
    def _parse_value(self, value: str, value_type: str) -> Any:
        """Parse a stored value based on its type."""
        try:
            if value_type == 'bool':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif value_type == 'int':
                return int(value)
            elif value_type == 'float':
                return float(value)
            elif value_type == 'json':
                return json.loads(value)
            else:
                return value
        except Exception as e:
            logger.error(f"Failed to parse value '{value}' as {value_type}: {e}")
            return value
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        # Check cache first
        if key in self._cache:
            return self._cache[key]
            
        # Parse nested key
        parts = key.split('.')
        if len(parts) >= 2:
            category = parts[0]
            setting_key = '.'.join(parts[1:])
            
            with get_db_manager().get_session() as session:
                setting = session.query(Setting).filter_by(
                    category=category,
                    key=setting_key
                ).first()
                
                if setting:
                    value = self._parse_value(setting.value, setting.value_type)
                    self._cache[key] = value
                    return value
                    
        return default
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        # Parse nested key
        parts = key.split('.')
        if len(parts) < 2:
            raise ValueError(f"Invalid key format: {key}. Use 'category.key' format.")
            
        category = parts[0]
        setting_key = '.'.join(parts[1:])
        
        # Determine value type
        value_type = self._get_value_type(value)
        
        # Convert value to string
        if value_type == 'json':
            value_str = json.dumps(value)
        else:
            value_str = str(value)
            
        with get_db_manager().get_session() as session:
            # Find existing setting
            setting = session.query(Setting).filter_by(
                category=category,
                key=setting_key
            ).first()
            
            if setting:
                # Update existing
                setting.value = value_str
                setting.value_type = value_type
            else:
                # Create new
                setting = Setting(
                    category=category,
                    key=setting_key,
                    value=value_str,
                    value_type=value_type
                )
                session.add(setting)
                
            session.flush()
            
        # Update cache
        self._cache[key] = value
        logger.info(f"Updated setting: {key}")
        
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in a category."""
        result = {}
        
        with get_db_manager().get_session() as session:
            settings = session.query(Setting).filter_by(category=category).all()
            
            for setting in settings:
                result[setting.key] = self._parse_value(setting.value, setting.value_type)
                
        return result
        
    def set_category(self, category: str, values: Dict[str, Any]) -> None:
        """Set multiple settings in a category."""
        for key, value in values.items():
            self.set(f"{category}.{key}", value)
            
    def delete(self, key: str) -> bool:
        """Delete a setting."""
        parts = key.split('.')
        if len(parts) < 2:
            return False
            
        category = parts[0]
        setting_key = '.'.join(parts[1:])
        
        with get_db_manager().get_session() as session:
            setting = session.query(Setting).filter_by(
                category=category,
                key=setting_key
            ).first()
            
            if setting:
                session.delete(setting)
                session.flush()
                
                # Remove from cache
                if key in self._cache:
                    del self._cache[key]
                    
                logger.info(f"Deleted setting: {key}")
                return True
                
        return False
        
    def export_settings(self) -> Dict[str, Dict[str, Any]]:
        """Export all settings."""
        result = {}
        
        with get_db_manager().get_session() as session:
            settings = session.query(Setting).order_by(Setting.category, Setting.key).all()
            
            for setting in settings:
                if setting.category not in result:
                    result[setting.category] = {}
                    
                result[setting.category][setting.key] = self._parse_value(
                    setting.value, 
                    setting.value_type
                )
                
        return result
        
    def import_settings(self, settings_data: Dict[str, Dict[str, Any]]) -> int:
        """Import settings from dictionary."""
        imported = 0
        
        for category, settings in settings_data.items():
            for key, value in settings.items():
                self.set(f"{category}.{key}", value)
                imported += 1
                
        logger.info(f"Imported {imported} settings")
        return imported
        
    def refresh_cache(self) -> None:
        """Refresh the settings cache from database."""
        self._load_cache()
        logger.info("Settings cache refreshed")
        

# Global config instance
db_config = DatabaseConfig()