from collections import deque
from dataclasses import dataclass
from uuid import uuid4

from .song import Song
from .queue_entry import QueueEntry
from .types import uuid_hex_t
from .read_write_lock import ReadWriteLock, with_write_lock, with_read_lock


@dataclass
class Room:
    name: str
    max_queue_len: int = 420
    max_history_len: int = 690
    uuid: uuid_hex_t = uuid4().hex

    def __post_init__(self):
        self.__queue: deque[QueueEntry] = deque([], maxlen=self.max_queue_len)
        self.__history: deque[QueueEntry] = deque([], maxlen=self.max_history_len)
        self.lock = ReadWriteLock()

    def __dequeue_to_transmit(self, dq: deque):
        return [entry.to_transmit for entry in dq]

    @property
    @with_read_lock
    def __queue_in_transmittable_format(self) -> list[dict]:
        return self.__dequeue_to_transmit(self.__queue)

    @property
    @with_read_lock
    def __history_in_transmittable_format(self) -> list[dict]:
        return self.__dequeue_to_transmit(self.__history)

    @property
    @with_read_lock
    def admin_to_transmit_info(self) -> dict:
        # get user as base and extend context
        to_transmit = self.user_to_transmit_info
        to_transmit["uuid"] = self.uuid
        return to_transmit

    @property
    @with_read_lock
    def user_to_transmit_info(self) -> dict:
        to_transmit = {
            "name": self.name,
            "queue": self.__queue_in_transmittable_format,
            "history": self.__history_in_transmittable_format
            }
        return to_transmit

    @with_write_lock
    def add_to_queue(self, song: Song, user: str = "Unknown"):
        self.__queue.append(QueueEntry(song, user))

    @with_write_lock
    def pop_from_queue(self) -> QueueEntry:
        entry = self.__queue.popleft()
        self.__history.append(entry)
        return entry

    def __next__(self) -> QueueEntry:
        return self.pop_from_queue()
