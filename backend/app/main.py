from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
import logging

from .database import engine, get_db, Base
from .models import LogAnalysis
from .schemas import LogAnalysisCreate, LogAnalysisResponse, LogAnalysisList

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create database tables on startup
Base.metadata.create_all(bind=engine)

# initialise FastAPI app
app = FastAPI(
    title="AI Log Analyser - Backend",
    description="Backend API for the AI Log Analyser application",
    version="1.0.0"
)

# configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI service URL from environment variable
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}

@app.post("/api/analyse", response_model=LogAnalysisResponse)
async def create_analysis(
    request: LogAnalysisCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating analysis for: {request.title}")

    # save initial record to database
    db_analysis = LogAnalysis(
        title=request.title,
        original_logs=request.original_logs
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    try:
        # call AI service
        async with httpx.AsyncClient(timeout=60.0) as client:
            ai_response = await client.post(
                f"{AI_SERVICE_URL}/analyse",
                json={
                    "logs": request.original_logs,
                    "context": ""
                }
            )
            ai_response.raise_for_status()
            ai_data = ai_response.json()

        # update database record with AI analysis
        db_analysis.what_went_wrong = ai_data["what_went_wrong"]
        db_analysis.where_it_went_wrong = ai_data["where_it_went_wrong"]
        db_analysis.suggested_fix = ai_data["suggested_fix"]
        db_analysis.severity = ai_data["severity"]
        db_analysis.raw_analysis = ai_data["raw_analysis"]
        db.commit()
        db.refresh(db_analysis)

        logger.info(f"Analysis complete for ID: {db_analysis.id}")
        return db_analysis

    except httpx.TimeoutException:
        logger.error("AI service timed out")
        raise HTTPException(
            status_code=504,
            detail="AI service timed out. Please try again."
        )
    except Exception as e:
        logger.error(f"Error calling AI service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI analysis: {str(e)}"
        )

@app.get("/api/analyses", response_model=List[LogAnalysisList])
async def get_analyses(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    analyses = db.query(LogAnalysis)\
        .order_by(LogAnalysis.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return analyses

@app.get("/api/analyses/{analysis_id}", response_model=LogAnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    analysis = db.query(LogAnalysis)\
        .filter(LogAnalysis.id == analysis_id)\
        .first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    return analysis

@app.delete("/api/analyses/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    analysis = db.query(LogAnalysis)\
        .filter(LogAnalysis.id == analysis_id)\
        .first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )

    db.delete(analysis)
    db.commit()
    return {"message": f"Analysis {analysis_id} deleted successfully"}