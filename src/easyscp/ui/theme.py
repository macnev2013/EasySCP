"""Theme and color management for EasySCP."""

import customtkinter as ctk
from typing import Dict, Tuple, Optional

class ThemeManager:
    """Manages application theming and colors."""
    
    # Color palette
    COLORS = {
        # Primary colors
        "primary": {"light": "#3b82f6", "dark": "#2563eb"},
        "primary_hover": {"light": "#2563eb", "dark": "#1d4ed8"},
        
        # Success colors  
        "success": {"light": "#10b981", "dark": "#059669"},
        "success_hover": {"light": "#059669", "dark": "#047857"},
        
        # Warning colors
        "warning": {"light": "#f59e0b", "dark": "#d97706"},
        "warning_pulse": {"light": "#fbbf24", "dark": "#f59e0b"},
        
        # Danger colors
        "danger": {"light": "#dc2626", "dark": "#b91c1c"},
        "danger_hover": {"light": "#b91c1c", "dark": "#991b1b"},
        
        # Info colors
        "info": {"light": "#6366f1", "dark": "#4f46e5"},
        "info_hover": {"light": "#4f46e5", "dark": "#4338ca"},
        
        # Neutral colors
        "neutral": {"light": "gray75", "dark": "gray25"},
        "neutral_hover": {"light": "gray65", "dark": "gray35"},
        
        # Text colors
        "text_primary": {"light": "gray10", "dark": "gray90"},
        "text_secondary": {"light": "gray40", "dark": "gray60"},
        "text_disabled": {"light": "gray60", "dark": "gray40"},
        
        # Background colors
        "bg_primary": {"light": "gray98", "dark": "gray10"},
        "bg_secondary": {"light": "gray95", "dark": "gray15"},
        "bg_hover": {"light": "gray95", "dark": "gray15"},
        
        # Border colors
        "border_primary": {"light": "gray80", "dark": "gray20"},
        "border_selected": {"light": "#3b82f6", "dark": "#2563eb"},
    }
    
    @classmethod
    def get_color(cls, color_name: str, mode: Optional[str] = None) -> Tuple[str, str]:
        """Get color tuple for light/dark modes."""
        if color_name not in cls.COLORS:
            return ("gray50", "gray50")
        
        color = cls.COLORS[color_name]
        if mode == "light":
            return color["light"]
        elif mode == "dark":
            return color["dark"]
        else:
            # Return tuple for automatic mode switching
            return (color["light"], color["dark"])
    
    @classmethod
    def apply_theme(cls, theme: str = "light", color_scheme: str = "blue") -> None:
        """Apply theme to the application."""
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme(color_scheme)
    
    @classmethod
    def get_button_colors(cls, style: str = "primary") -> Dict[str, Tuple[str, str]]:
        """Get button colors based on style."""
        styles = {
            "primary": {
                "fg_color": cls.get_color("primary"),
                "hover_color": cls.get_color("primary_hover")
            },
            "success": {
                "fg_color": cls.get_color("success"),
                "hover_color": cls.get_color("success_hover")
            },
            "danger": {
                "fg_color": cls.get_color("danger"),
                "hover_color": cls.get_color("danger_hover")
            },
            "info": {
                "fg_color": cls.get_color("info"),
                "hover_color": cls.get_color("info_hover")
            },
            "neutral": {
                "fg_color": cls.get_color("neutral"),
                "hover_color": cls.get_color("neutral_hover")
            }
        }
        return styles.get(style, styles["primary"])
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Get color for status indicators."""
        status_colors = {
            "connected": cls.get_color("success"),
            "connecting": cls.get_color("warning"),
            "disconnected": cls.get_color("danger"),
            "error": cls.get_color("danger")
        }
        return status_colors.get(status, cls.get_color("neutral"))[0]  # Return light mode color for now