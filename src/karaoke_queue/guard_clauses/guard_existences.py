from karaoke_queue.data_models.exceptions import make_bad_request_room_unknown, make_raise_bad_request
from karaoke_queue.data_models.player import Player
from karaoke_queue.data_models.room import Room
from karaoke_queue.data_models.song import Song
from karaoke_queue.data_models.types import player_uuid_hex_t
from karaoke_queue.database import songs_db
from karaoke_queue.room_manager import RoomManager

room_manager = RoomManager()


def try_get_room(room_name: str) -> Room:
    room = room_manager.get_room(room_name)

    if room is None:
        raise make_bad_request_room_unknown(room_name)

    return room


def try_get_player_by_uuid(room_name: str, player_id: player_uuid_hex_t) -> Player:

    player = room_manager.get_player(room_name, player_id)

    if player is None:
        raise make_raise_bad_request(f"Could not verify player by id: '{player_id}'")

    return player


def try_get_song(song_id: int) -> Song:
    song = songs_db.get_song_by_primary_key(song_id)

    if song is None:
        raise make_raise_bad_request(f"Song with id: '{song_id}' is unknown")

    return song
