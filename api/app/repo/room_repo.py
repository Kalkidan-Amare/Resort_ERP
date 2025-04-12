from sqlalchemy.orm import Session
from typing import List, Optional

from app.domain.models.room import Room
from app.domain.schemas.room import RoomCreate, RoomUpdate

class RoomRepository:
    def create_room(self, db: Session, room: RoomCreate) -> Room:
        db_room = Room(
            room_number=room.room_number,
            floor=room.floor,
            is_available=room.is_available,
            room_type_id=room.room_type_id
        )
        db.add(db_room)
        db.commit()
        db.refresh(db_room)
        return db_room
    
    def get_room(self, db: Session, room_id: int) -> Optional[Room]:
        return db.query(Room).filter(Room.id == room_id).first()
    
    def get_rooms(self, db: Session, skip: int = 0, limit: int = 100) -> List[Room]:
        return db.query(Room).offset(skip).limit(limit).all()
    
    def update_room(self, db: Session, room_id: int, room: RoomUpdate) -> Optional[Room]:
        db_room = self.get_room(db, room_id)
        if db_room:
            update_data = room.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_room, key, value)
            db.commit()
            db.refresh(db_room)
        return db_room
    
    def delete_room(self, db: Session, room_id: int) -> bool:
        db_room = self.get_room(db, room_id)
        if db_room:
            db.delete(db_room)
            db.commit()
            return True
        return False 
   
    def get_all_rooms(self, db: Session) -> List[Room]:
        return db.query(Room).all()
