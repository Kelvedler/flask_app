import click

from elastic_migrations import run
from elastic_migrations.base import DIRECTION_FORWARDS


@click.command()
@click.option('--direction', '-d', default=DIRECTION_FORWARDS,
              help='migration direction - forwards or reverse; defaults to forwards')
@click.option('--versions', '-v', default=1,
              help='number of migrations to apply; defaults to 1; 0 means all migrations will be applied')
@click.option('--current', '-c', default=False, is_flag=True,
              help='show current migration version')
def cli(direction, versions, current):
    run(direction, versions, current)
