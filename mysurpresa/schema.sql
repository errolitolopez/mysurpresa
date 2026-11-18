-- MySurpresa tables. CREATE ... IF NOT EXISTS: safe to run again, existing data is kept.

-- Key/value settings: the hashed admin password, shop name, Messenger username...
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- A mystery parcel that was bought. Only the admin sees parcels (cost is private).
CREATE TABLE IF NOT EXISTS parcels (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    cost       INTEGER,                      -- what the parcel cost, in centavos (optional)
    bought_on  TEXT,                         -- ISO day, e.g. 2026-11-18 (optional)
    note       TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One thing for sale. Prices are in centavos (125000 = ₱1,250.00), never floats.
CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    parcel_id   INTEGER REFERENCES parcels (id) ON DELETE SET NULL,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price       INTEGER NOT NULL,
    -- draft: only the admin sees it. available / reserved / sold: shown in the shop.
    status      TEXT NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'available', 'reserved', 'sold')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Photos of an item. The files are in instance/photos/<filename>.jpg (and -thumb.jpg).
-- The photo with the lowest position is the cover shown in the shop list.
CREATE TABLE IF NOT EXISTS photos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id    INTEGER NOT NULL REFERENCES items (id) ON DELETE CASCADE,
    filename   TEXT NOT NULL UNIQUE,
    position   INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_items_status ON items (status);
CREATE INDEX IF NOT EXISTS idx_items_parcel ON items (parcel_id);
CREATE INDEX IF NOT EXISTS idx_photos_item ON photos (item_id, position);
