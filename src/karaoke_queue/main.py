import asyncio

from fastapi import FastAPI
from fastapi import UploadFile

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


@app.post("/v1/queue")
async def queue(title: str):
    """
    Transcribe audio file.
    :param file: Song to queue.

    :return: position
    """
    pass


@app.get("/v1/status/{task_id}")
async def status(task_id: str):
    """
    Get the status of queue.
    :return: Status of the queue.
    """
    pass


# @app.on_event("startup")
# async def schedule_periodic():
#     """
#     Schedule the periodic function to run every seconds.
#     """
#     loop = asyncio.get_event_loop()
#     loop.create_task(periodic())
