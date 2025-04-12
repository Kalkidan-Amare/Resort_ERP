from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationships
    issues_created = relationship("Issue", back_populates="created_by")
    issues_assigned = relationship("Issue", foreign_keys="Issue.assigned_to_id", back_populates="assigned_to")
    issues_escalated = relationship("Issue", foreign_keys="Issue.escalated_by_id", back_populates="escalated_by")
    issues_resolved = relationship("Issue", foreign_keys="Issue.resolved_by_id", back_populates="resolved_by")