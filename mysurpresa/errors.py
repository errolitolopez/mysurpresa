"""Errors the services raise when a request can't be done. The web layer turns them into
JSON answers like {"error": "Name is required."} with the right HTTP status."""

from flask import jsonify


class AppError(Exception):
    status = 400

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class ValidationError(AppError):
    """The request has bad or missing data (400)."""
    status = 400


class UnauthorizedError(AppError):
    """Not logged in, or the wrong password (401)."""
    status = 401


class NotFoundError(AppError):
    """It doesn't exist (404)."""
    status = 404


class TooManyRequestsError(AppError):
    """Too many wrong passwords (429)."""
    status = 429


class ServiceUnavailableError(AppError):
    """The app is not set up yet, e.g. no admin password (503)."""
    status = 503


def register_error_handlers(app):
    @app.errorhandler(413)
    def handle_too_big(error):
        megabytes = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return jsonify(error=f"The photo is too big (at most {megabytes} MB)."), 413

    @app.errorhandler(AppError)
    def handle_app_error(error):
        # Nothing of a failed request is saved: the connection closes without commit.
        return jsonify(error=error.message), error.status
