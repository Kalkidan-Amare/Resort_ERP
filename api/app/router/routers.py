from fastapi import APIRouter
from app.router.endpoints.room_router import router as room_router

router = APIRouter()
router.include_router(room_router, prefix="/api", tags=["rooms"])
