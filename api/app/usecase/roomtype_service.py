from sqlalchemy.orm import Session
from typing import List, Optional

from app.domain.schemas.roomtype import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
from app.repo.roomtype_repo import RoomTypeRepository

class RoomTypeService:
    def __init__(self):
        self.repository = RoomTypeRepository()
    
    def create_room_type(self, db: Session, room_type: RoomTypeCreate) -> RoomTypeResponse:
        return self.repository.create_room_type(db, room_type)
    
    def get_room_type(self, db: Session, room_type_id: int) -> Optional[RoomTypeResponse]:
        return self.repository.get_room_type(db, room_type_id)
    
    def get_room_types(self, db: Session, skip: int = 0, limit: int = 100) -> List[RoomTypeResponse]:
        return self.repository.get_room_types(db, skip, limit)
    
    def update_room_type(self, db: Session, room_type_id: int, room_type: RoomTypeUpdate) -> Optional[RoomTypeResponse]:
        return self.repository.update_room_type(db, room_type_id, room_type)
    
    def delete_room_type(self, db: Session, room_type_id: int) -> bool:
        return self.repository.delete_room_type(db, room_type_id) 