import inspect
import os
import sqlite3
from sqlite3 import Connection
from time import sleep
from typing import Optional

from ..data_models.song import Song
from ..log_setup import logger

DB = os.getenv("DB_FILE", "data/karaoke_queue.sqlite")
SONGS_TABLE = os.getenv("SONGS_TABLE", "songs")
HISTORY_TABLE = os.getenv("HISTORY_TABLE", "history")
tables = [SONGS_TABLE, HISTORY_TABLE]

SONGS_TABLE_COLUMN_ORDER = ("title", "artist", "duration")
HISTORY_TABLE_COLUMN_ORDER = ("title", "artist", "time_played")

SONGS_TABLE_COLUMN_ORDER_AS_STR = f"({', '.join(SONGS_TABLE_COLUMN_ORDER)})"
HISTORY_TABLE_COLUMN_ORDER_AS_STR = f"({', '.join(HISTORY_TABLE_COLUMN_ORDER)})"


def mk_songs_table_if_not_exists(table=SONGS_TABLE, conn=None, db=DB):

    scheme = f"""
        CREATE TABLE {table} (
            title VARCHAR,
            artist VARCHAR,
            duration REAL,
            id INTEGER PRIMARY KEY autoincrement
        );
    """

    _make_table_if_not_exists(table, scheme, conn=conn, db=db)


def mk_history_table_if_not_exists(table=HISTORY_TABLE, conn=None, db=DB):

    schema = f"""
        CREATE TABLE {table} (
            title VARCHAR,
            artist VARCHAR,
            time_played TIMESTAMP PRIMARY KEY
        );
    """
    _make_table_if_not_exists(table, schema, conn=conn, db=db)


def setup_db(*, songs_table=SONGS_TABLE, history_table=HISTORY_TABLE, conn=None, db=DB) -> Connection:
    """
    Wrapper around get_connection() and mk_incident_table()
    :returns: A new connection of the one given if exists
    """
    conn = conn or get_connection(db)
    mk_history_table_if_not_exists(table=history_table, conn=conn, db=db)
    mk_songs_table_if_not_exists(table=songs_table, conn=conn, db=db)
    return conn


def get_connection(db=DB, max_tries=3) -> Optional[Connection]:

    # Create a new SQLite database
    conn = None
    for i in range(1, max_tries+1):

        try:
            conn = sqlite3.connect(db)
            break

        except sqlite3.OperationalError as e:
            logger.error(f"Can't open '{db}' (try {i}/{max_tries}), maybe due to a sub-folder not existing")
            sleep(0.5)  # wait a moment

    else:
        logger.error(f"Could not connect to '{db}'")

    return conn


def connect_if_needed(fn):
    """
    Create a new connection if none is given  as kwarg
    Ths **requires** the connection argument to be a kwarg named 'conn'
    Why this decorator?
    If no conn is given a new one shall be created, but we should also close it in the end.
    But if one is given, we don't wanna randomly close it. Maybe the passed one shall be reused.
    To implement this if conn is None plus the eventual closing in each function is redundant.
    Hence, the decorator.
    """
    # black magic to get default kwargs
    full_spec = inspect.getfullargspec(fn)
    kw_only_defaults = full_spec[5]

    def conn_ensured_fn(*args, **kwargs):
        if kwargs.get('conn', None) is None:
            conn = get_connection(kwargs.get("db", kwargs.get("db") or kw_only_defaults["db"]))
            kwargs['conn'] = conn
            res = fn(*args, **kwargs)
            conn.close()
            return res

        return fn(*args, **kwargs)

    # even more black magic to restore signature
    sig = inspect.signature(fn)
    conn_ensured_fn.__signature__ = sig.replace(
        parameters=[param.replace(default=None) for param in sig.parameters.values()]
    )

    return conn_ensured_fn


def song_entries_to_song_objects(song_rows: list[tuple, ...]) -> list[Song]:
    return [Song(*inc) for inc in song_rows]


def _make_table_if_not_exists(table: str, create_schema: str, conn=None, db=DB):
    return __make_table_if_not_exists(table, create_schema, conn=conn, db=db)


@connect_if_needed
def __make_table_if_not_exists(table: str, create_schema: str, conn=None, db=DB):
    conn = conn or get_connection(db=db)

    result = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
    if result.fetchone() is not None:
        logger.debug(f"Table '{table}' exists, nothing will be created")
        return

    conn.execute(create_schema)

    conn.commit()


def get_values_in_order(obj: Song, order: tuple[str, ...] = SONGS_TABLE_COLUMN_ORDER) -> tuple:
    """
    Get attributes as tuple from an object

    :param obj: the object to source the values from
    :param order: the order the params are inserted in the SQL statement

    :returns: tuple containing all attributes in the same order (attr is None if not exists)
    """
    # I love pythons black magic
    vals = []
    for attr in order:
        # I love pythons black magic
        val = getattr(obj, attr.strip(), None)

        vals.append(val)

    if None in vals:
        logger.warning(f"NoneType found in '{obj}'")

    return tuple(vals)
