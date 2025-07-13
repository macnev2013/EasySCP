# EasySCP Design System

This document outlines the global design system for EasySCP, providing consistent styling and theming across the entire application.

## Overview

The design system is based on a minimal black and white aesthetic with the following principles:
- Clean, minimal interface
- Consistent spacing and typography
- Monochromatic color scheme
- Sharp, geometric elements (no rounded corners)
- Clear visual hierarchy

## Usage

### Importing the Design System

```python
from .design_system import design, styles, components
```

### Colors

The design system provides a limited color palette focused on black, white, and subtle grays:

```python
# Get color tuples for CustomTkinter
bg_color = design.get_color("bg_primary")  # Returns ("white", "white")
text_color = design.get_color("text_primary")  # Returns ("black", "black")
border_color = design.get_color("border_primary")  # Returns ("black", "black")
```

Available colors:
- `white` - Pure white
- `black` - Pure black
- `gray_95`, `gray_97`, `gray_30`, `gray_20` - Various gray shades
- `bg_primary`, `bg_secondary`, `bg_hover` - Background colors
- `text_primary`, `text_secondary` - Text colors
- `border_primary`, `border_secondary` - Border colors

### Typography

Consistent font sizing and weights:

```python
# Get font configurations
heading_font = design.get_font("heading_large")  # Returns ("Arial", 20, "bold")
body_font = design.get_font("body_medium")  # Returns ("Arial", 12)
```

Available fonts:
- `heading_large`, `heading_medium`, `heading_small` - For headings
- `body_large`, `body_medium`, `body_small` - For body text
- `caption` - For small text
- `monospace` - For code/terminal text

### Spacing

Consistent spacing values:

```python
# Get spacing values
small_padding = design.get_spacing("sm")  # Returns 4
medium_padding = design.get_spacing("md")  # Returns 8
large_padding = design.get_spacing("lg")  # Returns 12
```

Available spacing:
- `xs` (2px), `sm` (4px), `md` (8px), `lg` (12px), `xl` (16px), `xxl` (20px), `xxxl` (24px)

### Sizes

Standard component sizes:

```python
button_height = design.get_size("button_height")  # Returns 32
border_width = design.get_size("border_width")  # Returns 1
```

## Components

### Using the Component Factory

The component factory creates pre-styled UI elements:

#### Buttons

```python
# Primary button (white background, black border)
primary_btn = components.create_button(
    parent=frame,
    text="Save",
    command=save_function
)

# Secondary button (gray background)
secondary_btn = components.create_button(
    parent=frame,
    text="Cancel",
    command=cancel_function,
    style="secondary"
)
```

#### Input Fields

```python
# Entry field with black border
entry = components.create_entry(
    parent=frame,
    placeholder_text="Enter text...",
    width=200
)
```

#### Labels

```python
# Primary label (black text)
label = components.create_label(
    parent=frame,
    text="Username:",
    style="primary"
)

# Heading label (larger, bold)
heading = components.create_label(
    parent=frame,
    text="Settings",
    style="heading"
)

# Secondary label (gray text)
sublabel = components.create_label(
    parent=frame,
    text="Optional field",
    style="secondary"
)
```

#### Frames

```python
# Basic frame
frame = components.create_frame(parent=container)

# Frame with border
bordered_frame = components.create_frame(
    parent=container,
    style="bordered"
)

# Selected/highlighted frame
selected_frame = components.create_frame(
    parent=container,
    style="selected"
)
```

#### Dropdowns

```python
# Basic dropdown
dropdown = components.create_dropdown(
    parent=frame,
    values=["Option 1", "Option 2", "Option 3"]
)

# Dropdown with border (returns wrapper frame)
bordered_dropdown = components.create_bordered_dropdown(
    parent=frame,
    values=["Option 1", "Option 2", "Option 3"],
    width=200
)
```

### Using Style Builders

For more control, use the style builders directly:

```python
# Get button style dictionary
button_style = styles.button(style="primary")
custom_button = ctk.CTkButton(parent, **button_style, text="Custom")

# Get entry style dictionary
entry_style = styles.entry()
custom_entry = ctk.CTkEntry(parent, **entry_style)
```

## Customization

You can override any style properties by passing additional keyword arguments:

```python
# Override default button colors
custom_button = components.create_button(
    parent=frame,
    text="Special Button",
    fg_color=("red", "red"),  # Override background
    width=150  # Override width
)
```

## Migration Guide

To migrate existing components to use the design system:

### Before (manual styling):
```python
button = ctk.CTkButton(
    parent,
    text="Save",
    corner_radius=0,
    fg_color=("white", "white"),
    hover_color=("gray95", "gray95"),
    text_color=("black", "black"),
    border_width=1,
    border_color=("black", "black"),
    height=32
)
```

### After (design system):
```python
button = components.create_button(parent, text="Save")
```

## Best Practices

1. **Always use the design system** for new components
2. **Import once** at the top of your file: `from .design_system import design, styles, components`
3. **Use semantic names** rather than hardcoded values
4. **Override sparingly** - only when absolutely necessary
5. **Test in both light and dark modes** (when applicable)
6. **Maintain consistency** across similar components

## Examples

See the updated `main_window.py` for examples of how existing components have been converted to use the design system.