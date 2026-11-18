"""The SQLite database: one connection per request, creating the tables, and the init-db command."""

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

# Like myguro: on a new database the admin password is "admin", and it must be changed at the first
# login (the app opens Settings until it is). The keys are the ones AuthService uses.
DEFAULT_ADMIN_PASSWORD = "admin"
PASSWORD_KEY = "password_hash"
MUST_CHANGE_KEY = "must_change_password"


def get_db():
    """Return the database connection for the current request (opened once per request)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # rows behave like dicts: row["name"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tables and the default admin password (safe to run again, existing data is kept)."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    create_default_password(db)
    db.commit()


def create_default_password(db):
    """Set the password to "admin" (to be changed at first login) when there is none yet."""
    if db.execute("SELECT 1 FROM settings WHERE key = ?", (PASSWORD_KEY,)).fetchone():
        return
    db.execute("INSERT INTO settings (key, value) VALUES (?, ?)",
               (PASSWORD_KEY, generate_password_hash(DEFAULT_ADMIN_PASSWORD)))
    db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, '1')", (MUST_CHANGE_KEY,))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create the tables (safe to run again, existing data is kept)."""
    init_db()
    click.echo("Database ready.")


def init_app(app):
    """Register the database helpers with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    # Make sure the tables and the default password exist before the first request, so a new
    # server (PythonAnywhere) needs no separate setup step.
    with app.app_context():
        init_db()
