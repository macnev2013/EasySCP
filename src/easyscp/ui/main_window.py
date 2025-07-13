"""Main window component."""

import customtkinter as ctk
from typing import Optional
import subprocess
import platform

from .server_list import ServerListPanel
from .dialogs import ServerDialog, ConfirmDialog, SettingsDialog
from .snippet_dialog import SnippetManagerDialog
from .design_system import design, styles, components
from ..storage import Server, ServerStorage
from ..utils.logger import logger

class MainWindow:
    """Main application window."""
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("EasySCP - SSH Connection Manager")
        self.root.geometry("500x600")
        self.root.minsize(450, 500)
        
        # Initialize components
        self.storage = ServerStorage()
        self.current_server: Optional[Server] = None
        
        # Set up UI
        self.setup_ui()
        
        # Load servers
        self.refresh_server_list()
        
    def setup_ui(self) -> None:
        """Set up the main window UI."""
        # Main container
        main_container = components.create_frame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # Header with settings
        header_frame = components.create_frame(
            main_container, 
            height=design.get_size("header_height")
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Bottom border for header
        border_frame = ctk.CTkFrame(
            main_container, 
            height=1, 
            fg_color=design.get_color("border_primary")
        )
        border_frame.pack(fill="x")
        
        # Title
        title_label = components.create_label(
            header_frame,
            text="SSH Connections",
            style="heading"
        )
        title_label.pack(side="left", padx=design.get_spacing("xxl"))
        
        # Settings button
        self.settings_btn = components.create_button(
            header_frame,
            text="⚙",
            command=self.open_settings,
            width=36,
            height=36
        )
        self.settings_btn.pack(side="right", padx=design.get_spacing("lg"))
        
        # Server list panel
        self.server_list = ServerListPanel(main_container)
        self.server_list.on_connect_files = self.open_file_explorer
        self.server_list.on_connect_terminal = self.open_terminal
        self.server_list.on_add_server = self.add_server
        self.server_list.on_edit_server = self.edit_server
        self.server_list.on_delete_server = self.delete_server
        self.server_list.on_manage_snippets = self.manage_snippets
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-comma>", lambda e: self.open_settings())  # Ctrl+, for settings
        self.root.bind("<Control-n>", lambda e: self.server_list._handle_add())  # Ctrl+N for new server
        self.root.bind("<Control-q>", lambda e: self.root.quit())  # Ctrl+Q to quit
        self.root.bind("<F1>", lambda e: self._show_help())  # F1 for help
        self.root.bind("<Control-f>", lambda e: self._focus_search())  # Ctrl+F to focus search
        
    def refresh_server_list(self) -> None:
        """Refresh the server list."""
        servers = self.storage.get_all_servers()
        self.server_list.refresh(servers)
        
    def add_server(self) -> None:
        """Add a new server."""
        dialog = ServerDialog(self.root, "Add Server")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.storage.add_server(dialog.result)
            self.refresh_server_list()
            logger.info(f"Added server: {dialog.result.name}")
            
    def edit_server(self, server_id: int) -> None:
        """Edit an existing server."""
        server = self.storage.get_server(server_id)
        if not server:
            return
            
        dialog = ServerDialog(self.root, "Edit Server", server)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.storage.update_server(server_id, dialog.result)
            self.refresh_server_list()
            logger.info(f"Updated server: {dialog.result.name}")
            
    def delete_server(self, server_id: int) -> None:
        """Delete a server."""
        server = self.storage.get_server(server_id)
        if not server:
            return
            
        dialog = ConfirmDialog(
            self.root,
            "Delete Server",
            f"Are you sure you want to delete '{server.name}'?"
        )
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Disconnect if this server is connected
            if self.current_server and self.current_server.id == server_id:
                self.disconnect()
                
            self.storage.delete_server(server_id)
            self.refresh_server_list()
            logger.info(f"Deleted server: {server.name}")
            
    def open_file_explorer(self, server: Server) -> None:
        """Open custom file explorer window."""
        from .file_explorer_window import FileExplorerWindow
        
        # Create new window for file explorer
        explorer_window = FileExplorerWindow(self.root, server, self.storage)
        logger.info(f"Opened file explorer for {server.name}")
        
    def open_terminal(self, server: Server) -> None:
        """Open custom terminal window."""
        from .terminal_window import TerminalWindow
        
        # Create new window for terminal
        terminal_window = TerminalWindow(self.root, server, self.storage)
        logger.info(f"Opened terminal for {server.name}")
    
    def manage_snippets(self, server_id: int) -> None:
        """Open snippet manager for a server."""
        server = self.storage.get_server(server_id)
        if server:
            dialog = SnippetManagerDialog(
                self.root,
                server.id,
                server.name,
                self.storage
            )
            self.root.wait_window(dialog.dialog)
        
            
    def open_settings(self) -> None:
        """Open the settings dialog."""
        dialog = SettingsDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            logger.info("Settings updated from UI")
            # Refresh UI elements that might be affected by settings
            if hasattr(self, 'file_manager'):
                self.file_manager.refresh_files()
    
    
    def _focus_search(self) -> None:
        """Focus the search entry in server list."""
        if hasattr(self.server_list, 'search_entry'):
            self.server_list.search_entry.focus()
    
    def _show_help(self) -> None:
        """Show help dialog with keyboard shortcuts."""
        help_dialog = ctk.CTkToplevel(self.root)
        help_dialog.title("Keyboard Shortcuts")
        help_dialog.geometry("500x400")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # Center the dialog
        help_dialog.update_idletasks()
        x = (help_dialog.winfo_screenwidth() // 2) - (250)
        y = (help_dialog.winfo_screenheight() // 2) - (200)
        help_dialog.geometry(f'+{x}+{y}')
        
        # Main frame
        main_frame = ctk.CTkFrame(help_dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="⌨ Keyboard Shortcuts",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))
        
        # Shortcuts list
        shortcuts = [
            ("Ctrl+N", "Add new server"),
            ("Ctrl+F", "Focus search"),
            ("Ctrl+,", "Open settings"),
            ("Ctrl+Q", "Quit application"),
            ("F1", "Show this help"),
            ("Click/Enter", "Open explorer for server"),
            ("Delete", "Delete selected server")
        ]
        
        # Create scrollable frame for shortcuts
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        for shortcut, description in shortcuts:
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row_frame,
                text=shortcut,
                font=("Consolas", 12, "bold"),
                width=120,
                anchor="w"
            ).pack(side="left", padx=(10, 20))
            
            ctk.CTkLabel(
                row_frame,
                text=description,
                font=("Arial", 12),
                anchor="w"
            ).pack(side="left")
        
        # Close button
        ctk.CTkButton(
            main_frame,
            text="Close",
            command=help_dialog.destroy,
            width=100,
            height=36,
            corner_radius=6
        ).pack()
        
        # Bind escape key
        help_dialog.bind('<Escape>', lambda e: help_dialog.destroy())