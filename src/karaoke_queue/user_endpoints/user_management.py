from fastapi import APIRouter

from karaoke_queue.session_manager import SessionManager
from karaoke_queue.user_endpoints.user_checks import verify_session_exists

router = APIRouter(
    prefix="/v1"
)

session_manager = SessionManager()


@router.get("/join/{session_id}")
async def join_session(session_id: str, user_name):
    session = verify_session_exists(session_id)
