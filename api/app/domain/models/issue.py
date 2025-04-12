from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_type = Column(String, index=True)
    catagory = Column(String)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="Open")
    priority = Column(String)
    assigned_to = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    resolved_at = Column(String)
    closed_at = Column(String)
    escalated_at = Column(String)
    picture_url = Column(String)
    closed_by = Column(String)
    escalated_by = Column(String)
    # Change created_by to store the user's ID instead of a string.
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", back_populates="issues_created")

    # Change assigned_to to store the user's ID instead of a string.
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="issues_assigned")

    # Change escalated_by to store the user's ID instead of a string.
    escalated_by_id = Column(Integer, ForeignKey("users.id"))
    escalated_by = relationship("User", foreign_keys=[escalated_by_id], back_populates="issues_escalated")

    # Add resolved_by association to store the user's ID.
    resolved_by_id = Column(Integer, ForeignKey("users.id"))
    resolved_by = relationship("User", foreign_keys=[resolved_by_id], back_populates="issues_resolved")

    # Add room association using room_id.
    room_id = Column(Integer, ForeignKey("rooms.id"))
    room = relationship("Room", back_populates="issues")