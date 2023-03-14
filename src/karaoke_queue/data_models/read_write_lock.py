# Credits: ChatGPT, modified by chris

import threading
from typing import Callable


class ReadWriteLock:
    def __init__(self):
        self._lock = threading.RLock()  # RLock so a thread can enter a read process after write
        self._read_ready = threading.Condition(self._lock)
        self._readers = 0

    def acquire_read(self):
        """Acquire a read lock. Multiple threads can hold this type of lock.
        It is exclusive with write locks."""
        self._read_ready.acquire()
        try:
            self._readers += 1
        finally:
            self._read_ready.release()

    def release_read(self):
        """Release a read lock."""
        self._read_ready.acquire()
        try:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()
        finally:
            self._read_ready.release()

    def acquire_write(self):
        """Acquire a write-lock. Only one thread can hold this lock, and
        only when no read locks are also held."""
        self._read_ready.acquire()
        # ensures that the lock is only taken when there really are no reading threads left
        # if readers are left the thread will release the lock and wait again
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
        """Release a write-lock."""
        self._read_ready.release()

    def __enter__(self):
        """ Only here to notify the user how to use it properly """
        if self.__class__ is ReadWriteLock:
            raise ValueError("Use `with lock.read:` or `with lock.write:` instead")

    @property
    def read(self):
        """Context manager for read lock.
        Use `with lock.read:` to acquire and release the lock.
        """
        return _RWLockContextManager(self, read=True)

    @property
    def write(self):
        """Context manager for write lock.
        Use `with lock.write:` to acquire and release the lock.
        """
        return _RWLockContextManager(self, read=False)


class _RWLockContextManager:
    """ Helper class to enable two different context-managers for read and write mode"""
    def __init__(self, lock: ReadWriteLock, read: bool):
        self._lock = lock
        self._read = read

    def __enter__(self):
        if self._read:
            self._lock.acquire_read()
        else:
            self._lock.acquire_write()

    def __exit__(self, *args):
        if self._read:
            self._lock.release_read()
        else:
            self._lock.release_write()


def with_read_lock(fn: Callable):
    """
    Decorator that makes your function allocate the classes rw-lock in read-mode
    Ths **requires** the lock of the class to be accessible as `self.lock`
    """
    def threaded_wrapper(self, *args, **kwargs):
        with self.lock.read:
            return fn(self, *args, **kwargs)

    return threaded_wrapper


def with_write_lock(fn: Callable):
    """
    Decorator that makes your function allocate the classes rw-lock in write-mode
    Ths **requires** the lock of the class to be accessible as `self.lock`
    """
    def threaded_wrapper(self, *args, **kwargs):
        with self.lock.write:
            return fn(self, *args, **kwargs)

    return threaded_wrapper
