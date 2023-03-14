from copy import deepcopy
from typing import Callable

from .data_models.read_write_lock import ReadWriteLock, with_write_lock, with_read_lock
from .data_models.session import Session
from .data_models.types import session_name_t


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


class SessionManager:
    """ Threadsafe session manager """

    def __init__(self):
        self.__sessions: dict[session_name_t, Session] = {}
        self.lock = ReadWriteLock()

    @with_write_lock
    def add_session(self, key: session_name_t) -> Session:
        """
        If the sessions key already exists a number will be added like
        "cool_session" -> "cool_session-1"
        :return: the session with unique name and other properties
        """
        key_base = key
        i = 1
        while key in self.__sessions:
            key = f"{key_base}-{i}"
            i += 1

        session = Session(key)
        self.__sessions[key] = session
        return session

    @with_read_lock
    def get_session(self, key: session_name_t):
        return self.__sessions.get(key, None)

    @property
    def sessions(self):
        return deepcopy(self.__sessions)


if __name__ == '__main__':
    s = SessionManager()
    name = s.add_session("hi", 42)
    print(name)
    name2 = s.add_session("hi", 43)

    print(name2)

    print(s.sessions)


