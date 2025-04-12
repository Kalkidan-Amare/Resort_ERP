from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.domain.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.repo.booking_repo import BookingRepository

class BookingService:
    def __init__(self):
        self.repository = BookingRepository()
    
    def create_booking(self, db: Session, booking: BookingCreate) -> BookingResponse:
        try:
            return self.repository.create_booking(db, booking)
        except ValueError as e:
            raise ValueError(str(e))
    
    def get_booking(self, db: Session, booking_id: int) -> Optional[BookingResponse]:
        return self.repository.get_booking(db, booking_id)
    
    def get_bookings(self, db: Session, skip: int = 0, limit: int = 100) -> List[BookingResponse]:
        return self.repository.get_bookings(db, skip, limit)
    
    def get_bookings_by_email(self, db: Session, email: str) -> List[BookingResponse]:
        return self.repository.get_bookings_by_email(db, email)
    
    def update_booking(self, db: Session, booking_id: int, booking: BookingUpdate) -> Optional[BookingResponse]:
        try:
            return self.repository.update_booking(db, booking_id, booking)
        except ValueError as e:
            raise ValueError(str(e))
    
    def delete_booking(self, db: Session, booking_id: int) -> bool:
        return self.repository.delete_booking(db, booking_id)
    
    def confirm_booking(self, db: Session, booking_id: int) -> Optional[BookingResponse]:
        return self.repository.confirm_booking(db, booking_id) 