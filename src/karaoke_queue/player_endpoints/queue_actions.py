from fastapi import APIRouter

from guard_clauses.guard_existences import try_get_room, try_get_song, try_get_player_by_uuid
from guard_clauses.guard_convertes import try_convert_param_to_int
from ..endpoint_base_generators import get_room_user_endpoint
from ..room_manager import RoomManager

router = APIRouter(
    prefix="/v1/user"
)

session_manager = RoomManager()


@router.get("/{room_name}/queue_song")
async def queue_song(room_name: str, song_id: int, user_name: str):
    # TODO: Username
    """
    Ann song to queue.
    :param room_name: room to queue to
    :param song_id: Song to queue.
    :param user_name: Name of the user that requested the song

    :return: current room state
    """
    room = verify_room_exists(room_name)

    song = songs_db.get_song_by_primary_key(song_id)
    room.add_to_queue(song, user_name)
    return {
        "room": room.user_to_transmit_info,
        "links": {},
    }
