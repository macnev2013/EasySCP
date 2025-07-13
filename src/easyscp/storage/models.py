"""Data models for EasySCP."""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Server:
    """Server configuration model."""
    id: int
    name: str
    host: str
    port: int
    username: str
    password: Optional[str] = None
    use_key_auth: bool = False
    private_key_path: Optional[str] = None
    private_key_passphrase: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'use_key_auth': self.use_key_auth,
            'private_key_path': self.private_key_path,
            'private_key_passphrase': self.private_key_passphrase
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Server':
        """Create from dictionary."""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            host=data.get('host', ''),
            port=data.get('port', 22),
            username=data.get('username', ''),
            password=data.get('password'),
            use_key_auth=data.get('use_key_auth', False),
            private_key_path=data.get('private_key_path'),
            private_key_passphrase=data.get('private_key_passphrase')
        )

@dataclass
class Snippet:
    """Command snippet model."""
    id: int
    server_id: int
    name: str
    command: str
    description: Optional[str] = None
    is_script: bool = False
    order_index: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'server_id': self.server_id,
            'name': self.name,
            'description': self.description,
            'command': self.command,
            'is_script': self.is_script,
            'order_index': self.order_index
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Snippet':
        """Create from dictionary."""
        return cls(
            id=data.get('id', 0),
            server_id=data.get('server_id', 0),
            name=data.get('name', ''),
            description=data.get('description'),
            command=data.get('command', ''),
            is_script=data.get('is_script', False),
            order_index=data.get('order_index', 0)
        )