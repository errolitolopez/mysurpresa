"""The admin password rule."""

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 200


def is_valid_password(password):
    return isinstance(password, str) and MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH
