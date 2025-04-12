from typing import Optional
from pydantic import BaseModel

from app.domain.schemas.roomtype import RoomTypeResponse

# Room Schemas
class RoomBase(BaseModel):
    room_number: str
    floor: int
    is_available: bool = True
    room_type_id: int

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    floor: Optional[int] = None
    is_available: Optional[bool] = None
    room_type_id: Optional[int] = None

class RoomResponse(RoomBase):
    id: int
    room_type: RoomTypeResponse
    
    class Config:
        from_attributes = True
