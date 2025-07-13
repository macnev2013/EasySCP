"""Database models for EasySCP."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import validates

from .db_base import Base
from ..utils.logger import logger

class ServerConnection(Base):
    """Database model for SSH server connections."""
    
    __tablename__ = "server_connections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=22, nullable=False)
    username = Column(String(255), nullable=False)
    password_encrypted = Column(Text, nullable=True)  # Encrypted password
    
    # Additional fields
    description = Column(Text, nullable=True)
    group = Column(String(100), nullable=True, default="Default")
    
    # Authentication options
    use_key_auth = Column(Boolean, default=False)
    private_key_path = Column(String(500), nullable=True)
    private_key_passphrase_encrypted = Column(Text, nullable=True)
    
    # Connection options
    timeout = Column(Integer, default=30)
    keepalive_interval = Column(Integer, default=60)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_connected = Column(DateTime, nullable=True)
    connection_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    @validates('port')
    def validate_port(self, key, port):
        """Validate port number."""
        if not 1 <= port <= 65535:
            raise ValueError(f"Invalid port number: {port}")
        return port
        
    @validates('timeout')
    def validate_timeout(self, key, timeout):
        """Validate timeout value."""
        if timeout < 1:
            raise ValueError(f"Invalid timeout: {timeout}")
        return timeout
        
    @property
    def password(self) -> Optional[str]:
        """Get decrypted password."""
        if self.password_encrypted:
            from .database import get_db_manager
            return get_db_manager().decrypt_value(self.password_encrypted)
        return None
        
    @password.setter
    def password(self, value: Optional[str]) -> None:
        """Set encrypted password."""
        if value:
            from .database import get_db_manager
            self.password_encrypted = get_db_manager().encrypt_value(value)
        else:
            self.password_encrypted = None
            
    @property
    def private_key_passphrase(self) -> Optional[str]:
        """Get decrypted private key passphrase."""
        if self.private_key_passphrase_encrypted:
            from .database import get_db_manager
            return get_db_manager().decrypt_value(self.private_key_passphrase_encrypted)
        return None
        
    @private_key_passphrase.setter
    def private_key_passphrase(self, value: Optional[str]) -> None:
        """Set encrypted private key passphrase."""
        if value:
            from .database import get_db_manager
            self.private_key_passphrase_encrypted = get_db_manager().encrypt_value(value)
        else:
            self.private_key_passphrase_encrypted = None
            
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,  # This will decrypt
            'description': self.description,
            'group': self.group,
            'use_key_auth': self.use_key_auth,
            'private_key_path': self.private_key_path,
            'private_key_passphrase': self.private_key_passphrase,  # This will decrypt
            'timeout': self.timeout,
            'keepalive_interval': self.keepalive_interval,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_connected': self.last_connected.isoformat() if self.last_connected else None,
            'connection_count': self.connection_count,
            'is_active': self.is_active
        }
        
    def __repr__(self):
        return f"<ServerConnection(id={self.id}, name='{self.name}', host='{self.host}:{self.port}')>"

class ConnectionLog(Base):
    """Database model for connection history."""
    
    __tablename__ = "connection_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, nullable=False)
    connected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    disconnected_at = Column(DateTime, nullable=True)
    connection_type = Column(String(50), nullable=False)  # 'file_manager' or 'terminal'
    status = Column(String(50), nullable=False, default='connected')  # connected, disconnected, failed
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ConnectionLog(server_id={self.server_id}, type='{self.connection_type}', status='{self.status}')>"

class Setting(Base):
    """Database model for application settings."""
    
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False, default='string')  # string, int, float, bool, json
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Create unique constraint on category + key
    __table_args__ = (
        UniqueConstraint('category', 'key', name='_category_key_uc'),
    )
    
    def __repr__(self):
        return f"<Setting(category='{self.category}', key='{self.key}', value='{self.value}')>"

class Snippet(Base):
    """Database model for server command snippets."""
    
    __tablename__ = "snippets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    command = Column(Text, nullable=False)
    is_script = Column(Boolean, default=False)  # True if it's a multi-line script
    order_index = Column(Integer, default=0)  # For custom ordering
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'server_id': self.server_id,
            'name': self.name,
            'description': self.description,
            'command': self.command,
            'is_script': self.is_script,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Snippet(id={self.id}, server_id={self.server_id}, name='{self.name}')>"