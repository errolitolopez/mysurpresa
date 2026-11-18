"""Shape database rows into JSON for the admin pages (photo names become photo addresses)."""

from flask import url_for


def photo_url(name, thumb=False):
    """photo_url("k3J9x") -> "/photos/k3J9x.jpg"; with thumb=True -> "/photos/k3J9x-thumb.jpg"."""
    if not name:
        return None
    return url_for("shop.photo", filename=f"{name}-thumb.jpg" if thumb else f"{name}.jpg")


def item_json(item):
    return {
        "id": item["id"],
        "parcel_id": item["parcel_id"],
        "parcel_name": item["parcel_name"],
        "name": item["name"],
        "description": item["description"],
        "price": item["price"],
        "status": item["status"],
        "photo_count": item["photo_count"],
        "thumb_url": photo_url(item["cover"], thumb=True),
        "shop_url": url_for("shop.item_page", item_id=item["id"]),
        "created_at": item["created_at"],
    }


def parcel_json(parcel):
    return {
        "id": parcel["id"],
        "name": parcel["name"],
        "cost": parcel["cost"],
        "bought_on": parcel["bought_on"],
        "note": parcel["note"],
        "item_count": parcel["item_count"],
        "sold_count": parcel["sold_count"],
        "sold_total": parcel["sold_total"],
    }


def photo_json(photo):
    return {
        "id": photo["id"],
        "url": photo_url(photo["filename"]),
        "thumb_url": photo_url(photo["filename"], thumb=True),
    }
