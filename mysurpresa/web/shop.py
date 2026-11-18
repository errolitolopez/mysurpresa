"""The public shop: the item list, an item's page, and the photo files. No login needed."""

import re

from flask import Blueprint, abort, current_app, render_template, request, send_from_directory

from mysurpresa.database import get_db
from mysurpresa.errors import NotFoundError
from mysurpresa.services import ItemService, PhotoService, ShopService
from mysurpresa.web.security import is_admin

bp = Blueprint("shop", __name__)

# Photo files are named by domain/photos.py: random letters, then ".jpg" or "-thumb.jpg".
PHOTO_FILENAME = re.compile(r"^[A-Za-z0-9_-]+\.jpg$")
PHOTO_CACHE_SECONDS = 365 * 24 * 60 * 60  # a photo's file never changes, so cache it long


def items_service():
    return ItemService(get_db(), current_app.config["PHOTO_DIR"])


@bp.get("/")
def index():
    show_all = request.args.get("show") != "available"
    items = items_service().shop_list()
    if not show_all:
        items = [item for item in items if item["status"] == "available"]
    return render_template("shop.html", shop=ShopService(get_db()).get(), items=items,
                           show_all=show_all)


@bp.get("/item/<int:item_id>")
def item_page(item_id):
    try:
        item = items_service().shop_get(item_id, is_admin=is_admin())
    except NotFoundError:
        abort(404)
    photos = PhotoService(get_db(), current_app.config["PHOTO_DIR"]).list(item_id)
    return render_template("item.html", shop=ShopService(get_db()).get(), item=item,
                           photos=photos)


@bp.get("/photos/<filename>")
def photo(filename):
    if not PHOTO_FILENAME.match(filename):
        abort(404)
    return send_from_directory(current_app.config["PHOTO_DIR"], filename,
                               max_age=PHOTO_CACHE_SECONDS)


@bp.app_errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return {"error": "Not found."}, 404
    return render_template("not_found.html", shop=ShopService(get_db()).get()), 404
