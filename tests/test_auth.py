"""Admin login, logout, lockout, password rules and page protection."""

from conftest import PASSWORD, error


def test_admin_pages_send_shoppers_to_login(anonymous):
    for path in ("/admin", "/admin/settings"):
        response = anonymous.get(path)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/login")


def test_admin_api_answers_401_to_shoppers(anonymous):
    assert anonymous.get("/api/items").status_code == 401
    assert anonymous.post("/api/items", json={"name": "x", "price": 1}).status_code == 401


def test_login_and_logout(anonymous):
    assert anonymous.post("/api/login", json={"password": PASSWORD}).status_code == 200
    assert anonymous.get("/api/items").status_code == 200
    assert anonymous.get("/login").headers["Location"].endswith("/admin")
    anonymous.post("/api/logout")
    assert anonymous.get("/api/items").status_code == 401


def test_wrong_password(anonymous):
    response = anonymous.post("/api/login", json={"password": "nope-nope"})
    assert response.status_code == 401
    assert error(response) == "Wrong password."


def test_five_wrong_passwords_lock_the_device(anonymous):
    for _ in range(5):
        anonymous.post("/api/login", json={"password": "nope-nope"})
    response = anonymous.post("/api/login", json={"password": PASSWORD})
    assert response.status_code == 429


def test_changes_need_the_page_header(anonymous):
    """Another website can't post to the admin API from the admin's browser (CSRF)."""
    anonymous.post("/api/login", json={"password": PASSWORD})
    response = anonymous.post("/api/items", json={"name": "Bag", "price": 100})
    assert response.status_code == 400
    assert anonymous.post("/api/items", json={"name": "Bag", "price": 100},
                          headers={"X-Requested-With": "fetch"}).status_code == 201


def test_change_password(client, anonymous):
    response = client.post("/api/password", json={
        "current_password": PASSWORD, "new_password": "new-password-1",
        "confirm_password": "new-password-1"})
    assert response.status_code == 200
    assert anonymous.post("/api/login", json={"password": "new-password-1"}).status_code == 200


def test_change_password_checks_current_and_length(client):
    response = client.post("/api/password", json={
        "current_password": "wrong", "new_password": "new-password-1",
        "confirm_password": "new-password-1"})
    assert error(response) == "Current password is wrong."
    response = client.post("/api/password", json={
        "current_password": PASSWORD, "new_password": "short", "confirm_password": "short"})
    assert error(response) == "Password must be at least 8 characters."
    response = client.post("/api/password", json={
        "current_password": PASSWORD, "new_password": "new-password-1",
        "confirm_password": "other-password"})
    assert error(response) == "The new passwords don't match."
