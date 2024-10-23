import sqlite3
import click
from flask import current_app, g


def get_database():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def _close_database(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def _init_database():
    db = get_database()
    from os import listdir

    for file in listdir('app/database/schemas'):
        if file.endswith('.sql'):
            try:
                with open(f'app/database/schemas/{file}', mode='r', encoding='utf-8') as f:
                    db.executescript(f.read())
                current_app.logger.info(f'Database schema file {file} is executed.')
            except Exception as e:
                current_app.logger.error(e)


@click.command('init-db')
def _init_db_command():
    _init_database()
    current_app.logger.info(f'Database inited.')


def init_app(app):
    app.teardown_appcontext(_close_database)
    app.cli.add_command(_init_db_command)
