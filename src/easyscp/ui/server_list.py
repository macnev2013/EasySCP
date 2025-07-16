"""Server list panel component."""

import customtkinter as ctk
from typing import Callable, Optional, Dict

from ..storage import Server
from ..utils.logger import logger

class ServerListPanel:
    """Panel for displaying and managing server list."""
    
    def __init__(self, parent: ctk.CTkFrame):
        self.parent = parent
        self.server_frames: Dict[int, ctk.CTkFrame] = {}
        self.on_connect_files: Optional[Callable] = None
        self.on_connect_terminal: Optional[Callable] = None
        self.on_add_server: Optional[Callable] = None
        self.on_edit_server: Optional[Callable] = None
        self.on_delete_server: Optional[Callable] = None
        self.on_manage_snippets: Optional[Callable] = None
        self.selected_server_id: Optional[int] = None
        self.all_servers: list[Server] = []
        
        # Create main container that fills parent
        self.container = ctk.CTkFrame(parent, fg_color=("white", "white"))
        self.container.pack(fill="both", expand=True)
        
        self.setup_ui()
        self._setup_keyboard_navigation()
        
    def setup_ui(self) -> None:
        """Set up the server list UI."""
        # Header with title and search
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(10, 10))
        
        ctk.CTkLabel(
            header_frame, 
            text="Servers", 
            font=("Arial", 20, "bold"),
            text_color=("black", "black")
        ).pack(side="left")
        
        # Server count
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 12),
            text_color=("gray30", "gray30")
        )
        self.count_label.pack(side="left", padx=(10, 0))
        
        # Search bar
        search_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_var = ctk.StringVar()
        # Use trace_add for Python 3.13+ compatibility
        try:
            self.search_var.trace_add("write", lambda *args: self._on_search_changed())
        except AttributeError:
            # Fallback for older Python versions
            self.search_var.trace("w", self._on_search_changed)
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search servers...",
            textvariable=self.search_var,
            height=36,
            corner_radius=0,
            border_width=1,
            border_color=("black", "black"),
            fg_color=("white", "white"),
            text_color=("black", "black")
        )
        self.search_entry.pack(fill="x")
        
        # Action buttons with better styling
        button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Add button - minimal styling
        ctk.CTkButton(
            button_frame, 
            text="+ Add Server", 
            command=self._handle_add,
            width=110,
            height=36,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        ).pack(side="left", padx=(0, 8))
        
        # Edit button
        self.edit_btn = ctk.CTkButton(
            button_frame, 
            text="✏ Edit", 
            command=self._handle_edit,
            width=90,
            height=36,
            corner_radius=0,
            state="disabled",
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        )
        self.edit_btn.pack(side="left", padx=(0, 8))
        
        # Delete button - minimal styling
        self.delete_btn = ctk.CTkButton(
            button_frame, 
            text="🗑 Delete", 
            command=self._handle_delete,
            width=90,
            height=36,
            corner_radius=0,
            state="disabled",
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        )
        self.delete_btn.pack(side="left", padx=(0, 8))
        
        # Snippets button - minimal styling
        self.snippets_btn = ctk.CTkButton(
            button_frame, 
            text="📋 Snippets", 
            command=self._handle_snippets,
            width=100,
            height=36,
            corner_radius=0,
            state="disabled",
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        )
        self.snippets_btn.pack(side="left")
        
        # Server list container with improved styling
        list_frame = ctk.CTkFrame(self.container, corner_radius=0, fg_color=("white", "white"))
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.server_list = ctk.CTkScrollableFrame(
            list_frame,
            corner_radius=0,
            fg_color=("white", "white"),
            scrollbar_button_color=("gray70", "gray70"),
            scrollbar_button_hover_color=("gray50", "gray50")
        )
        self.server_list.pack(fill="both", expand=True)
        
        # Empty state message
        self.empty_frame = ctk.CTkFrame(self.server_list, fg_color="transparent")
        
        # Server icon
        icon_label = ctk.CTkLabel(
            self.empty_frame,
            text="🖥️",
            font=("Arial", 48)
        )
        icon_label.pack(pady=(80, 20))
        
        self.empty_label = ctk.CTkLabel(
            self.empty_frame,
            text="No SSH connections yet",
            font=("Arial", 16, "bold"),
            text_color=("black", "black")
        )
        self.empty_label.pack()
        
        self.empty_sublabel = ctk.CTkLabel(
            self.empty_frame,
            text="Add your first server to get started",
            font=("Arial", 13),
            text_color=("gray30", "gray30")
        )
        self.empty_sublabel.pack(pady=(5, 30))
        
        # Add server button in empty state - minimal
        ctk.CTkButton(
            self.empty_frame,
            text="+ Add Server",
            command=self._handle_add,
            width=140,
            height=40,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black"),
            font=("Arial", 14)
        ).pack()
        
    def refresh(self, servers: list[Server]) -> None:
        """Refresh the server list."""
        # Store original servers
        self.all_servers = servers
        
        # Update count
        count = len(servers)
        self.count_label.configure(text=f"({count})" if count > 0 else "")
        
        # Clear existing frames
        for frame in self.server_frames.values():
            frame.destroy()
        self.server_frames.clear()
        
        # Show empty state or servers
        if not servers:
            self.empty_frame.pack(fill="both", expand=True)
        else:
            self.empty_frame.pack_forget()
            # Add server items
            for server in servers:
                self._create_server_item(server)
                
        # Reset selection
        self.selected_server_id = None
        self._update_button_states()
            
    def _create_server_item(self, server: Server) -> None:
        """Create a server list item."""
        frame = ctk.CTkFrame(
            self.server_list,
            corner_radius=0,
            border_width=1,
            border_color=("black", "black"),
            fg_color=("white", "white")
        )
        frame.pack(fill="x", pady=4)
        
        # Store original colors for hover effect
        frame._original_fg_color = ("white", "white")
        frame._hover_color = ("gray97", "gray97")
        
        # Make frame clickable for selection only
        frame.bind("<Button-1>", lambda e: self._select_server(server.id))
        frame.bind("<Enter>", lambda e: self._on_frame_enter(frame))
        frame.bind("<Leave>", lambda e: self._on_frame_leave(frame))
        
        # Server info with better padding
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=16, pady=12)
        info_frame.bind("<Button-1>", lambda e: self._select_server(server.id))
        info_frame.bind("<Enter>", lambda e: self._on_frame_enter(frame))
        info_frame.bind("<Leave>", lambda e: self._on_frame_leave(frame))
        
        name_label = ctk.CTkLabel(
            info_frame, 
            text=server.name, 
            font=("Arial", 15, "bold"),
            anchor="w",
            text_color=("black", "black")
        )
        name_label.pack(fill="x")
        name_label.bind("<Button-1>", lambda e: self._select_server(server.id))
        name_label.bind("<Enter>", lambda e: self._on_frame_enter(frame))
        name_label.bind("<Leave>", lambda e: self._on_frame_leave(frame))
        
        details_text = f"{server.username}@{server.host}:{server.port}"
        host_label = ctk.CTkLabel(
            info_frame, 
            text=details_text, 
            font=("Arial", 12),
            text_color=("gray30", "gray30"),
            anchor="w"
        )
        host_label.pack(fill="x", pady=(2, 0))
        host_label.bind("<Button-1>", lambda e: self._select_server(server.id))
        host_label.bind("<Enter>", lambda e: self._on_frame_enter(frame))
        host_label.bind("<Leave>", lambda e: self._on_frame_leave(frame))
        
        # Action buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(side="right", padx=12)
        
        # File Explorer button - minimal
        files_btn = ctk.CTkButton(
            button_frame,
            text="📁 Files",
            width=85,
            height=32,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black"),
            command=lambda: self._handle_connect_files(server)
        )
        files_btn.pack(side="left", padx=(0, 6))
        
        # Terminal button - minimal
        terminal_btn = ctk.CTkButton(
            button_frame,
            text="💻 Terminal",
            width=95,
            height=32,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black"),
            command=lambda: self._handle_connect_terminal(server)
        )
        terminal_btn.pack(side="left")
        
        self.server_frames[server.id] = frame
        
    def _select_server(self, server_id: int) -> None:
        """Select a server."""
        self.selected_server_id = server_id
        
        # Update visual selection with better highlighting
        for sid, frame in self.server_frames.items():
            if sid == server_id:
                frame.configure(
                    border_color=("black", "black"),
                    border_width=2
                )
            else:
                frame.configure(
                    border_color=("black", "black"),
                    border_width=1
                )
        
        self._update_button_states()
                
    def _handle_connect_files(self, server: Server) -> None:
        """Handle file explorer connection."""
        self._select_server(server.id)
        if self.on_connect_files:
            self.on_connect_files(server)
            
    def _handle_connect_terminal(self, server: Server) -> None:
        """Handle terminal connection."""
        self._select_server(server.id)
        if self.on_connect_terminal:
            self.on_connect_terminal(server)
            
    def _handle_add(self) -> None:
        """Handle add server button."""
        if self.on_add_server:
            self.on_add_server()
            
    def _handle_edit(self) -> None:
        """Handle edit server button."""
        if self.selected_server_id and self.on_edit_server:
            self.on_edit_server(self.selected_server_id)
            
    def _handle_delete(self) -> None:
        """Handle delete server button."""
        if self.selected_server_id and self.on_delete_server:
            self.on_delete_server(self.selected_server_id)
    
    def _handle_snippets(self) -> None:
        """Handle manage snippets button."""
        if self.selected_server_id and self.on_manage_snippets:
            self.on_manage_snippets(self.selected_server_id)
    
    def _update_button_states(self) -> None:
        """Update edit and delete button states."""
        if self.selected_server_id:
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
            self.snippets_btn.configure(state="normal")
        else:
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            self.snippets_btn.configure(state="disabled")
    
    def _on_search_changed(self, *args) -> None:
        """Handle search text change."""
        if not hasattr(self, 'all_servers'):
            return
            
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # Show all servers
            self.refresh(self.all_servers)
        else:
            # Filter servers
            filtered = [
                server for server in self.all_servers
                if search_term in server.name.lower() or
                   search_term in server.host.lower() or
                   search_term in server.username.lower()
            ]
            self.refresh(filtered)
    
    def _on_frame_enter(self, frame: ctk.CTkFrame) -> None:
        """Handle mouse enter on server frame."""
        if frame not in [f for f in self.server_frames.values()]:
            return
        # Only apply hover if not selected
        server_id = [sid for sid, f in self.server_frames.items() if f == frame][0]
        if server_id != self.selected_server_id:
            frame.configure(fg_color=frame._hover_color)
    
    def _on_frame_leave(self, frame: ctk.CTkFrame) -> None:
        """Handle mouse leave on server frame."""
        if frame not in [f for f in self.server_frames.values()]:
            return
        # Only reset if not selected
        server_id = [sid for sid, f in self.server_frames.items() if f == frame][0]
        if server_id != self.selected_server_id:
            frame.configure(fg_color=frame._original_fg_color)
    
    def _setup_keyboard_navigation(self) -> None:
        """Set up keyboard navigation for the server list."""
        self.container.bind("<Up>", self._navigate_up)
        self.container.bind("<Down>", self._navigate_down)
        self.container.bind("<Return>", self._connect_selected)
        self.container.bind("<Delete>", lambda e: self._handle_delete())
        
        # Make container focusable
        self.container.focus_set()
    
    def _navigate_up(self, event) -> None:
        """Navigate up in the server list."""
        if not self.all_servers:
            return
        
        current_idx = -1
        if self.selected_server_id:
            for i, server in enumerate(self.all_servers):
                if server.id == self.selected_server_id:
                    current_idx = i
                    break
        
        new_idx = max(0, current_idx - 1) if current_idx > 0 else len(self.all_servers) - 1
        self._select_server(self.all_servers[new_idx].id)
    
    def _navigate_down(self, event) -> None:
        """Navigate down in the server list."""
        if not self.all_servers:
            return
        
        current_idx = -1
        if self.selected_server_id:
            for i, server in enumerate(self.all_servers):
                if server.id == self.selected_server_id:
                    current_idx = i
                    break
        
        new_idx = min(len(self.all_servers) - 1, current_idx + 1) if current_idx < len(self.all_servers) - 1 else 0
        self._select_server(self.all_servers[new_idx].id)
    
    def _connect_selected(self, event) -> None:
        """Connect to the selected server."""
        if self.selected_server_id and self.on_connect_files:
            for server in self.all_servers:
                if server.id == self.selected_server_id:
                    self.on_connect_files(server)
                    break