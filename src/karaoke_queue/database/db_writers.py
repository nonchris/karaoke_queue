from .db_base import SONGS_TABLE_COLUMN_ORDER_AS_STR, DB, get_values_in_order, \
    SONGS_TABLE_COLUMN_ORDER
from .db_base import SONGS_TABLE, connect_if_needed
from .db_getters import get_song
from ..data_models.song import Song
from ..log_setup import logger


def add_song(song: Song, order=SONGS_TABLE_COLUMN_ORDER_AS_STR, conn=None, db=DB, table=SONGS_TABLE):
    return __add_song(song, order=order, conn=conn, db=db, table=table)


@connect_if_needed
def __add_song(song: Song, order=SONGS_TABLE_COLUMN_ORDER_AS_STR, conn=None, db=DB, table=SONGS_TABLE):

    statement = f"INSERT INTO {table} {order} VALUES (?, ?, ?, ?);"
    vals = get_values_in_order(song, order)
    conn.execute(statement, vals)
    conn.commit()


def update_song(song: Song, fields_to_update=SONGS_TABLE_COLUMN_ORDER, conn=None, db=DB, table=SONGS_TABLE):
    """ Update an entry. For simplicity all fields beside the uuid will be overwritten by default. """
    return __update_song(song, fields_to_update=fields_to_update, conn=conn, db=db, table=table)


@connect_if_needed
def __update_song(song: Song, fields_to_update=SONGS_TABLE_COLUMN_ORDER, conn=None, db=DB, table=SONGS_TABLE):

    update_fields = ', '.join(f"{column} = ?" for column in fields_to_update)

    statement = f"UPDATE {table} SET {update_fields} WHERE title='{song.title}' AND artist='{song.artist}';"

    vals = get_values_in_order(song, fields_to_update)

    conn.execute(statement, vals)
    conn.commit()


def insert_or_update_song(song: Song, conn=None, db=DB, table=SONGS_TABLE):
    """
    Creates new entry if song is not yet registered

    :param song: The song to update in the db
    :param conn: an optional existing connection to use
    :param db: optional overwrite of path to db
    :param table: optional overwrite of the used table name
    """

    # query version of incident in db
    query = get_song(song, conn=conn, db=db, table=table)

    # incident does not yet exist - create it
    if query is None:
        add_song(song, conn=conn, db=db, table=table)
        logger.info(f"Created song: {song.title=}, {song.artist=}")
        return

    update_song(song, conn=conn)
    logger.info(f"Updated song: {song.title=}, {song.artist=}")
