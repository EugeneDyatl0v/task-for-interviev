import click

from src.management.delete.conf_codes import delete_conf_codes


@click.group()
def cli():
    pass


cli.add_command(delete_conf_codes)
