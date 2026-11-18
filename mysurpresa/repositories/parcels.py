"""The parcels table, with item counts and money totals for the admin."""

from mysurpresa.repositories.base import Repository

# Each parcel with: how many items it has, how many are sold, and what the sold ones made.
PARCEL_SUMMARY = """
    SELECT p.*,
           COUNT(i.id) AS item_count,
           COALESCE(SUM(i.status = 'sold'), 0) AS sold_count,
           COALESCE(SUM(CASE WHEN i.status = 'sold' THEN i.price END), 0) AS sold_total
      FROM parcels p
      LEFT JOIN items i ON i.parcel_id = p.id
"""


class ParcelRepository(Repository):
    def list(self):
        """Every parcel, newest first, with its totals."""
        return self.all(PARCEL_SUMMARY + " GROUP BY p.id ORDER BY p.id DESC")

    def get(self, parcel_id):
        """The parcel with its totals, or None."""
        return self.one(PARCEL_SUMMARY + " WHERE p.id = ? GROUP BY p.id", (parcel_id,))

    def add(self, name, cost, bought_on, note):
        cursor = self.execute(
            "INSERT INTO parcels (name, cost, bought_on, note) VALUES (?, ?, ?, ?)",
            (name, cost, bought_on, note),
        )
        return cursor.lastrowid

    def update(self, parcel_id, name, cost, bought_on, note):
        self.execute(
            "UPDATE parcels SET name = ?, cost = ?, bought_on = ?, note = ? WHERE id = ?",
            (name, cost, bought_on, note, parcel_id),
        )

    def delete(self, parcel_id):
        """Delete the parcel. Its items stay, without a parcel (ON DELETE SET NULL)."""
        self.execute("DELETE FROM parcels WHERE id = ?", (parcel_id,))
