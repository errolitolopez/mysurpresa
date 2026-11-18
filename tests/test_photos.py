"""Photo upload: resized, location data removed, cover order, limits, and files removed."""

import io
import os

from PIL import Image

from conftest import PHOTO_DIR, add_item, error, image_file, upload_photo


def saved_files():
    return sorted(os.listdir(PHOTO_DIR))


def test_upload_makes_small_jpegs_without_exif(client):
    item = add_item(client)
    exif = Image.Exif()
    exif[0x8825] = {2: (14.0, 35.0, 0.0)}  # GPS info: where the photo was taken
    response = upload_photo(client, item["id"], image_file(size=(4000, 3000), exif=exif))
    assert response.status_code == 201, response.get_json()
    photo = response.get_json()["photo"]

    full = client.get(photo["url"])
    thumb = client.get(photo["thumb_url"])
    assert full.status_code == 200 and thumb.status_code == 200
    with Image.open(io.BytesIO(full.data)) as image:
        assert image.format == "JPEG"
        assert max(image.size) == 1600
        assert len(image.getexif()) == 0
    with Image.open(io.BytesIO(thumb.data)) as image:
        assert max(image.size) == 600


def test_png_with_transparency_is_accepted(client):
    item = add_item(client)
    buffer = io.BytesIO()
    Image.new("RGBA", (100, 100), (0, 0, 0, 0)).save(buffer, "PNG")
    buffer.seek(0)
    assert upload_photo(client, item["id"], (buffer, "x.png")).status_code == 201


def test_not_a_picture_is_refused(client):
    item = add_item(client)
    response = upload_photo(client, item["id"], (io.BytesIO(b"<script>hi</script>"), "evil.jpg"))
    assert response.status_code == 400
    assert error(response) == "This file is not a picture that can be opened."
    gif = io.BytesIO()
    Image.new("RGB", (10, 10)).save(gif, "GIF")
    gif.seek(0)
    assert "JPEG, PNG or WebP" in error(upload_photo(client, item["id"], (gif, "a.gif")))
    assert saved_files() == []


def test_first_photo_is_the_cover_and_can_change(client):
    item = add_item(client)
    first = upload_photo(client, item["id"]).get_json()["photo"]
    second = upload_photo(client, item["id"]).get_json()["photo"]
    assert client.get(f"/api/items/{item['id']}").get_json()["item"]["thumb_url"] == first["thumb_url"]

    client.post(f"/api/photos/{second['id']}/cover")
    photos = client.get(f"/api/items/{item['id']}/photos").get_json()["photos"]
    assert [photo["id"] for photo in photos] == [second["id"], first["id"]]


def test_at_most_ten_photos(client):
    item = add_item(client)
    for _ in range(10):
        assert upload_photo(client, item["id"], image_file(size=(50, 50))).status_code == 201
    response = upload_photo(client, item["id"], image_file(size=(50, 50)))
    assert error(response) == "An item can have at most 10 photos."


def test_deleting_photo_or_item_removes_the_files(client):
    item = add_item(client)
    photo = upload_photo(client, item["id"]).get_json()["photo"]
    upload_photo(client, item["id"])
    assert len(saved_files()) == 4  # two photos, each full + thumbnail

    client.delete(f"/api/photos/{photo['id']}")
    assert len(saved_files()) == 2
    client.delete(f"/api/items/{item['id']}")
    assert saved_files() == []


def test_photo_route_only_serves_photo_names(anonymous):
    assert anonymous.get("/photos/..%2Fsecret_key").status_code == 404
    assert anonymous.get("/photos/missing.jpg").status_code == 404
