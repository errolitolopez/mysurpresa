"""The photos table. The files themselves are handled by domain/photos.py."""

from mysurpresa.repositories.base import Repository


class PhotoRepository(Repository):
    def list_for_item(self, item_id):
        """The item's photos, cover first."""
        return self.all(
            "SELECT * FROM photos WHERE item_id = ? ORDER BY position, id", (item_id,)
        )

    def get(self, photo_id):
        """The photo, or None."""
        return self.one("SELECT * FROM photos WHERE id = ?", (photo_id,))

    def add(self, item_id, filename):
        """Add a photo at the end of the item's photos."""
        position = self.value(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM photos WHERE item_id = ?", (item_id,)
        )
        cursor = self.execute(
            "INSERT INTO photos (item_id, filename, position) VALUES (?, ?, ?)",
            (item_id, filename, position),
        )
        return cursor.lastrowid

    def make_cover(self, photo):
        """Move the photo before all other photos of its item."""
        lowest = self.value(
            "SELECT COALESCE(MIN(position), 0) FROM photos WHERE item_id = ?", (photo["item_id"],)
        )
        self.execute("UPDATE photos SET position = ? WHERE id = ?", (lowest - 1, photo["id"]))

    def delete(self, photo_id):
        self.execute("DELETE FROM photos WHERE id = ?", (photo_id,))

    def count(self, item_id):
        return self.value("SELECT COUNT(*) FROM photos WHERE item_id = ?", (item_id,))
