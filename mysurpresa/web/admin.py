"""Admin pages and the admin JSON API: items, photos, parcels and shop settings."""

from flask import Blueprint, abort, current_app, jsonify, render_template, request

from mysurpresa.database import get_db
from mysurpresa.errors import NotFoundError, ValidationError
from mysurpresa.services import AuthService, ItemService, ParcelService, PhotoService, ShopService
from mysurpresa.web.presenters import item_json, parcel_json, photo_json
from mysurpresa.web.security import admin_api, admin_page, json_body

bp = Blueprint("admin", __name__)


def items_service():
    return ItemService(get_db(), current_app.config["PHOTO_DIR"])


def photos_service():
    return PhotoService(get_db(), current_app.config["PHOTO_DIR"])


# --- pages ---

@bp.get("/admin")
@admin_page
def items_page():
    return render_template("admin_items.html")


@bp.get("/admin/items/<int:item_id>")
@admin_page
def item_page(item_id):
    try:
        item = items_service().get(item_id)
    except NotFoundError:
        abort(404)
    return render_template("admin_item.html", item=item)


@bp.get("/admin/settings")
@admin_page
def settings_page():
    return render_template("admin_settings.html",
                           must_change_password=AuthService(get_db()).must_change_password())


# --- items ---

@bp.get("/api/items")
@admin_api
def api_items():
    parcel_id = request.args.get("parcel_id", type=int)
    service = items_service()
    items = service.list(request.args.get("status") or None, parcel_id)
    return jsonify(items=[item_json(item) for item in items], counts=service.counts())


@bp.post("/api/items")
@admin_api
def api_add_item():
    return jsonify(item=item_json(items_service().add(json_body()))), 201


@bp.get("/api/items/<int:item_id>")
@admin_api
def api_item(item_id):
    return jsonify(item=item_json(items_service().get(item_id)))


@bp.put("/api/items/<int:item_id>")
@admin_api
def api_update_item(item_id):
    return jsonify(item=item_json(items_service().update(item_id, json_body())))


@bp.post("/api/items/<int:item_id>/status")
@admin_api
def api_item_status(item_id):
    item = items_service().set_status(item_id, json_body().get("status"))
    return jsonify(item=item_json(item))


@bp.delete("/api/items/<int:item_id>")
@admin_api
def api_delete_item(item_id):
    items_service().delete(item_id)
    return jsonify(ok=True)


# --- photos ---

@bp.get("/api/items/<int:item_id>/photos")
@admin_api
def api_photos(item_id):
    return jsonify(photos=[photo_json(photo) for photo in photos_service().list(item_id)])


@bp.post("/api/items/<int:item_id>/photos")
@admin_api
def api_add_photo(item_id):
    photo = photos_service().add(item_id, request.files.get("photo"))
    return jsonify(photo=photo_json(photo)), 201


@bp.post("/api/photos/<int:photo_id>/cover")
@admin_api
def api_photo_cover(photo_id):
    photos_service().make_cover(photo_id)
    return jsonify(ok=True)


@bp.delete("/api/photos/<int:photo_id>")
@admin_api
def api_delete_photo(photo_id):
    photos_service().delete(photo_id)
    return jsonify(ok=True)


# --- parcels ---

@bp.get("/api/parcels")
@admin_api
def api_parcels():
    return jsonify(parcels=[parcel_json(parcel) for parcel in ParcelService(get_db()).list()])


@bp.post("/api/parcels")
@admin_api
def api_add_parcel():
    return jsonify(parcel=parcel_json(ParcelService(get_db()).add(json_body()))), 201


@bp.put("/api/parcels/<int:parcel_id>")
@admin_api
def api_update_parcel(parcel_id):
    return jsonify(parcel=parcel_json(ParcelService(get_db()).update(parcel_id, json_body())))


@bp.delete("/api/parcels/<int:parcel_id>")
@admin_api
def api_delete_parcel(parcel_id):
    ParcelService(get_db()).delete(parcel_id)
    return jsonify(ok=True)


# --- settings ---

@bp.get("/api/settings")
@admin_api
def api_settings():
    return jsonify(settings=ShopService(get_db()).get())


@bp.put("/api/settings")
@admin_api
def api_save_settings():
    return jsonify(settings=ShopService(get_db()).save(json_body()))


@bp.post("/api/password")
@admin_api
def api_change_password():
    data = json_body()
    if data.get("new_password") != data.get("confirm_password"):
        raise ValidationError("The new passwords don't match.")
    AuthService(get_db()).change_password(data.get("current_password"), data.get("new_password"))
    return jsonify(ok=True)
