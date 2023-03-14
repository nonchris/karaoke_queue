from fastapi import FastAPI

from .data_models.session import Session
from .data_models.types import uuid_hex_t
from .session_manager import SessionManager
from .version import __version__


description = """
Karaoke Queue API to queue Songs.

## Users

You will be able to:

* **Create** a new entry in the queue.
* **Read** the status of the queue
"""

app = FastAPI(
    title="Karaoke Queue API",
    description=description,
    version=__version__,
    # terms_of_service="PLACEHOLDER",
    contact={
        "name": "GitHub Repository",
        "url": "https://github.com/nonchris/karaoke_queue/",
    },
)

session_manager = SessionManager()


def get_session_admin_endpoint(session: Session, base="/v1/manage/{}/{}"):
    return base.format(session.name, session.uuid)


@app.get("/v1/new_session")
async def new_session(name: str):
    """
    Open a new session
    :param name: Name of the session

    :return: Information for session
    """
    session = session_manager.add_session(name)
    return {"session": session.admin_to_transmit_info,
            "links": {
                "admin_panel": get_session_admin_endpoint(session)
            }
        }


@app.get("/v1/manage/{session_name}/{uuid}")
def admin_panel(session_name: str, uuid: uuid_hex_t):
    session = session_manager.get_session(session_name)
    if session is None:
        return {}

    if session.uuid != uuid:
        return {"session": session.user_to_transmit_info,
                "links": {}}

    return {"session": session.admin_to_transmit_info,
            "links": {
                "close": f"{get_session_admin_endpoint(session)}/close",
                "edit_queue": f"{get_session_admin_endpoint(session)}/edit_queue"
            }}


@app.get("/v1/manage/{session_name}/{uuid}/close", status_code=501)
def close_session(session_name: str, uuid: uuid_hex_t):
    return {}


@app.get("/v1/manage/{session_name}/{uuid}/edit_queue", status_code=501)
def edit_queue(session_name: str, uuid: uuid_hex_t):
    return {}


@app.post("/v1/queue")
async def queue(title: str):
    """
    Transcribe audio file.
    :param title: Song to queue.

    :return: position
    """
    pass


@app.get("/v1/status/{task_id}")
async def status(task_id: str):
    """
    Get the status of queue.
    :return: Status of the queue.
    """
    return {"active": True}


# @app.on_event("startup")
# async def schedule_periodic():
#     """
#     Schedule the periodic function to run every seconds.
#     """
#     loop = asyncio.get_event_loop()
#     loop.create_task(periodic())
