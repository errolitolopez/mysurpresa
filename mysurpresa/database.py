"""The SQLite database: one connection per request, creating the tables, and the init-db command."""

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


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
    """Create the tables (safe to run again, existing data is kept)."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    db.commit()


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
