import datetime as dt
from dataclasses import dataclass

from .song import Song


@dataclass
class QueueEntry:
    song: Song
    user: str
    time_of_entry: dt.datetime = dt.datetime.now()

    @property
    def to_transmit(self):
        return {
            "user": self.user,
            "time_of_entry": self.time_of_entry.timestamp(),
            "song": self.song.to_transmit,
        }

