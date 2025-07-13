"""Settings dialog for EasySCP."""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Dict, Any, Optional

from .base import BaseDialog
from ..utils.config import config
from ..utils.logger import logger


class SettingsDialog(BaseDialog):
    """Dialog for managing application settings."""
    
    def __init__(self, parent: ctk.CTk):
        self.original_theme = config.get("appearance.theme", "light")
        self.original_color = config.get("appearance.color_scheme", "blue")
        self.temp_settings: Dict[str, Any] = {}
        super().__init__(parent, "Settings")
        
    def setup_ui(self) -> None:
        """Set up the settings dialog UI."""
        self.dialog.geometry("600x500")
        
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, fg_color=("white", "white"))
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(
            main_frame, 
            fg_color=("white", "white"), 
            segmented_button_fg_color=("white", "white"), 
            segmented_button_selected_color=("gray95", "gray95"), 
            segmented_button_selected_hover_color=("gray90", "gray90"), 
            segmented_button_unselected_color=("white", "white"), 
            segmented_button_unselected_hover_color=("gray98", "gray98"), 
            text_color=("black", "black"),
            border_width=1,

        )
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.appearance_tab = self.notebook.add("Appearance")
        self.connection_tab = self.notebook.add("Connection")
        self.file_manager_tab = self.notebook.add("File Manager")
        self.terminal_tab = self.notebook.add("Terminal")
        
        # Setup each tab
        self._setup_appearance_tab()
        self._setup_connection_tab()
        self._setup_file_manager_tab()
        self._setup_terminal_tab()
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Apply",
            command=self._apply_settings,
            width=100,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="OK",
            command=self._save_and_close,
            width=100,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=100,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        ).pack(side="right", padx=5)
        
    def _setup_appearance_tab(self) -> None:
        """Set up the appearance settings tab."""
        frame = ctk.CTkFrame(self.appearance_tab, fg_color=("white", "white"))
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Theme selection
        ctk.CTkLabel(frame, text="Theme:", anchor="w", text_color=("black", "black")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        # Convert saved theme value to display value
        saved_theme = config.get("appearance.theme", "light")
        display_theme = "dark (Beta)" if saved_theme == "dark" else saved_theme
        self.theme_var = ctk.StringVar(value=display_theme)
        
        # Create wrapper frame for border effect
        theme_wrapper = ctk.CTkFrame(frame, fg_color=("black", "black"), corner_radius=0)
        theme_wrapper.grid(row=0, column=1, padx=5, pady=5)
        
        theme_menu = ctk.CTkOptionMenu(
            theme_wrapper,
            values=["light", "dark (Beta)", "system"],
            variable=self.theme_var,
            command=self._preview_theme,
            width=196,
            height=26,
            corner_radius=0,
            fg_color=("white", "white"),
            button_color=("white", "white"),
            button_hover_color=("white", "white"),
            dropdown_fg_color=("white", "white"),
            dropdown_hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            dropdown_text_color=("black", "black")
        )
        theme_menu.pack(padx=1, pady=1)
        
        # Note about dark mode beta
        note_label = ctk.CTkLabel(
            frame, 
            text="Note: Dark mode is currently in beta and may have visual inconsistencies",
            font=("Arial", 10),
            text_color=("gray30", "gray30"),
            anchor="w"
        )
        note_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 10))
        
        # Create a frame for restart warning that will be shown when theme changes
        self.restart_warning_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.restart_warning_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(10, 5))
        
        # Color scheme selection
        ctk.CTkLabel(frame, text="Color Scheme:", anchor="w", text_color=("black", "black")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.color_var = ctk.StringVar(value=config.get("appearance.color_scheme", "blue"))
        
        # Create wrapper frame for border effect
        color_wrapper = ctk.CTkFrame(frame, fg_color=("black", "black"), corner_radius=0)
        color_wrapper.grid(row=2, column=1, padx=5, pady=5)
        
        color_menu = ctk.CTkOptionMenu(
            color_wrapper,
            values=["blue", "green", "dark-blue"],
            variable=self.color_var,
            command=self._preview_color,
            width=196,
            height=26,
            corner_radius=0,
            fg_color=("white", "white"),
            button_color=("white", "white"),
            button_hover_color=("white", "white"),
            dropdown_fg_color=("white", "white"),
            dropdown_hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            dropdown_text_color=("black", "black")
        )
        color_menu.pack(padx=1, pady=1)
        
    def _setup_connection_tab(self) -> None:
        """Set up the connection settings tab."""
        frame = ctk.CTkFrame(self.connection_tab, fg_color=("white", "white"))
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Default port
        ctk.CTkLabel(frame, text="Default SSH Port:", anchor="w", text_color=("black", "black")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.port_var = ctk.StringVar(value=str(config.get("connection.default_port", 22)))
        port_entry = ctk.CTkEntry(frame, textvariable=self.port_var, width=200, corner_radius=0, border_width=1, border_color=("black", "black"), fg_color=("white", "white"), text_color=("black", "black"))
        port_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Connection timeout
        ctk.CTkLabel(frame, text="Timeout (seconds):", anchor="w", text_color=("black", "black")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.timeout_var = ctk.StringVar(value=str(config.get("connection.timeout", 30)))
        timeout_entry = ctk.CTkEntry(frame, textvariable=self.timeout_var, width=200, corner_radius=0, border_width=1, border_color=("black", "black"), fg_color=("white", "white"), text_color=("black", "black"))
        timeout_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Keepalive interval
        ctk.CTkLabel(frame, text="Keepalive Interval (seconds):", anchor="w", text_color=("black", "black")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.keepalive_var = ctk.StringVar(value=str(config.get("connection.keepalive_interval", 60)))
        keepalive_entry = ctk.CTkEntry(frame, textvariable=self.keepalive_var, width=200, corner_radius=0, border_width=1, border_color=("black", "black"), fg_color=("white", "white"), text_color=("black", "black"))
        keepalive_entry.grid(row=2, column=1, padx=5, pady=5)
        
    def _setup_file_manager_tab(self) -> None:
        """Set up the file manager settings tab."""
        frame = ctk.CTkFrame(self.file_manager_tab, fg_color=("white", "white"))
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show hidden files
        self.show_hidden_var = ctk.BooleanVar(value=config.get("file_manager.show_hidden_files", False))
        hidden_check = ctk.CTkCheckBox(
            frame,
            text="Show hidden files",
            variable=self.show_hidden_var,
            text_color=("black", "black"),
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            border_color=("black", "black"),
            checkmark_color=("black", "black")
        )
        hidden_check.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Default download path
        ctk.CTkLabel(frame, text="Default Download Path:", anchor="w", text_color=("black", "black")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        path_frame = ctk.CTkFrame(frame, fg_color="transparent")
        path_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.download_path_var = ctk.StringVar(
            value=config.get("file_manager.default_download_path", str(Path.home() / "Downloads"))
        )
        path_entry = ctk.CTkEntry(path_frame, textvariable=self.download_path_var, width=350, corner_radius=0, border_width=1, border_color=("black", "black"), fg_color=("white", "white"), text_color=("black", "black"))
        path_entry.pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            path_frame,
            text="Browse",
            command=self._browse_download_path,
            width=80,
            corner_radius=0,
            fg_color=("white", "white"),
            hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            border_width=1,
            border_color=("black", "black")
        ).pack(side="left")
        
    def _setup_terminal_tab(self) -> None:
        """Set up the terminal settings tab."""
        frame = ctk.CTkFrame(self.terminal_tab, fg_color=("white", "white"))
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Font family
        ctk.CTkLabel(frame, text="Font Family:", anchor="w", text_color=("black", "black")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.font_family_var = ctk.StringVar(value=config.get("terminal.font_family", "Consolas"))
        
        # Create wrapper frame for border effect
        font_wrapper = ctk.CTkFrame(frame, fg_color=("black", "black"), corner_radius=0)
        font_wrapper.grid(row=0, column=1, padx=5, pady=5)
        
        font_menu = ctk.CTkOptionMenu(
            font_wrapper,
            values=["Consolas", "Courier New", "Monaco", "Menlo", "Ubuntu Mono", "Source Code Pro"],
            variable=self.font_family_var,
            width=196,
            height=26,
            corner_radius=0,
            fg_color=("white", "white"),
            button_color=("white", "white"),
            button_hover_color=("white", "white"),
            dropdown_fg_color=("white", "white"),
            dropdown_hover_color=("gray95", "gray95"),
            text_color=("black", "black"),
            dropdown_text_color=("black", "black")
        )
        font_menu.pack(padx=1, pady=1)
        
        # Font size
        ctk.CTkLabel(frame, text="Font Size:", anchor="w", text_color=("black", "black")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.font_size_var = ctk.StringVar(value=str(config.get("terminal.font_size", 11)))
        size_entry = ctk.CTkEntry(frame, textvariable=self.font_size_var, width=200, corner_radius=0, border_width=1, border_color=("black", "black"), fg_color=("white", "white"), text_color=("black", "black"))
        size_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Buffer size
        ctk.CTkLabel(frame, text="Buffer Size (lines):", anchor="w", text_color=("black", "black")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.buffer_size_var = ctk.StringVar(value=str(config.get("terminal.buffer_size", 10000)))
        buffer_entry = ctk.CTkEntry(frame, textvariable=self.buffer_size_var, width=200, corner_radius=0, border_width=1, border_color=("black", "black"), fg_color=("white", "white"), text_color=("black", "black"))
        buffer_entry.grid(row=2, column=1, padx=5, pady=5)
        
    def _browse_download_path(self) -> None:
        """Browse for download directory."""
        current_path = self.download_path_var.get()
        if not Path(current_path).exists():
            current_path = str(Path.home())
            
        path = filedialog.askdirectory(
            title="Select Default Download Directory",
            initialdir=current_path
        )
        
        if path:
            self.download_path_var.set(path)
            
    def _preview_theme(self, theme: str) -> None:
        """Preview theme change."""
        # Handle "dark (Beta)" option
        actual_theme = "dark" if theme == "dark (Beta)" else theme
        # Don't apply theme immediately - just store it
        self.temp_settings["appearance.theme"] = actual_theme
        
        # Show restart warning if theme changed
        self._show_restart_warning()
        
    def _preview_color(self, color: str) -> None:
        """Preview color scheme change."""
        # Don't apply color scheme immediately - just store it
        self.temp_settings["appearance.color_scheme"] = color
        
        # Show restart warning
        self._show_restart_warning()
    
    def _show_restart_warning(self) -> None:
        """Show restart warning in the appearance tab."""
        # Clear any existing warning
        for widget in self.restart_warning_frame.winfo_children():
            widget.destroy()
        
        # Create warning message
        warning_label = ctk.CTkLabel(
            self.restart_warning_frame,
            text="⚠️ Theme changes require application restart",
            font=("Arial", 11, "bold"),
            text_color=("black", "black")
        )
        warning_label.pack(anchor="w")
        
    def _validate_settings(self) -> bool:
        """Validate all settings."""
        try:
            # Validate port
            port = int(self.port_var.get())
            if not 1 <= port <= 65535:
                raise ValueError("Port must be between 1 and 65535")
                
            # Validate timeout
            timeout = int(self.timeout_var.get())
            if timeout < 1:
                raise ValueError("Timeout must be at least 1 second")
                
            # Validate keepalive
            keepalive = int(self.keepalive_var.get())
            if keepalive < 0:
                raise ValueError("Keepalive interval must be 0 or greater")
                
            # Validate font size
            font_size = int(self.font_size_var.get())
            if not 6 <= font_size <= 72:
                raise ValueError("Font size must be between 6 and 72")
                
            # Validate buffer size
            buffer_size = int(self.buffer_size_var.get())
            if not 100 <= buffer_size <= 100000:
                raise ValueError("Buffer size must be between 100 and 100000")
                
            # Validate download path
            download_path = self.download_path_var.get()
            if not Path(download_path).exists():
                raise ValueError(f"Download path does not exist: {download_path}")
                
            return True
            
        except ValueError as e:
            self.show_error(str(e))
            return False
            
    def _collect_settings(self) -> Dict[str, Any]:
        """Collect all settings from the UI."""
        # Handle "dark (Beta)" option
        theme = self.theme_var.get()
        actual_theme = "dark" if theme == "dark (Beta)" else theme
        
        settings = {
            "appearance.theme": actual_theme,
            "appearance.color_scheme": self.color_var.get(),
            "connection.default_port": int(self.port_var.get()),
            "connection.timeout": int(self.timeout_var.get()),
            "connection.keepalive_interval": int(self.keepalive_var.get()),
            "file_manager.show_hidden_files": self.show_hidden_var.get(),
            "file_manager.default_download_path": self.download_path_var.get(),
            "terminal.font_family": self.font_family_var.get(),
            "terminal.font_size": int(self.font_size_var.get()),
            "terminal.buffer_size": int(self.buffer_size_var.get()),
        }
        return settings
        
    def _apply_settings(self) -> None:
        """Apply settings without closing dialog."""
        if not self._validate_settings():
            return
            
        settings = self._collect_settings()
        
        # Check if theme/color scheme changed
        theme_changed = settings["appearance.theme"] != self.original_theme
        color_changed = settings["appearance.color_scheme"] != self.original_color
        
        # Save all settings
        for key, value in settings.items():
            config.set(key, value)
            
        logger.info("Settings applied")
        
        # Show restart message if theme changed
        if theme_changed or color_changed:
            messagebox.showinfo(
                "Restart Required",
                "Theme changes will be applied after restarting the application."
            )
        
        # Update originals for cancel comparison
        self.original_theme = settings["appearance.theme"]
        self.original_color = settings["appearance.color_scheme"]
        
    def _save_and_close(self) -> None:
        """Save settings and close dialog."""
        if not self._validate_settings():
            return
            
        settings = self._collect_settings()
        
        # Check if theme/color scheme changed
        theme_changed = settings["appearance.theme"] != self.original_theme
        color_changed = settings["appearance.color_scheme"] != self.original_color
        
        # Save all settings
        for key, value in settings.items():
            config.set(key, value)
            
        logger.info("Settings saved")
        
        # Show restart message if theme changed
        if theme_changed or color_changed:
            messagebox.showinfo(
                "Restart Required",
                "Theme changes will be applied after restarting the application.\n\nPlease close and reopen EasySCP."
            )
        
        self.result = True
        self.dialog.destroy()
        
    def _cancel(self) -> None:
        """Cancel without saving changes."""
        # No need to restore appearance since we don't apply it immediately
        self.result = False
        self.dialog.destroy()