from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class LogAnalysis(Base):
    __tablename__ = "log_analyses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    original_logs = Column(Text, nullable=False)
    what_went_wrong = Column(Text, nullable=True)
    where_it_went_wrong = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    severity = Column(String(50), nullable=True)
    raw_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())