import os
import sys
import importlib.util
from pathlib import Path
from elastic_migrations.base import Migration, MigrationError, DIRECTION_FORWARDS, DIRECTIONS, DIRECTION_REVERSE
from sqlalchemy import Table, Column, String, MetaData, select, exc, update, insert, delete

from app_core.db import engine

BASE_DIR = Path(__file__).resolve().parent

DIRECTORY = 'migrations'
TABLE_COLUMN_NAME = 'version_num'

metadata_obj = MetaData()

elastic_version_table = Table(
    'elastic_version',
    metadata_obj,
    Column(TABLE_COLUMN_NAME, String(50))
)


def get_migration_filenames():
    filenames = []

    for filename in os.listdir(os.path.join(BASE_DIR, DIRECTORY)):
        name, extension = os.path.splitext(filename)
        if extension == '.py':
            filenames.append(filename)
    return filenames


def get_migration_from_filename(filename):
    name, _ = os.path.splitext(filename)
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE_DIR, DIRECTORY, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.migration


def get_initial_migration(migrations: list[Migration]):
    initial = None
    for migration in migrations:
        if migration.depends_on is None:
            if not initial:
                initial = migration
            else:
                raise MigrationError(f'Multiple initial migrations exist: {initial.filename}, {migration.filename}')
    if not initial:
        raise MigrationError('Initial migration (depends_on=None) not found')
    return initial


def get_next_migration(migrations: list[Migration], previous: Migration):
    next_migrations = []
    for migration in migrations:
        if migration.depends_on == previous.filename:
            next_migrations.append(migration)
    if not next_migrations:
        raise MigrationError(f'Next migration not found for {previous.filename}')
    elif len(next_migrations) == 1:
        return next_migrations[0]
    else:
        raise MigrationError(f'Multiple migrations depends on {previous.filename}')


def get_current_migration_version():
    try:
        with engine.connect() as conn:
            elastic_version = conn.execute(select(elastic_version_table.c.version_num)).one()
    except exc.ProgrammingError:
        raise MigrationError('No version table')
    except exc.MultipleResultsFound:
        raise MigrationError('Multiple version entries found')
    except exc.NoResultFound:
        return None
    else:
        return elastic_version._asdict()[TABLE_COLUMN_NAME]


def actualize_migration_version(version_num):
    with engine.connect() as conn:
        try:
            conn.execute(select(elastic_version_table.c.version_num)).one()
        except exc.NoResultFound:
            conn.execute(insert(elastic_version_table).values(version_num=version_num))
        else:
            if version_num:
                conn.execute(update(elastic_version_table).values(version_num=version_num))
            else:
                conn.execute(delete(elastic_version_table))
        conn.commit()


def order_migrations(migrations: list[Migration]):
    ordered_migrations = [get_initial_migration(migrations)]
    migrations.remove(ordered_migrations[-1])
    migrations_amount = len(migrations)
    for _ in range(migrations_amount):
        latest_migration = ordered_migrations[-1]
        ordered_migrations.append(get_next_migration(migrations, latest_migration))
        migrations.remove(ordered_migrations[-1])
    return ordered_migrations


def get_index_by_filename(migrations: list[Migration], filename):
    for index, migration in enumerate(migrations):
        if migration.filename == filename:
            return index
    raise ValueError('Item is not in the list')


def get_migrations_to_apply(ordered_migrations, current_index, direction):
    if direction not in DIRECTIONS:
        raise MigrationError('Unknown direction')
    elif direction == DIRECTION_FORWARDS:
        return ordered_migrations[current_index + 1:] if current_index is not None else ordered_migrations.copy()
    elif current_index is None:
        return []
    else:
        migrations_to_apply = ordered_migrations[:current_index + 1]
        migrations_to_apply.reverse()
        return migrations_to_apply


def limit_to_versions_number(ordered_migrations, versions: int):
    if versions == 0:
        return ordered_migrations
    elif versions < 0:
        raise ValueError('Invalid versions number')
    return ordered_migrations[:versions]


def apply_migrations(migrations_to_apply, current_migration, direction):
    err = None
    updated_migration = current_migration
    print('{} migrations'.format('applying' if direction == DIRECTION_FORWARDS else 'unapplying'))
    for migration in migrations_to_apply:
        try:
            migration.run(direction)
        except Exception as e:
            print(f'\tfailed to run migration {migration.filename}')
            err = e
            break
        else:
            print(f'\t{migration.filename}')
            if not migration.depends_on and direction == DIRECTION_REVERSE:
                updated_migration = None
            else:
                if direction == DIRECTION_FORWARDS:
                    updated_migration = migration.filename
                else:
                    updated_migration = migration.depends_on
    if updated_migration != current_migration:
        actualize_migration_version(updated_migration)
    if err:
        raise Exception(err)


def run(direction=DIRECTION_FORWARDS, versions=1):
    migration_filenames = get_migration_filenames()
    if not migration_filenames:
        return

    migrations = []
    for filename in migration_filenames:
        migrations.append(get_migration_from_filename(filename))
    ordered_migrations = order_migrations(migrations)

    current_migration = get_current_migration_version()
    current_index = get_index_by_filename(ordered_migrations, current_migration) if current_migration else None

    migrations_to_apply = get_migrations_to_apply(ordered_migrations, current_index, direction)
    if not migrations_to_apply:
        return

    migrations_to_apply = limit_to_versions_number(migrations_to_apply, versions)

    apply_migrations(migrations_to_apply, current_migration, direction)


if __name__ == '__main__':
    run()
