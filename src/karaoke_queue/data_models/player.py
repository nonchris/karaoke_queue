import datetime as dt
from dataclasses import dataclass
from typing import Union
from uuid import uuid4

from .types import datetime_string_t, player_uuid_hex_t, player_name_t


@dataclass
class Player:
    name: player_name_t
    uuid: player_uuid_hex_t = None
    joined: dt.datetime = dt.datetime.now()

    def __post_init__(self):
        self.uuid = uuid4().hex if self.uuid is None else self.uuid

    @property
    def to_transmit(self):
        return {"name": self.name,
                "uuid": self.uuid,
                "joined": self.joined.timestamp()}
