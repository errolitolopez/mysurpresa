"""Photos of an item: upload, make cover, delete."""

from mysurpresa.domain.photos import delete_photo_files, new_photo_name, save_photo
from mysurpresa.errors import NotFoundError, ValidationError
from mysurpresa.services.base import Service

MAX_PHOTOS_PER_ITEM = 10


class PhotoService(Service):
    def __init__(self, db, photo_dir):
        super().__init__(db)
        self.photo_dir = photo_dir

    def list(self, item_id):
        self.item(item_id)
        return self.photos.list_for_item(item_id)

    def add(self, item_id, file):
        """Save an uploaded photo for the item. Raises ValidationError for a bad file."""
        self.item(item_id)
        if file is None or not file.filename:
            raise ValidationError("Choose a photo.")
        if self.photos.count(item_id) >= MAX_PHOTOS_PER_ITEM:
            raise ValidationError(f"An item can have at most {MAX_PHOTOS_PER_ITEM} photos.")
        name = new_photo_name()
        save_photo(file.stream, self.photo_dir, name)
        try:
            photo_id = self.photos.add(item_id, name)
            self.commit()
        except Exception:
            # The row wasn't saved, so the files would be left over: remove them.
            delete_photo_files(self.photo_dir, name)
            raise
        return self.photos.get(photo_id)

    def make_cover(self, photo_id):
        """Show this photo first (in the shop list and on the item page)."""
        self.photos.make_cover(self.get(photo_id))
        self.commit()

    def delete(self, photo_id):
        photo = self.get(photo_id)
        self.photos.delete(photo_id)
        self.commit()
        delete_photo_files(self.photo_dir, photo["filename"])

    def get(self, photo_id):
        """The photo; raises NotFoundError when there is none."""
        photo = self.photos.get(photo_id)
        if photo is None:
            raise NotFoundError("Photo not found.")
        return photo

    def item(self, item_id):
        if self.items.get(item_id) is None:
            raise NotFoundError("Item not found.")
