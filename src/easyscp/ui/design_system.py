"""Global design system for EasySCP - Minimal black and white theme."""

import customtkinter as ctk
from typing import Dict, Tuple, Optional, Any


class DesignSystem:
    """Centralized design system for consistent styling across the application."""
    
    # === COLOR PALETTE ===
    COLORS = {
        # Core colors - minimal black and white
        "white": ("white", "white"),
        "black": ("black", "black"),
        
        # Gray scale
        "gray_95": ("gray95", "gray95"),
        "gray_97": ("gray97", "gray97"),
        "gray_30": ("gray30", "gray30"),
        "gray_20": ("gray20", "gray20"),
        
        # Background colors
        "bg_primary": ("white", "white"),
        "bg_secondary": ("gray97", "gray97"),
        "bg_hover": ("gray95", "gray95"),
        
        # Text colors
        "text_primary": ("black", "black"),
        "text_secondary": ("gray30", "gray30"),
        
        # Border colors
        "border_primary": ("black", "black"),
        "border_secondary": ("gray30", "gray30"),
    }
    
    # === TYPOGRAPHY ===
    FONTS = {
        "heading_large": ("Arial", 20, "bold"),
        "heading_medium": ("Arial", 18, "bold"),
        "heading_small": ("Arial", 15, "bold"),
        "body_large": ("Arial", 14),
        "body_medium": ("Arial", 12),
        "body_small": ("Arial", 11),
        "caption": ("Arial", 10),
        "monospace": ("Consolas", 11),
    }
    
    # === SPACING ===
    SPACING = {
        "xs": 2,
        "sm": 4,
        "md": 8,
        "lg": 12,
        "xl": 16,
        "xxl": 20,
        "xxxl": 24,
    }
    
    # === SIZES ===
    SIZES = {
        "button_height": 32,
        "input_height": 32,
        "header_height": 50,
        "border_width": 1,
        "border_width_selected": 2,
    }
    
    @classmethod
    def get_color(cls, color_name: str) -> Tuple[str, str]:
        """Get color tuple for the design system."""
        return cls.COLORS.get(color_name, cls.COLORS["black"])
    
    @classmethod
    def get_font(cls, font_name: str) -> Tuple[str, int, str]:
        """Get font configuration."""
        return cls.FONTS.get(font_name, cls.FONTS["body_medium"])
    
    @classmethod
    def get_spacing(cls, size: str) -> int:
        """Get spacing value."""
        return cls.SPACING.get(size, cls.SPACING["md"])
    
    @classmethod
    def get_size(cls, size_name: str) -> int:
        """Get size value."""
        return cls.SIZES.get(size_name, 32)


class StyleBuilder:
    """Builder class for creating consistent UI element styles."""
    
    @staticmethod
    def button(style: str = "primary", disabled: bool = False) -> Dict[str, Any]:
        """Create button style configuration."""
        base_style = {
            "corner_radius": 0,
            "border_width": DesignSystem.get_size("border_width"),
            "border_color": DesignSystem.get_color("border_primary"),
            "height": DesignSystem.get_size("button_height"),
            "font": DesignSystem.get_font("body_medium"),
        }
        
        if disabled:
            base_style.update({
                "fg_color": DesignSystem.get_color("bg_secondary"),
                "hover_color": DesignSystem.get_color("bg_secondary"),
                "text_color": DesignSystem.get_color("text_secondary"),
            })
        else:
            if style == "primary":
                base_style.update({
                    "fg_color": DesignSystem.get_color("bg_primary"),
                    "hover_color": DesignSystem.get_color("bg_hover"),
                    "text_color": DesignSystem.get_color("text_primary"),
                })
            elif style == "secondary":
                base_style.update({
                    "fg_color": DesignSystem.get_color("bg_secondary"),
                    "hover_color": DesignSystem.get_color("bg_hover"),
                    "text_color": DesignSystem.get_color("text_primary"),
                })
        
        return base_style
    
    @staticmethod
    def entry() -> Dict[str, Any]:
        """Create entry/input field style configuration."""
        return {
            "corner_radius": 0,
            "border_width": DesignSystem.get_size("border_width"),
            "border_color": DesignSystem.get_color("border_primary"),
            "fg_color": DesignSystem.get_color("bg_primary"),
            "text_color": DesignSystem.get_color("text_primary"),
            "height": DesignSystem.get_size("input_height"),
            "font": DesignSystem.get_font("body_medium"),
        }
    
    @staticmethod
    def frame(style: str = "primary") -> Dict[str, Any]:
        """Create frame style configuration."""
        base_style = {
            "corner_radius": 0,
            "fg_color": DesignSystem.get_color("bg_primary"),
        }
        
        if style == "bordered":
            base_style.update({
                "border_width": DesignSystem.get_size("border_width"),
                "border_color": DesignSystem.get_color("border_primary"),
            })
        elif style == "selected":
            base_style.update({
                "border_width": DesignSystem.get_size("border_width_selected"),
                "border_color": DesignSystem.get_color("border_primary"),
            })
        
        return base_style
    
    @staticmethod
    def label(style: str = "primary") -> Dict[str, Any]:
        """Create label style configuration."""
        base_style = {
            "font": DesignSystem.get_font("body_medium"),
        }
        
        if style == "heading":
            base_style.update({
                "font": DesignSystem.get_font("heading_medium"),
                "text_color": DesignSystem.get_color("text_primary"),
            })
        elif style == "secondary":
            base_style.update({
                "text_color": DesignSystem.get_color("text_secondary"),
            })
        else:  # primary
            base_style.update({
                "text_color": DesignSystem.get_color("text_primary"),
            })
        
        return base_style
    
    @staticmethod
    def dropdown() -> Dict[str, Any]:
        """Create dropdown/option menu style configuration."""
        return {
            "corner_radius": 0,
            "fg_color": DesignSystem.get_color("bg_primary"),
            "button_color": DesignSystem.get_color("bg_primary"),
            "button_hover_color": DesignSystem.get_color("bg_hover"),
            "dropdown_fg_color": DesignSystem.get_color("bg_primary"),
            "dropdown_hover_color": DesignSystem.get_color("bg_hover"),
            "text_color": DesignSystem.get_color("text_primary"),
            "dropdown_text_color": DesignSystem.get_color("text_primary"),
            "height": DesignSystem.get_size("input_height"),
            "font": DesignSystem.get_font("body_medium"),
        }
    
    @staticmethod
    def checkbox() -> Dict[str, Any]:
        """Create checkbox style configuration."""
        return {
            "fg_color": DesignSystem.get_color("bg_primary"),
            "hover_color": DesignSystem.get_color("bg_hover"),
            "border_color": DesignSystem.get_color("border_primary"),
            "checkmark_color": DesignSystem.get_color("text_primary"),
            "text_color": DesignSystem.get_color("text_primary"),
            "font": DesignSystem.get_font("body_medium"),
        }
    
    @staticmethod
    def scrollable_frame() -> Dict[str, Any]:
        """Create scrollable frame style configuration."""
        return {
            "corner_radius": 0,
            "fg_color": DesignSystem.get_color("bg_primary"),
            "scrollbar_button_color": ("gray70", "gray70"),
            "scrollbar_button_hover_color": ("gray50", "gray50"),
        }
    
    @staticmethod
    def tab_view() -> Dict[str, Any]:
        """Create tab view style configuration."""
        return {
            "fg_color": DesignSystem.get_color("bg_primary"),
            "segmented_button_fg_color": DesignSystem.get_color("bg_primary"),
            "segmented_button_selected_color": DesignSystem.get_color("bg_secondary"),
            "segmented_button_selected_hover_color": DesignSystem.get_color("bg_hover"),
            "segmented_button_unselected_color": DesignSystem.get_color("bg_primary"),
            "segmented_button_unselected_hover_color": DesignSystem.get_color("bg_hover"),
            "text_color": DesignSystem.get_color("text_primary"),
        }
    
    @staticmethod
    def configure_treeview_style():
        """Configure ttk.Treeview styling to match design system."""
        from tkinter import ttk
        
        style = ttk.Style()
        
        # Configure Treeview
        style.configure("Treeview",
                       background="white",
                       foreground="black",
                       fieldbackground="white",
                       borderwidth=0,
                       relief="flat")
        
        # Configure Treeview headings
        style.configure("Treeview.Heading",
                       background="white",
                       foreground="black",
                       borderwidth=1,
                       relief="solid")
        
        # Configure selected items
        style.map("Treeview",
                 background=[("selected", "gray95")],
                 foreground=[("selected", "black")])
        
        # Configure scrollbars
        style.configure("Vertical.TScrollbar",
                       background="gray70",
                       troughcolor="white",
                       borderwidth=0,
                       arrowcolor="black")
        
        style.configure("Horizontal.TScrollbar",
                       background="gray70",
                       troughcolor="white",
                       borderwidth=0,
                       arrowcolor="black")


class ComponentFactory:
    """Factory class for creating styled UI components."""
    
    @staticmethod
    def create_button(parent, text: str, command=None, style: str = "primary", **kwargs) -> ctk.CTkButton:
        """Create a styled button."""
        button_style = StyleBuilder.button(style)
        button_style.update(kwargs)  # Allow custom overrides
        
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            **button_style
        )
    
    @staticmethod
    def create_entry(parent, **kwargs) -> ctk.CTkEntry:
        """Create a styled entry field."""
        entry_style = StyleBuilder.entry()
        entry_style.update(kwargs)  # Allow custom overrides
        
        return ctk.CTkEntry(parent, **entry_style)
    
    @staticmethod
    def create_label(parent, text: str, style: str = "primary", **kwargs) -> ctk.CTkLabel:
        """Create a styled label."""
        label_style = StyleBuilder.label(style)
        label_style.update(kwargs)  # Allow custom overrides
        
        return ctk.CTkLabel(parent, text=text, **label_style)
    
    @staticmethod
    def create_frame(parent, style: str = "primary", **kwargs) -> ctk.CTkFrame:
        """Create a styled frame."""
        frame_style = StyleBuilder.frame(style)
        frame_style.update(kwargs)  # Allow custom overrides
        
        return ctk.CTkFrame(parent, **frame_style)
    
    @staticmethod
    def create_dropdown(parent, values: list, **kwargs) -> ctk.CTkOptionMenu:
        """Create a styled dropdown."""
        dropdown_style = StyleBuilder.dropdown()
        dropdown_style.update(kwargs)  # Allow custom overrides
        
        return ctk.CTkOptionMenu(parent, values=values, **dropdown_style)
    
    @staticmethod
    def create_bordered_dropdown(parent, values: list, **kwargs) -> ctk.CTkFrame:
        """Create a dropdown with border wrapper."""
        # Create wrapper frame for border effect
        wrapper = ctk.CTkFrame(parent, fg_color=DesignSystem.get_color("border_primary"), corner_radius=0)
        
        dropdown_style = StyleBuilder.dropdown()
        dropdown_style.update(kwargs)  # Allow custom overrides
        dropdown_style["width"] = dropdown_style.get("width", 200) - 4  # Account for padding
        dropdown_style["height"] = dropdown_style.get("height", 32) - 4  # Account for padding
        
        dropdown = ctk.CTkOptionMenu(wrapper, values=values, **dropdown_style)
        dropdown.pack(padx=1, pady=1)
        
        return wrapper
    
    @staticmethod
    def create_scrollable_frame(parent, **kwargs) -> ctk.CTkScrollableFrame:
        """Create a styled scrollable frame."""
        scrollable_style = StyleBuilder.scrollable_frame()
        scrollable_style.update(kwargs)  # Allow custom overrides
        
        return ctk.CTkScrollableFrame(parent, **scrollable_style)


# Global instances for easy access
design = DesignSystem()
styles = StyleBuilder()
components = ComponentFactory()