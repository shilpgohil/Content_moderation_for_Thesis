"""
Moderator API - Content moderation wrapper for FastAPI.
Provides gatekeeper functionality before thesis analysis.
"""

import os
from typing import List, Optional
from pydantic import BaseModel
from content_moderation import ContentModerator
from content_moderation.config import LIGHTWEIGHT_CONFIG, DEFAULT_CONFIG


# Use lightweight mode for free tier deployment (512MB RAM)
USE_LIGHTWEIGHT = os.getenv("LIGHTWEIGHT_MODE", "true").lower() == "true"

# Singleton moderator instance (lazy loaded)
_moderator_instance = None


class ModerationRequest(BaseModel):
    """Request body for moderation endpoint."""
    text: str


class ModerationIssue(BaseModel):
    """Individual moderation issue with fix suggestion."""
    type: str
    found: str
    suggestion: str


class ModerationResponse(BaseModel):
    """Response from moderation endpoint."""
    decision: str  # PASS, FLAG, BLOCK
    risk_score: float
    is_finance_related: bool
    issues: List[ModerationIssue]
    explanation: str
    can_proceed: bool


class ManualReviewRequest(BaseModel):
    """Request body for manual review submission."""
    text: str
    reason: str
    user_email: str


class ManualReviewResponse(BaseModel):
    """Response from manual review submission."""
    status: str
    review_id: str
    message: str


def get_moderator() -> ContentModerator:
    """Get or create the moderator singleton."""
    global _moderator_instance
    if _moderator_instance is None:
        config = LIGHTWEIGHT_CONFIG if USE_LIGHTWEIGHT else DEFAULT_CONFIG
        print(f"[ModeratorAPI] Initializing moderator (lightweight={USE_LIGHTWEIGHT})")
        _moderator_instance = ContentModerator(config=config)
    return _moderator_instance


def _get_suggestion(flag: str) -> str:
    """Generate helpful suggestion based on flag type."""
    suggestions = {
        "scam": "Remove promotional language, guaranteed returns claims, or contact solicitations.",
        "toxicity": "Remove offensive language, personal attacks, or hostile content.",
        "off_topic": "Ensure your thesis focuses on investment strategy and financial analysis.",
        "low_substance": "Add more specific data, analysis, or evidence to support your claims.",
        "external_redirect": "Remove external links or contact information.",
        "empty_content": "Please enter your investment thesis text."
    }
    
    # Match flag to suggestion
    flag_lower = flag.lower()
    for key, suggestion in suggestions.items():
        if key in flag_lower:
            return suggestion
    
    return "Review and revise the flagged content."


def _extract_found_text(flag: str, original_text: str) -> str:
    """Extract the text that triggered the flag."""
    # Try to extract specific phrase from flag
    if ":" in flag:
        parts = flag.split(":", 1)
        if len(parts) > 1:
            return parts[1].strip()[:100]
    return flag[:100]


def moderate_content(text: str) -> ModerationResponse:
    """
    Moderate content and return structured response.
    
    Returns:
        ModerationResponse with decision, issues, and whether user can proceed.
    """
    moderator = get_moderator()
    result = moderator.moderate(text)
    
    # Convert flags to structured issues
    issues = []
    for flag in result.get("flags", []):
        issue_type = "scam" if "scam" in flag.lower() else \
                     "toxicity" if any(t in flag.lower() for t in ["toxic", "profan", "hate"]) else \
                     "off_topic" if "topic" in flag.lower() else \
                     "other"
        
        issues.append(ModerationIssue(
            type=issue_type,
            found=_extract_found_text(flag, text),
            suggestion=_get_suggestion(flag)
        ))
    
    decision = result.get("decision", "FLAG")
    
    # User can only proceed if decision is PASS
    # FLAG and BLOCK both require edits (per user requirement)
    can_proceed = decision == "PASS"
    
    return ModerationResponse(
        decision=decision,
        risk_score=result.get("risk_score", 0.0),
        is_finance_related=result.get("is_finance_related", False),
        issues=issues,
        explanation=result.get("explanation", ""),
        can_proceed=can_proceed
    )


def submit_manual_review(request: ManualReviewRequest) -> ManualReviewResponse:
    """
    Submit content for manual review.
    
    In a production system, this would:
    1. Store the request in a database
    2. Send email notification to admin
    3. Return a tracking ID
    
    For now, we just log and return a mock response.
    """
    import uuid
    review_id = str(uuid.uuid4())[:8]
    
    # TODO: Implement actual storage/notification
    print(f"[ManualReview] Submitted review {review_id} from {request.user_email}")
    print(f"[ManualReview] Reason: {request.reason}")
    print(f"[ManualReview] Text length: {len(request.text)} chars")
    
    return ManualReviewResponse(
        status="submitted",
        review_id=review_id,
        message=f"Your request has been submitted (ID: {review_id}). We'll review within 24 hours."
    )
