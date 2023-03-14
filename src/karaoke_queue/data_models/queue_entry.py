import datetime as dt
from dataclasses import dataclass

from .player import Player
from .song import Song


@dataclass
class QueueEntry:
    song: Song
    player: Player
    time_of_entry: dt.datetime = dt.datetime.now()

    @property
    def to_transmit(self):
        return {
            "player": self.player.to_transmit,
            "time_of_entry": self.time_of_entry.timestamp(),
            "song": self.song.to_transmit,
        }

