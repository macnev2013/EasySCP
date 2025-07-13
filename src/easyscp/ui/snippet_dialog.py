"""Snippet management dialog for EasySCP."""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List

from .base import BaseDialog
from .design_system import design, styles, components
from ..storage import ServerStorage, Snippet
from ..utils.logger import logger


class SnippetEditDialog(BaseDialog):
    """Dialog for adding/editing a snippet."""
    
    def __init__(self, parent: ctk.CTk, server_id: int, snippet: Optional[Snippet] = None):
        self.server_id = server_id
        self.snippet = snippet
        self.is_edit = snippet is not None
        title = "Edit Snippet" if self.is_edit else "Add Snippet"
        super().__init__(parent, title)
    
    def setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.dialog.geometry("600x500")
        
        # Main frame
        main_frame = components.create_frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=design.get_spacing("xxl"), pady=design.get_spacing("xxl"))
        
        # Name field
        name_label = components.create_label(
            main_frame,
            text="Snippet Name:",
            font=design.get_font("body_medium")
        )
        name_label.pack(anchor="w", pady=(0, design.get_spacing("sm")))
        
        self.name_entry = components.create_entry(
            main_frame,
            placeholder_text="e.g., Check disk space"
        )
        self.name_entry.pack(fill="x", pady=(0, design.get_spacing("lg")))
        
        # Description field
        desc_label = components.create_label(
            main_frame,
            text="Description (optional):",
            font=design.get_font("body_medium")
        )
        desc_label.pack(anchor="w", pady=(0, design.get_spacing("sm")))
        
        self.desc_entry = components.create_entry(
            main_frame,
            placeholder_text="Brief description of what this snippet does"
        )
        self.desc_entry.pack(fill="x", pady=(0, design.get_spacing("lg")))
        
        # Command type selection
        type_label = components.create_label(
            main_frame,
            text="Command Type:",
            font=design.get_font("body_medium")
        )
        type_label.pack(anchor="w", pady=(0, design.get_spacing("sm")))
        
        type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_frame.pack(anchor="w", pady=(0, design.get_spacing("lg")))
        
        self.command_type = ctk.StringVar(value="single")
        
        single_radio = ctk.CTkRadioButton(
            type_frame,
            text="Single line command",
            variable=self.command_type,
            value="single",
            fg_color=design.get_color("text_primary"),
            hover_color=design.get_color("text_secondary"),
            text_color=design.get_color("text_primary"),
            font=design.get_font("body_medium")
        )
        single_radio.pack(side="left", padx=(0, design.get_spacing("xl")))
        
        script_radio = ctk.CTkRadioButton(
            type_frame,
            text="Multi-line script",
            variable=self.command_type,
            value="script",
            fg_color=design.get_color("text_primary"),
            hover_color=design.get_color("text_secondary"),
            text_color=design.get_color("text_primary"),
            font=design.get_font("body_medium")
        )
        script_radio.pack(side="left")
        
        # Command field
        command_label = components.create_label(
            main_frame,
            text="Command/Script:",
            font=design.get_font("body_medium")
        )
        command_label.pack(anchor="w", pady=(0, design.get_spacing("sm")))
        
        # Text widget for command (supports multi-line)
        text_frame = components.create_frame(main_frame, style="bordered")
        text_frame.pack(fill="both", expand=True, pady=(0, design.get_spacing("xl")))
        
        self.command_text = ctk.CTkTextbox(
            text_frame,
            fg_color=design.get_color("bg_primary"),
            text_color=design.get_color("text_primary"),
            font=design.get_font("monospace"),
            corner_radius=0
        )
        self.command_text.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Load existing data if editing
        if self.snippet:
            self.name_entry.insert(0, self.snippet.name)
            if self.snippet.description:
                self.desc_entry.insert(0, self.snippet.description)
            self.command_text.insert("1.0", self.snippet.command)
            self.command_type.set("script" if self.snippet.is_script else "single")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        save_btn = components.create_button(
            button_frame,
            text="Save",
            command=self._save,
            width=100
        )
        save_btn.pack(side="left", padx=(0, design.get_spacing("md")))
        
        cancel_btn = components.create_button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=100,
            style="secondary"
        )
        cancel_btn.pack(side="left")
        
        # Focus on name entry
        self.name_entry.focus()
    
    def _save(self) -> None:
        """Save the snippet."""
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip() or None
        command = self.command_text.get("1.0", "end-1c").strip()
        is_script = self.command_type.get() == "script"
        
        # Validate
        if not name:
            self.show_error("Please enter a snippet name.")
            return
        
        if not command:
            self.show_error("Please enter a command or script.")
            return
        
        # Create or update snippet
        if self.is_edit:
            self.snippet.name = name
            self.snippet.description = description
            self.snippet.command = command
            self.snippet.is_script = is_script
            self.result = self.snippet
        else:
            self.result = Snippet(
                id=0,
                server_id=self.server_id,
                name=name,
                description=description,
                command=command,
                is_script=is_script,
                order_index=0
            )
        
        self.dialog.destroy()


class SnippetManagerDialog(BaseDialog):
    """Dialog for managing server snippets."""
    
    def __init__(self, parent: ctk.CTk, server_id: int, server_name: str, storage: ServerStorage):
        self.server_id = server_id
        self.server_name = server_name
        self.storage = storage
        self.snippets: List[Snippet] = []
        super().__init__(parent, f"Manage Snippets - {server_name}")
    
    def setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.dialog.geometry("700x500")
        
        # Main frame
        main_frame = components.create_frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=design.get_spacing("xxl"), pady=design.get_spacing("xxl"))
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, design.get_spacing("xl")))
        
        title_label = components.create_label(
            header_frame,
            text=f"Snippets for {self.server_name}",
            style="heading",
            font=design.get_font("heading_small")
        )
        title_label.pack(side="left")
        
        add_btn = components.create_button(
            header_frame,
            text="+ Add Snippet",
            command=self._add_snippet,
            width=120
        )
        add_btn.pack(side="right")
        
        # Snippet list frame
        list_frame = components.create_frame(main_frame, style="bordered")
        list_frame.pack(fill="both", expand=True, pady=(0, design.get_spacing("xl")))
        
        # Scrollable frame for snippets
        self.scroll_frame = components.create_scrollable_frame(list_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Load snippets
        self._load_snippets()
        
        # Close button
        close_btn = components.create_button(
            main_frame,
            text="Close",
            command=self.dialog.destroy,
            width=100
        )
        close_btn.pack()
    
    def _load_snippets(self) -> None:
        """Load and display snippets."""
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Load snippets from storage
        self.snippets = self.storage.get_snippets(self.server_id)
        
        if not self.snippets:
            # Show empty state
            empty_label = components.create_label(
                self.scroll_frame,
                text="No snippets yet. Click 'Add Snippet' to create one.",
                style="secondary"
            )
            empty_label.pack(pady=design.get_spacing("xxxl"))
            return
        
        # Display snippets
        for i, snippet in enumerate(self.snippets):
            self._create_snippet_widget(snippet, i)
    
    def _create_snippet_widget(self, snippet: Snippet, index: int) -> None:
        """Create a widget for a snippet."""
        # Container frame
        container = components.create_frame(self.scroll_frame)
        container.pack(fill="x", pady=(0, design.get_spacing("md")), padx=design.get_spacing("md"))
        
        # Content frame
        content_frame = ctk.CTkFrame(container, fg_color="transparent")
        content_frame.pack(fill="x", padx=design.get_spacing("md"), pady=design.get_spacing("md"))
        
        # Name and description
        name_label = components.create_label(
            content_frame,
            text=snippet.name,
            font=design.get_font("body_medium")
        )
        name_label.pack(anchor="w")
        
        if snippet.description:
            desc_label = components.create_label(
                content_frame,
                text=snippet.description,
                style="secondary",
                font=design.get_font("body_small")
            )
            desc_label.pack(anchor="w", pady=(design.get_spacing("xs"), 0))
        
        # Command preview (first line only)
        command_preview = snippet.command.split('\n')[0]
        if len(snippet.command.split('\n')) > 1 or len(command_preview) > 50:
            command_preview = command_preview[:50] + "..."
        
        cmd_label = components.create_label(
            content_frame,
            text=f"Command: {command_preview}",
            font=design.get_font("monospace"),
            text_color=design.get_color("text_secondary")
        )
        cmd_label.pack(anchor="w", pady=(design.get_spacing("xs"), 0))
        
        # Action buttons
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.pack(fill="x", padx=design.get_spacing("md"))
        
        # Move up/down buttons
        if index > 0:
            up_btn = components.create_button(
                action_frame,
                text="↑",
                command=lambda: self._move_snippet(index, -1),
                width=30
            )
            up_btn.pack(side="left", padx=(0, design.get_spacing("xs")))
        
        if index < len(self.snippets) - 1:
            down_btn = components.create_button(
                action_frame,
                text="↓",
                command=lambda: self._move_snippet(index, 1),
                width=30
            )
            down_btn.pack(side="left", padx=(0, design.get_spacing("md")))
        
        # Edit button
        edit_btn = components.create_button(
            action_frame,
            text="Edit",
            command=lambda s=snippet: self._edit_snippet(s),
            width=60
        )
        edit_btn.pack(side="left", padx=(0, design.get_spacing("xs")))
        
        # Delete button
        delete_btn = components.create_button(
            action_frame,
            text="Delete",
            command=lambda s=snippet: self._delete_snippet(s),
            width=60,
            style="secondary"
        )
        delete_btn.pack(side="left")
        
        # Separator
        if index < len(self.snippets) - 1:
            sep = ctk.CTkFrame(self.scroll_frame, height=1, fg_color=design.get_color("border_secondary"))
            sep.pack(fill="x", padx=design.get_spacing("md"), pady=(0, design.get_spacing("md")))
    
    def _add_snippet(self) -> None:
        """Add a new snippet."""
        dialog = SnippetEditDialog(self.dialog, self.server_id)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            snippet_id = self.storage.add_snippet(dialog.result)
            if snippet_id:
                self._load_snippets()
    
    def _edit_snippet(self, snippet: Snippet) -> None:
        """Edit a snippet."""
        dialog = SnippetEditDialog(self.dialog, self.server_id, snippet)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            if self.storage.update_snippet(dialog.result):
                self._load_snippets()
    
    def _delete_snippet(self, snippet: Snippet) -> None:
        """Delete a snippet."""
        result = messagebox.askyesno(
            "Delete Snippet",
            f"Are you sure you want to delete the snippet '{snippet.name}'?"
        )
        
        if result:
            if self.storage.delete_snippet(snippet.id):
                self._load_snippets()
    
    def _move_snippet(self, index: int, direction: int) -> None:
        """Move a snippet up or down."""
        new_index = index + direction
        if 0 <= new_index < len(self.snippets):
            # Swap snippets
            self.snippets[index], self.snippets[new_index] = self.snippets[new_index], self.snippets[index]
            
            # Update order in database
            snippet_ids = [s.id for s in self.snippets]
            if self.storage.reorder_snippets(self.server_id, snippet_ids):
                self._load_snippets()