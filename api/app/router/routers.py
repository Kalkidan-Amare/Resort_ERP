from fastapi import APIRouter
from app.router.endpoints.room_router import router as room_router
from app.router.endpoints.roomtype_router import router as roomtype_router
from app.router.endpoints.booking_router import router as booking_router

router = APIRouter()
router.include_router(room_router, prefix="/api", tags=["rooms"])
router.include_router(roomtype_router, prefix="/api", tags=["room_types"])
router.include_router(booking_router, prefix="/api", tags=["bookings"])
