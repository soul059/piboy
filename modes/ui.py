import os
from PIL import ImageFont

MAX_MENU_ITEMS = 4 # Max items to show on screen at once

def draw_menu(draw, title, items, selected_index, offset):
    """Generic function to draw a scrollable menu."""
    font = ImageFont.load_default()
    draw.text((0, 0), f"--- {title} ---", fill="white", font=font)
    
    if not items:
        draw.text((5, 25), "No files found!", fill="white", font=font)
        return

    for i in range(offset, min(offset + MAX_MENU_ITEMS, len(items))):
        display_text = f"{'> ' if i == selected_index else '  '}{os.path.basename(items[i])}"
        if len(display_text) > 20:
            display_text = display_text[:17] + "..."
        y_pos = 12 + (i - offset) * 12
        draw.text((0, y_pos), display_text, fill="white", font=font)
