from typing import Optional, List
from pydantic import BaseModel

class IssueInput(BaseModel):
    title: str
    description: str
    status: str
    priority: str
    assigned_to: Optional[int] = None
    photo: Optional[str] = None