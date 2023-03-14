import datetime as dt
from dataclasses import dataclass
from typing import Union
from uuid import uuid4

from .types import datetime_string_t, player_uuid_hex_t


@dataclass
class Player:
    name: str
    uuid: player_uuid_hex_t = uuid4().hex
    joined: dt.datetime = dt.datetime.now()

    @property
    def to_transmit(self):
        return {"name": self.name,
                "uuid": self.uuid,
                "joined": self.joined.timestamp()}
