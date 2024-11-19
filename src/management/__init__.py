from src.management.create.superuser import create_superuser
from src.management.delete.conf_codes import delete_conf_codes

import click


@click.group()
def cli():
    pass


cli.add_command(create_superuser)
cli.add_command(delete_conf_codes)
