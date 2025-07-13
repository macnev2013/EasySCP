"""Server storage using encrypted database."""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from .database import get_db_manager
from .db_models import ServerConnection, ConnectionLog, Snippet as SnippetDB
from .models import Server, Snippet
from ..utils.logger import logger

class ServerStorage:
    """Manage server configurations using encrypted database."""
    
    def __init__(self):
        """Initialize server storage."""
        logger.info("Initialized database-based server storage")
        
    def _db_to_server(self, db_server: ServerConnection) -> Server:
        """Convert database model to Server model."""
        return Server(
            id=db_server.id,
            name=db_server.name,
            host=db_server.host,
            port=db_server.port,
            username=db_server.username,
            password=db_server.password,  # Automatically decrypted
            use_key_auth=db_server.use_key_auth,
            private_key_path=db_server.private_key_path,
            private_key_passphrase=db_server.private_key_passphrase  # Automatically decrypted
        )
        
    def _server_to_db(self, server: Server, db_server: Optional[ServerConnection] = None) -> ServerConnection:
        """Convert Server model to database model."""
        if db_server is None:
            db_server = ServerConnection()
            
        db_server.name = server.name
        db_server.host = server.host
        db_server.port = server.port
        db_server.username = server.username
        
        # Authentication settings
        db_server.use_key_auth = server.use_key_auth
        db_server.private_key_path = server.private_key_path
        
        # Only update password if provided
        if server.password is not None:
            db_server.password = server.password  # Automatically encrypted
            
        # Only update passphrase if provided
        if server.private_key_passphrase is not None:
            db_server.private_key_passphrase = server.private_key_passphrase  # Automatically encrypted
            
        return db_server
        
    def add_server(self, server: Server) -> int:
        """Add a new server to database."""
        with get_db_manager().get_session() as session:
            try:
                db_server = self._server_to_db(server)
                session.add(db_server)
                session.flush()  # Get the ID before commit
                
                server_id = db_server.id
                logger.info(f"Added server: {server.name} (ID: {server_id})")
                return server_id
                
            except IntegrityError:
                logger.error(f"Server with name '{server.name}' already exists")
                raise ValueError(f"Server with name '{server.name}' already exists")
                
    def update_server(self, server_id: int, updated_server: Server) -> bool:
        """Update an existing server in database."""
        with get_db_manager().get_session() as session:
            db_server = session.query(ServerConnection).filter_by(id=server_id).first()
            
            if not db_server:
                logger.error(f"Server with ID {server_id} not found")
                return False
                
            try:
                self._server_to_db(updated_server, db_server)
                session.flush()
                
                logger.info(f"Updated server: {updated_server.name} (ID: {server_id})")
                return True
                
            except IntegrityError:
                logger.error(f"Server with name '{updated_server.name}' already exists")
                raise ValueError(f"Server with name '{updated_server.name}' already exists")
                
    def delete_server(self, server_id: int) -> bool:
        """Delete a server from database."""
        with get_db_manager().get_session() as session:
            db_server = session.query(ServerConnection).filter_by(id=server_id).first()
            
            if not db_server:
                logger.error(f"Server with ID {server_id} not found")
                return False
                
            server_name = db_server.name
            session.delete(db_server)
            
            # Also delete connection logs for this server
            session.query(ConnectionLog).filter_by(server_id=server_id).delete()
            
            logger.info(f"Deleted server: {server_name} (ID: {server_id})")
            return True
            
    def get_server(self, server_id: int) -> Optional[Server]:
        """Get a server by ID from database."""
        with get_db_manager().get_session() as session:
            db_server = session.query(ServerConnection).filter_by(id=server_id, is_active=True).first()
            
            if db_server:
                return self._db_to_server(db_server)
                
            return None
            
    def get_all_servers(self, include_inactive: bool = False) -> List[Server]:
        """Get all servers from database."""
        with get_db_manager().get_session() as session:
            query = session.query(ServerConnection)
            
            if not include_inactive:
                query = query.filter_by(is_active=True)
                
            db_servers = query.order_by(ServerConnection.name).all()
            
            return [self._db_to_server(db_server) for db_server in db_servers]
            
    def search_servers(self, search_term: str) -> List[Server]:
        """Search servers by name or host."""
        with get_db_manager().get_session() as session:
            search_pattern = f"%{search_term}%"
            
            db_servers = session.query(ServerConnection).filter(
                ServerConnection.is_active == True,
                or_(
                    ServerConnection.name.like(search_pattern),
                    ServerConnection.host.like(search_pattern),
                    ServerConnection.description.like(search_pattern)
                )
            ).order_by(ServerConnection.name).all()
            
            return [self._db_to_server(db_server) for db_server in db_servers]
            
    def get_servers_by_group(self, group: str) -> List[Server]:
        """Get servers by group."""
        with get_db_manager().get_session() as session:
            db_servers = session.query(ServerConnection).filter_by(
                group=group,
                is_active=True
            ).order_by(ServerConnection.name).all()
            
            return [self._db_to_server(db_server) for db_server in db_servers]
            
    def log_connection(self, server_id: int, connection_type: str) -> int:
        """Log a new connection."""
        with get_db_manager().get_session() as session:
            # Update last connected time and increment counter
            db_server = session.query(ServerConnection).filter_by(id=server_id).first()
            if db_server:
                db_server.last_connected = datetime.utcnow()
                db_server.connection_count += 1
                
            # Create connection log
            log = ConnectionLog(
                server_id=server_id,
                connection_type=connection_type,
                status='connected'
            )
            session.add(log)
            session.flush()
            
            return log.id
            
    def log_disconnection(self, log_id: int, error_message: Optional[str] = None) -> None:
        """Log a disconnection."""
        with get_db_manager().get_session() as session:
            log = session.query(ConnectionLog).filter_by(id=log_id).first()
            if log:
                log.disconnected_at = datetime.utcnow()
                log.status = 'failed' if error_message else 'disconnected'
                log.error_message = error_message
                
    def get_recent_connections(self, limit: int = 10) -> List[dict]:
        """Get recent connection history."""
        with get_db_manager().get_session() as session:
            logs = session.query(ConnectionLog).order_by(
                ConnectionLog.connected_at.desc()
            ).limit(limit).all()
            
            result = []
            for log in logs:
                # Get server info
                server = session.query(ServerConnection).filter_by(id=log.server_id).first()
                if server:
                    result.append({
                        'server_name': server.name,
                        'server_host': server.host,
                        'connected_at': log.connected_at,
                        'disconnected_at': log.disconnected_at,
                        'connection_type': log.connection_type,
                        'status': log.status,
                        'error_message': log.error_message
                    })
                    
            return result
            
    def export_servers(self) -> List[dict]:
        """Export all servers (for backup)."""
        with get_db_manager().get_session() as session:
            db_servers = session.query(ServerConnection).all()
            return [db_server.to_dict() for db_server in db_servers]
            
    def import_servers(self, servers_data: List[dict]) -> int:
        """Import servers from backup."""
        imported_count = 0
        
        with get_db_manager().get_session() as session:
            for server_data in servers_data:
                # Check if server already exists
                existing = session.query(ServerConnection).filter_by(
                    name=server_data.get('name')
                ).first()
                
                if not existing:
                    db_server = ServerConnection()
                    
                    # Set fields
                    for field in ['name', 'host', 'port', 'username', 'description', 
                                'group', 'use_key_auth', 'private_key_path', 
                                'timeout', 'keepalive_interval', 'is_active']:
                        if field in server_data:
                            setattr(db_server, field, server_data[field])
                            
                    # Set encrypted fields
                    if 'password' in server_data and server_data['password']:
                        db_server.password = server_data['password']
                    if 'private_key_passphrase' in server_data and server_data['private_key_passphrase']:
                        db_server.private_key_passphrase = server_data['private_key_passphrase']
                        
                    session.add(db_server)
                    imported_count += 1
                    
        logger.info(f"Imported {imported_count} servers")
        return imported_count
    
    # Snippet Management Methods
    
    def _db_to_snippet(self, db_snippet: SnippetDB) -> Snippet:
        """Convert database snippet to Snippet model."""
        return Snippet(
            id=db_snippet.id,
            server_id=db_snippet.server_id,
            name=db_snippet.name,
            description=db_snippet.description,
            command=db_snippet.command,
            is_script=db_snippet.is_script,
            order_index=db_snippet.order_index
        )
    
    def _snippet_to_db(self, snippet: Snippet, db_snippet: Optional[SnippetDB] = None) -> SnippetDB:
        """Convert Snippet model to database model."""
        if db_snippet is None:
            db_snippet = SnippetDB()
        
        db_snippet.server_id = snippet.server_id
        db_snippet.name = snippet.name
        db_snippet.description = snippet.description
        db_snippet.command = snippet.command
        db_snippet.is_script = snippet.is_script
        db_snippet.order_index = snippet.order_index
        
        return db_snippet
    
    def get_snippets(self, server_id: int) -> List[Snippet]:
        """Get all snippets for a server."""
        with get_db_manager().get_session() as session:
            db_snippets = session.query(SnippetDB).filter_by(
                server_id=server_id
            ).order_by(SnippetDB.order_index, SnippetDB.name).all()
            
            return [self._db_to_snippet(db_snippet) for db_snippet in db_snippets]
    
    def add_snippet(self, snippet: Snippet) -> int:
        """Add a new snippet."""
        with get_db_manager().get_session() as session:
            # Get max order index for this server
            max_order = session.query(SnippetDB.order_index).filter_by(
                server_id=snippet.server_id
            ).order_by(SnippetDB.order_index.desc()).first()
            
            if max_order and max_order[0] is not None:
                snippet.order_index = max_order[0] + 1
            else:
                snippet.order_index = 0
            
            db_snippet = self._snippet_to_db(snippet)
            session.add(db_snippet)
            session.commit()
            
            logger.info(f"Added snippet '{snippet.name}' for server {snippet.server_id}")
            return db_snippet.id
    
    def update_snippet(self, snippet: Snippet) -> bool:
        """Update an existing snippet."""
        with get_db_manager().get_session() as session:
            db_snippet = session.query(SnippetDB).filter_by(id=snippet.id).first()
            if not db_snippet:
                logger.error(f"Snippet {snippet.id} not found")
                return False
            
            self._snippet_to_db(snippet, db_snippet)
            session.commit()
            
            logger.info(f"Updated snippet {snippet.id}")
            return True
    
    def delete_snippet(self, snippet_id: int) -> bool:
        """Delete a snippet."""
        with get_db_manager().get_session() as session:
            db_snippet = session.query(SnippetDB).filter_by(id=snippet_id).first()
            if not db_snippet:
                logger.error(f"Snippet {snippet_id} not found")
                return False
            
            session.delete(db_snippet)
            session.commit()
            
            logger.info(f"Deleted snippet {snippet_id}")
            return True
    
    def reorder_snippets(self, server_id: int, snippet_ids: List[int]) -> bool:
        """Reorder snippets for a server."""
        with get_db_manager().get_session() as session:
            for index, snippet_id in enumerate(snippet_ids):
                db_snippet = session.query(SnippetDB).filter_by(
                    id=snippet_id,
                    server_id=server_id
                ).first()
                if db_snippet:
                    db_snippet.order_index = index
            
            session.commit()
            logger.info(f"Reordered snippets for server {server_id}")
            return True