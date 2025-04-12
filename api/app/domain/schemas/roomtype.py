from typing import Optional
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