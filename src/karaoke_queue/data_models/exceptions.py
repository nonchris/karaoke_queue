from fastapi import status, HTTPException


def raise_bad_request(detail: str):
    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


def raise_bad_request_session_unknown(name: str):
    raise_bad_request(f"Unknown session '{name}'")
