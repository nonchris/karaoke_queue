from fastapi import APIRouter

from .user_checks import verify_room_exists
from ..database import songs_db
from ..room_manager import RoomManager
from ..data_models.exceptions import make_bad_request_room_unknown, make_raise_bad_request

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
