from copy import deepcopy
from typing import Callable, Optional

from karaoke_queue.data_models.exceptions import make_raise_bad_request
from karaoke_queue.data_models.player import Player
from .log_setup import logger
from .data_models.read_write_lock import ReadWriteLock, with_write_lock, with_read_lock
from .data_models.room import Room
from .data_models.types import room_name_t, player_uuid_hex_t, player_name_t


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
        # maybe add a set of usernames to get a check for duplicates faster than iterating over all users?
        self.__players: dict[room_name_t, dict[player_uuid_hex_t, Player]] = {}
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
        self.__players[key] = {}
        return room

    @with_write_lock
    def add_player(self, room: str, player_name: player_name_t) -> Player:
        """
        :return: new Player instance if name is free
        :raises: BadRequest if player name is already taken
        """
        if self.get_player_by_name(room, player_name) is not None:
            raise make_raise_bad_request(f"Username '{player_name}' is already taken.")

        player = Player(player_name)
        self.__players[room][player.uuid] = player

        return player

    @with_read_lock
    def get_player(self, room: str, player_id: player_uuid_hex_t) -> Optional[Player]:
        return self.__players[room].get(player_id, None)

    @with_read_lock
    def get_player_by_name(self, room: str, player_name: player_name_t) -> Optional[Player]:
        players = self.__get_players(room)
        for player in players:
            if player.name == player_name:
                return player

        return None

    @with_read_lock
    def get_players(self, room: str) -> list[Player]:
        return deepcopy(self.__get_players(room))

    def __get_players(self, room: str) -> list[Player]:
        return [*self.__players[room].values()]

    @with_read_lock
    def get_players_to_transmit(self, room: str) -> list[dict]:
        return [player.to_transmit for player in self.__players[room].values()]

    @with_write_lock
    def remove_player(self, room: str, player_uuid: player_uuid_hex_t):
        players = self.__players[room]
        if player_uuid in players:
            del players[player_uuid]

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


