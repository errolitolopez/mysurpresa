"""Parcels: cost, totals of sold items, and deleting a parcel keeps its items."""

from conftest import add_item, add_parcel, error


def test_parcel_totals(client):
    parcel = add_parcel(client, cost=150000)
    add_item(client, price=100000, status="sold", parcel_id=parcel["id"])
    add_item(client, price=30000, status="sold", parcel_id=parcel["id"])
    add_item(client, price=50000, status="available", parcel_id=parcel["id"])

    [summary] = client.get("/api/parcels").get_json()["parcels"]
    assert summary["item_count"] == 3
    assert summary["sold_count"] == 2
    assert summary["sold_total"] == 130000
    assert summary["cost"] == 150000


def test_parcel_checks(client):
    assert error(client.post("/api/parcels", json={})) == "Name is required."
    assert "date" in error(client.post("/api/parcels", json={"name": "P", "bought_on": "18/11"}))
    response = client.post("/api/parcels", json={"name": "P", "cost": ""})
    assert response.get_json()["parcel"]["cost"] is None


def test_update_parcel(client):
    parcel = add_parcel(client)
    response = client.put(f"/api/parcels/{parcel['id']}", json={"name": "Parcel #2", "cost": 99})
    assert response.get_json()["parcel"]["name"] == "Parcel #2"
    assert response.get_json()["parcel"]["bought_on"] is None


def test_delete_parcel_keeps_items(client):
    parcel = add_parcel(client)
    item = add_item(client, parcel_id=parcel["id"])
    assert client.delete(f"/api/parcels/{parcel['id']}").status_code == 200
    assert client.get(f"/api/items/{item['id']}").get_json()["item"]["parcel_id"] is None
