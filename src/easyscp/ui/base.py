"""Base UI components."""

import customtkinter as ctk
from typing import Optional, Callable
from abc import ABC, abstractmethod
from .design_system import design, components

class BaseTab(ABC):
    """Base class for tab components."""
    
    def __init__(self, parent: ctk.CTkFrame):
        self.parent = parent
        self.setup_ui()
        
    @abstractmethod
    def setup_ui(self) -> None:
        """Set up the tab UI."""
        pass
        
    @abstractmethod
    def on_connect(self) -> None:
        """Called when connection is established."""
        pass
        
    @abstractmethod
    def on_disconnect(self) -> None:
        """Called when connection is closed."""
        pass

class BaseDialog(ABC):
    """Base class for dialog windows."""
    
    def __init__(self, parent: ctk.CTk, title: str):
        self.result = None
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(fg_color=design.get_color("bg_primary"))
        
        self.setup_ui()
        self.center_window()
        
    @abstractmethod
    def setup_ui(self) -> None:
        """Set up the dialog UI."""
        pass
        
    def center_window(self) -> None:
        """Center the dialog on parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'+{x}+{y}')
        
    def show_error(self, message: str) -> None:
        """Show error message."""
        error = ctk.CTkToplevel(self.dialog)
        error.title("Error")
        error.geometry("380x140")
        error.transient(self.dialog)
        error.grab_set()
        error.configure(fg_color=design.get_color("bg_primary"))
        
        # Main container
        container = components.create_frame(error)
        container.pack(fill="both", expand=True, padx=design.get_spacing("xxl"), pady=design.get_spacing("xxl"))
        
        # Error message
        message_label = components.create_label(
            container,
            text=message,
            wraplength=320
        )
        message_label.pack(pady=(0, design.get_spacing("xxl")))
        
        # OK button
        ok_btn = components.create_button(
            container,
            text="OK",
            command=error.destroy,
            width=80
        )
        ok_btn.pack()