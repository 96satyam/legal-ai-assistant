from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON
from app.core.database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    analysis_type = Column(Text)
    results = Column(JSON) # JSON type is great for storing flexible data
    created_at = Column(TIMESTAMP)