"""Prices are whole centavos (int) everywhere, so there are no rounding errors."""

from mysurpresa.errors import ValidationError

MAX_PRICE = 10_000_000_00  # ₱10,000,000.00: anything bigger is surely a typo


def peso(centavos):
    """peso(125000) -> "₱1,250"; peso(12550) -> "₱125.50" (no .00 for whole pesos)."""
    if centavos is None:
        return ""
    pesos, cents = divmod(int(centavos), 100)
    return f"₱{pesos:,}" if cents == 0 else f"₱{pesos:,}.{cents:02d}"


def clean_price(value, label="Price", required=True):
    """A price in centavos from the API (an int), or None when it is optional and empty."""
    if value is None or value == "":
        if required:
            raise ValidationError(f"{label} is required.")
        return None
    # bool is a kind of int in Python; True must not become 1 centavo.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{label} must be a whole number of centavos.")
    if value < 0 or value > MAX_PRICE:
        raise ValidationError(f"{label} must be between ₱0 and {peso(MAX_PRICE)}.")
    return value
