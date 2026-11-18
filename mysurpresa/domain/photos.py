"""Turning an uploaded phone photo into the two small JPEG files the shop shows.

Every photo is opened and saved again by Pillow, which:
- checks it really is a picture (a renamed file is refused),
- turns it upright (phones save the rotation separately, in the EXIF data),
- drops all EXIF data, including the GPS location where the photo was taken,
- makes it smaller, so pages load fast and the free hosting space lasts.
"""

import os
import secrets

from PIL import Image, ImageOps, UnidentifiedImageError

from mysurpresa.errors import ValidationError

ALLOWED_FORMATS = ("JPEG", "PNG", "WEBP")
MAX_PIXELS = 50_000_000  # 50 megapixels; bigger is refused (also stops "image bombs")
FULL_SIZE = 1600         # longest side of the photo on the item page, in pixels
THUMB_SIZE = 600         # longest side of the photo in the shop list
JPEG_QUALITY = 82


def new_photo_name():
    """A random name like "k3J9x...": photo addresses can't be guessed or counted."""
    return secrets.token_urlsafe(12)


def photo_paths(folder, name):
    """(full photo path, thumbnail path) for a photo name."""
    return os.path.join(folder, f"{name}.jpg"), os.path.join(folder, f"{name}-thumb.jpg")


def save_photo(file, folder, name):
    """Check the uploaded file and save the full photo and the thumbnail as JPEG.

    Raises ValidationError when the file is not a JPEG, PNG or WebP picture.
    """
    try:
        with Image.open(file) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValidationError("Photo must be a JPEG, PNG or WebP picture.")
            if image.width * image.height > MAX_PIXELS:
                raise ValidationError("Photo is too large. Use a photo under 50 megapixels.")
            image = ImageOps.exif_transpose(image)
            image = flatten(image)
            full_path, thumb_path = photo_paths(folder, name)
            for path, size in ((full_path, FULL_SIZE), (thumb_path, THUMB_SIZE)):
                copy = image.copy()
                copy.thumbnail((size, size), Image.LANCZOS)
                # No exif= argument: the saved file has no EXIF data (no location).
                copy.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError):
        raise ValidationError("This file is not a picture that can be opened.")


def flatten(image):
    """JPEG has no transparency: put a see-through PNG on a white background."""
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGBA")
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.getchannel("A"))
        return background
    return image.convert("RGB")


def delete_photo_files(folder, name):
    """Remove both files of a photo (fine if they are already gone)."""
    for path in photo_paths(folder, name):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
