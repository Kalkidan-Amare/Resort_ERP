from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Booking Schemas
class BookingBase(BaseModel):
    room_id: int
    email: EmailStr
    phone: str
    check_in_time: datetime
    check_out_time: datetime

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    is_confirmed: Optional[bool] = None

class BookingResponse(BookingBase):
    id: int
    is_confirmed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True 