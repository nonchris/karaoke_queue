from karaoke_queue.data_models.exceptions import make_bad_request_session_unknown
from karaoke_queue.data_models.session import Session
from karaoke_queue.session_manager import SessionManager

session_manager = SessionManager()


def verify_session_exists(session_name: str) -> Session:
    session = session_manager.get_session(session_name)

    if session is None:
        raise make_bad_request_session_unknown(session_name)

    return session
