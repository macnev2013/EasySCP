"""Manage multiple SSH connections."""

from typing import Dict, Optional
from .ssh_connection import SSHConnection
from ..utils.logger import logger

class ConnectionManager:
    """Manage multiple SSH connections."""
    
    def __init__(self):
        self.connections: Dict[int, SSHConnection] = {}
        self.active_connection_id: Optional[int] = None
        
    def create_connection(self, server_id: int) -> SSHConnection:
        """Create a new SSH connection for a server."""
        if server_id in self.connections:
            self.close_connection(server_id)
            
        connection = SSHConnection()
        self.connections[server_id] = connection
        return connection
        
    def get_connection(self, server_id: int) -> Optional[SSHConnection]:
        """Get connection for a server."""
        return self.connections.get(server_id)
        
    def get_active_connection(self) -> Optional[SSHConnection]:
        """Get the currently active connection."""
        if self.active_connection_id:
            return self.connections.get(self.active_connection_id)
        return None
        
    def set_active_connection(self, server_id: int) -> None:
        """Set the active connection."""
        if server_id in self.connections:
            self.active_connection_id = server_id
            logger.info(f"Set active connection to server {server_id}")
            
    def close_connection(self, server_id: int) -> None:
        """Close a specific connection."""
        if server_id in self.connections:
            self.connections[server_id].disconnect()
            del self.connections[server_id]
            
            if self.active_connection_id == server_id:
                self.active_connection_id = None
                
            logger.info(f"Closed connection to server {server_id}")
            
    def close_all_connections(self) -> None:
        """Close all connections."""
        for server_id in list(self.connections.keys()):
            self.close_connection(server_id)
            
        logger.info("Closed all connections")