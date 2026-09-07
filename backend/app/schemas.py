from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LogAnalysisCreate(BaseModel):
    title: str
    original_logs: str

class LogAnalysisResponse(BaseModel):
    id: int
    title: str
    original_logs: str
    what_went_wrong: Optional[str] = None
    where_it_went_wrong: Optional[str] = None
    suggested_fix: Optional[str] = None
    severity: Optional[str] = None
    raw_analysis: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LogAnalysisList(BaseModel):
    id: int
    title: str
    severity: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True