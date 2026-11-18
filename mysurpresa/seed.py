"""Three sample items with real photos (mysurpresa/sample_photos), for trying out the shop.

Run with: flask --app app seed

Only runs on an empty shop, so it never mixes sample items with real ones.
Remove them later from the admin page (delete each item and the parcel).
The photos are from Wikimedia Commons; authors and licenses are in sample_photos/CREDITS.md.
"""

import os

import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.datastructures import FileStorage

from mysurpresa.database import get_db
from mysurpresa.services import ItemService, ParcelService, PhotoService

SAMPLE_PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_photos")

PARCEL = {"name": "Mystery parcel #1", "cost": 1500_00, "bought_on": "2026-11-15",
          "note": "Sample parcel"}

# (photo file, name, price in pesos, status, description)
ITEMS = [
    ("running-shoes.jpg", "Running shoes, size 9", 1250, "available",
     "Asics Gel-Cumulus 22, navy blue. Like new, worn once.\n\n"
     "Sample photo: Petar Milošević, CC BY-SA 4.0"),
    ("headphones.jpg", "Vintage stereo headphones", 650, "reserved",
     "Elega DR 243C, made in Japan. Tested, both sides working. Some wear on the band.\n\n"
     "Sample photo: R. Henrik Nilsson, CC BY 4.0"),
    ("backpack.jpg", "Hiking backpack 50 L", 980, "available",
     "Blue and grey, many pockets, rain cover included. Good for weekend hikes."),
]


@click.command("seed")
@with_appcontext
def seed_command():
    """Add a sample parcel and three items with real photos (only when the shop has no items yet)."""
    db = get_db()
    photo_dir = current_app.config["PHOTO_DIR"]
    items = ItemService(db, photo_dir)
    if items.list():
        click.echo("The shop already has items, so no samples were added.")
        return

    parcel = ParcelService(db).add(PARCEL)
    photos = PhotoService(db, photo_dir)
    for filename, name, price, status, description in ITEMS:
        item = items.add({"parcel_id": parcel["id"], "name": name, "price": price * 100,
                          "status": status, "description": description})
        with open(os.path.join(SAMPLE_PHOTO_DIR, filename), "rb") as f:
            photos.add(item["id"], FileStorage(stream=f, filename=filename))
    click.echo(f"Added 1 parcel and {len(ITEMS)} items with photos.")
