"""The set-password command: flask --app app set-password"""

import click
from flask.cli import with_appcontext

from mysurpresa.database import get_db
from mysurpresa.errors import ValidationError
from mysurpresa.services import AuthService


@click.command("set-password")
@with_appcontext
@click.password_option("--password", prompt="New admin password", help="At least 8 characters.")
@click.option("--temporary", is_flag=True,
              help="The admin must change it on the Settings page after the first login.")
def set_password_command(password, temporary):
    """Set or change the admin password."""
    try:
        AuthService(get_db()).set_password(password, temporary=temporary)
    except ValidationError as error:
        raise click.BadParameter(error.message)
    if temporary:
        click.echo("Temporary password saved. It must be changed after the first login.")
    else:
        click.echo("Password saved.")
