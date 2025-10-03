from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime

    class Config:
        from_attributes = True # Helps Pydantic work with SQLAlchemy models