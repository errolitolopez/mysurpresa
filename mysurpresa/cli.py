"""The set-password command: flask --app app set-password"""

import click
from flask.cli import with_appcontext

from mysurpresa.database import get_db
from mysurpresa.errors import ValidationError
from mysurpresa.services import AuthService


@click.command("set-password")
@with_appcontext
@click.password_option("--password", prompt="New admin password", help="At least 8 characters.")
def set_password_command(password):
    """Set or change the admin password."""
    try:
        AuthService(get_db()).set_password(password)
    except ValidationError as error:
        raise click.BadParameter(error.message)
    click.echo("Password saved.")
