"""Admin login page, login and logout."""

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

from mysurpresa.database import get_db
from mysurpresa.services import AuthService
from mysurpresa.web.security import is_admin, json_body

bp = Blueprint("auth", __name__)


@bp.get("/login")
def login_page():
    if is_admin():
        return redirect(url_for("admin.items_page"))
    return render_template("login.html")


@bp.post("/api/login")
def api_login():
    throttle = current_app.extensions["login_throttle"]
    AuthService(get_db()).login(json_body().get("password", ""), request.remote_addr, throttle)
    session.clear()
    session.permanent = True
    session["admin"] = True
    # login.js opens Settings instead of the items when the password must be changed first.
    return jsonify(ok=True, must_change_password=AuthService(get_db()).must_change_password())


@bp.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify(ok=True)
