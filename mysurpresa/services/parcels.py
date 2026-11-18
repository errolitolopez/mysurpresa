"""Parcels: the mystery parcels that were bought (admin only)."""

from mysurpresa.domain.money import clean_price
from mysurpresa.domain.text import clean_day, clean_text
from mysurpresa.errors import NotFoundError
from mysurpresa.services.base import Service

MAX_PARCEL_NAME_LENGTH = 80
MAX_NOTE_LENGTH = 500


def clean_parcel(data):
    """(name, cost, bought_on, note) from the posted JSON; raises ValidationError."""
    return (
        clean_text(data.get("name"), "Name", MAX_PARCEL_NAME_LENGTH, required=True),
        clean_price(data.get("cost"), "Cost", required=False),
        clean_day(data.get("bought_on"), "Date bought"),
        clean_text(data.get("note"), "Note", MAX_NOTE_LENGTH),
    )


class ParcelService(Service):
    def list(self):
        return self.parcels.list()

    def get(self, parcel_id):
        """The parcel; raises NotFoundError when there is none."""
        parcel = self.parcels.get(parcel_id)
        if parcel is None:
            raise NotFoundError("Parcel not found.")
        return parcel

    def add(self, data):
        parcel_id = self.parcels.add(*clean_parcel(data))
        self.commit()
        return self.get(parcel_id)

    def update(self, parcel_id, data):
        self.get(parcel_id)
        self.parcels.update(parcel_id, *clean_parcel(data))
        self.commit()
        return self.get(parcel_id)

    def delete(self, parcel_id):
        """Delete the parcel; its items are kept, without a parcel."""
        self.get(parcel_id)
        self.parcels.delete(parcel_id)
        self.commit()
