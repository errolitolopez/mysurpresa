"""App settings that aren't business rules: where things are stored, sessions and upload size."""

import os
import secrets
from datetime import timedelta

# One photo straight from a phone camera is usually 2 to 8 MB. Photos are uploaded one per
# request and made smaller on the server, so this only limits a single photo.
MAX_UPLOAD_MB = 20


def configure(app, test_config=None):
    """Set the database path, photo folder, secret key and cookie settings on the Flask app."""
    # The instance/ folder holds private files (database, secret key, photos). It is not in git.
    os.makedirs(app.instance_path, exist_ok=True)
    # MYSURPRESA_DATABASE and MYSURPRESA_PHOTOS let the tests use throwaway copies.
    app.config["DATABASE"] = os.environ.get(
        "MYSURPRESA_DATABASE", os.path.join(app.instance_path, "mysurpresa.db")
    )
    app.config["PHOTO_DIR"] = os.environ.get(
        "MYSURPRESA_PHOTOS", os.path.join(app.instance_path, "photos")
    )
    os.makedirs(app.config["PHOTO_DIR"], exist_ok=True)

    # Stay logged in for 30 days so the password isn't asked every time.
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    # Online the site is HTTPS, so the login cookie is only ever sent over HTTPS.
    # Set MYSURPRESA_HTTPS=1 there (see README). Not on this computer: plain http:// would
    # then never get the cookie, and logging in would fail.
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("MYSURPRESA_HTTPS") == "1"
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
    app.secret_key = load_secret_key(app.instance_path)
    if test_config:
        app.config.update(test_config)


def load_secret_key(instance_path):
    """The secret key signs the login cookie. Create one the first time and reuse it after."""
    path = os.path.join(instance_path, "secret_key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    with open(path) as f:
        return f.read().strip()
