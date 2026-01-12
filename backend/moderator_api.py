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
    """
    Find the exact occurrence of a term in the original text.
    Returns the matched word/phrase as found in the text (preserving case).
    """
    import re
    text_lower = text.lower()
    term_lower = term.lower()
    
    # For single words, use word boundary matching to get exact word
    if ' ' not in term_lower and len(term_lower) <= 20:
        pattern = r'\b' + re.escape(term_lower) + r'\w*\b'
        match = re.search(pattern, text_lower)
        if match:
            # Return the word as it appears in original text (preserves case)
            return text[match.start():match.end()]
    else:
        # For phrases, find exact position
        pos = text_lower.find(term_lower)
        if pos != -1:
            return text[pos:pos + len(term)]
    
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
    
    # Extract detailed information from flags - show ALL issues, no deduplication
    for flag in result.get("flags", []):
        # Parse flag format: "type:detail" or "toxic:category:term" or just "type"
        parts = flag.split(":")
        flag_type = parts[0].strip() if parts else flag.strip()
        
        # Determine issue category and matched text based on flag format
        if flag_type == "toxic":
            if len(parts) >= 3:
                # New format: toxic:category:term
                issue_type = parts[1].strip()
                matched_text = parts[2].strip()
            elif len(parts) == 2:
                # Old format: toxic:category
                issue_type = parts[1].strip()
                matched_text = _find_flagged_toxic_word(text, issue_type)
            else:
                issue_type = "toxicity"
                matched_text = _find_flagged_toxic_word(text, issue_type)
        elif flag_type == "scam":
            issue_type = "scam"
            matched_text = parts[1].strip() if len(parts) > 1 else "promotional content"
        elif flag_type == "fuzzy":
            issue_type = "scam (misspelled)"
            matched_text = parts[1].strip() if len(parts) > 1 else ""
        elif flag_type == "semantic":
            issue_type = "similar to scam"
            matched_text = parts[1].strip() if len(parts) > 1 else ""
        else:
            issue_type = flag_type
            matched_text = parts[1].strip() if len(parts) > 1 else flag_type
        
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
    Loads terms from toxic_terms.json and searches for exact matches.
    """
    import json
    import re
    from pathlib import Path
    
    text_lower = text.lower()
    
    # Load toxic terms from JSON
    data_path = Path(__file__).parent / "content_moderation" / "data" / "toxic_terms.json"
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            toxic_data = json.load(f)
    except Exception:
        # Fallback if file not found
        return category.replace("_", " ")
    
    # Map category names to JSON keys
    category_mapping = {
        "severe_profanity": "severe_profanity",
        "mild_profanity": "mild_profanity",
        "personal_attack": "personal_attacks",
        "hate_speech": "hate_speech_patterns",
        "threat": "threat_patterns",
        "harassment": "harassment_patterns",
        "mockery": "mockery_patterns",
        "doxxing": "doxxing_patterns",
        "defamation": "defamation_patterns",
        "spam": "spam_indicators",
    }
    
    # Find which JSON key to use
    json_key = None
    category_lower = category.lower()
    for cat_name, key in category_mapping.items():
        if cat_name in category_lower:
            json_key = key
            break
    
    # If no specific mapping, try all categories
    if json_key:
        terms_to_check = toxic_data.get(json_key, [])
    else:
        # Check ALL categories to find the match
        terms_to_check = []
        for key, terms in toxic_data.items():
            if isinstance(terms, list):
                terms_to_check.extend(terms)
    
    # Search for each term in the text
    for term in terms_to_check:
        term_lower = term.lower()
        
        # For single words, use word boundary matching
        if ' ' not in term_lower and len(term_lower) <= 15:
            pattern = r'\b' + re.escape(term_lower) + r'\w*\b'
            match = re.search(pattern, text_lower)
            if match:
                # Return the actual matched text from original (preserves case)
                return text[match.start():match.end()]
        else:
            # For phrases, use substring match
            pos = text_lower.find(term_lower)
            if pos != -1:
                return text[pos:pos + len(term)]
    
    # If nothing found, return cleaned category name
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
