from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.domain.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.usecase.room_service import RoomService

router = APIRouter()
service = RoomService()

@router.post("/rooms/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    return service.create_room(db, room)

@router.get("/rooms/", response_model=List[RoomResponse])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = service.get_rooms(db, skip, limit)
    return rooms

@router.get("/rooms/{room_id}", response_model=RoomResponse)
def read_room(room_id: int, db: Session = Depends(get_db)):
    room = service.get_room(db, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/rooms/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, room: RoomUpdate, db: Session = Depends(get_db)):
    updated_room = service.update_room(db, room_id, room)
    if updated_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated_room

@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    success = service.delete_room(db, room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return None
