"""Terminal Window for SSH connections."""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, font as tkfont
import threading
import queue
from typing import Optional
import time
import pyte

from ..storage import Server, ServerStorage, Snippet
from ..connections import SSHConnection, ConnectionManager
from ..utils.logger import logger
from ..utils.config import config
from .design_system import design, styles, components


class TerminalWindow:
    """Custom terminal window for SSH connections."""
    
    def __init__(self, parent: ctk.CTk, server: Server, storage: ServerStorage):
        self.parent = parent
        self.server = server
        self.storage = storage
        self.connection: Optional[SSHConnection] = None
        self.channel = None
        self.output_queue = queue.Queue()
        self.running = True
        
        # Terminal emulator
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.ByteStream(self.screen)
        
        # Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"Terminal - {server.name}")
        self.window.geometry("800x600")
        self.window.minsize(600, 400)
        
        # Connection manager
        self.connection_manager = ConnectionManager()
        
        # Log connection
        self.connection_log_id = self.storage.log_connection(server.id, "terminal")
        
        # Set up UI
        self.setup_ui()
        
        # Connect to server
        self.connect_to_server()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Schedule terminal size update
        self.window.after(500, self.update_terminal_size)
        
    def setup_ui(self) -> None:
        """Set up the terminal UI."""
        # Header with connection info
        header_frame = ctk.CTkFrame(self.window, height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Connection status
        status_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_container.pack(side="left", fill="y", padx=20)
        
        self.status_indicator = ctk.CTkLabel(
            status_container,
            text="●",
            font=("Arial", 14),
            text_color="#f59e0b"
        )
        self.status_indicator.pack(side="left", padx=(0, 8))
        
        self.status_label = ctk.CTkLabel(
            status_container,
            text=f"Connecting to {self.server.name}...",
            font=("Arial", 12)
        )
        self.status_label.pack(side="left")
        
        # Terminal controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", fill="y", padx=20)
        
        # Clear button
        self.clear_btn = ctk.CTkButton(
            controls_frame,
            text="Clear",
            width=70,
            height=30,
            command=self.clear_terminal,
            state="disabled",
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35")
        )
        self.clear_btn.pack(side="left", padx=5)
        
        # Copy button
        self.copy_btn = ctk.CTkButton(
            controls_frame,
            text="Copy",
            width=70,
            height=30,
            command=self.copy_selection,
            state="disabled",
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35")
        )
        self.copy_btn.pack(side="left", padx=5)
        
        # Main content area with paned window
        main_paned = tk.PanedWindow(
            self.window,
            orient=tk.HORIZONTAL,
            sashwidth=4,
            bg=design.get_color("border_primary")[0],
            borderwidth=0
        )
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Terminal frame
        terminal_frame = ctk.CTkFrame(main_paned)
        
        # Terminal text widget
        self.terminal = tk.Text(
            terminal_frame,
            bg="black",
            fg="white",
            insertbackground="white",
            selectbackground="#4a4a4a",
            font=(
                config.get("terminal.font_family", "Consolas"),
                config.get("terminal.font_size", 11)
            ),
            wrap=tk.NONE,
            cursor="xterm"
        )
        self.terminal.pack(side="left", fill="both", expand=True)
        
        # Terminal scrollbar
        v_scrollbar = ttk.Scrollbar(terminal_frame, orient="vertical", command=self.terminal.yview)
        v_scrollbar.pack(side="right", fill="y")
        
        # Add terminal frame to paned window
        main_paned.add(terminal_frame, width=600, minsize=400)
        
        # Snippets panel
        snippets_frame = components.create_frame(main_paned, style="bordered")
        
        # Snippets header
        snippets_header = components.create_frame(snippets_frame)
        snippets_header.pack(fill="x", padx=design.get_spacing("md"), pady=design.get_spacing("md"))
        
        snippets_label = components.create_label(
            snippets_header,
            text="Snippets",
            style="heading",
            font=design.get_font("heading_small")
        )
        snippets_label.pack(side="left")
        
        # Toggle button to show/hide snippets
        self.toggle_snippets_btn = components.create_button(
            snippets_header,
            text="×",
            width=25,
            command=self.toggle_snippets_panel
        )
        self.toggle_snippets_btn.pack(side="right")
        
        # Snippets list
        self.snippets_container = components.create_scrollable_frame(snippets_frame)
        self.snippets_container.pack(fill="both", expand=True, padx=design.get_spacing("md"), pady=(0, design.get_spacing("md")))
        
        # Load snippets
        self.load_snippets()
        
        # Add snippets frame to paned window
        main_paned.add(snippets_frame, width=200, minsize=150)
        
        # Store reference to paned window
        self.main_paned = main_paned
        
        # Horizontal scrollbar for terminal
        h_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.terminal.xview)
        h_scrollbar.pack(fill="x", padx=10)
        self.terminal.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Configure tags for colors
        # ANSI color mapping
        self.color_map = {
            'black': '#000000',
            'red': '#dc2626',
            'green': '#10b981',
            'brown': '#f59e0b',
            'blue': '#3b82f6',
            'magenta': '#a855f7',
            'cyan': '#06b6d4',
            'white': '#e5e5e5',
            'default': '#ffffff',
            # Bright colors
            'brightblack': '#525252',
            'brightred': '#ef4444',
            'brightgreen': '#22c55e',
            'brightyellow': '#fbbf24',
            'brightblue': '#60a5fa',
            'brightmagenta': '#c084fc',
            'brightcyan': '#22d3ee',
            'brightwhite': '#ffffff'
        }
        
        # Configure color tags
        for name, color in self.color_map.items():
            self.terminal.tag_config(f"fg_{name}", foreground=color)
            self.terminal.tag_config(f"bg_{name}", background=color)
        
        # Configure style tags
        self.terminal.tag_config("bold", font=(config.get("terminal.font_family", "Consolas"), config.get("terminal.font_size", 11), "bold"))
        self.terminal.tag_config("italics", font=(config.get("terminal.font_family", "Consolas"), config.get("terminal.font_size", 11), "italic"))
        self.terminal.tag_config("underscore", underline=True)
        self.terminal.tag_config("reverse", foreground="black", background="white")
        
        # Bind events
        self.terminal.bind("<Key>", self.on_key_press)
        self.terminal.bind("<Control-c>", self.send_interrupt)
        self.terminal.bind("<Control-v>", self.paste_text)
        
    def connect_to_server(self) -> None:
        """Connect to the SSH server."""
        def connect():
            try:
                # Create connection
                self.connection = self.connection_manager.create_connection(self.server.id)
                
                # Connect with authentication parameters
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
                    # Open shell channel
                    self.channel = self.connection.client.invoke_shell()
                    self.channel.settimeout(0.1)
                    
                    # Update UI in main thread
                    self.window.after(0, self.on_connection_success)
                    
                    # Start output reader thread
                    threading.Thread(target=self.read_output, daemon=True).start()
                    
                    # Start output processor
                    self.window.after(100, self.process_output)
                else:
                    self.window.after(0, self.on_connection_failed)
                    
            except Exception as e:
                logger.error(f"Connection error: {e}")
                self.window.after(0, self.on_connection_failed)
        
        # Connect in thread
        threading.Thread(target=connect, daemon=True).start()
        
    def on_connection_success(self) -> None:
        """Handle successful connection."""
        self.status_indicator.configure(text_color="#10b981")
        self.status_label.configure(text=f"Connected to {self.server.name}")
        
        # Enable controls
        self.clear_btn.configure(state="normal")
        self.copy_btn.configure(state="normal")
        
        # Focus terminal
        self.terminal.focus_set()
        
    def on_connection_failed(self) -> None:
        """Handle failed connection."""
        self.status_indicator.configure(text_color="#dc2626")
        self.status_label.configure(text="Connection failed")
        
        self.terminal.insert("1.0", f"Failed to connect to {self.server.name}\n", "fg_red")
        self.terminal.insert("end", "Please check your connection settings.\n", "fg_red")
        
        # Close window after delay
        self.window.after(3000, self.window.destroy)
        
    def read_output(self) -> None:
        """Read output from SSH channel."""
        while self.running and self.channel:
            try:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096)
                    self.output_queue.put(data)
                time.sleep(0.01)
            except:
                time.sleep(0.1)
                
    def process_output(self) -> None:
        """Process output from queue."""
        try:
            while True:
                data = self.output_queue.get_nowait()
                # Feed data to terminal emulator
                self.stream.feed(data)
                # Update display
                self.update_display()
        except queue.Empty:
            pass
            
        if self.running:
            self.window.after(50, self.process_output)
            
    def update_display(self) -> None:
        """Update terminal display based on pyte screen."""
        # Clear terminal
        self.terminal.delete("1.0", tk.END)
        
        # Get screen content
        for y in range(self.screen.lines):
            line = self.screen.buffer[y]
            col = 0
            
            for x in range(self.screen.columns):
                char = line[x]
                
                # Build tag list for this character
                tags = []
                
                # Foreground color
                if char.fg != 'default':
                    tags.append(f"fg_{char.fg}")
                
                # Background color
                if char.bg != 'default':
                    tags.append(f"bg_{char.bg}")
                
                # Styles
                if char.bold:
                    tags.append("bold")
                if char.italics:
                    tags.append("italics")
                if char.underscore:
                    tags.append("underscore")
                if char.reverse:
                    tags.append("reverse")
                
                # Insert character
                self.terminal.insert(f"{y+1}.{col}", char.data, tuple(tags))
                col += 1
            
            # Add newline if not last line
            if y < self.screen.lines - 1:
                self.terminal.insert(f"{y+1}.end", "\n")
        
        # Set cursor position
        cursor_y = self.screen.cursor.y + 1
        cursor_x = self.screen.cursor.x
        self.terminal.mark_set(tk.INSERT, f"{cursor_y}.{cursor_x}")
        
        # Make cursor visible
        self.terminal.see(tk.INSERT)
            
    def on_key_press(self, event) -> str:
        """Handle key press in terminal."""
        if not self.channel or not self.running:
            return "break"
        
        # Special keys
        key_map = {
            'Up': '\x1b[A',
            'Down': '\x1b[B',
            'Right': '\x1b[C',
            'Left': '\x1b[D',
            'Home': '\x1b[H',
            'End': '\x1b[F',
            'Prior': '\x1b[5~',  # Page Up
            'Next': '\x1b[6~',   # Page Down
            'Delete': '\x1b[3~',
            'Insert': '\x1b[2~',
            'F1': '\x1bOP',
            'F2': '\x1bOQ',
            'F3': '\x1bOR',
            'F4': '\x1bOS',
            'F5': '\x1b[15~',
            'F6': '\x1b[17~',
            'F7': '\x1b[18~',
            'F8': '\x1b[19~',
            'F9': '\x1b[20~',
            'F10': '\x1b[21~',
            'F11': '\x1b[23~',
            'F12': '\x1b[24~',
        }
        
        if event.keysym in key_map:
            self.channel.send(key_map[event.keysym])
            return "break"
        
        # Enter key
        if event.keysym == 'Return':
            self.channel.send('\r')
            return "break"
        
        # Backspace
        if event.keysym == 'BackSpace':
            self.channel.send('\x7f')
            return "break"
        
        # Tab
        if event.keysym == 'Tab':
            self.channel.send('\t')
            return "break"
        
        # Escape
        if event.keysym == 'Escape':
            self.channel.send('\x1b')
            return "break"
        
        # Control keys
        if event.state & 0x4:  # Control key pressed
            if event.keysym.lower() in 'abcdefghijklmnopqrstuvwxyz':
                # Send Ctrl+letter
                self.channel.send(chr(ord(event.keysym.lower()) - ord('a') + 1))
                return "break"
        
        # Regular characters
        if event.char and ord(event.char) >= 32:
            self.channel.send(event.char)
            return "break"
        
        return "break"
                
    def send_interrupt(self, event=None) -> str:
        """Send Ctrl+C to the terminal."""
        if self.channel:
            try:
                self.channel.send('\x03')  # Ctrl+C
            except:
                pass
        return "break"
    
    def paste_text(self, event=None) -> str:
        """Paste text from clipboard."""
        try:
            text = self.window.clipboard_get()
            if text and self.channel:
                # Send the text to the server
                self.channel.send(text)
        except:
            pass
        return "break"
        
    def clear_terminal(self) -> None:
        """Clear terminal output."""
        # Clear the screen in pyte
        self.screen.reset()
        # Update display
        self.update_display()
        # Send clear command to server as well
        if self.channel:
            try:
                self.channel.send('clear\r')
            except:
                pass
        
    def copy_selection(self) -> None:
        """Copy selected text to clipboard."""
        try:
            selection = self.terminal.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.window.clipboard_clear()
            self.window.clipboard_append(selection)
        except:
            pass
    
    def load_snippets(self) -> None:
        """Load and display snippets for the current server."""
        # Clear existing widgets
        for widget in self.snippets_container.winfo_children():
            widget.destroy()
        
        # Get snippets from storage
        snippets = self.storage.get_snippets(self.server.id)
        
        if not snippets:
            # Show empty state
            empty_label = components.create_label(
                self.snippets_container,
                text="No snippets",
                style="secondary",
                font=design.get_font("caption")
            )
            empty_label.pack(pady=design.get_spacing("lg"))
            return
        
        # Display snippets
        for snippet in snippets:
            self._create_snippet_button(snippet)
    
    def _create_snippet_button(self, snippet: Snippet) -> None:
        """Create a clickable button for a snippet."""
        # Container
        container = components.create_frame(self.snippets_container)
        container.pack(fill="x", pady=(0, design.get_spacing("sm")))
        
        # Button
        btn = components.create_button(
            container,
            text=snippet.name,
            command=lambda: self.execute_snippet(snippet),
            width=150
        )
        btn.pack(fill="x")
        
        # Show command preview on hover
        if snippet.description:
            tooltip_text = snippet.description
        else:
            # Show first line of command
            command_preview = snippet.command.split('\n')[0]
            if len(command_preview) > 30:
                command_preview = command_preview[:30] + "..."
            tooltip_text = command_preview
        
        # Create simple tooltip label
        tooltip = components.create_label(
            container,
            text=tooltip_text,
            style="secondary",
            font=design.get_font("caption"),
            wraplength=150
        )
        tooltip.pack(fill="x", padx=design.get_spacing("sm"))
    
    def execute_snippet(self, snippet: Snippet) -> None:
        """Execute a snippet in the terminal."""
        if not self.channel:
            logger.warning("No active channel to execute snippet")
            return
        
        try:
            if snippet.is_script:
                # For multi-line scripts, send each line with a newline
                lines = snippet.command.split('\n')
                for line in lines:
                    self.channel.send(line + '\r')
                    # Small delay between lines to avoid overwhelming the terminal
                    time.sleep(0.05)
            else:
                # For single commands, just send it
                self.channel.send(snippet.command + '\r')
            
            logger.info(f"Executed snippet: {snippet.name}")
        except Exception as e:
            logger.error(f"Failed to execute snippet: {e}")
    
    def toggle_snippets_panel(self) -> None:
        """Toggle visibility of the snippets panel."""
        # Get current sash position
        sash_pos = self.main_paned.sash_coord(0)[0]
        window_width = self.window.winfo_width()
        
        # If panel is mostly hidden, show it; otherwise hide it
        if sash_pos > window_width - 50:
            # Show panel
            self.main_paned.sash_place(0, window_width - 200, 0)
        else:
            # Hide panel
            self.main_paned.sash_place(0, window_width - 5, 0)
            
    def on_close(self) -> None:
        """Handle window close."""
        self.running = False
        
        # Log disconnection
        if self.connection_log_id:
            self.storage.log_disconnection(self.connection_log_id)
            
        # Close connection
        if self.channel:
            try:
                self.channel.close()
            except:
                pass
                
        if self.connection:
            self.connection_manager.close_connection(self.server.id)
            
        # Destroy window
        self.window.destroy()
    
    def update_terminal_size(self) -> None:
        """Update terminal size based on window size."""
        # Calculate terminal size in characters
        self.terminal.update_idletasks()
        
        # Get font metrics
        font = tkfont.Font(font=self.terminal['font'])
        char_width = font.measure('M')
        char_height = font.metrics('linespace')
        
        # Get terminal widget size
        width_pixels = self.terminal.winfo_width()
        height_pixels = self.terminal.winfo_height()
        
        # Calculate characters that fit
        if width_pixels > 1 and height_pixels > 1:
            cols = max(80, width_pixels // char_width)
            rows = max(24, height_pixels // char_height)
            
            # Resize pyte screen
            self.screen.resize(rows, cols)
            
            # Update terminal size on server
            if self.channel:
                try:
                    self.channel.resize_pty(width=cols, height=rows)
                except:
                    pass
        
        # Schedule next update
        if self.running:
            self.window.after(500, self.update_terminal_size)