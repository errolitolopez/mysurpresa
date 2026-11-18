"""The items table. Lists come with the cover photo (the photo with the lowest position)."""

from mysurpresa.repositories.base import Repository

# An item plus its cover photo name, photo count and parcel name.
ITEM_WITH_COVER = """
    SELECT i.*,
           (SELECT filename FROM photos ph WHERE ph.item_id = i.id
             ORDER BY ph.position, ph.id LIMIT 1) AS cover,
           (SELECT COUNT(*) FROM photos ph WHERE ph.item_id = i.id) AS photo_count,
           p.name AS parcel_name
      FROM items i
      LEFT JOIN parcels p ON p.id = i.parcel_id
"""

# Drafts first (the admin still has to finish them; the shop never shows them), then available,
# reserved and sold; newest first inside each.
SHOP_ORDER = """
    ORDER BY CASE i.status WHEN 'draft' THEN 0 WHEN 'available' THEN 1 WHEN 'reserved' THEN 2
             ELSE 3 END, i.id DESC
"""


class ItemRepository(Repository):
    def list(self, statuses, parcel_id=None):
        """Items with one of the given statuses (optionally only one parcel's), shop order."""
        marks = ", ".join("?" for _ in statuses)
        sql = ITEM_WITH_COVER + f" WHERE i.status IN ({marks})"
        params = list(statuses)
        if parcel_id is not None:
            sql += " AND i.parcel_id = ?"
            params.append(parcel_id)
        return self.all(sql + SHOP_ORDER, params)

    def get(self, item_id):
        """The item with its cover, or None."""
        return self.one(ITEM_WITH_COVER + " WHERE i.id = ?", (item_id,))

    def add(self, parcel_id, name, description, price, status):
        cursor = self.execute(
            "INSERT INTO items (parcel_id, name, description, price, status) VALUES (?, ?, ?, ?, ?)",
            (parcel_id, name, description, price, status),
        )
        return cursor.lastrowid

    def update(self, item_id, parcel_id, name, description, price, status):
        self.execute(
            "UPDATE items SET parcel_id = ?, name = ?, description = ?, price = ?, status = ?, "
            "updated_at = datetime('now') WHERE id = ?",
            (parcel_id, name, description, price, status, item_id),
        )

    def delete(self, item_id):
        """Delete the item. Its photo rows go too (ON DELETE CASCADE); the files are removed
        by the service."""
        self.execute("DELETE FROM items WHERE id = ?", (item_id,))

    def count_by_status(self):
        """{"available": 3, "sold": 5, ...} for the admin page."""
        rows = self.all("SELECT status, COUNT(*) AS count FROM items GROUP BY status")
        return {row["status"]: row["count"] for row in rows}
