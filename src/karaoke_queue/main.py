from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoint_base_generators import get_session_user_endpoint
from .endpoint_base_generators import get_session_admin_endpoint
from .data_models.session import Session
from .data_models.types import uuid_hex_t
from .session_manager import SessionManager
from .version import __version__
from .admin_endpoints import admin_panel
from .user_endpoints import queue_actions


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

# TODO: should potentially remove that wildcard (...)
origins = [
    "*",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_panel.router)
app.include_router(queue_actions.router)

session_manager = SessionManager()


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
                "admin_panel": get_session_admin_endpoint(session),
                "queue_song": f"{get_session_user_endpoint(session)}/queue_song",
                "next_song": f"{get_session_admin_endpoint(session)}/next"
            }
        }


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
