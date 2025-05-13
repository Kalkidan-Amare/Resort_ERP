from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

class RoomType(Base):
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price_per_night = Column(Float)
    
    rooms = relationship("Room", back_populates="room_type")
