"""MySurpresa: a small online shop for the items found in mystery parcels.

Shoppers only look (no accounts): they browse the items and message the seller on Messenger.
Only the admin logs in, to add items, photos and prices.

Layers (each only uses the ones below it):
  web/           Flask blueprints: shop pages, admin pages and the admin JSON API
  services/      use cases (one class per area), commit when the work is done
  repositories/  all SQL, one class per table
  domain/        rules with no Flask or SQL: cleaning input, prices, photos
"""

import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from mysurpresa import cli, config, database, seed
from mysurpresa.domain.money import peso
from mysurpresa.errors import register_error_handlers
from mysurpresa.services import LoginThrottle
from mysurpresa.web import BLUEPRINTS


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    config.configure(app, test_config)

    # Online (PythonAnywhere), the app sits behind a proxy that handles HTTPS. ProxyFix lets Flask
    # see the real "https://" (share links and Facebook previews use the right address) and the
    # visitor's own address (the wrong-password lockout is per visitor, not for everyone behind the
    # proxy). Only behind a proxy: without one these headers could be faked. Like myguro's
    # MYGURO_TRUST_PROXY, it is turned on in the WSGI file (README).
    if os.environ.get("MYSURPRESA_TRUST_PROXY") == "1":
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    database.init_app(app)
    app.cli.add_command(cli.set_password_command)
    app.cli.add_command(seed.seed_command)
    app.extensions["login_throttle"] = LoginThrottle()

    register_error_handlers(app)
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    # {{ item.price|peso }} -> "₱1,250" in templates
    app.add_template_filter(peso, "peso")

    @app.after_request
    def security_headers(response):
        """Small safety headers: no guessing file types, no showing the site inside other sites."""
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    return app
