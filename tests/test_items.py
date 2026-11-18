"""Adding, changing, filtering and deleting items (admin)."""

from conftest import add_item, add_parcel, error


def test_add_item_is_a_draft_by_default(client):
    response = client.post("/api/items", json={"name": " Bag ", "price": 50000})
    item = response.get_json()["item"]
    assert response.status_code == 201
    assert item["name"] == "Bag"
    assert item["status"] == "draft"
    assert item["thumb_url"] is None


def test_item_checks(client):
    assert error(client.post("/api/items", json={"price": 100})) == "Name is required."
    assert error(client.post("/api/items", json={"name": "Bag"})) == "Price is required."
    assert "whole number" in error(client.post("/api/items", json={"name": "Bag", "price": 1.5}))
    assert "between" in error(client.post("/api/items", json={"name": "Bag", "price": -1}))
    assert "Status" in error(client.post("/api/items", json={"name": "Bag", "price": 1, "status": "gone"}))
    assert error(client.post("/api/items", json={"name": "Bag", "price": 1, "parcel_id": 99})) \
        == "Parcel not found."


def test_update_and_mark_sold(client):
    parcel = add_parcel(client)
    item = add_item(client, status="draft")
    response = client.put(f"/api/items/{item['id']}", json={
        "name": "Adidas shoes", "price": 99900, "status": "available",
        "parcel_id": parcel["id"], "description": "Size 9\nLike new"})
    updated = response.get_json()["item"]
    assert updated["name"] == "Adidas shoes"
    assert updated["parcel_name"] == "Parcel #1"
    assert updated["description"] == "Size 9\nLike new"

    response = client.post(f"/api/items/{item['id']}/status", json={"status": "sold"})
    assert response.get_json()["item"]["status"] == "sold"
    assert response.get_json()["item"]["name"] == "Adidas shoes"


def test_list_filters_and_counts(client):
    parcel = add_parcel(client)
    add_item(client, name="A", status="available", parcel_id=parcel["id"])
    add_item(client, name="B", status="sold")
    add_item(client, name="C", status="draft")

    data = client.get("/api/items").get_json()
    assert [item["name"] for item in data["items"]] == ["C", "A", "B"]
    assert data["counts"] == {"draft": 1, "available": 1, "reserved": 0, "sold": 1}
    assert [i["name"] for i in client.get("/api/items?status=sold").get_json()["items"]] == ["B"]
    assert [i["name"] for i in client.get(f"/api/items?parcel_id={parcel['id']}").get_json()["items"]] == ["A"]


def test_delete_item(client):
    item = add_item(client)
    assert client.delete(f"/api/items/{item['id']}").status_code == 200
    assert client.get(f"/api/items/{item['id']}").status_code == 404


def test_seed_adds_samples_once(client):
    from conftest import flask_app
    runner = flask_app.test_cli_runner()
    assert "Added 2 parcels and 9 items" in runner.invoke(args=["seed"]).output
    assert "already has items" in runner.invoke(args=["seed"]).output
    items = client.get("/api/items").get_json()["items"]
    assert len(items) == 9 and all(item["thumb_url"] for item in items)
