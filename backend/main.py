"""
Thesis Content Guard - Unified Backend API
Combines Content Moderation + Thesis Strength Analyzer

Flow: User submits thesis → Moderation check → If PASS → Thesis analysis
"""

import os
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

# Import modules
from moderator_api import (
    ModerationRequest, ModerationResponse, 
    ManualReviewRequest, ManualReviewResponse,
    moderate_content, submit_manual_review
)
from analyzer import StrengthAnalyzer
from models import StrengthReport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Thesis Content Guard API",
    description="Content Moderation + Thesis Strength Analyzer",
    version="1.0.0"
)

# CORS configuration - Allow frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://thesisguardian.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============ Health Check ============

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Thesis Content Guard API",
        "endpoints": ["/api/moderate", "/api/analyze", "/api/manual-review"]
    }


@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "moderation": "ready",
        "analysis": "ready"
    }


# ============ Content Moderation ============

@app.post("/api/moderate", response_model=ModerationResponse)
async def moderate_thesis(request: ModerationRequest):
    """
    Step 1: Check content before analysis.
    
    Returns decision (PASS/FLAG/BLOCK) with detailed issues and suggestions.
    Only PASS allows proceeding to thesis analysis.
    """
    try:
        logger.info(f"Moderating content ({len(request.text)} chars)")
        
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text too short")
        
        # Run moderation (CPU-bound, use threadpool)
        result = await run_in_threadpool(moderate_content, request.text)
        
        logger.info(f"Moderation result: {result.decision} (risk: {result.risk_score:.2f})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Moderation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============ Manual Review ============

@app.post("/api/manual-review", response_model=ManualReviewResponse)
async def request_manual_review(request: ManualReviewRequest):
    """
    Submit blocked content for manual review.
    
    Users can request human review if they believe their content was wrongly blocked.
    """
    try:
        logger.info(f"Manual review request from {request.user_email}")
        
        if not request.user_email or "@" not in request.user_email:
            raise HTTPException(status_code=400, detail="Valid email required")
        
        result = submit_manual_review(request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual review submission failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============ Thesis Analysis ============

class AnalyzeResponse(BaseModel):
    """Response from thesis analysis."""
    overall_score: float
    grade: str
    component_scores: dict
    quick_stats: dict
    ml_features: dict
    sentence_analyses: list
    synthesis: dict
    audit_table: list
    logic_chain: list
    weakness_report: dict
    consistency_issues: list
    bias_analysis: dict


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_thesis(file: UploadFile = File(...)):
    """
    Step 2: Analyze thesis strength.
    
    Should only be called AFTER moderation returns PASS.
    Accepts file upload (.txt).
    """
    try:
        logger.info("Starting thesis analysis")
        
        # Read file
        contents = await file.read()
        text = contents.decode("utf-8")
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Thesis text must be at least 50 characters"
            )
        
        # Run analysis (heavy, use threadpool)
        analyzer = StrengthAnalyzer(verbose=True)
        result = await run_in_threadpool(analyzer.analyze, text)
        
        logger.info(f"Analysis complete: {result.overall_score}/100 ({result.grade})")
        return result.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============ Warmup Endpoint ============

@app.post("/api/warmup")
async def warmup():
    """
    Preload ML models.
    Call this on deployment startup to reduce cold start latency.
    """
    try:
        logger.info("Warming up models...")
        
        # Warm up moderation
        from moderator_api import get_moderator
        get_moderator()
        
        # Warm up spaCy for analysis
        from shared.model_manager import get_spacy
        get_spacy()
        
        logger.info("Warmup complete")
        return {"status": "models loaded"}
        
    except Exception as e:
        logger.error(f"Warmup failed: {e}", exc_info=True)
        return {"status": "warmup failed", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
