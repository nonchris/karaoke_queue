from typing import Union, Optional, Any

from data_models.song import Song
from database.db_base import SONGS_TABLE, DB, song_entries_to_song_objects, connect_if_needed
from log_setup import logger


# this function is not generified because its unique thing is that it just queries one distinct object
def get_song_by_title_and_author(title: str, artist: str, conn=None, db=DB, table=SONGS_TABLE) -> Optional[Song]:
    return __get_song_by_title_and_author(title, artist, conn=conn, db=db, table=table)


@connect_if_needed
def __get_song_by_title_and_author(title: str, artist: str, conn=None, db=DB, table=SONGS_TABLE) -> Optional[Song]:
    """ Get song by its primary identifier or just pass the whole incident, we'll extract the uuid 4U :3 """

    statement = f"SELECT * FROM {table} WHERE title='{title}' AND artist='{artist}';"

    result = conn.execute(statement)
    res = result.fetchone()

    if res is None:
        logger.warning(f"There is no song for {title=}, {artist=}")
        return None

    return Song(*res)


def get_song(song: Song, conn=None, db=DB, table=SONGS_TABLE) -> Optional[Song]:
    return get_song_by_title_and_author(song.title, song.artist, conn=conn, db=db, table=table)


def get_songs_by_field(column: str, order_desc=True, conn=None, db=DB, table=SONGS_TABLE) -> Optional[list[Song]]:
    return __get_songs_by_field(column, order_desc=order_desc, conn=conn, db=db, table=table)


@connect_if_needed
def __get_songs_by_field(column: str, order_desc=True, conn=None, db=DB, table=SONGS_TABLE) -> Optional[list[Song]]:

    statement = f"SELECT * FROM {table} ORDER BY {column} {'DESC' if order_desc else 'ASC'};"

    result = conn.execute(statement)

    queried_incidents = result.fetchall()

    incidents = song_entries_to_song_objects(queried_incidents)

    return incidents


def get_songs_where(field: str, identifier: Union[Song, Any], comparator="=", order_desc=True, conn=None, db=DB, table=SONGS_TABLE) -> Optional[list[Song]]:
    """ The generic query function for incidents by one condition """
    return __get_songs_where(field, identifier, comparator=comparator, order_desc=order_desc, conn=conn, db=db, table=table)


@connect_if_needed
def __get_songs_where(field: str, identifier: Union[Song, Any], comparator="=", order_desc=True, conn=None, db=DB, table=SONGS_TABLE) -> Optional[list[Song]]:

    key = getattr(identifier, field) if isinstance(identifier, Song) else identifier
    statement = f"SELECT * FROM {table} WHERE {field}{comparator}? ORDER BY {field} {'DESC' if order_desc else 'ASC'};"

    result = conn.execute(statement, (key,))
    res = result.fetchall()

    if not res:
        logger.warning(f"There are no songs for identifier='{key}'")
        return None

    return song_entries_to_song_objects(res)


def get_all_songs(fields: tuple[str] = ("*",), order_by="title", order_desc=True, conn=None, db=DB, table=SONGS_TABLE) -> Optional[Union[list[tuple], list[Song]]]:
    """ :returns: A list of songs if queried for all fields (*), else a list of tuples representing each row """
    return __get_all_songs(fields=fields, order_by=order_by, order_desc=order_desc, conn=conn, db=db, table=table)


def __get_all_songs(fields: tuple[str] = ("*",), order_by="title", order_desc=True, conn=None, db=DB, table=SONGS_TABLE) -> Optional[Union[list[tuple], list[Song]]]:
    fields = ", ".join(fields)
    statement = f"SELECT {fields} FROM {table} ORDER BY {order_by} { 'DESC' if order_desc else 'ASC'};"

    result = conn.execute(statement)
    res = result.fetchall()

    if not res:
        logger.warning(f"There are no songs")
        return None

    if fields == ("*",):
        return song_entries_to_song_objects(res)

    return res


def get_latest_play_time(conn=None, db=DB, table=SONGS_TABLE):
    return __get_latest_play_time(conn=conn, db=db, table=table)


def __get_latest_play_time(conn=None, db=DB, table=SONGS_TABLE):
    cursor = conn.cursor()

    query = f"SELECT * FROM {table} ORDER BY time_played DESC LIMIT 1"
    cursor.execute(query)

    result = cursor.fetchone()
    conn.close()

    return result

