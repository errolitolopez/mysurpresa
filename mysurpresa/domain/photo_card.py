"""The downloadable picture of an item: its photo with the name and price under it, ready to post.

1080 x 1350 pixels (4:5), the size Facebook and Instagram show biggest in a feed.
Drawn with the bundled DejaVu fonts (mysurpresa/fonts), so it looks the same on every server.
"""

import io
import os

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1350
PHOTO_HEIGHT = 1080           # the photo takes the top square, the text the band under it
MARGIN = 56
NAME_SIZE = 44
PRICE_SIZE = 76
SHOP_SIZE = 30
BASELINE = HEIGHT - 44        # the price and the shop name stand on this line
MAX_NAME_LINES = 2
JPEG_QUALITY = 90

# The same colours as the shop (glass.css, neumorphic light): page grey, text, accent gradient.
BACKGROUND = (224, 229, 236)
TEXT = (33, 37, 41)
MUTED = (108, 117, 125)
ACCENT_FROM = (79, 70, 229)    # #4f46e5
ACCENT_TO = (6, 182, 212)      # #06b6d4
STATUS_COLOURS = {"reserved": (255, 193, 7), "sold": (108, 117, 125)}

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def wrap(draw, text, font, width, max_lines):
    """The text split into lines that fit the width; the last line ends with "…" if it was cut."""
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) <= width:
            line = candidate
            continue
        if line:
            lines.append(line)
        line = word
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] += "…"
    # A single word wider than the line (rare): cut letters until it fits.
    lines = [shorten(draw, line, font, width) for line in lines]
    return lines


def shorten(draw, line, font, width):
    if draw.textlength(line, font=font) <= width:
        return line
    while line and draw.textlength(line + "…", font=font) > width:
        line = line[:-1]
    return line + "…"


def gradient_text(image, position, text, font, anchor):
    """Draw text filled with the accent gradient (left to right), like the prices in the shop."""
    left, top, right, bottom = ImageDraw.Draw(image).textbbox(position, text, font=font, anchor=anchor)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).text(position, text, font=font, fill=255, anchor=anchor)
    gradient = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(gradient)
    span = max(right - left, 1)
    # Across the whole width, not only the text box: a glyph can reach a little outside its box
    # (the bars of ₱), and that part must be coloured too. Outside the box the colour stays the end colour.
    for x in range(image.width):
        t = min(max((x - left) / span, 0), 1)
        colour = tuple(round(a + (b - a) * t) for a, b in zip(ACCENT_FROM, ACCENT_TO))
        draw.line((x, top - 10, x, bottom + 10), fill=colour)
    image.paste(gradient, (0, 0), mask)


def make_photo_card(photo_path, name, price_text, shop_name, status=None):
    """The picture as JPEG bytes. status "reserved" or "sold" adds a label on the photo."""
    card = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(card)

    # The whole photo, never cropped, centred in the top square.
    with Image.open(photo_path) as photo:
        photo = photo.convert("RGB")
        photo.thumbnail((WIDTH, PHOTO_HEIGHT), Image.LANCZOS)
        card.paste(photo, ((WIDTH - photo.width) // 2, (PHOTO_HEIGHT - photo.height) // 2))

    if status in STATUS_COLOURS:
        label = status.upper()
        font = ImageFont.truetype(BOLD, 40)
        text_width = draw.textlength(label, font=font)
        box = (MARGIN, MARGIN, MARGIN + text_width + 48, MARGIN + 72)
        draw.rounded_rectangle(box, radius=36, fill=STATUS_COLOURS[status])
        colour = TEXT if status == "reserved" else (255, 255, 255)
        draw.text((MARGIN + 24, MARGIN + 36), label, font=font, fill=colour, anchor="lm")

    text_width = WIDTH - 2 * MARGIN
    name_font = ImageFont.truetype(BOLD, NAME_SIZE)
    price_font = ImageFont.truetype(BOLD, PRICE_SIZE)
    shop_font = ImageFont.truetype(REGULAR, SHOP_SIZE)

    y = PHOTO_HEIGHT + 28
    for line in wrap(draw, name, name_font, text_width, MAX_NAME_LINES):
        draw.text((MARGIN, y), line, font=name_font, fill=TEXT)
        y += NAME_SIZE + 12
    gradient_text(card, (MARGIN, BASELINE), price_text, price_font, anchor="ls")
    draw.text((WIDTH - MARGIN, BASELINE), shop_name, font=shop_font, fill=MUTED, anchor="rs")

    buffer = io.BytesIO()
    card.save(buffer, "JPEG", quality=JPEG_QUALITY, optimize=True)
    return buffer.getvalue()
