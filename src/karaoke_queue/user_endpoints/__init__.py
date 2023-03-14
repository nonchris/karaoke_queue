from fastapi import APIRouter

from ..session_manager import SessionManager

router = APIRouter(
    prefix="/v1/manage"
)
session_manager = SessionManager()

