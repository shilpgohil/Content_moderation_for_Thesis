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


def _get_detailed_suggestion(issue_type: str, matched_text: str) -> str:
    """Generate specific, actionable suggestions based on issue type and matched content."""
    suggestions = {
        "severe_profanity": f"Remove the profane language: \"{matched_text}\". Use professional language instead.",
        "mild_profanity": f"Consider removing \"{matched_text}\" for a more professional tone.",
        "personal_attack": f"Remove the personal attack: \"{matched_text}\". Focus on the investment argument.",
        "hate_speech": f"Remove hate speech content. This type of language is not acceptable.",
        "threat": f"Remove threatening language: \"{matched_text}\". Keep content civil.",
        "harassment": f"Remove harassment: \"{matched_text}\". Maintain respectful discourse.",
        "defamation": f"Remove potentially defamatory statement about: \"{matched_text}\".",
        "scam": f"Remove scam-like language: \"{matched_text}\". Avoid guaranteed returns claims.",
        "off_topic": "Ensure your content focuses on investment analysis and financial strategy.",
        "low_finance_relevance": "Add more specific financial data, metrics, and investment reasoning.",
        "external_redirect": f"Remove external links or contact info: \"{matched_text}\".",
        "spam": "Remove promotional content and marketing language.",
    }
    
    for key, suggestion in suggestions.items():
        if key in issue_type.lower():
            return suggestion
    
    return f"Review and revise: \"{matched_text[:50]}...\""


def _find_text_in_content(text: str, term: str) -> str:
    """Find the exact occurrence of a term in the original text with context."""
    import re
    text_lower = text.lower()
    term_lower = term.lower()
    
    # Find position in original text
    pos = text_lower.find(term_lower)
    if pos != -1:
        # Extract with some context (10 chars before and after)
        start = max(0, pos - 10)
        end = min(len(text), pos + len(term) + 10)
        excerpt = text[start:end]
        
        # Clean up: find word boundaries
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."
        
        return excerpt.strip()
    
    return term


def moderate_content(text: str) -> ModerationResponse:
    """
    Moderate content and return structured response with DETAILED issue information.
    
    Returns:
        ModerationResponse with decision, detailed issues showing exact flagged text,
        and whether user can proceed.
    """
    moderator = get_moderator()
    result = moderator.moderate(text)
    
    issues = []
    seen_types = set()  # Avoid duplicate issue types
    
    # Extract detailed information from flags
    for flag in result.get("flags", []):
        # Parse flag format: "type:matched" or just "type"
        if ":" in flag:
            parts = flag.split(":", 1)
            flag_type = parts[0].strip()
            flag_detail = parts[1].strip()
        else:
            flag_type = flag.strip()
            flag_detail = flag.strip()
        
        # Skip duplicates of same type
        if flag_type in seen_types:
            continue
        seen_types.add(flag_type)
        
        # Determine issue category and get matched text
        if flag_type == "toxic":
            issue_type = flag_detail  # e.g., "severe_profanity"
            # For toxicity, we need to find the actual word in the text
            matched_text = _find_flagged_toxic_word(text, issue_type)
        elif flag_type == "scam":
            issue_type = "scam"
            matched_text = flag_detail if flag_detail else "promotional content"
        elif flag_type == "fuzzy":
            issue_type = "scam (misspelled)"
            matched_text = flag_detail
        elif flag_type == "semantic":
            issue_type = "similar to scam"
            matched_text = flag_detail
        else:
            issue_type = flag_type
            matched_text = flag_detail
        
        # Find the actual text in the user's content for context
        found_excerpt = _find_text_in_content(text, matched_text) if matched_text else issue_type
        
        issues.append(ModerationIssue(
            type=issue_type.replace("_", " ").title(),
            found=found_excerpt,
            suggestion=_get_detailed_suggestion(issue_type, matched_text)
        ))
    
    decision = result.get("decision", "FLAG")
    can_proceed = decision == "PASS"
    
    return ModerationResponse(
        decision=decision,
        risk_score=result.get("risk_score", 0.0),
        is_finance_related=result.get("is_finance_related", False),
        issues=issues,
        explanation=result.get("explanation", ""),
        can_proceed=can_proceed
    )


def _find_flagged_toxic_word(text: str, category: str) -> str:
    """
    Find the actual toxic word in the text based on category.
    This checks against common patterns to extract the exact flagged term.
    """
    import re
    text_lower = text.lower()
    
    # Common severe profanity patterns
    severe_patterns = [
        r'\bf+u+c+k+\w*',
        r'\bs+h+i+t+\w*',
        r'\ba+s+s+\b',
        r'\bb+i+t+c+h+\w*',
        r'\bc+u+n+t+\w*',
        r'\bd+a+m+n+\w*',
    ]
    
    if "profan" in category.lower():
        for pattern in severe_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return text[match.start():match.end()]
    
    if "attack" in category.lower():
        attack_patterns = [r'\bidiot\w*', r'\bstupid\w*', r'\bmoron\w*', r'\btrash\b', r'\bloser\w*']
        for pattern in attack_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return text[match.start():match.end()]
    
    # Default: return category name if nothing specific found
    return category.replace("_", " ")


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
