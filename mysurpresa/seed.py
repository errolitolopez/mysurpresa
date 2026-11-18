"""Sample parcels and items (with drawn placeholder photos) for trying out the shop.

Run with: flask --app app seed

Only runs on an empty shop, so it never mixes sample items with real ones.
Remove them later from the admin page (delete each item and parcel).
"""

import io

import click
from flask import current_app
from flask.cli import with_appcontext
from PIL import Image, ImageDraw, ImageFont
from werkzeug.datastructures import FileStorage

from mysurpresa.database import get_db
from mysurpresa.services import ItemService, ParcelService, PhotoService

FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"]

# (name, cost in pesos, day bought, note)
PARCELS = [
    ("Mystery parcel #1", 1500, "2026-11-02", "Shopee mystery box, big size"),
    ("Mystery parcel #2", 2200, "2026-11-15", "Returned parcels bundle"),
]

# (parcel number or None, name, price in pesos, status, description, photo colours)
ITEMS = [
    (1, "Running shoes, size 9", 1250, "available",
     "Like new, worn once.\nWith box.", [(214, 51, 132), (60, 60, 90)]),
    (1, "Wireless earbuds", 650, "available",
     "Complete with charging case and cable. Tested, working.", [(40, 120, 200)]),
    (1, "Leather sling bag", 480, "reserved",
     "Brown, adjustable strap. Small scratch at the back.", [(150, 90, 50), (120, 70, 40)]),
    (1, "Stainless tumbler 40 oz", 350, "sold",
     "Keeps drinks cold for 24 hours. With straw.", [(30, 150, 130)]),
    (2, "Smart watch", 899, "available",
     "Black strap, heart rate and step counter. Charger included.", [(30, 30, 40), (80, 80, 100)]),
    (2, "Kids' building blocks (500 pcs)", 420, "available",
     "Sealed, never opened.", [(240, 180, 30)]),
    (2, "Ring light with tripod", 550, "sold",
     "10 inch, 3 light colours, phone holder.", [(230, 230, 235)]),
    (2, "Perfume 100 ml", 300, "draft",
     "Still need to take better photos.", [(180, 120, 200)]),
    (None, "Mini rice cooker", 750, "available",
     "1 liter, good for 2 to 3 people. Bought separately, not from a parcel.", [(200, 60, 60)]),
]


def font(size):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def placeholder_photo(name, colour, number):
    """A square picture in one colour with the item name, as an uploaded file would be."""
    image = Image.new("RGB", (1200, 1200), colour)
    draw = ImageDraw.Draw(image)
    text = (255, 255, 255) if sum(colour) < 500 else (40, 40, 40)
    # A simple gift box in the middle, so it looks like a picture and not just a colour.
    draw.rounded_rectangle((420, 380, 780, 700), radius=30, outline=text, width=18)
    draw.line((600, 380, 600, 700), fill=text, width=18)
    draw.line((420, 470, 780, 470), fill=text, width=18)
    draw.text((600, 840), name, fill=text, font=font(64), anchor="mm")
    draw.text((600, 940), f"Sample photo {number}", fill=text, font=font(40), anchor="mm")
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=90)
    buffer.seek(0)
    return FileStorage(stream=buffer, filename=f"sample-{number}.jpg")


@click.command("seed")
@with_appcontext
def seed_command():
    """Add sample parcels and items with photos (only when the shop has no items yet)."""
    db = get_db()
    photo_dir = current_app.config["PHOTO_DIR"]
    items = ItemService(db, photo_dir)
    if items.list():
        click.echo("The shop already has items, so no samples were added.")
        return

    parcel_ids = {}
    for number, (name, cost, bought_on, note) in enumerate(PARCELS, start=1):
        parcel = ParcelService(db).add(
            {"name": name, "cost": cost * 100, "bought_on": bought_on, "note": note})
        parcel_ids[number] = parcel["id"]

    photos = PhotoService(db, photo_dir)
    for parcel_number, name, price, status, description, colours in ITEMS:
        item = items.add({"parcel_id": parcel_ids.get(parcel_number), "name": name,
                          "price": price * 100, "status": status, "description": description})
        for number, colour in enumerate(colours, start=1):
            photos.add(item["id"], placeholder_photo(name, colour, number))
    click.echo(f"Added {len(PARCELS)} parcels and {len(ITEMS)} items with photos.")
