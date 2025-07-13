"""File Explorer Window for SSH connections."""

import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
from typing import Optional, List, Tuple
import threading

from .design_system import design, styles, components
from .dialogs import InputDialog
from ..storage import Server, ServerStorage
from ..connections import SSHConnection, ConnectionManager
from ..utils.logger import logger
from ..utils.helpers import format_file_size
from ..utils.config import config


class FileExplorerWindow:
    """Custom file explorer window for SSH connections."""
    
    def __init__(self, parent: ctk.CTk, server: Server, storage: ServerStorage):
        self.parent = parent
        self.server = server
        self.storage = storage
        self.connection: Optional[SSHConnection] = None
        self.current_path: str = "/"
        self.selected_item: Optional[str] = None
        self.running = True
        self._window_valid = True
        
        # Create window with design system styling
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"File Explorer - {server.name}")
        self.window.geometry("900x600")
        self.window.minsize(700, 500)
        self.window.configure(fg_color=design.get_color("bg_primary"))
        
        # Connection manager
        self.connection_manager = ConnectionManager()
        
        # Log connection
        self.connection_log_id = self.storage.log_connection(server.id, "file_explorer")
        
        # Set up UI
        self.setup_ui()
        
        # Connect to server
        self.connect_to_server()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_ui(self) -> None:
        """Set up the file explorer UI."""
        # Header with connection info
        header_frame = components.create_frame(
            self.window,
            height=design.get_size("header_height")
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Bottom border for header
        border_frame = ctk.CTkFrame(
            self.window,
            height=1,
            fg_color=design.get_color("border_primary")
        )
        border_frame.pack(fill="x")
        
        # Connection status
        status_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_container.pack(side="left", fill="y", padx=design.get_spacing("xxl"))
        
        self.status_indicator = components.create_label(
            status_container,
            text="●",
            font=("Arial", 14),
            text_color=design.get_color("text_secondary")
        )
        self.status_indicator.pack(side="left", padx=(0, design.get_spacing("md")))
        
        self.status_label = components.create_label(
            status_container,
            text=f"Connecting to {self.server.name}...",
            font=design.get_font("body_medium")
        )
        self.status_label.pack(side="left")
        
        # Path navigation
        nav_frame = components.create_frame(self.window)
        nav_frame.pack(fill="x", padx=design.get_spacing("lg"), pady=design.get_spacing("sm"))
        
        # Navigation buttons
        self.back_btn = components.create_button(
            nav_frame,
            text="←",
            width=40,
            command=self.go_back
        )
        self.back_btn.configure(state="disabled")
        self.back_btn.pack(side="left", padx=(0, design.get_spacing("sm")))
        
        self.up_btn = components.create_button(
            nav_frame,
            text="↑",
            width=40,
            command=self.go_up
        )
        self.up_btn.configure(state="disabled")
        self.up_btn.pack(side="left", padx=(0, design.get_spacing("sm")))
        
        self.refresh_btn = components.create_button(
            nav_frame,
            text="⟳",
            width=40,
            command=self.refresh_files
        )
        self.refresh_btn.configure(state="disabled")
        self.refresh_btn.pack(side="left", padx=(0, design.get_spacing("lg")))
        
        # Path entry
        self.path_var = ctk.StringVar(value="/")
        self.path_entry = components.create_entry(
            nav_frame,
            textvariable=self.path_var
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, design.get_spacing("lg")))
        self.path_entry.bind("<Return>", lambda e: self.navigate_to_path())
        
        # Toolbar
        toolbar_frame = components.create_frame(self.window)
        toolbar_frame.pack(fill="x", padx=design.get_spacing("lg"), pady=design.get_spacing("sm"))
        
        buttons = [
            ("📥 Download", self.download_file),
            ("📤 Upload", self.upload_file),
            ("📁 New Folder", self.create_folder),
            ("🗑️ Delete", self.delete_file),
            ("✏️ Rename", self.rename_file)
        ]
        
        self.toolbar_buttons = []
        for text, command in buttons:
            btn = components.create_button(
                toolbar_frame,
                text=text,
                command=command,
                width=100
            )
            btn.configure(state="disabled")
            btn.pack(side="left", padx=design.get_spacing("xs"))
            self.toolbar_buttons.append(btn)
        
        # Show connection problems hint
        hint_label = components.create_label(
            toolbar_frame,
            text="Tip: Click refresh if files don't load",
            style="secondary",
            font=design.get_font("caption")
        )
        hint_label.pack(side="right", padx=design.get_spacing("lg"))
        
        # File list
        list_frame = components.create_frame(self.window, style="bordered")
        list_frame.pack(fill="both", expand=True, padx=design.get_spacing("lg"), pady=design.get_spacing("sm"))
        
        # Configure treeview styling
        styles.configure_treeview_style()
        
        # Create treeview
        self.tree = ttk.Treeview(
            list_frame,
            columns=("type", "size", "modified", "permissions"),
            show="tree headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Modified")
        self.tree.heading("permissions", text="Permissions")
        
        self.tree.column("#0", width=300)
        self.tree.column("type", width=80)
        self.tree.column("size", width=100)
        self.tree.column("modified", width=180)
        self.tree.column("permissions", width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Double-Button-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Status bar
        status_bar = components.create_frame(
            self.window,
            height=30
        )
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)
        
        # Top border for status bar
        status_border = ctk.CTkFrame(
            self.window,
            height=1,
            fg_color=design.get_color("border_primary")
        )
        status_border.pack(fill="x", before=status_bar)
        
        self.info_label = components.create_label(
            status_bar,
            text="Ready",
            font=design.get_font("body_small")
        )
        self.info_label.pack(side="left", padx=design.get_spacing("lg"))
        
    def connect_to_server(self) -> None:
        """Connect to the SSH server."""
        def connect():
            try:
                # Create connection
                self.connection = self.connection_manager.create_connection(self.server.id)
                
                # Connect
                success = self.connection.connect(
                    self.server.host,
                    self.server.port,
                    self.server.username,
                    self.server.password or "",
                    use_key_auth=self.server.use_key_auth,
                    private_key_path=self.server.private_key_path,
                    private_key_passphrase=self.server.private_key_passphrase
                )
                
                if success:
                    # Update UI in main thread
                    self.window.after(0, self.on_connection_success)
                else:
                    self.window.after(0, self.on_connection_failed)
                    
            except Exception as e:
                logger.error(f"Connection error: {e}")
                self.window.after(0, self.on_connection_failed)
        
        # Connect in thread
        threading.Thread(target=connect, daemon=True).start()
        
    def on_connection_success(self) -> None:
        """Handle successful connection."""
        self.status_indicator.configure(text_color=design.get_color("text_primary"))
        self.status_label.configure(text=f"Connected to {self.server.name}")
        
        # Enable controls
        self.back_btn.configure(state="normal")
        self.up_btn.configure(state="normal")
        self.refresh_btn.configure(state="normal")
        for btn in self.toolbar_buttons:
            btn.configure(state="normal")
        
        # Load initial directory
        self.refresh_files()
        
    def on_connection_failed(self) -> None:
        """Handle failed connection."""
        self.status_indicator.configure(text_color=design.get_color("text_primary"))
        self.status_label.configure(text="Connection failed")
        
        messagebox.showerror(
            "Connection Error",
            f"Failed to connect to {self.server.name}.\nPlease check your connection settings."
        )
        
        # Close window after delay
        self.window.after(2000, self.window.destroy)
        
    def refresh_files(self) -> None:
        """Refresh the file list."""
        if not self.connection or not self.is_window_valid():
            return
            
        # Clear tree
        try:
            self.tree.delete(*self.tree.get_children())
        except:
            return
        
        # Update status
        self.safe_ui_update(self.info_label, "configure", text="Loading...")
        
        # Disable refresh button while loading
        self.safe_ui_update(self.refresh_btn, "configure", state="disabled")
        
        def load_files():
            try:
                # Check if window is still valid before proceeding
                if not self.is_window_valid():
                    return
                    
                # List files
                files = self.connection.list_files(self.current_path)
                
                # Update UI in main thread
                if self.is_window_valid():
                    self.window.after(0, lambda: self.display_files(files))
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error listing files: {error_msg}")
                if self.is_window_valid():
                    self.window.after(0, lambda msg=error_msg: self.handle_load_error(msg))
            finally:
                # Re-enable refresh button
                if self.is_window_valid():
                    self.window.after(0, lambda: self.safe_ui_update(self.refresh_btn, "configure", state="normal"))
        
        # Load in thread
        threading.Thread(target=load_files, daemon=True).start()
    
    def handle_load_error(self, error_msg: str) -> None:
        """Handle file loading errors."""
        if not self.is_window_valid():
            return
            
        self.safe_ui_update(self.info_label, "configure", text="Error loading files")
        
        # Check if it's a connection issue
        if "SSH session not active" in error_msg or "Connection lost" in error_msg:
            # Show reconnection option
            result = messagebox.askretrycancel(
                "Connection Error",
                f"Lost connection to {self.server.name}.\nWould you like to reconnect?"
            )
            if result:
                self.reconnect()
            else:
                self.window.destroy()
        else:
            # Show regular error
            self.show_error(f"Error loading files: {error_msg}")
        
    def display_files(self, files: List[dict]) -> None:
        """Display files in the tree."""
        if not self.is_window_valid():
            return
            
        # Clear tree
        try:
            self.tree.delete(*self.tree.get_children())
        except:
            return
        
        # Add parent directory if not root
        if self.current_path != "/":
            self.tree.insert("", 0, text="..", values=("Directory", "", "", ""))
        
        # Sort files (directories first)
        dirs = [f for f in files if f['type'] == 'directory']
        files_only = [f for f in files if f['type'] != 'directory']
        
        dirs.sort(key=lambda x: x['name'].lower())
        files_only.sort(key=lambda x: x['name'].lower())
        
        # Add items
        for item in dirs + files_only:
            icon = "📁" if item['type'] == 'directory' else "📄"
            size = "" if item['type'] == 'directory' else format_file_size(item.get('size', 0))
            
            # Format modified time
            modified = ""
            if 'modified' in item:
                try:
                    dt = datetime.fromtimestamp(item['modified'])
                    modified = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            self.tree.insert(
                "",
                "end",
                text=f"{icon} {item['name']}",
                values=(
                    item['type'].capitalize(),
                    size,
                    modified,
                    item.get('permissions', '')
                ),
                tags=(item['type'],)
            )
        
        # Update status
        try:
            count = len(self.tree.get_children())
            if self.current_path != "/":
                count -= 1  # Exclude parent directory
            self.safe_ui_update(self.info_label, "configure", text=f"{count} items")
            
            # Update path
            self.path_var.set(self.current_path)
        except:
            pass
        
    def on_double_click(self, event) -> None:
        """Handle double-click on item."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_type = item['values'][0]
        
        if name == "..":
            self.go_up()
        elif item_type == "Directory":
            # Navigate to directory
            new_path = os.path.join(self.current_path, name).replace("\\", "/")
            if not new_path.startswith("/"):
                new_path = "/" + new_path
            self.current_path = new_path
            self.refresh_files()
            
    def on_select(self, event) -> None:
        """Handle item selection."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_item = item['text'].replace("📁 ", "").replace("📄 ", "")
        else:
            self.selected_item = None
            
    def go_back(self) -> None:
        """Go back to previous directory."""
        # TODO: Implement navigation history
        pass
        
    def go_up(self) -> None:
        """Go up one directory level."""
        if self.current_path == "/":
            return
            
        self.current_path = os.path.dirname(self.current_path)
        if not self.current_path:
            self.current_path = "/"
        self.refresh_files()
        
    def navigate_to_path(self) -> None:
        """Navigate to path in entry."""
        path = self.path_var.get()
        if path:
            self.current_path = path
            self.refresh_files()
            
    def download_file(self) -> None:
        """Download selected file."""
        if not self.selected_item or self.selected_item == "..":
            return
            
        # Get item type
        selection = self.tree.selection()
        if not selection:
            return
        item_type = self.tree.item(selection[0])['values'][0]
        
        if item_type == "Directory":
            messagebox.showinfo("Info", "Directory download not supported yet.")
            return
            
        # Ask for save location
        local_path = filedialog.asksaveasfilename(
            defaultextension="",
            initialfile=self.selected_item
        )
        
        if local_path:
            remote_path = os.path.join(self.current_path, self.selected_item).replace("\\", "/")
            
            # Download in thread
            def download():
                try:
                    if self.is_window_valid():
                        self.window.after(0, lambda: self.safe_ui_update(self.info_label, "configure", text="Downloading..."))
                    self.connection.download_file(remote_path, local_path)
                    if self.is_window_valid():
                        self.window.after(0, lambda: self.safe_ui_update(self.info_label, "configure", text="Download complete"))
                except Exception as e:
                    if self.is_window_valid():
                        self.window.after(0, lambda: self.show_error(f"Download failed: {str(e)}"))
                    
            threading.Thread(target=download, daemon=True).start()
            
    def upload_file(self) -> None:
        """Upload file to current directory."""
        local_path = filedialog.askopenfilename()
        if not local_path:
            return
            
        filename = os.path.basename(local_path)
        remote_path = os.path.join(self.current_path, filename).replace("\\", "/")
        
        # Upload in thread
        def upload():
            try:
                if self.is_window_valid():
                    self.window.after(0, lambda: self.safe_ui_update(self.info_label, "configure", text="Uploading..."))
                self.connection.upload_file(local_path, remote_path)
                if self.is_window_valid():
                    self.window.after(0, lambda: self.safe_ui_update(self.info_label, "configure", text="Upload complete"))
                    self.window.after(0, self.refresh_files)
            except Exception as e:
                if self.is_window_valid():
                    self.window.after(0, lambda: self.show_error(f"Upload failed: {str(e)}"))
                
        threading.Thread(target=upload, daemon=True).start()
        
    def create_folder(self) -> None:
        """Create new folder."""
        # Ask for folder name
        dialog = InputDialog(
            parent=self.window,
            title="New Folder",
            prompt="Enter folder name:",
            placeholder="folder_name"
        )
        folder_name = dialog.get_input()
        
        if folder_name:
            remote_path = os.path.join(self.current_path, folder_name).replace("\\", "/")
            
            def create():
                try:
                    self.connection.create_directory(remote_path)
                    self.window.after(0, self.refresh_files)
                except Exception as e:
                    self.window.after(0, lambda: self.show_error(f"Failed to create folder: {str(e)}"))
                    
            threading.Thread(target=create, daemon=True).start()
            
    def delete_file(self) -> None:
        """Delete selected file or folder."""
        if not self.selected_item or self.selected_item == "..":
            return
            
        # Confirm deletion
        result = messagebox.askyesno(
            "Delete",
            f"Are you sure you want to delete '{self.selected_item}'?"
        )
        
        if result:
            remote_path = os.path.join(self.current_path, self.selected_item).replace("\\", "/")
            
            def delete():
                try:
                    # Check if directory
                    selection = self.tree.selection()
                    if selection:
                        item_type = self.tree.item(selection[0])['values'][0]
                        if item_type == "Directory":
                            self.connection.delete_directory(remote_path)
                        else:
                            self.connection.delete_file(remote_path)
                    
                    self.window.after(0, self.refresh_files)
                except Exception as e:
                    self.window.after(0, lambda: self.show_error(f"Failed to delete: {str(e)}"))
                    
            threading.Thread(target=delete, daemon=True).start()
            
    def rename_file(self) -> None:
        """Rename selected file or folder."""
        if not self.selected_item or self.selected_item == "..":
            return
            
        # Ask for new name
        dialog = InputDialog(
            parent=self.window,
            title="Rename",
            prompt="Enter new name:",
            placeholder="new_name",
            initial_value=self.selected_item
        )
        new_name = dialog.get_input()
        
        if new_name and new_name != self.selected_item:
            old_path = os.path.join(self.current_path, self.selected_item).replace("\\", "/")
            new_path = os.path.join(self.current_path, new_name).replace("\\", "/")
            
            def rename():
                try:
                    self.connection.rename(old_path, new_path)
                    self.window.after(0, self.refresh_files)
                except Exception as e:
                    self.window.after(0, lambda: self.show_error(f"Failed to rename: {str(e)}"))
                    
            threading.Thread(target=rename, daemon=True).start()
            
    def show_error(self, message: str) -> None:
        """Show error message."""
        self.info_label.configure(text="Error")
        messagebox.showerror("Error", message)
        
    def is_window_valid(self) -> bool:
        """Check if window is still valid and not destroyed."""
        try:
            return self._window_valid and self.window.winfo_exists()
        except:
            return False
    
    def safe_ui_update(self, widget, method: str, *args, **kwargs) -> None:
        """Safely update UI element if window is still valid."""
        if self.is_window_valid():
            try:
                getattr(widget, method)(*args, **kwargs)
            except Exception as e:
                logger.debug(f"UI update failed: {e}")
    
    def on_close(self) -> None:
        """Handle window close."""
        # Mark window as invalid
        self._window_valid = False
        
        # Stop running
        self.running = False
        
        # Log disconnection
        if self.connection_log_id:
            self.storage.log_disconnection(self.connection_log_id)
            
        # Close connection
        if self.connection:
            self.connection_manager.close_connection(self.server.id)
            
        # Destroy window
        self.window.destroy()
    
    def reconnect(self) -> None:
        """Attempt to reconnect to the server."""
        self.status_indicator.configure(text_color=design.get_color("text_secondary"))
        self.status_label.configure(text="Reconnecting...")
        self.info_label.configure(text="Reconnecting...")
        
        # Disable all controls
        self.back_btn.configure(state="disabled")
        self.up_btn.configure(state="disabled")
        self.refresh_btn.configure(state="disabled")
        for btn in self.toolbar_buttons:
            btn.configure(state="disabled")
        
        def reconnect_thread():
            try:
                # Close existing connection
                if self.connection:
                    self.connection_manager.close_connection(self.server.id)
                
                # Small delay
                import time
                time.sleep(1)
                
                # Create new connection
                self.connection = self.connection_manager.create_connection(self.server.id)
                
                # Connect
                success = self.connection.connect(
                    self.server.host,
                    self.server.port,
                    self.server.username,
                    self.server.password or "",
                    use_key_auth=self.server.use_key_auth,
                    private_key_path=self.server.private_key_path,
                    private_key_passphrase=self.server.private_key_passphrase
                )
                
                if success:
                    self.window.after(0, self.on_reconnect_success)
                else:
                    self.window.after(0, self.on_reconnect_failed)
                    
            except Exception as e:
                logger.error(f"Reconnection error: {e}")
                self.window.after(0, self.on_reconnect_failed)
        
        threading.Thread(target=reconnect_thread, daemon=True).start()
    
    def on_reconnect_success(self) -> None:
        """Handle successful reconnection."""
        self.status_indicator.configure(text_color=design.get_color("text_primary"))
        self.status_label.configure(text=f"Connected to {self.server.name}")
        self.info_label.configure(text="Ready")
        
        # Enable controls
        self.back_btn.configure(state="normal")
        self.up_btn.configure(state="normal")
        self.refresh_btn.configure(state="normal")
        for btn in self.toolbar_buttons:
            btn.configure(state="normal")
        
        # Refresh current directory
        self.refresh_files()
    
    def on_reconnect_failed(self) -> None:
        """Handle failed reconnection."""
        self.status_indicator.configure(text_color=design.get_color("text_primary"))
        self.status_label.configure(text="Reconnection failed")
        self.info_label.configure(text="Connection lost")
        
        # Show error dialog
        messagebox.showerror(
            "Reconnection Failed",
            f"Failed to reconnect to {self.server.name}.\nPlease check your connection and try again."
        )
        
        # Close window
        self.window.after(1000, self.window.destroy)