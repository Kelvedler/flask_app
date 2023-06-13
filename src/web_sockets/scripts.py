import click

from web_sockets import run


@click.command()
def cli():
    run()
