import datetime as dt
from dataclasses import dataclass
from typing import Union

from .types import datetime_string_t


datetime_str_format = "%Y-%m-%d %H:%M:%S.%f"


@dataclass
class Song:
    title: str
    artist: str
    duration: float = None
    _last_time_played: Union[dt.datetime, datetime_string_t] = None
    prev_times_played: list[dt.datetime] = None

    def __query_self(self):
        return songs_db.get_song(self)

    def __post_init__(self):
        # if we get new context over last play time, we write it into object
        if self._last_time_played is not None:
            # parse string to datetime
            if isinstance(self._last_time_played, str):
                self._last_time_played = dt.datetime.strptime(self._last_time_played, datetime_str_format)

    # # TODO: last time played doesn't make any sense in its current form when supporting multiple sessions
    # @property
    # def last_time_played(self) -> dt.datetime:
    #     # try to get more context from database if asked for this value
    #     if self._last_time_played is None:
    #         self._last_time_played = self.__query_self()._last_time_played
    #
    #     return self._last_time_played
    #
    # @last_time_played.setter
    # def last_time_played(self, value: Union[dt.datetime, datetime_string_t]):
    #     self._last_time_played = dt.datetime.strptime(value, datetime_str_format) if isinstance(value, str) else value
    #     songs_db.update_song(self, fields_to_update=("",))

    @property
    def to_transmit(self):
        to_transmit = {
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
        }

        return to_transmit








