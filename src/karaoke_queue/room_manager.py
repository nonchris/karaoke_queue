from copy import deepcopy
from typing import Callable, Optional

from .log_setup import logger
from .data_models.read_write_lock import ReadWriteLock, with_write_lock, with_read_lock
from .data_models.room import Room
from .data_models.types import room_name_t


def with_lock(fn: Callable):
    """
    Decorator that makes your function allocate the classes lock
    Ths **requires** the lock of the class to be accessible as `self.lock`
    It's recommended to use Recursive Locks so that you can use the decorator at sub-functions too
    """
    def threaded_wrapper(self, *args, **kwargs):
        with self.lock:
            return fn(self, *args, **kwargs)

    return threaded_wrapper


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            logger.debug(f"The object '{cls.__name__}' was already initialized, returning inited object")
        return cls._instances[cls]


class RoomManager(metaclass=Singleton):
    """ Threadsafe room manager """

    def __init__(self):
        self.__rooms: dict[room_name_t, Room] = {}
        self.lock = ReadWriteLock()

    @with_write_lock
    def add_room(self, key: room_name_t) -> Room:
        """
        If the rooms key already exists a number will be added like
        "cool_room" -> "cool_room-1"
        :return: the room with unique name and other properties
        """
        key_base = key
        i = 1
        while key in self.__rooms:
            key = f"{key_base}-{i}"
            i += 1

        room = Room(key)
        self.__rooms[key] = room
        return room

    @with_read_lock
    def get_room(self, key: room_name_t) -> Optional[Room]:
        return self.__rooms.get(key, None)

    @property
    def rooms(self):
        return deepcopy(self.__rooms)


if __name__ == '__main__':
    s = RoomManager()
    name = s.add_room("hi", 42)
    print(name)
    name2 = s.add_room("hi", 43)

    print(name2)

    print(s.rooms)


