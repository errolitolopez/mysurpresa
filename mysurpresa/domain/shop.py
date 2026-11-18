"""The shop's own settings: its name, tagline, and where buyers send a message."""

import re

from mysurpresa.domain.text import clean_text
from mysurpresa.errors import ValidationError

MAX_SHOP_NAME_LENGTH = 60
MAX_TAGLINE_LENGTH = 140
MAX_URL_LENGTH = 200

DEFAULTS = {
    "shop_name": "MySurpresa",
    "tagline": "MySurpresa na abot kaya",
    "messenger_username": "",
    "facebook_url": "",
}

# A Facebook / Messenger username: letters, numbers and dots (at least 5 characters), or the
# number of a profile. Only these characters are allowed so it is safe inside a link.
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9.]{5,50}$")


def clean_messenger_username(value):
    """ "https://m.me/my.page" or "m.me/my.page" or "my.page" -> "my.page"; "" when empty."""
    text = str(value or "").strip().rstrip("/")
    text = re.sub(r"^(https?://)?(www\.)?(m\.me|facebook\.com|fb\.com|messenger\.com/t)/", "", text)
    if not text:
        return ""
    if not USERNAME_PATTERN.match(text):
        raise ValidationError("Messenger username can only have letters, numbers and dots, "
                              "like the part after m.me/ in your Messenger link.")
    return text


def clean_facebook_url(value):
    """A link to the shop's Facebook page; must be https://facebook.com/... or empty."""
    text = clean_text(value, "Facebook page link", MAX_URL_LENGTH)
    if not text:
        return ""
    if not re.match(r"^https://(www\.|m\.|web\.)?facebook\.com/\S+$", text):
        raise ValidationError("Facebook page link must start with https://facebook.com/")
    return text


def clean_shop_settings(data):
    """Check every shop setting sent by the admin. Returns the cleaned values."""
    return {
        "shop_name": clean_text(data.get("shop_name"), "Shop name", MAX_SHOP_NAME_LENGTH,
                                required=True),
        "tagline": clean_text(data.get("tagline"), "Tagline", MAX_TAGLINE_LENGTH),
        "messenger_username": clean_messenger_username(data.get("messenger_username")),
        "facebook_url": clean_facebook_url(data.get("facebook_url")),
    }
