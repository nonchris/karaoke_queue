from fastapi import APIRouter

from ..endpoint_base_generators import get_room_admin_endpoint
from ..room_manager import RoomManager
from ..data_models.types import uuid_hex_t
from ..data_models.room import Room
from ..data_models.exceptions import make_bad_request_room_unknown, make_raise_bad_request, make_internal_server_error

router = APIRouter(
    prefix="/api/v1/manage"
)
room_manager = RoomManager()

auth_url = "/{session_name}/{uuid}"


def ensure_session_and_uuid(session_name: str, uuid: uuid_hex_t) -> Room:
    """ A function that shall fail if something is wrong """
    session = room_manager.get_room(session_name)
    if session is None:
        raise make_bad_request_room_unknown(session_name)

    if session.uuid != uuid:
        raise make_raise_bad_request(f"Invalid admin token")

    return session


@router.get(f"{auth_url}")
def admin_panel(session_name: str, uuid: uuid_hex_t):
    """ Base panel for admin actions"""
    session = ensure_session_and_uuid(session_name, uuid)

    return {"session": session.admin_to_transmit_info,
            "links": {
                "close": f"{get_room_admin_endpoint(session)}/close",
                "edit_queue": f"{get_room_admin_endpoint(session)}/edit_queue"
            }}


@router.get(f"{auth_url}/next")
def next_song(session_name: str, uuid: uuid_hex_t):
    """
    Get first song in queue, song will be removed to queue and be put in history
    :return: "next" as song that is the next in queue and additional context
    """
    session = ensure_session_and_uuid(session_name, uuid)

    entry = next(session)
    if entry is None:
        raise make_internal_server_error("No songs in queue")

    return {"next": entry.to_transmit,
            "session": session.admin_to_transmit_info,
            "links": {}}


@router.get(f"/{auth_url}/close", status_code=501)
def close_session(session_name: str, uuid: uuid_hex_t):
    return {}


@router.get(f"/{auth_url}/edit_queue/", status_code=501)
def edit_queue(session_name: str, uuid: uuid_hex_t):
    return {}
