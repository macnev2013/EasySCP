"""SSH connection handling."""

import paramiko
from typing import Optional, Tuple, List
from pathlib import Path
import os
import stat

from ..utils.logger import logger
from ..utils.config import config

class SSHConnection:
    """Manage SSH connections using Paramiko."""
    
    def __init__(self):
        self.client: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.transport: Optional[paramiko.Transport] = None
        self.is_connected: bool = False
        
    def connect(self, host: str, port: int, username: str, password: str = None,
                use_key_auth: bool = False, private_key_path: str = None, 
                private_key_passphrase: str = None) -> bool:
        """Establish SSH connection to server."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            timeout = config.get("connection.timeout", 30)
            
            # Prepare connection parameters
            connect_params = {
                "hostname": host,
                "port": port,
                "username": username,
                "timeout": timeout,
            }
            
            if use_key_auth and private_key_path:
                # Load private key
                pkey = self._load_private_key(private_key_path, private_key_passphrase)
                if pkey:
                    connect_params["pkey"] = pkey
                    connect_params["look_for_keys"] = False
                    connect_params["allow_agent"] = False
                else:
                    logger.error(f"Failed to load private key from {private_key_path}")
                    return False
            else:
                # Use password authentication
                connect_params["password"] = password
                connect_params["look_for_keys"] = False
                connect_params["allow_agent"] = False
            
            self.client.connect(**connect_params)
            
            self.transport = self.client.get_transport()
            if self.transport:
                keepalive = config.get("connection.keepalive_interval", 60)
                self.transport.set_keepalive(keepalive)
                
            self.sftp = self.client.open_sftp()
            self.is_connected = True
            
            logger.info(f"Connected to {host}:{port} as {username}")
            return True
            
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {username}@{host}")
        except paramiko.SSHException as e:
            logger.error(f"SSH connection error: {e}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            
        self.disconnect()
        return False
        
    def disconnect(self) -> None:
        """Close SSH connection."""
        if self.sftp:
            try:
                self.sftp.close()
            except:
                pass
            self.sftp = None
            
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
            
        self.transport = None
        self.is_connected = False
        logger.info("Disconnected from server")
    
    def _load_private_key(self, key_path: str, passphrase: Optional[str] = None) -> Optional[paramiko.PKey]:
        """Load private key from file (supports PEM and PPK formats)."""
        try:
            # First try to detect key type from file content
            with open(key_path, 'r') as f:
                first_line = f.readline().strip()
            
            # Try different key types based on file content
            if 'RSA' in first_line:
                try:
                    return paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
                except Exception:
                    pass
            elif 'DSA' in first_line or 'DSS' in first_line:
                try:
                    return paramiko.DSSKey.from_private_key_file(key_path, password=passphrase)
                except Exception:
                    pass
            elif 'EC' in first_line:
                try:
                    return paramiko.ECDSAKey.from_private_key_file(key_path, password=passphrase)
                except Exception:
                    pass
            elif 'OPENSSH' in first_line:
                try:
                    return paramiko.Ed25519Key.from_private_key_file(key_path, password=passphrase)
                except Exception:
                    pass
            elif 'PuTTY-User-Key-File' in first_line:
                # PPK file - need to convert or handle specially
                logger.warning("PPK files detected. Attempting to load...")
                # Try all key types for PPK
                for key_class in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey, paramiko.Ed25519Key]:
                    try:
                        return key_class.from_private_key_file(key_path, password=passphrase)
                    except Exception:
                        continue
            
            # If no specific type detected, try all key types
            for key_class in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey, paramiko.Ed25519Key]:
                try:
                    return key_class.from_private_key_file(key_path, password=passphrase)
                except Exception:
                    continue
                    
            logger.error(f"Unable to load private key from {key_path}")
            return None
            
        except FileNotFoundError:
            logger.error(f"Private key file not found: {key_path}")
            return None
        except paramiko.PasswordRequiredException:
            logger.error(f"Private key requires a passphrase: {key_path}")
            return None
        except Exception as e:
            logger.error(f"Error loading private key from {key_path}: {e}")
            return None
        
    def execute_command(self, command: str) -> Tuple[str, str]:
        """Execute command on remote server."""
        if not self.is_connected or not self.client:
            return "", "Not connected to server"
            
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode('utf-8', errors='replace')
            error = stderr.read().decode('utf-8', errors='replace')
            return output, error
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return "", str(e)
            
    def list_directory(self, path: str = ".") -> List[paramiko.SFTPAttributes]:
        """List directory contents."""
        if not self.sftp:
            return []
            
        try:
            return self.sftp.listdir_attr(path)
        except Exception as e:
            logger.error(f"Failed to list directory {path}: {e}")
            return []
            
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from server."""
        if not self.sftp:
            return False
            
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.sftp.get(remote_path, local_path)
            logger.info(f"Downloaded {remote_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
            
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to server."""
        if not self.sftp:
            return False
            
        try:
            self.sftp.put(local_path, remote_path)
            logger.info(f"Uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
            
    def create_directory(self, path: str) -> bool:
        """Create directory on server."""
        if not self.sftp:
            return False
            
        try:
            self.sftp.mkdir(path)
            logger.info(f"Created directory {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory: {e}")
            return False
            
    def delete_file(self, path: str) -> bool:
        """Delete file on server."""
        if not self.sftp:
            return False
            
        try:
            self.sftp.remove(path)
            logger.info(f"Deleted file {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
            
    def get_current_directory(self) -> str:
        """Get current working directory."""
        if not self.sftp:
            return "/"
            
        try:
            return self.sftp.getcwd() or "/"
        except:
            return "/"
            
    def change_directory(self, path: str) -> bool:
        """Change current directory."""
        if not self.sftp:
            return False
            
        try:
            self.sftp.chdir(path)
            return True
        except Exception as e:
            logger.error(f"Failed to change directory: {e}")
            return False
            
    def list_files(self, path: str = ".") -> List[dict]:
        """List files in directory with detailed information."""
        if not self.sftp:
            raise Exception("SFTP connection not available")
            
        if not self.is_connected:
            raise Exception("SSH session not active")
            
        try:
            # Set timeout for the operation
            original_timeout = self.sftp.sock.gettimeout()
            self.sftp.sock.settimeout(10.0)  # 10 second timeout
            
            try:
                items = []
                attrs = self.sftp.listdir_attr(path)
                
                for attr in attrs:
                    item = {
                        'name': attr.filename,
                        'type': 'directory' if stat.S_ISDIR(attr.st_mode) else 'file',
                        'size': attr.st_size,
                        'modified': attr.st_mtime,
                        'permissions': oct(attr.st_mode)[-3:]
                    }
                    items.append(item)
                    
                return items
            finally:
                # Restore original timeout
                self.sftp.sock.settimeout(original_timeout)
                
        except IOError as e:
            if e.errno == 2:
                raise Exception(f"Directory not found: {path}")
            else:
                logger.error(f"IO error listing files in {path}: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to list files in {path}: {e}")
            # Check if connection is still alive
            if not self._test_connection():
                self.is_connected = False
                raise Exception("Connection lost")
            raise
    
    def _test_connection(self) -> bool:
        """Test if the SSH connection is still active."""
        try:
            if self.client and self.transport and self.transport.is_active():
                # Try a simple operation
                self.client.exec_command('echo test', timeout=2)
                return True
        except:
            pass
        return False
            
    def delete_directory(self, path: str) -> bool:
        """Delete directory on server."""
        if not self.sftp:
            return False
            
        try:
            self.sftp.rmdir(path)
            logger.info(f"Deleted directory {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete directory: {e}")
            return False
            
    def rename(self, old_path: str, new_path: str) -> bool:
        """Rename file or directory."""
        if not self.sftp:
            return False
            
        try:
            self.sftp.rename(old_path, new_path)
            logger.info(f"Renamed {old_path} to {new_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to rename: {e}")
            return False