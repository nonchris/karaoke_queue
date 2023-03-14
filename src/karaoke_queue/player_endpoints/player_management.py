from fastapi import APIRouter

from karaoke_queue.room_manager import RoomManager
from guard_clauses.guard_existences import try_get_room

router = APIRouter(
    prefix="/v1"
)

room_manager = RoomManager()


@router.get("/join/{room_id}")
async def join_room(room_id: str, user_name):
    room = try_get_room(room_id)
