"""What every service shares."""

from mysurpresa.repositories import (
    ItemRepository, ParcelRepository, PhotoRepository, SettingsRepository,
)


class Service:
    """A use case runs inside one service method: it checks the request, changes data through
    the repositories, and commits only when everything worked. On an error (mysurpresa.errors)
    it stops, and nothing it changed is saved."""

    def __init__(self, db):
        self.db = db
        self.items = ItemRepository(db)
        self.parcels = ParcelRepository(db)
        self.photos = PhotoRepository(db)
        self.settings = SettingsRepository(db)

    def commit(self):
        self.db.commit()
