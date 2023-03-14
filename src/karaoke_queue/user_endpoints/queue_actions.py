from fastapi import APIRouter

from ..database import songs_db
from ..session_manager import SessionManager
from ..data_models.exceptions import make_bad_request_session_unknown, make_raise_bad_request

router = APIRouter(
    prefix="/v1/user"
)

session_manager = SessionManager()


@router.get("/{session_name}/queue_song")
async def queue_song(session_name: str, song_id: int, user_name: str):
    # TODO: Username
    """
    Ann song to queue.
    :param session_name: Session to queue to
    :param song_id: Song to queue.
    :param user_name: Name of the user that requested the song

    :return: current session state
    """
    session = session_manager.get_session(session_name)

    if session is None:
        raise make_bad_request_session_unknown(session_name)

    song = songs_db.get_song_by_primary_key(song_id)
    session.add_to_queue(song, user_name)
    return {
        "session": session.user_to_transmit_info,
        "links": {},
    }
