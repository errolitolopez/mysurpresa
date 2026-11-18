"""Who is logged in, and decorators that let only the admin open a page or API."""

from functools import wraps

from flask import jsonify, redirect, request, session, url_for


def is_admin():
    return session.get("admin") is True


def json_body():
    """The posted JSON object, or {} when there is none."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def must_change_password():
    """True while the admin still has the temporary password (see AuthService)."""
    from mysurpresa.database import get_db
    from mysurpresa.services import AuthService
    return AuthService(get_db()).must_change_password()


def admin_page(view):
    """For admin HTML pages: send anyone else to the login page. While the password is a
    temporary one, every admin page goes to Settings, where it is changed."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not is_admin():
            return redirect(url_for("auth.login_page"))
        if request.endpoint != "admin.settings_page" and must_change_password():
            return redirect(url_for("admin.settings_page"))
        return view(*args, **kwargs)
    return wrapper


def admin_api(view):
    """For admin API routes: answer 401 when not logged in.

    The admin's own pages send every request with the header X-Requested-With: fetch.
    Another website can't add that header to a request it makes in the admin's browser,
    so it can't change anything here (this blocks "cross-site request forgery").
    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not is_admin():
            return jsonify(error="Please log in."), 401
        if request.method != "GET" and request.headers.get("X-Requested-With") != "fetch":
            return jsonify(error="Please reload the page and try again."), 400
        return view(*args, **kwargs)
    return wrapper
