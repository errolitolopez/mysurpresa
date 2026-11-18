# MySurpresa

A small online shop for the items we got from mystery parcels. Shoppers browse the items and
message us on Messenger to buy. No shopper accounts, no payments on the site: only the admin
logs in, to add items, photos and prices.

Built with Python (Flask), SQLite, Pillow, vanilla JavaScript and Bootstrap 5.

## Features

**Shop (anyone, no login)**
- Item grid: photo, name, price, status (Available / Reserved / Sold). Available first, sold
  items stay visible but faded. "All" / "Available" filter
- Item page: photo carousel, price, description
- **Message to buy**: opens Messenger (`m.me/<username>`) with the item name, price and link
  already written in
- **Share** (phone share sheet: Messenger, Facebook, Viber...), **Facebook** (share dialog),
  **Copy link**
- Link previews: each item page has `og:` tags, so a shared link shows the photo, name and price
  on Facebook and Messenger

**Admin (`/admin`, one password)**
- Add an item (it starts as a hidden draft), then add up to 10 photos from the phone (camera or
  gallery). The first photo is the cover; any photo can be made the cover
- Edit name, price, status, parcel, description; delete an item with its photos
- Parcels: name, cost, date bought, note. Each parcel shows items sold, money in and profit.
  Only the admin sees parcels and costs
- Settings: shop name, tagline, Messenger username (paste the whole m.me link if you like),
  Facebook page link, change password

## Why it is low risk

| Risk | How it is handled |
|------|-------------------|
| Shoppers' personal data | None is collected: no accounts, no forms |
| Payments / fraud | No payments on the site; deals happen in Messenger |
| Admin password guessed | Only a hash is saved; 5 wrong tries lock that device out for 15 minutes |
| Another site acting as the admin (CSRF) | Changes need a header only the admin pages send, and the cookie is `SameSite=Lax` |
| Photos showing where you live | Every photo is re-saved without EXIF data (GPS location removed) |
| Fake or harmful uploads | Only real JPEG/PNG/WebP pictures are accepted (opened and re-saved by Pillow), max 50 megapixels |
| Running out of space | Photos are shrunk to 1600 px (about 150–300 KB) plus a 600 px thumbnail |
| Names with HTML | Everything is escaped (Jinja on the shop, `textContent` in the admin) |

## Getting started

Requires Python 3.10+.

```bash
./run.sh          # run on this computer: http://127.0.0.1:5000
./run.sh phone    # also open it from a phone on the same Wi-Fi
```

The first run creates the virtual environment, installs Flask and Pillow, creates the database
and asks for the admin password (at least 8 characters). Then open `/login`.

Try it with sample items: `.venv/bin/flask --app app seed` (only on an empty shop).

Change the password later on the Settings page, or with `.venv/bin/flask --app app set-password`.

## Files

| Path | What is there |
|------|---------------|
| `instance/mysurpresa.db` | The database (not in git) |
| `instance/photos/` | Item photos, `<random>.jpg` and `<random>-thumb.jpg` (not in git) |
| `instance/secret_key` | Signs the login cookie (not in git) |
| `mysurpresa/` | The app: `web/` → `services/` → `repositories/` → `domain/` |

Back up `instance/` to keep the items and photos.

## Put it online (PythonAnywhere)

1. Upload the code: `git clone <repo> ~/mysurpresa` in a Bash console.
2. Install: `cd ~/mysurpresa && pip3.12 install --user -r requirements.txt`
   (use the same Python version as the web app).
3. `flask --app app init-db` and `flask --app app set-password`.
4. Web tab → Add a new web app → Manual configuration → same Python version. In the WSGI file:

   ```python
   import os, sys
   os.environ["MYSURPRESA_HTTPS"] = "1"   # login cookie only over https
   sys.path.insert(0, "/home/<username>/mysurpresa")
   from app import app as application
   ```

5. Web tab → turn on **Force HTTPS**, then Reload.

Note: a free PythonAnywhere account has only **one** web app.

## Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```
