"""The Flask side: one blueprint per area, kept thin. A route reads the request, calls a service,
and returns a page or JSON; errors from services become JSON answers (mysurpresa.errors)."""

from mysurpresa.web import admin, auth, shop

BLUEPRINTS = [shop.bp, auth.bp, admin.bp]
