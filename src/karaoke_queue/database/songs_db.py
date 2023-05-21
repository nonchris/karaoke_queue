from karaoke_queue.database.db_base import *
from karaoke_queue.database.db_writers import *
from karaoke_queue.database.db_getters import *


# the song DB will probably not update during a session
# so we can cache the results
# TODO: make update function in case something changed anyways
__all_song_query: list[tuple] = get_all_songs(fields=("title",))
_all_artists_query: list[tuple] = get_all_songs(fields=("artist",), order_by="artist", distinct=True)

ALL_TITLES_LIST: list[str] = [song[0] for song in __all_song_query]
ALL_ARTISTS_LIST: list[str] = [artist[0] for artist in _all_artists_query]

if __name__ == '__main__':
    setup_db()
    s = Song("Never gonna give you up", "rick astley", 6.9, 10)
