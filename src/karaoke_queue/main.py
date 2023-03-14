from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .endpoint_base_generators import get_room_user_endpoint
from .endpoint_base_generators import get_room_admin_endpoint
from .data_models.room import Room
from .data_models.types import uuid_hex_t
from .room_manager import RoomManager
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

room_manager = RoomManager()


@app.get("/v1/new_room")
async def new_room(name: str):
    """
    Open a new room
    :param name: Name of the room

    :return: Information for room
    """
    room = room_manager.add_room(name)
    return {"room": room.admin_to_transmit_info,
            "links": {
                "admin_panel": get_room_admin_endpoint(room),
                "queue_song": f"{get_room_user_endpoint(room)}/queue_song",
                "next_song": f"{get_room_admin_endpoint(room)}/next"
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
