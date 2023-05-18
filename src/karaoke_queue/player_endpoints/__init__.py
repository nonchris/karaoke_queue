from fastapi import APIRouter

from ..room_manager import RoomManager

router = APIRouter(
    prefix="/api/v1/manage"
)
session_manager = RoomManager()
