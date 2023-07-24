import click

from elastic_migrations import run
from elastic_migrations.base import DIRECTION_FORWARDS


@click.command()
@click.option('--direction', default=DIRECTION_FORWARDS,
              help='migration direction - forwards or reverse; defaults to forwards')
@click.option('--versions', default=1,
              help='number of migrations to apply; defaults to 1; 0 means all migrations will be applied')
def cli(direction, versions):
    run(direction, versions)
