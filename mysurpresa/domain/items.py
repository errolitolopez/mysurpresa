"""What an item may look like: its name, description and status."""

from mysurpresa.domain.text import clean_text
from mysurpresa.errors import ValidationError

MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 2000

# draft: only the admin sees it. The others are shown in the shop.
STATUSES = ("draft", "available", "reserved", "sold")
PUBLIC_STATUSES = ("available", "reserved", "sold")


def clean_item_name(value):
    return clean_text(value, "Name", MAX_NAME_LENGTH, required=True)


def clean_description(value):
    return clean_text(value, "Description", MAX_DESCRIPTION_LENGTH)


def clean_status(value):
    status = str(value or "").strip().lower()
    if status not in STATUSES:
        raise ValidationError("Status must be draft, available, reserved or sold.")
    return status
