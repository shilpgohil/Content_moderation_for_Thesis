

import os
from typing import List, Optional
from pydantic import BaseModel
from content_moderation import ContentModerator
from content_moderation.config import LIGHTWEIGHT_CONFIG, DEFAULT_CONFIG



USE_LIGHTWEIGHT = os.getenv("LIGHTWEIGHT_MODE", "true").lower() == "true"


_moderator_instance = None


class ModerationRequest(BaseModel):
    text: str


class ModerationIssue(BaseModel):
    type: str
    found: str
    suggestion: str


class ModerationResponse(BaseModel):
    decision: str  # PASS, FLAG, BLOCK
    risk_score: float
    is_finance_related: bool
    issues: List[ModerationIssue]
    explanation: str
    can_proceed: bool


class ManualReviewRequest(BaseModel):
    text: str
    reason: str
    user_email: str


class ManualReviewResponse(BaseModel):
    status: str
    review_id: str
    message: str


def get_moderator() -> ContentModerator:
    global _moderator_instance
    if _moderator_instance is None:
        config = LIGHTWEIGHT_CONFIG if USE_LIGHTWEIGHT else DEFAULT_CONFIG
        print(f"[ModeratorAPI] Initializing moderator (lightweight={USE_LIGHTWEIGHT})")
        _moderator_instance = ContentModerator(config=config)
    return _moderator_instance


def _get_detailed_suggestion(issue_type: str, matched_text: str) -> str:
    suggestions = {
        "severe_profanity": f"Remove the profane language: \"{matched_text}\". Use professional language instead.",
        "mild_profanity": f"Consider removing \"{matched_text}\" for a more professional tone.",
        "personal_attack": f"Remove the personal attack: \"{matched_text}\". Focus on the investment argument.",
        "hate_speech": "Remove hate speech content. This type of language is not acceptable.",
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
    import re
    text_lower = text.lower()
    term_lower = term.lower()
    
    # For single words, use word boundary matching to get exact word
    if ' ' not in term_lower and len(term_lower) <= 20:
        pattern = r'\b' + re.escape(term_lower) + r'\w*\b'
        match = re.search(pattern, text_lower)
        if match:
            return text[match.start():match.end()]
    else:
        pos = text_lower.find(term_lower)
        if pos != -1:
            return text[pos:pos+len(term)]
    
    return term


def moderate_content(text: str) -> ModerationResponse:
    moderator = get_moderator()
    result = moderator.moderate(text)
    
    issues = []
    
    for flag in result.get("flags", []):
        parts = flag.split(":")
        flag_type = parts[0].strip() if parts else flag.strip()
        
        if flag_type == "toxic":
            if len(parts) >= 3:
                issue_type = parts[1].strip()
                matched_text = parts[2].strip()
            elif len(parts) == 2:
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
    import json
    import re
    from pathlib import Path
    
    text_lower = text.lower()
    
    data_path = Path(__file__).parent / "content_moderation" / "data" / "toxic_terms.json"
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            toxic_data = json.load(f)
    except Exception:
        return category.replace("_", " ")
    
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
    
    json_key = None
    category_lower = category.lower()
    for cat_name, key in category_mapping.items():
        if cat_name in category_lower:
            json_key = key
            break
    
    if json_key:
        terms_to_check = toxic_data.get(json_key, [])
    else:
        terms_to_check = []
        for key, terms in toxic_data.items():
            if isinstance(terms, list):
                terms_to_check.extend(terms)
    
    for term in terms_to_check:
        term_lower = term.lower()
        
        if ' ' not in term_lower and len(term_lower) <= 15:
            pattern = r'\b' + re.escape(term_lower) + r'\w*\b'
            match = re.search(pattern, text_lower)
            if match:
                return text[match.start():match.end()]
        else:
            pos = text_lower.find(term_lower)
            if pos != -1:
                return text[pos:pos + len(term)]
    
    return category.replace("_", " ")


def submit_manual_review(request: ManualReviewRequest) -> ManualReviewResponse:
    import uuid
    review_id = str(uuid.uuid4())[:8]
    
    print(f"[ManualReview] Submitted review {review_id} from {request.user_email}")
    print(f"[ManualReview] Reason: {request.reason}")
    print(f"[ManualReview] Text length: {len(request.text)} chars")
    
    return ManualReviewResponse(
        status="submitted",
        review_id=review_id,
        message=f"Your request has been submitted (ID: {review_id}). We'll review within 24 hours."
    )
