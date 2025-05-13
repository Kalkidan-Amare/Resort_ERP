from sqlalchemy.orm import Session
from typing import List, Optional

from app.domain.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.repo.room_repo import RoomRepository

class RoomService:
    def __init__(self):
        self.repository = RoomRepository()
    
    def create_room(self, db: Session, room: RoomCreate) -> RoomResponse:
        return self.repository.create_room(db, room)
    
    def get_room(self, db: Session, room_id: int) -> Optional[RoomResponse]:
        return self.repository.get_room(db, room_id)
    
    def get_rooms(self, db: Session, skip: int = 0, limit: int = 100) -> List[RoomResponse]:
        return self.repository.get_rooms(db, skip, limit)
    
    def update_room(self, db: Session, room_id: int, room: RoomUpdate) -> Optional[RoomResponse]:
        return self.repository.update_room(db, room_id, room)
    
    def delete_room(self, db: Session, room_id: int) -> bool:
        return self.repository.delete_room(db, room_id)
