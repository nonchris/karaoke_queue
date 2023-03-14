from karaoke_queue.data_models.exceptions import make_bad_request_room_unknown
from karaoke_queue.data_models.room import Room
from karaoke_queue.room_manager import RoomManager

room_manager = RoomManager()


def verify_room_exists(room_name: str) -> Room:
    room = room_manager.get_room(room_name)

    if room is None:
        raise make_bad_request_room_unknown(room_name)

    return room
