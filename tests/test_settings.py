"""Shop settings: defaults, cleaning a pasted Messenger link, and checks."""

from conftest import error


def save(client, **changes):
    data = {"shop_name": "MySurpresa", "tagline": "", "messenger_username": "",
            "facebook_url": ""}
    data.update(changes)
    return client.put("/api/settings", json=data)


def test_defaults(client):
    settings = client.get("/api/settings").get_json()["settings"]
    assert settings["shop_name"] == "MySurpresa"
    assert settings["messenger_username"] == ""


def test_pasted_messenger_link_becomes_username(client):
    for pasted in ("https://m.me/my.shop.ph", "m.me/my.shop.ph/", "my.shop.ph",
                   "https://www.facebook.com/my.shop.ph"):
        response = save(client, messenger_username=pasted)
        assert response.get_json()["settings"]["messenger_username"] == "my.shop.ph", pasted


def test_bad_messenger_username(client):
    assert "letters, numbers and dots" in error(save(client, messenger_username='x"><script>'))


def test_facebook_link_must_be_facebook(client):
    assert "https://facebook.com/" in error(save(client, facebook_url="javascript:alert(1)"))
    response = save(client, facebook_url="https://www.facebook.com/my.shop.ph")
    assert response.status_code == 200


def test_shop_name_shows_in_shop(client, anonymous):
    save(client, shop_name="Surpresa ni Ate", tagline="Ukay finds")
    page = anonymous.get("/").get_data(as_text=True)
    assert "Surpresa ni Ate" in page and "Ukay finds" in page
