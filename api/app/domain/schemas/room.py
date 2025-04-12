from typing import Optional, List
from pydantic import BaseModel

# Room Type Schemas
class RoomTypeBase(BaseModel):
    name: str
    description: str
    price_per_night: float

class RoomTypeCreate(RoomTypeBase):
    pass

class RoomTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_night: Optional[float] = None

class RoomTypeResponse(RoomTypeBase):
    id: int
    
    class Config:
        from_attributes = True

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
