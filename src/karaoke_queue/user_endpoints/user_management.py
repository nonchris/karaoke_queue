from fastapi import APIRouter

from karaoke_queue.room_manager import RoomManager
from karaoke_queue.user_endpoints.user_checks import verify_room_exists

router = APIRouter(
    prefix="/v1"
)

room_manager = RoomManager()


@router.get("/join/{room_id}")
async def join_room(room_id: str, user_name):
    room = verify_room_exists(room_id)
