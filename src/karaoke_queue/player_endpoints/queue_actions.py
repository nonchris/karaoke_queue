from fastapi import APIRouter, Request

from karaoke_queue.guard_clauses.guard_existences import try_get_room, try_get_song, try_get_player_by_uuid
from karaoke_queue.guard_clauses.guard_convertes import try_convert_param_to_int
from ..endpoint_base_generators import get_room_user_endpoint
from ..room_manager import RoomManager

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


@router.get("/{room_name}/queue_song")
async def queue_song(request: Request):
    """
    Ann song to queue.
    :param room_name: room to queue to
    :param song_id: Song to queue.
    :param user_name: Name of the user that requested the song

    :return: current room state
    """

    room_name = request.path_params["room_name"]
    room = try_get_room(room_name)

    user_id = request.cookies.get("player_id")
    player = try_get_player_by_uuid(room.name, user_id)

    song_id_str = request.query_params.get("song_id")
    song_id = try_convert_param_to_int(song_id_str, argument="song_id")
    song = try_get_song(song_id)

    room.add_to_queue(song, player)
    return {
        "room": room.user_to_transmit_info,
        "links": {
            "queue_menu": f"{get_room_user_endpoint(room)}/queue_menu",
        },
    }
