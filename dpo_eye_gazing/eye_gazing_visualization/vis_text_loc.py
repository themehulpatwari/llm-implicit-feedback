from PIL import Image, ImageDraw, ImageFont

def visualize_char_positions_multiline(text, font_path=None, font_size=12):
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    line_height = font_size * 1.2  # vertical spacing between lines

    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)

    char_positions = []
    x_cursor = 0
    y_cursor = 0

    for char in text:
        if char == "\n":
            # Reset x, advance y — don't record a bbox for \n
            x_cursor = 0
            y_cursor += line_height
            continue

        bbox = draw.textbbox((x_cursor, y_cursor), char, font=font)
        char_positions.append({
            "char": char,
            "x": bbox[0], "y": bbox[1],
            "width": bbox[2] - bbox[0],
            "height": bbox[3] - bbox[1]
        })
        x_cursor = bbox[2]

    # --- Render visualization ---
    max_x = max(p["x"] + p["width"] for p in char_positions) + 20
    max_y = max(p["y"] + p["height"] for p in char_positions) + 20

    img = Image.new("RGB", (int(max_x), int(max_y)), "white")
    draw = ImageDraw.Draw(img)

    # Draw full text for reference
    draw.multiline_text((0, 0), text, font=font, fill="black", spacing=font_size * 0.2)

    # Draw per-character bounding boxes
    for cp in char_positions:
        draw.rectangle(
            [cp["x"], cp["y"], cp["x"] + cp["width"], cp["y"] + cp["height"]],
            outline="red"
        )

    img.show()
    return char_positions

visualize_char_positions_multiline(
    "Hello, World!\nThis is a test."
)