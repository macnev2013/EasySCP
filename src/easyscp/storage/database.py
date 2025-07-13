"""Database configuration and management for EasySCP."""

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from cryptography.fernet import Fernet

from .db_base import Base
from ..utils.logger import logger

class DatabaseManager:
    """Manages database connections and encryption."""
    
    def __init__(self, db_path: str = "easyscp.db", key_file: str = "db_key.key"):
        self.db_path = db_path
        self.key_file = key_file
        self.cipher = self._get_or_create_cipher()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        
        self._init_database()
        
    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption cipher for database."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logger.info("Created new database encryption key")
        return Fernet(key)
        
    def _init_database(self) -> None:
        """Initialize database connection and tables."""
        # Create SQLite database with encryption support
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={
                "check_same_thread": False,  # Allow multi-threading
            },
            poolclass=StaticPool,  # Use static pool for SQLite
            echo=False  # Set to True for SQL debugging
        )
        
        # Enable foreign keys for SQLite
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Import models to ensure they are registered with Base
        from . import db_models
        
        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized at {self.db_path}")
        
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
            
    def encrypt_value(self, value: str) -> str:
        """Encrypt a string value."""
        if value:
            return self.cipher.encrypt(value.encode()).decode()
        return ""
        
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a string value."""
        if encrypted_value:
            try:
                return self.cipher.decrypt(encrypted_value.encode()).decode()
            except Exception as e:
                logger.error(f"Failed to decrypt value: {e}")
                return ""
        return ""
        
    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

# Global database manager instance (initialized on first use)
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create the database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# For backward compatibility
db_manager = get_db_manager()