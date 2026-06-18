import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties

def get_char_positions_multiline(text, font_size=14):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    fp = FontProperties(size=font_size)
    renderer = fig.canvas.get_renderer()

    # ✅ Measure real line height from a reference character
    ref = ax.text(0, 0, "Ag", fontproperties=fp, transform=ax.transAxes, alpha=0)
    ref_bbox = ref.get_window_extent(renderer=renderer)
    inv = ax.transAxes.inverted()
    p0 = inv.transform((ref_bbox.x0, ref_bbox.y0))
    p1 = inv.transform((ref_bbox.x1, ref_bbox.y1))
    line_height = (p1[1] - p0[1]) * 1.4  # real height + 40% leading
    ref.remove()

    x_start, y_start = 0.05, 0.85
    x_cursor, y_cursor = x_start, y_start
    char_data = []

    for char in text:
        if char == "\n":
            x_cursor = x_start
            y_cursor -= line_height  # ✅ uses measured height, not guessed
            continue

        t = ax.text(x_cursor, y_cursor, char, fontproperties=fp,
                    transform=ax.transAxes, alpha=0)
        bbox = t.get_window_extent(renderer=renderer)

        p0 = inv.transform((bbox.x0, bbox.y0))
        p1 = inv.transform((bbox.x1, bbox.y1))
        char_w = p1[0] - p0[0]
        char_h = p1[1] - p0[1]

        char_data.append({
            "char": char,
            "x": x_cursor, "y": y_cursor,
            "width": char_w, "height": char_h
        })

        t.set_alpha(1)
        x_cursor += char_w

    for cd in char_data:
        rect = patches.Rectangle(
            (cd["x"], cd["y"]),
            cd["width"], cd["height"],
            linewidth=0.6, edgecolor="red",
            facecolor="none", transform=ax.transAxes
        )
        ax.add_patch(rect)

    plt.tight_layout()
    plt.show()
    return char_data

sample = "Hello, World!\nThis is line two.\nAnd line three!"
positions = get_char_positions_multiline(sample)