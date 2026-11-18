"""The public shop: what shoppers see, the Messenger button, and link previews."""

from conftest import add_item, upload_photo


def set_messenger(client, username="mysurpresa.shop"):
    response = client.put("/api/settings", json={
        "shop_name": "MySurpresa", "tagline": "Finds!", "messenger_username": username,
        "facebook_url": ""})
    assert response.status_code == 200, response.get_json()


def test_shop_lists_public_items_available_first(client, anonymous):
    add_item(client, name="Sold bag", status="sold")
    add_item(client, name="Secret draft", status="draft")
    add_item(client, name="Nice shoes", status="available")
    page = anonymous.get("/").get_data(as_text=True)
    assert "Nice shoes" in page and "Sold bag" in page
    assert "Secret draft" not in page
    assert page.index("Nice shoes") < page.index("Sold bag")

    available_only = anonymous.get("/?show=available").get_data(as_text=True)
    assert "Nice shoes" in available_only and "Sold bag" not in available_only


def test_draft_is_hidden_from_shoppers_but_admin_can_preview(client, anonymous):
    item = add_item(client, status="draft")
    assert anonymous.get(f"/item/{item['id']}").status_code == 404
    assert client.get(f"/item/{item['id']}").status_code == 200


def test_item_page_has_messenger_button_and_preview_tags(client, anonymous):
    set_messenger(client)
    item = add_item(client, name="Nike shoes", price=125000)
    upload_photo(client, item["id"])
    page = anonymous.get(f"/item/{item['id']}").get_data(as_text=True)
    assert "https://m.me/mysurpresa.shop?text=Hi%21" in page
    assert "Nike%20shoes" in page
    assert '<meta property="og:title" content="Nike shoes · ₱1,250">' in page
    assert 'property="og:image" content="http://localhost/photos/' in page
    assert "facebook.com/sharer/sharer.php?u=http%3A//localhost/item/" in page


def test_sold_item_has_no_message_button(client, anonymous):
    set_messenger(client)
    item = add_item(client, status="sold")
    page = anonymous.get(f"/item/{item['id']}").get_data(as_text=True)
    assert "m.me/" not in page
    assert "Sold" in page


def test_names_are_escaped(client, anonymous):
    item = add_item(client, name="<script>alert(1)</script>")
    page = anonymous.get(f"/item/{item['id']}").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page


def test_unknown_item_shows_friendly_page(anonymous):
    response = anonymous.get("/item/999")
    assert response.status_code == 404
    assert "no longer here" in response.get_data(as_text=True)


def test_item_with_photos_has_full_screen_button(client, anonymous):
    item = add_item(client)
    assert 'id="fullscreen-toggle"' not in anonymous.get(f"/item/{item['id']}").get_data(as_text=True)
    upload_photo(client, item["id"])
    page = anonymous.get(f"/item/{item['id']}").get_data(as_text=True)
    assert 'id="fullscreen-toggle"' in page and "js/item.js" in page
