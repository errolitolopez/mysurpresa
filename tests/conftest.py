"""Shared test setup: a throwaway database and photo folder, emptied before each test.

Run with: .venv/bin/pytest
"""

import io
import os
import shutil
import sqlite3
import tempfile

import pytest
from PIL import Image

# The app reads these paths when it is imported.
_TEST_DIR = tempfile.mkdtemp(prefix="mysurpresa-tests-")
os.environ["MYSURPRESA_DATABASE"] = os.path.join(_TEST_DIR, "test.db")
os.environ["MYSURPRESA_PHOTOS"] = os.path.join(_TEST_DIR, "photos")

from app import app as flask_app  # noqa: E402  (must come after setting the paths)

PASSWORD = "test-password"
PHOTO_DIR = os.environ["MYSURPRESA_PHOTOS"]
HEADERS = {"X-Requested-With": "fetch"}


def reset_database():
    """Empty every table and the photo folder, then create the tables and the password again."""
    connection = sqlite3.connect(os.environ["MYSURPRESA_DATABASE"])
    tables = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")]
    connection.execute("PRAGMA foreign_keys = OFF")
    for table in tables:
        connection.execute(f"DELETE FROM {table}")
    connection.commit()
    connection.close()
    shutil.rmtree(PHOTO_DIR, ignore_errors=True)
    os.makedirs(PHOTO_DIR)
    runner = flask_app.test_cli_runner()
    assert runner.invoke(args=["init-db"]).exit_code == 0
    assert runner.invoke(args=["set-password", "--password", PASSWORD]).exit_code == 0


@pytest.fixture(autouse=True)
def fresh_database():
    reset_database()
    flask_app.extensions["login_throttle"].reset()
    yield


@pytest.fixture
def anonymous():
    """A test client that is not logged in (a shopper)."""
    return flask_app.test_client()


@pytest.fixture
def client():
    """A test client logged in as the admin. Sends the X-Requested-With header like the pages."""
    test_client = flask_app.test_client()
    response = test_client.post("/api/login", json={"password": PASSWORD})
    assert response.status_code == 200, response.get_json()
    test_client.environ_base["HTTP_X_REQUESTED_WITH"] = "fetch"
    return test_client


def add_parcel(client, name="Parcel #1", cost=150000, bought_on="2026-11-18"):
    response = client.post("/api/parcels", json={"name": name, "cost": cost, "bought_on": bought_on})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["parcel"]


def add_item(client, name="Nike shoes", price=125000, status="available", parcel_id=None,
             description=""):
    response = client.post("/api/items", json={
        "name": name, "price": price, "status": status, "parcel_id": parcel_id,
        "description": description,
    })
    assert response.status_code == 201, response.get_json()
    return response.get_json()["item"]


def image_file(size=(2400, 1800), image_format="JPEG", exif=None, name="photo.jpg"):
    """An in-memory picture, like one picked from a phone."""
    buffer = io.BytesIO()
    image = Image.new("RGB", size, (200, 50, 120))
    if exif is not None:
        image.save(buffer, image_format, exif=exif)
    else:
        image.save(buffer, image_format)
    buffer.seek(0)
    return (buffer, name)


def upload_photo(client, item_id, file=None):
    return client.post(f"/api/items/{item_id}/photos", data={"photo": file or image_file()},
                       content_type="multipart/form-data")


def error(response):
    return response.get_json()["error"]
