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
- **Message us**: opens Messenger (`m.me/<username>`) with the item name, price and link
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

The first run creates the virtual environment and installs Flask and Pillow. The database is
created when the app starts. Log in at `/login` with the password **`admin`**: the app then opens
Settings and asks for your own password (at least 8 characters) before anything else.

Try it with 3 sample items with real photos: `.venv/bin/flask --app app seed` (only on an empty shop;
photo credits in `mysurpresa/sample_photos/CREDITS.md`).

Change the password later on the Settings page. Locked out? `.venv/bin/flask --app app set-password --temporary`
sets a new one that must be changed again after logging in.

## Files

| Path | What is there |
|------|---------------|
| `instance/mysurpresa.db` | The database (not in git) |
| `instance/photos/` | Item photos, `<random>.jpg` and `<random>-thumb.jpg` (not in git) |
| `instance/secret_key` | Signs the login cookie (not in git) |
| `mysurpresa/` | The app: `web/` → `services/` → `repositories/` → `domain/` |

Back up `instance/` to keep the items and photos.

## Put it online (PythonAnywhere)

Live at https://mysurpresa.pythonanywhere.com (PythonAnywhere user `mysurpresa`). Full steps, updates
and pitfalls: `docs/mysurpresa/hosting.md` in the workspace (same setup as myguro).

Short version: clone into `~/mysurpresa`, make the venv `~/mysurpresa-venv`, Web tab → Manual
configuration, and in the WSGI file:

```python
import os
import sys
sys.path.insert(0, "/home/mysurpresa/mysurpresa")
os.environ["MYSURPRESA_TRUST_PROXY"] = "1"  # behind PythonAnywhere's proxy: real https and visitor address
os.environ["MYSURPRESA_HTTPS"] = "1"        # the login cookie only over https
from mysurpresa import create_app
application = create_app()
```

Reload, then log in with `admin` and choose your own password.

## Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```
