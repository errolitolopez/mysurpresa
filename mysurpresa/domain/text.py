"""Cleaning the short texts the admin types: names, descriptions, notes."""

from datetime import date

from mysurpresa.errors import ValidationError


def clean_text(value, label, max_length, required=False):
    """Trimmed text; raises when required and empty, or longer than max_length."""
    text = str(value or "").strip()
    if required and not text:
        raise ValidationError(f"{label} is required.")
    if len(text) > max_length:
        raise ValidationError(f"{label} is too long (at most {max_length} characters).")
    return text


def clean_day(value, label="Date"):
    """An ISO day "2026-11-18", or None when empty."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ValidationError(f"{label} must be a date like 2026-11-18.")
