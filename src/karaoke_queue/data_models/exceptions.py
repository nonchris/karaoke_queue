from fastapi import status, HTTPException


def make_raise_bad_request(detail: str):
    return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


def make_bad_request_room_unknown(name: str):
    return make_raise_bad_request(f"Unknown room '{name}'")


def make_internal_server_error(detail: str):
    return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
