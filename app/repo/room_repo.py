from sqlalchemy.orm import Session
from typing import List, Optional

from app.domain.models.room import Room
from app.domain.models.roomtype import RoomType
from app.domain.schemas.room import RoomCreate, RoomUpdate, RoomTypeCreate, RoomTypeUpdate

class RoomRepository:
    def create_room_type(self, db: Session, room_type: RoomTypeCreate) -> RoomType:
        db_room_type = RoomType(
            name=room_type.name,
            description=room_type.description,
            price_per_night=room_type.price_per_night
        )
        db.add(db_room_type)
        db.commit()
        db.refresh(db_room_type)
        return db_room_type
    
    def get_room_type(self, db: Session, room_type_id: int) -> Optional[RoomType]:
        return db.query(RoomType).filter(RoomType.id == room_type_id).first()
    
    def get_room_types(self, db: Session, skip: int = 0, limit: int = 100) -> List[RoomType]:
        return db.query(RoomType).offset(skip).limit(limit).all()
    
    def update_room_type(self, db: Session, room_type_id: int, room_type: RoomTypeUpdate) -> Optional[RoomType]:
        db_room_type = self.get_room_type(db, room_type_id)
        if db_room_type:
            update_data = room_type.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_room_type, key, value)
            db.commit()
            db.refresh(db_room_type)
        return db_room_type
    
    def delete_room_type(self, db: Session, room_type_id: int) -> bool:
        db_room_type = self.get_room_type(db, room_type_id)
        if db_room_type:
            db.delete(db_room_type)
            db.commit()
            return True
        return False
    
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