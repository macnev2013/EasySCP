"""Terminal tab component."""

import customtkinter as ctk
import threading
import queue
from typing import Optional

from .base import BaseTab
from ..connections import SSHConnection
from ..utils.logger import logger
from ..utils.config import config

class TerminalTab(BaseTab):
    """Terminal tab for command execution."""
    
    def __init__(self, parent: ctk.CTkFrame):
        self.connection: Optional[SSHConnection] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.command_history: list[str] = []
        self.history_index: int = -1
        super().__init__(parent)
        
    def setup_ui(self) -> None:
        """Set up the terminal UI."""
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Terminal output
        font_family = config.get("terminal.font_family", "Consolas")
        font_size = config.get("terminal.font_size", 11)
        
        self.output_text = ctk.CTkTextbox(
            main_frame,
            font=(font_family, font_size),
            wrap="none"
        )
        self.output_text.pack(fill="both", expand=True, padx=5, pady=(5, 0))
        
        # Command input
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        self.prompt_label = ctk.CTkLabel(
            input_frame,
            text="$ ",
            font=(font_family, font_size)
        )
        self.prompt_label.pack(side="left", padx=(5, 0))
        
        self.command_entry = ctk.CTkEntry(
            input_frame,
            font=(font_family, font_size)
        )
        self.command_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Bind events
        self.command_entry.bind("<Return>", self._execute_command)
        self.command_entry.bind("<Up>", self._history_up)
        self.command_entry.bind("<Down>", self._history_down)
        
        # Execute button
        ctk.CTkButton(
            input_frame,
            text="Execute",
            command=self._execute_command,
            width=80,
            height=28,
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35")
        ).pack(side="right", padx=5)
        
        # Show welcome message
        self._show_welcome()
        
        # Start output updater
        self._update_output()
        
    def _show_welcome(self) -> None:
        """Show welcome message when not connected."""
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "Terminal not connected.\n")
        self.output_text.insert("end", "Connect to a server to start using the terminal.\n")
        self.command_entry.configure(state="disabled")
        
    def set_connection(self, connection: SSHConnection) -> None:
        """Set the SSH connection."""
        self.connection = connection
        
    def on_connect(self) -> None:
        """Called when connection is established."""
        if self.connection:
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", "Terminal connected. Type commands below.\n\n")
            self.command_entry.configure(state="normal")
            self.command_entry.focus()
            
    def on_disconnect(self) -> None:
        """Called when connection is closed."""
        self.connection = None
        self._show_welcome()
        
    def _execute_command(self, event=None) -> None:
        """Execute the entered command."""
        if not self.connection or not self.connection.is_connected:
            return
            
        command = self.command_entry.get().strip()
        if not command:
            return
            
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Clear entry
        self.command_entry.delete(0, "end")
        
        # Display command
        self.output_queue.put(f"$ {command}\n")
        
        # Execute in thread
        def run_command():
            try:
                output, error = self.connection.execute_command(command)
                if output:
                    self.output_queue.put(output)
                if error:
                    self.output_queue.put(f"Error: {error}")
                if not output and not error:
                    self.output_queue.put("\n")
            except Exception as e:
                self.output_queue.put(f"Error executing command: {e}\n")
                
        threading.Thread(target=run_command, daemon=True).start()
        
    def _history_up(self, event) -> None:
        """Navigate up in command history."""
        if self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.command_history[self.history_index])
            
    def _history_down(self, event) -> None:
        """Navigate down in command history."""
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, "end")
            
    def _update_output(self) -> None:
        """Update terminal output from queue."""
        try:
            while True:
                text = self.output_queue.get_nowait()
                self.output_text.insert("end", text)
                self.output_text.see("end")
                
                # Limit buffer size
                buffer_size = config.get("terminal.buffer_size", 10000)
                content = self.output_text.get("1.0", "end")
                if len(content) > buffer_size:
                    # Remove old content
                    lines = content.split('\n')
                    remove_lines = len(lines) - (buffer_size // 100)
                    if remove_lines > 0:
                        self.output_text.delete("1.0", f"{remove_lines}.0")
                        
        except queue.Empty:
            pass
            
        # Schedule next update
        self.parent.after(50, self._update_output)