import click

from elastic_migrations import run
from elastic_migrations.base import DIRECTION_FORWARDS


@click.command()
@click.option('--direction', default=DIRECTION_FORWARDS,
              help='migration direction - forwards or reverse; defaults to forwards')
def cli(direction):
    run(direction)
