from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(Text)
    file_path = Column(Text)
    document_type = Column(Text)
    upload_date = Column(TIMESTAMP)

class Clause(Base):
    __tablename__ = "clauses"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    clause_type = Column(Text)
    content = Column(Text)
    risk_level = Column(Text)
    position = Column(Integer)