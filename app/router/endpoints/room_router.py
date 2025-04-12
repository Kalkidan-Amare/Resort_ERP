from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.domain.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
from app.usecase.room_service import RoomService

router = APIRouter()
service = RoomService()

# Room Type routes
@router.post("/room-types/", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
def create_room_type(room_type: RoomTypeCreate, db: Session = Depends(get_db)):
    return service.create_room_type(db, room_type)

@router.get("/room-types/", response_model=List[RoomTypeResponse])
def read_room_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    room_types = service.get_room_types(db, skip, limit)
    return room_types

@router.get("/room-types/{room_type_id}", response_model=RoomTypeResponse)
def read_room_type(room_type_id: int, db: Session = Depends(get_db)):
    room_type = service.get_room_type(db, room_type_id)
    if room_type is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    return room_type

@router.put("/room-types/{room_type_id}", response_model=RoomTypeResponse)
def update_room_type(room_type_id: int, room_type: RoomTypeUpdate, db: Session = Depends(get_db)):
    updated_room_type = service.update_room_type(db, room_type_id, room_type)
    if updated_room_type is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    return updated_room_type

@router.delete("/room-types/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_type(room_type_id: int, db: Session = Depends(get_db)):
    success = service.delete_room_type(db, room_type_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room type not found")
    return None

# Room routes
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
