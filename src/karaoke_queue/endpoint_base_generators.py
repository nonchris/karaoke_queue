from .data_models.room import Room


def get_room_admin_endpoint(room: Room, base="/v1/manage/{}/{}"):
    return base.format(room.name, room.uuid)


def get_room_user_endpoint(room: Room, base="/v1/user/{}"):
    return base.format(room.name)
