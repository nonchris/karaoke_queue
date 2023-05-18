from fastapi import APIRouter
from fastapi.responses import JSONResponse

from karaoke_queue.endpoint_base_generators import get_room_user_endpoint
from karaoke_queue.room_manager import RoomManager
from karaoke_queue.guard_clauses.guard_existences import try_get_room

router = APIRouter(
    prefix="/api/v1"
)

room_manager = RoomManager()


@router.get("/join/{room_id}")
async def join_room(room_id: str, player_name):
    """
    Allows player to join a room by a selected name (must be unique!)
    :param room_id: the room to join
    :param player_name: Name the player wants to be displayed as
    :return: Contains player & room info and session cookie to authenticate the user
    """
    room = try_get_room(room_id)
    player = room_manager.add_player(room.name, player_name)

    content = {
        "room": room.user_to_transmit_info,
        "player": player.to_transmit,
        "links": {
            "queue_menu": f"{get_room_user_endpoint(room)}/queue_menu"
        },
    }
    response = JSONResponse(content=content)
    response.set_cookie(key="player_id", value=player.uuid)

    return response
