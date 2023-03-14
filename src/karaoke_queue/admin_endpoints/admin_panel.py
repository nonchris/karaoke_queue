from fastapi import APIRouter

from ..endpoint_base_generators import get_session_admin_endpoint
from ..session_manager import SessionManager
from ..data_models.types import uuid_hex_t
from ..data_models.session import Session
from ..data_models.exceptions import make_bad_request_session_unknown, make_raise_bad_request

router = APIRouter(
    prefix="/v1/manage"
)
session_manager = SessionManager()

auth_url = "/{session_name}/{uuid}"


def ensure_session_and_uuid(session_name: str, uuid: uuid_hex_t) -> Session:
    """ A function that shall fail if something is wrong """
    session = session_manager.get_session(session_name)
    if session is None:
        raise make_bad_request_session_unknown(session_name)

    if session.uuid != uuid:
        raise make_raise_bad_request(f"Invalid admin token")

    return session


@router.get(f"{auth_url}")
def admin_panel(session_name: str, uuid: uuid_hex_t):

    session = ensure_session_and_uuid(session_name, uuid)

    return {"session": session.admin_to_transmit_info,
            "links": {
                "close": f"{get_session_admin_endpoint(session)}/close",
                "edit_queue": f"{get_session_admin_endpoint(session)}/edit_queue"
            }}


@router.get(f"/{auth_url}/close", status_code=501)
def close_session(session_name: str, uuid: uuid_hex_t):
    return {}


@router.get(f"/{auth_url}/edit_queue/", status_code=501)
def edit_queue(session_name: str, uuid: uuid_hex_t):
    return {}
