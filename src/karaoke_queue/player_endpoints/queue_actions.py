from fastapi import APIRouter, Request
from thefuzz import process

from karaoke_queue.guard_clauses.guard_existences import try_get_room, try_get_song, try_get_player_by_uuid
from karaoke_queue.guard_clauses.guard_convertes import try_convert_param_to_int
from ..endpoint_base_generators import get_room_user_endpoint
from ..room_manager import RoomManager

from karaoke_queue.database.songs_db import ALL_TITLES_LIST, ALL_ARTISTS_LIST

router = APIRouter(
    prefix="/api/v1/user"
)

room_manager = RoomManager()


@router.get("/{room_name}/queue_menu")
def queue_menu(room_name: str):
    # TODO this shall emit a menu page one day
    room = try_get_room(room_name)
    return {"room": room.user_to_transmit_info,
            "links": {
                "queue_song": f"{get_room_user_endpoint(room)}/queue_song",
            }
            }


@router.get("/{room_name}/queue_song/{song_id}")
async def queue_song(request: Request):
    """
    Add song to queue. Requires a valid session cookie.
    :param room_name: room to queue to
    :param song_id: Song to queue.

    :return: current room state
    """

    room_name = request.path_params["room_name"]
    room = try_get_room(room_name)

    user_id = request.cookies.get("player_id")
    player = try_get_player_by_uuid(room.name, user_id)

    song_id_str = request.path_params["song_id"]
    song_id = try_convert_param_to_int(song_id_str, argument="song_id")
    song = try_get_song(song_id)

    room.add_to_queue(song, player)
    return {
        "room": room.user_to_transmit_info,
        "links": {
            "queue_menu": f"{get_room_user_endpoint(room)}/queue_menu",
        },
    }

@router.get("/search_song/{song_name}")
def search_song(song_name: str) -> dict:
    """
    Search for songs in database
    Args:
        song_name: the string to search for
    Returns:
        a list
    """
    # TODO make 10 a parameter and not hardcoded in this file
    song_matches = process.extract(song_name, ALL_TITLES_LIST, limit=10)

    return {
        # TODO return more context to songs than just the title
        "songs": song_matches,
        "links": {
            # TODO
        }
    }
