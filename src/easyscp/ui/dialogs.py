"""Dialog windows for EasySCP."""

import customtkinter as ctk
from typing import Optional
from tkinter import filedialog

from .base import BaseDialog
from .settings_dialog import SettingsDialog
from .design_system import design, styles, components
from ..storage import Server
from ..utils.helpers import validate_port

class ServerDialog(BaseDialog):
    """Dialog for adding/editing server configuration."""
    
    def __init__(self, parent: ctk.CTk, title: str = "Server Configuration", 
                 server: Optional[Server] = None):
        self.server = server
        super().__init__(parent, title)
        
    def setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.dialog.geometry("520x650")
        
        # Main frame with design system styling
        main_frame = components.create_frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=design.get_spacing("xxxl"), pady=design.get_spacing("xxxl"))
        
        # Title for context
        title_text = "Edit Server Configuration" if self.server else "Add New Server"
        title_label = components.create_label(
            main_frame,
            text=title_text,
            style="heading"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, design.get_spacing("xxl")), sticky="w")
        
        # Basic server fields
        basic_fields = [
            ("Server Name:", "name_entry", "My Server", False, False),
            ("Host/IP Address:", "host_entry", "192.168.1.100 or example.com", False, False),
            ("Port:", "port_entry", "22", False, False),
            ("Username:", "username_entry", "root", False, False),
        ]
        
        current_row = 1
        for label_text, attr_name, placeholder, is_password, is_optional in basic_fields:
            # Label with design system styling
            label = components.create_label(
                main_frame,
                text=label_text,
                anchor="w"
            )
            label.grid(row=current_row, column=0, sticky="w", padx=design.get_spacing("sm"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
            
            # Entry with design system styling
            entry = components.create_entry(
                main_frame,
                width=320,
                placeholder_text=placeholder,
                show="*" if is_password else ""
            )
            entry.grid(row=current_row, column=1, padx=design.get_spacing("lg"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
            setattr(self, attr_name, entry)
            
            # Add required indicator
            if not is_optional:
                required = components.create_label(
                    main_frame,
                    text="*",
                    style="secondary"
                )
                required.grid(row=current_row, column=2, sticky="w", padx=0)
            
            current_row += 1
        
        # Authentication section separator
        sep_label = components.create_label(
            main_frame,
            text="Authentication Method",
            style="heading",
            font=design.get_font("heading_small")
        )
        sep_label.grid(row=current_row, column=0, columnspan=3, pady=(design.get_spacing("xxl"), design.get_spacing("lg")), sticky="w")
        current_row += 1
        
        # Authentication method selection
        auth_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        auth_frame.grid(row=current_row, column=0, columnspan=3, sticky="w", padx=design.get_spacing("sm"))
        current_row += 1
        
        # Initialize auth method variable
        self.auth_method = ctk.StringVar(value="password")
        
        # Password authentication radio button
        self.password_radio = ctk.CTkRadioButton(
            auth_frame,
            text="Password Authentication",
            variable=self.auth_method,
            value="password",
            command=self._on_auth_method_changed,
            fg_color=design.get_color("text_primary"),
            hover_color=design.get_color("text_secondary"),
            text_color=design.get_color("text_primary"),
            font=design.get_font("body_medium")
        )
        self.password_radio.pack(anchor="w", pady=(0, design.get_spacing("sm")))
        
        # Key authentication radio button
        self.key_radio = ctk.CTkRadioButton(
            auth_frame,
            text="Private Key Authentication (PEM/PPK)",
            variable=self.auth_method,
            value="key",
            command=self._on_auth_method_changed,
            fg_color=design.get_color("text_primary"),
            hover_color=design.get_color("text_secondary"),
            text_color=design.get_color("text_primary"),
            font=design.get_font("body_medium")
        )
        self.key_radio.pack(anchor="w")
        
        # Password field
        self.password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.password_frame.grid(row=current_row, column=0, columnspan=3, sticky="ew", pady=(design.get_spacing("lg"), 0))
        
        password_label = components.create_label(
            self.password_frame,
            text="Password:",
            anchor="w"
        )
        password_label.grid(row=0, column=0, sticky="w", padx=design.get_spacing("sm"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
        
        self.password_entry = components.create_entry(
            self.password_frame,
            width=320,
            placeholder_text="Enter password",
            show="*"
        )
        self.password_entry.grid(row=0, column=1, padx=design.get_spacing("lg"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
        
        current_row += 1
        
        # Key authentication fields (initially hidden)
        self.key_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.key_frame.grid(row=current_row, column=0, columnspan=3, sticky="ew", pady=(design.get_spacing("lg"), 0))
        self.key_frame.grid_remove()  # Initially hidden
        
        # Private key file selection
        key_label = components.create_label(
            self.key_frame,
            text="Private Key File:",
            anchor="w"
        )
        key_label.grid(row=0, column=0, sticky="w", padx=design.get_spacing("sm"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
        
        key_entry_frame = ctk.CTkFrame(self.key_frame, fg_color="transparent")
        key_entry_frame.grid(row=0, column=1, sticky="ew", padx=design.get_spacing("lg"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
        
        self.key_path_entry = components.create_entry(
            key_entry_frame,
            width=250,
            placeholder_text="Select private key file..."
        )
        self.key_path_entry.pack(side="left", padx=(0, design.get_spacing("sm")))
        
        browse_btn = components.create_button(
            key_entry_frame,
            text="Browse",
            command=self._browse_key_file,
            width=70
        )
        browse_btn.pack(side="left")
        
        # Key passphrase field
        passphrase_label = components.create_label(
            self.key_frame,
            text="Key Passphrase:",
            anchor="w"
        )
        passphrase_label.grid(row=1, column=0, sticky="w", padx=design.get_spacing("sm"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
        
        self.passphrase_entry = components.create_entry(
            self.key_frame,
            width=320,
            placeholder_text="Leave empty if key has no passphrase",
            show="*"
        )
        self.passphrase_entry.grid(row=1, column=1, padx=design.get_spacing("lg"), pady=(design.get_spacing("lg"), design.get_spacing("xs")))
        
        passphrase_optional = components.create_label(
            self.key_frame,
            text="(optional)",
            style="secondary",
            font=design.get_font("caption")
        )
        passphrase_optional.grid(row=1, column=2, sticky="w", padx=0)
        
        current_row += 1
        
        # Note about required fields
        note_label = components.create_label(
            main_frame,
            text="* Required fields",
            style="secondary",
            font=design.get_font("caption")
        )
        note_label.grid(row=current_row, column=0, columnspan=3, pady=(design.get_spacing("xl"), 0), sticky="w")
        current_row += 1
        
        # Load existing server data if editing
        if self.server:
            self.name_entry.insert(0, self.server.name)
            self.host_entry.insert(0, self.server.host)
            self.port_entry.insert(0, str(self.server.port))
            self.username_entry.insert(0, self.server.username)
            
            if self.server.use_key_auth:
                self.auth_method.set("key")
                if self.server.private_key_path:
                    self.key_path_entry.insert(0, self.server.private_key_path)
                if self.server.private_key_passphrase:
                    self.passphrase_entry.insert(0, self.server.private_key_passphrase)
                self._on_auth_method_changed()
            else:
                if self.server.password:
                    self.password_entry.insert(0, self.server.password)
        else:
            # Set default port for new servers
            self.port_entry.insert(0, "22")
                
        # Buttons with design system styling
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=current_row, column=0, columnspan=3, pady=(design.get_spacing("xxxl"), 0))
        
        # Save button
        save_btn = components.create_button(
            button_frame,
            text="Save",
            command=self._save,
            width=110
        )
        save_btn.pack(side="left", padx=(0, design.get_spacing("md")))
        
        # Cancel button
        cancel_btn = components.create_button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=110,
            style="secondary"
        )
        cancel_btn.pack(side="left")
        
        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self._save())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        # Focus on first field
        self.name_entry.focus()
    
    def _on_auth_method_changed(self):
        """Handle authentication method change."""
        if self.auth_method.get() == "password":
            self.password_frame.grid()
            self.key_frame.grid_remove()
        else:
            self.password_frame.grid_remove()
            self.key_frame.grid()
    
    def _browse_key_file(self):
        """Browse for private key file."""
        filename = filedialog.askopenfilename(
            title="Select Private Key File",
            filetypes=[
                ("All Key Files", "*.pem *.ppk *.key *.rsa *.dsa *.ecdsa *.ed25519 *_rsa *_dsa *_ecdsa *_ed25519"),
                ("PEM Files", "*.pem"),
                ("PPK Files", "*.ppk"),
                ("Key Files", "*.key"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.key_path_entry.delete(0, "end")
            self.key_path_entry.insert(0, filename)
    
        
    def _save(self) -> None:
        """Save server configuration."""
        # Get values
        name = self.name_entry.get().strip()
        host = self.host_entry.get().strip()
        port = validate_port(self.port_entry.get())
        username = self.username_entry.get().strip()
        
        # Get authentication details
        use_key_auth = self.auth_method.get() == "key"
        password = None
        private_key_path = None
        private_key_passphrase = None
        
        if use_key_auth:
            private_key_path = self.key_path_entry.get().strip()
            private_key_passphrase = self.passphrase_entry.get()
            if not private_key_passphrase:
                private_key_passphrase = None
        else:
            password = self.password_entry.get()
            if not password:
                password = None
        
        # Validate required fields
        if not all([name, host, username]):
            self.show_error("Please fill in all required fields:\n- Server Name\n- Host/IP\n- Username")
            return
        
        # Validate authentication
        if use_key_auth and not private_key_path:
            self.show_error("Please select a private key file for key authentication.")
            return
        elif not use_key_auth and not password:
            self.show_error("Please enter a password for password authentication.")
            return
            
        # Create result
        self.result = Server(
            id=self.server.id if self.server else 0,
            name=name,
            host=host,
            port=port,
            username=username,
            password=password,
            use_key_auth=use_key_auth,
            private_key_path=private_key_path,
            private_key_passphrase=private_key_passphrase
        )
        
        self.dialog.destroy()

class ConfirmDialog(BaseDialog):
    """Confirmation dialog."""
    
    def __init__(self, parent: ctk.CTk, title: str, message: str):
        self.message = message
        super().__init__(parent, title)
        
    def setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.dialog.geometry("450x220")
        
        # Main frame
        main_frame = components.create_frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=design.get_spacing("xxl"), pady=design.get_spacing("xxl"))
        
        # Warning icon
        icon_label = components.create_label(
            main_frame,
            text="⚠",
            font=("Arial", 32),
            text_color=design.get_color("text_primary")
        )
        icon_label.pack(pady=(design.get_spacing("lg"), design.get_spacing("xl")))
        
        # Message with design system typography
        message_label = components.create_label(
            main_frame,
            text=self.message,
            font=design.get_font("body_large"),
            wraplength=400
        )
        message_label.pack()
        
        # Buttons with design system styling
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(design.get_spacing("xxl"), 0))
        
        # Yes button - primary action
        yes_btn = components.create_button(
            button_frame,
            text="Yes, Delete",
            command=self._confirm,
            width=110
        )
        yes_btn.pack(side="left", padx=(0, design.get_spacing("md")))
        
        # Cancel button
        cancel_btn = components.create_button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=110,
            style="secondary"
        )
        cancel_btn.pack(side="left")
        
        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self._confirm())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
    def _confirm(self) -> None:
        """Confirm action."""
        self.result = True
        self.dialog.destroy()
        
    def _cancel(self) -> None:
        """Cancel action."""
        self.result = False
        self.dialog.destroy()

class InputDialog(BaseDialog):
    """Input dialog that matches the design system."""
    
    def __init__(self, parent: ctk.CTk, title: str, prompt: str, 
                 placeholder: str = "", initial_value: str = ""):
        self.prompt = prompt
        self.placeholder = placeholder
        self.initial_value = initial_value
        self.input_value = None
        super().__init__(parent, title)
        
    def setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.dialog.geometry("420x200")
        
        # Main frame
        main_frame = components.create_frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=design.get_spacing("xxl"), pady=design.get_spacing("xxl"))
        
        # Prompt label
        prompt_label = components.create_label(
            main_frame,
            text=self.prompt,
            font=design.get_font("body_large")
        )
        prompt_label.pack(pady=(design.get_spacing("md"), design.get_spacing("lg")))
        
        # Input entry
        self.entry = components.create_entry(
            main_frame,
            width=350,
            placeholder_text=self.placeholder
        )
        self.entry.pack(pady=(0, design.get_spacing("xxl")))
        
        # Set initial value if provided
        if self.initial_value:
            self.entry.insert(0, self.initial_value)
            self.entry.select_range(0, len(self.initial_value))
        
        # Buttons with design system styling
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        
        # OK button - primary action
        ok_btn = components.create_button(
            button_frame,
            text="OK",
            command=self._ok,
            width=100
        )
        ok_btn.pack(side="left", padx=(0, design.get_spacing("md")))
        
        # Cancel button
        cancel_btn = components.create_button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=100,
            style="secondary"
        )
        cancel_btn.pack(side="left")
        
        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self._ok())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
        # Focus on entry
        self.entry.focus()
        
    def _ok(self) -> None:
        """Handle OK button."""
        self.input_value = self.entry.get()
        self.result = True
        self.dialog.destroy()
        
    def _cancel(self) -> None:
        """Handle Cancel button."""
        self.result = False
        self.dialog.destroy()
        
    def get_input(self) -> Optional[str]:
        """Show dialog and return input value."""
        self.dialog.wait_window()
        return self.input_value if self.result else None