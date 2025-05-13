from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.domain.models.booking import Booking
from app.domain.models.room import Room
from app.domain.schemas.booking import BookingCreate, BookingUpdate

class BookingRepository:
    def create_booking(self, db: Session, booking: BookingCreate) -> Booking:
        # Check if the room is available for the booking period
        is_available = self._check_room_availability(
            db, 
            booking.room_id, 
            booking.check_in_time, 
            booking.check_out_time
        )
        
        if not is_available:
            raise ValueError("Room is not available for the selected dates")
        
        db_booking = Booking(
            room_id=booking.room_id,
            email=booking.email,
            phone=booking.phone,
            check_in_time=booking.check_in_time,
            check_out_time=booking.check_out_time
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        
        # Update room availability
        self._update_room_availability(db, booking.room_id, False)
        
        return db_booking
    
    def get_booking(self, db: Session, booking_id: int) -> Optional[Booking]:
        return db.query(Booking).filter(Booking.id == booking_id).first()
    
    def get_bookings(self, db: Session, skip: int = 0, limit: int = 100) -> List[Booking]:
        return db.query(Booking).offset(skip).limit(limit).all()
    
    def get_bookings_by_email(self, db: Session, email: str) -> List[Booking]:
        return db.query(Booking).filter(Booking.email == email).all()
    
    def update_booking(self, db: Session, booking_id: int, booking: BookingUpdate) -> Optional[Booking]:
        db_booking = self.get_booking(db, booking_id)
        if db_booking:
            update_data = booking.dict(exclude_unset=True)
            
            # If updating check-in or check-out times, check availability
            if 'check_in_time' in update_data or 'check_out_time' in update_data:
                check_in = update_data.get('check_in_time', db_booking.check_in_time)
                check_out = update_data.get('check_out_time', db_booking.check_out_time)
                
                # Exclude the current booking from availability check
                if not self._check_room_availability(db, db_booking.room_id, check_in, check_out, exclude_booking_id=booking_id):
                    raise ValueError("Room is not available for the selected dates")
            
            for key, value in update_data.items():
                setattr(db_booking, key, value)
            
            db.commit()
            db.refresh(db_booking)
        return db_booking
    
    def delete_booking(self, db: Session, booking_id: int) -> bool:
        db_booking = self.get_booking(db, booking_id)
        if db_booking:
            # Free up the room
            self._update_room_availability(db, db_booking.room_id, True)
            
            db.delete(db_booking)
            db.commit()
            return True
        return False
    
    def confirm_booking(self, db: Session, booking_id: int) -> Optional[Booking]:
        db_booking = self.get_booking(db, booking_id)
        if db_booking:
            db_booking.is_confirmed = True
            db.commit()
            db.refresh(db_booking)
        return db_booking
    
    def _check_room_availability(self, db: Session, room_id: int, check_in: datetime, check_out: datetime, exclude_booking_id: Optional[int] = None) -> bool:
        """Check if a room is available for a specific period"""
        query = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.check_out_time > check_in,
            Booking.check_in_time < check_out
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        overlapping_bookings = query.count()
        return overlapping_bookings == 0
    
    def _update_room_availability(self, db: Session, room_id: int, is_available: bool) -> None:
        """Update room availability status"""
        room = db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.is_available = is_available
            db.commit() 