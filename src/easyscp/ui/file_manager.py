"""File manager tab component."""

import customtkinter as ctk
from tkinter import ttk, filedialog
import os
from datetime import datetime
from typing import Optional

from .base import BaseTab
from ..connections import SSHConnection
from ..utils.helpers import format_file_size
from ..utils.logger import logger
from ..utils.config import config

class FileManagerTab(BaseTab):
    """File manager tab for browsing and managing remote files."""
    
    def __init__(self, parent: ctk.CTkFrame):
        self.connection: Optional[SSHConnection] = None
        self.current_path: str = "/"
        super().__init__(parent)
        
    def setup_ui(self) -> None:
        """Set up the file manager UI."""
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Path bar
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(path_frame, text="Path:", font=("Arial", 12)).pack(side="left", padx=5)
        self.path_label = ctk.CTkLabel(path_frame, text="/", font=("Arial", 12, "bold"))
        self.path_label.pack(side="left", padx=5)
        
        # Toolbar
        toolbar = ctk.CTkFrame(main_frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        buttons = [
            ("Refresh", self.refresh_files),
            ("Up", self.go_up),
            ("Download", self.download_file),
            ("Upload", self.upload_file),
            ("Delete", self.delete_file),
            ("New Folder", self.create_folder),
        ]
        
        for text, command in buttons:
            ctk.CTkButton(
                toolbar, 
                text=text, 
                command=command,
                width=90,
                height=28,
                fg_color=("gray85", "gray25"),
                hover_color=("gray75", "gray35")
            ).pack(side="left", padx=2)
            
        # File tree
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("type", "size", "modified"),
            show="tree headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Modified")
        
        self.tree.column("#0", width=300)
        self.tree.column("type", width=80)
        self.tree.column("size", width=100)
        self.tree.column("modified", width=180)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Double-Button-1>", self._on_double_click)
        
        # Show welcome message
        self._show_welcome()
        
    def _show_welcome(self) -> None:
        """Show welcome message when not connected."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", text="Connect to a server to browse files", values=("", "", ""))
        
    def set_connection(self, connection: SSHConnection) -> None:
        """Set the SSH connection."""
        self.connection = connection
        
    def on_connect(self) -> None:
        """Called when connection is established."""
        if self.connection:
            self.current_path = self.connection.get_current_directory()
            self.refresh_files()
            
    def on_disconnect(self) -> None:
        """Called when connection is closed."""
        self.connection = None
        self.current_path = "/"
        self.path_label.configure(text="/")
        self._show_welcome()
        
    def refresh_files(self) -> None:
        """Refresh the file list."""
        if not self.connection or not self.connection.is_connected:
            return
            
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # Get file list
            files = self.connection.list_directory(self.current_path)
            
            # Sort files (directories first, then by name)
            files.sort(key=lambda x: (not x.st_mode & 0o040000, x.filename.lower()))
            
            # Add files to tree
            for file_attr in files:
                name = file_attr.filename
                
                # Skip hidden files if configured
                if name.startswith('.') and not config.get("file_manager.show_hidden_files", False):
                    continue
                    
                # Determine file type
                if file_attr.st_mode & 0o040000:  # Directory
                    file_type = "Folder"
                    size = ""
                else:
                    file_type = "File"
                    size = format_file_size(file_attr.st_size)
                    
                # Format modification time
                modified = datetime.fromtimestamp(file_attr.st_mtime).strftime("%Y-%m-%d %H:%M")
                
                # Insert into tree
                self.tree.insert("", "end", text=name, values=(file_type, size, modified))
                
            # Update path label
            self.path_label.configure(text=self.current_path)
            
        except Exception as e:
            logger.error(f"Failed to refresh files: {e}")
            self.tree.insert("", "end", text=f"Error: {e}", values=("", "", ""))
            
    def go_up(self) -> None:
        """Navigate to parent directory."""
        if not self.connection or self.current_path == "/":
            return
            
        parent_path = os.path.dirname(self.current_path).replace("\\", "/")
        if self.connection.change_directory(parent_path):
            self.current_path = parent_path
            self.refresh_files()
            
    def _on_double_click(self, event) -> None:
        """Handle double-click on item."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        name = item["text"]
        file_type = item["values"][0]
        
        if file_type == "Folder" and self.connection:
            # Navigate into folder
            new_path = os.path.join(self.current_path, name).replace("\\", "/")
            if self.connection.change_directory(new_path):
                self.current_path = new_path
                self.refresh_files()
                
    def download_file(self) -> None:
        """Download selected file."""
        selection = self.tree.selection()
        if not selection or not self.connection:
            return
            
        item = self.tree.item(selection[0])
        name = item["text"]
        file_type = item["values"][0]
        
        if file_type != "File":
            return
            
        # Ask for save location
        default_dir = config.get("file_manager.default_download_path", str(os.path.expanduser("~/Downloads")))
        local_path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=name,
            title="Save file as..."
        )
        
        if local_path:
            remote_path = os.path.join(self.current_path, name).replace("\\", "/")
            if self.connection.download_file(remote_path, local_path):
                logger.info(f"Downloaded {name} successfully")
            else:
                logger.error(f"Failed to download {name}")
                
    def upload_file(self) -> None:
        """Upload file to current directory."""
        if not self.connection:
            return
            
        local_path = filedialog.askopenfilename(title="Select file to upload")
        if not local_path:
            return
            
        filename = os.path.basename(local_path)
        remote_path = os.path.join(self.current_path, filename).replace("\\", "/")
        
        if self.connection.upload_file(local_path, remote_path):
            logger.info(f"Uploaded {filename} successfully")
            self.refresh_files()
        else:
            logger.error(f"Failed to upload {filename}")
            
    def delete_file(self) -> None:
        """Delete selected file."""
        selection = self.tree.selection()
        if not selection or not self.connection:
            return
            
        item = self.tree.item(selection[0])
        name = item["text"]
        
        # Confirm deletion
        confirm = ctk.CTkToplevel(self.parent.winfo_toplevel())
        confirm.title("Confirm Delete")
        confirm.geometry("350x150")
        
        ctk.CTkLabel(confirm, text=f"Delete '{name}'?", font=("Arial", 14)).pack(pady=20)
        
        button_frame = ctk.CTkFrame(confirm)
        button_frame.pack(pady=10)
        
        def do_delete():
            remote_path = os.path.join(self.current_path, name).replace("\\", "/")
            if self.connection.delete_file(remote_path):
                logger.info(f"Deleted {name}")
                self.refresh_files()
            confirm.destroy()
            
        ctk.CTkButton(button_frame, text="Yes", command=do_delete, width=80, fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40")).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="No", command=confirm.destroy, width=80, fg_color=("gray75", "gray25"), hover_color=("gray65", "gray35")).pack(side="left", padx=5)
        
    def create_folder(self) -> None:
        """Create new folder in current directory."""
        if not self.connection:
            return
            
        # Ask for folder name
        dialog = ctk.CTkToplevel(self.parent.winfo_toplevel())
        dialog.title("New Folder")
        dialog.geometry("350x150")
        
        ctk.CTkLabel(dialog, text="Folder name:", font=("Arial", 12)).pack(pady=10)
        
        entry = ctk.CTkEntry(dialog, width=250)
        entry.pack(pady=5)
        entry.focus()
        
        def create():
            name = entry.get().strip()
            if name:
                remote_path = os.path.join(self.current_path, name).replace("\\", "/")
                if self.connection.create_directory(remote_path):
                    logger.info(f"Created folder {name}")
                    self.refresh_files()
            dialog.destroy()
            
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Create", command=create, width=80, fg_color=("gray85", "gray25"), hover_color=("gray75", "gray35")).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy, width=80, fg_color=("gray75", "gray25"), hover_color=("gray65", "gray35")).pack(side="left", padx=5)
        
        entry.bind("<Return>", lambda e: create())