from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.domain.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.usecase.booking_service import BookingService

router = APIRouter()
service = BookingService()

@router.post("/bookings/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    try:
        return service.create_booking(db, booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/bookings/", response_model=List[BookingResponse])
def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = service.get_bookings(db, skip, limit)
    return bookings

@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = service.get_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.get("/bookings/email/{email}", response_model=List[BookingResponse])
def read_bookings_by_email(email: str, db: Session = Depends(get_db)):
    bookings = service.get_bookings_by_email(db, email)
    return bookings

@router.put("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, booking: BookingUpdate, db: Session = Depends(get_db)):
    try:
        updated_booking = service.update_booking(db, booking_id, booking)
        if updated_booking is None:
            raise HTTPException(status_code=404, detail="Booking not found")
        return updated_booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    success = service.delete_booking(db, booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return None

@router.post("/bookings/{booking_id}/confirm", response_model=BookingResponse)
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    confirmed_booking = service.confirm_booking(db, booking_id)
    if confirmed_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return confirmed_booking 


'''
Your booking system now includes the following features:
Creating room bookings with email, phone, and date range
Smart room availability checking to prevent booking conflicts
Searching bookings by ID or email
Updating booking details
Confirming bookings
Automatic room availability status management
The API endpoints are accessible at:
POST /api/bookings/ - Create a new booking
GET /api/bookings/ - List all bookings
GET /api/bookings/{booking_id} - Get booking by ID
GET /api/bookings/email/{email} - Get bookings by email
PUT /api/bookings/{booking_id} - Update a booking
DELETE /api/bookings/{booking_id} - Delete a booking
POST /api/bookings/{booking_id}/confirm - Confirm a booking
The system will automatically prevent double bookings and update room availability.
'''