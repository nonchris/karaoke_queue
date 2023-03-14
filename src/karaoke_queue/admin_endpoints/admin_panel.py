from fastapi import APIRouter

from ..endpoint_base_generators import get_session_admin_endpoint
from ..session_manager import SessionManager
from ..data_models.types import uuid_hex_t
from ..data_models.exceptions import raise_bad_request_session_unknown, raise_bad_request

router = APIRouter(
    prefix="/v1/manage"
)
session_manager = SessionManager()


@router.get("/{session_name}/{uuid}/")
def admin_panel(session_name: str, uuid: uuid_hex_t):
    session = session_manager.get_session(session_name)
    if session is None:
        raise_bad_request_session_unknown(session_name)

    if session.uuid != uuid:
        return raise_bad_request(f"Invalid admin token")

    return {"session": session.admin_to_transmit_info,
            "links": {
                "close": f"{get_session_admin_endpoint(session)}/close",
                "edit_queue": f"{get_session_admin_endpoint(session)}/edit_queue"
            }}


@router.get("/{session_name}/{uuid}/close/", status_code=501)
def close_session(session_name: str, uuid: uuid_hex_t):
    return {}


@router.get("/{session_name}/{uuid}/edit_queue/", status_code=501)
def edit_queue(session_name: str, uuid: uuid_hex_t):
    return {}
