"""Helper functions for EasySCP."""

from typing import Union

def format_file_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def sanitize_path(path: str) -> str:
    """Sanitize file path for cross-platform compatibility."""
    return path.replace("\\", "/").strip()

def validate_port(port: Union[str, int]) -> int:
    """Validate and convert port number."""
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            return port_num
    except (ValueError, TypeError):
        pass
    return 22  # Default SSH port