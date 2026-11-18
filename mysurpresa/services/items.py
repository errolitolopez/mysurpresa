"""Items for sale: the admin adds, changes and deletes them; the shop lists the public ones."""

from mysurpresa.domain.items import (
    PUBLIC_STATUSES, STATUSES, clean_description, clean_item_name, clean_status,
)
from mysurpresa.domain.money import clean_price
from mysurpresa.domain.photos import delete_photo_files
from mysurpresa.errors import NotFoundError, ValidationError
from mysurpresa.services.base import Service


class ItemService(Service):
    def __init__(self, db, photo_dir):
        super().__init__(db)
        self.photo_dir = photo_dir  # where the photo files are, to delete them with the item

    # --- the shop (no login) ---

    def shop_list(self):
        """Items shown in the shop: available, then reserved, then sold."""
        return self.items.list(PUBLIC_STATUSES)

    def shop_get(self, item_id, is_admin=False):
        """A shop item. A draft is only shown to the admin (a preview); for anyone else it
        doesn't exist. Raises NotFoundError."""
        item = self.items.get(item_id)
        if item is None or (item["status"] == "draft" and not is_admin):
            raise NotFoundError("Item not found.")
        return item

    # --- admin ---

    def list(self, status=None, parcel_id=None):
        """All items, or only one status and/or one parcel's."""
        statuses = (clean_status(status),) if status else STATUSES
        return self.items.list(statuses, parcel_id)

    def get(self, item_id):
        """The item; raises NotFoundError when there is none."""
        item = self.items.get(item_id)
        if item is None:
            raise NotFoundError("Item not found.")
        return item

    def counts(self):
        """How many items have each status: {"draft": 1, "available": 4, ...}"""
        counts = self.items.count_by_status()
        return {status: counts.get(status, 0) for status in STATUSES}

    def add(self, data):
        item_id = self.items.add(*self.clean(data))
        self.commit()
        return self.get(item_id)

    def update(self, item_id, data):
        self.get(item_id)
        self.items.update(item_id, *self.clean(data))
        self.commit()
        return self.get(item_id)

    def set_status(self, item_id, status):
        """Quick change from the admin list, e.g. mark as sold."""
        item = self.get(item_id)
        self.items.update(item_id, item["parcel_id"], item["name"], item["description"],
                          item["price"], clean_status(status))
        self.commit()
        return self.get(item_id)

    def delete(self, item_id):
        """Delete the item and its photo files."""
        self.get(item_id)
        names = [photo["filename"] for photo in self.photos.list_for_item(item_id)]
        self.items.delete(item_id)
        self.commit()
        # Files go after the commit: if the commit had failed, the photos would still be there.
        for name in names:
            delete_photo_files(self.photo_dir, name)

    def clean(self, data):
        """(parcel_id, name, description, price, status) from the posted JSON."""
        parcel_id = data.get("parcel_id")
        if parcel_id in ("", None):
            parcel_id = None
        elif isinstance(parcel_id, bool) or not isinstance(parcel_id, int) \
                or self.parcels.get(parcel_id) is None:
            raise ValidationError("Parcel not found.")
        return (
            parcel_id,
            clean_item_name(data.get("name")),
            clean_description(data.get("description")),
            clean_price(data.get("price")),
            clean_status(data.get("status") or "draft"),
        )
