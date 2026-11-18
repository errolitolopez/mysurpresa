"""Admin login with the password, and setting the password."""

import time

from werkzeug.security import check_password_hash, generate_password_hash

from mysurpresa.database import MUST_CHANGE_KEY, PASSWORD_KEY
from mysurpresa.domain.password import MIN_PASSWORD_LENGTH, is_valid_password
from mysurpresa.errors import (
    ServiceUnavailableError, TooManyRequestsError, UnauthorizedError, ValidationError,
)
from mysurpresa.services.base import Service

# MUST_CHANGE_KEY is "1" while the password is a temporary one: the default "admin" of a new database,
# or one set with: flask --app app set-password --temporary. The admin then has to change it on the
# Settings page before using the other admin pages.


class LoginThrottle:
    """After too many wrong passwords, block that device for a while so it can't be guessed."""

    MAX_ATTEMPTS = 5
    LOCK_SECONDS = 15 * 60

    def __init__(self):
        self.failed = {}  # ip address -> {"count": wrong tries, "locked_until": timestamp}

    def check(self, key):
        record = self.failed.get(key, {"count": 0, "locked_until": 0})
        wait = int(record["locked_until"] - time.time())
        if wait > 0:
            raise TooManyRequestsError(
                f"Too many wrong passwords. Try again in {wait // 60 + 1} min.")

    def wrong(self, key):
        record = self.failed.get(key, {"count": 0, "locked_until": 0})
        record["count"] += 1
        if record["count"] >= self.MAX_ATTEMPTS:
            record = {"count": 0, "locked_until": time.time() + self.LOCK_SECONDS}
        self.failed[key] = record

    def passed(self, key):
        self.failed.pop(key, None)

    def reset(self):
        self.failed.clear()


class AuthService(Service):
    def login(self, password, ip, throttle):
        """Check the password. Raises an error when it is wrong, locked out or not set."""
        throttle.check(ip)
        password_hash = self.settings.get(PASSWORD_KEY)
        if password_hash is None:
            raise ServiceUnavailableError(
                "No admin password set yet. Run: flask --app app init-db")
        if not check_password_hash(password_hash, str(password or "")):
            throttle.wrong(ip)
            raise UnauthorizedError("Wrong password.")
        throttle.passed(ip)

    def has_password(self):
        return self.settings.get(PASSWORD_KEY) is not None

    def set_password(self, password, temporary=False):
        """Save the admin password. Only the hash is saved, never the password itself.
        temporary=True: the admin must change it after logging in."""
        if not is_valid_password(password):
            raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        self.settings.set(PASSWORD_KEY, generate_password_hash(password))
        self.settings.set(MUST_CHANGE_KEY, "1" if temporary else "0")
        self.commit()

    def must_change_password(self):
        """True while the password is a temporary one that has not been changed yet."""
        return self.settings.get(MUST_CHANGE_KEY) == "1"

    def change_password(self, current, new):
        """Change the password from the settings page: the current one must be right."""
        if not check_password_hash(self.settings.get(PASSWORD_KEY) or "", str(current or "")):
            raise ValidationError("Current password is wrong.")
        if str(new or "") == str(current or ""):
            raise ValidationError("The new password must be different from the current one.")
        self.set_password(new)
