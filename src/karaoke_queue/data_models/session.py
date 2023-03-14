from collections import deque
from dataclasses import dataclass
from uuid import uuid4

from .song import Song
from .types import uuid_hex_t
from .read_write_lock import ReadWriteLock, with_write_lock, with_read_lock


@dataclass
class Session:
    name: str
    max_queue_len: int = 420
    uuid: uuid_hex_t = uuid4().hex

    def __post_init__(self):
        self.queue: deque[Song] = deque([], maxlen=self.max_queue_len)
        self.lock = ReadWriteLock()

    @with_read_lock
    def __queue_in_transmittable_format(self):
        return [song.to_transmit for song in self.queue]

    @with_read_lock
    def admin_to_transmit_info(self) -> dict:
        to_transmit = {
            "name": self.name,
            "uuid": self.uuid,
            "queue": self.__queue_in_transmittable_format()
            }
        return to_transmit

    @with_read_lock
    def user_to_transmit_info(self) -> dict:
        to_transmit = {
            "name": self.name,
            "queue": self.__queue_in_transmittable_format()
            }
        return to_transmit

    @with_write_lock
    def add_song(self, song: Song):
        self.queue.append(song)
