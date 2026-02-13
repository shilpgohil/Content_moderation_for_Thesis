

import os
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel


from moderator_api import (
    ModerationRequest, ModerationResponse, 
    ManualReviewRequest, ManualReviewResponse,
    moderate_content, submit_manual_review
)
from analyzer import StrengthAnalyzer
from models import StrengthReport


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Thesis Content Guard API",
    description="Content Moderation + Thesis Strength Analyzer",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.on_event("startup")
async def startup_event():
    logger.info("Pre-warming ML models on startup...")
    try:

        from shared.model_manager import get_spacy, get_sentence_transformer
        get_spacy()
        get_sentence_transformer()
        

        from moderator_api import get_moderator
        get_moderator()
        
        logger.info("All models pre-warmed successfully - ready for requests")
    except Exception as e:
        logger.warning(f"Startup warmup partial failure (non-fatal): {e}")





@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Thesis Content Guard API",
        "endpoints": ["/api/moderate", "/api/analyze", "/api/manual-review"]
    }


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "moderation": "ready",
        "analysis": "ready"
    }




@app.post("/api/moderate", response_model=ModerationResponse)
async def moderate_thesis(request: ModerationRequest):
    try:
        logger.info(f"Moderating content ({len(request.text)} chars)")
        
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text too short")
        
        result = await run_in_threadpool(moderate_content, request.text)
        
        logger.info(f"Moderation result: {result.decision} (risk: {result.risk_score:.2f})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Moderation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/manual-review", response_model=ManualReviewResponse)
async def request_manual_review(request: ManualReviewRequest):
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




class AnalyzeResponse(BaseModel):
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
    try:
        logger.info("Starting thesis analysis")
        
        contents = await file.read()
        text = contents.decode("utf-8")
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Thesis text must be at least 50 characters"
            )
        
        analyzer = StrengthAnalyzer(verbose=True)
        result = await run_in_threadpool(analyzer.analyze, text)
        
        logger.info(f"Analysis complete: {result.overall_score}/100 ({result.grade})")
        return result.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/warmup")
async def warmup():
    try:
        logger.info("Warming up models (manual trigger)...")
        
        from shared.model_manager import get_spacy, get_sentence_transformer
        get_spacy()
        get_sentence_transformer()
        
        from moderator_api import get_moderator
        get_moderator()
        
        logger.info("Warmup complete")
        return {"status": "models loaded"}
        
    except Exception as e:
        logger.error(f"Warmup failed: {e}", exc_info=True)
        return {"status": "warmup failed", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
