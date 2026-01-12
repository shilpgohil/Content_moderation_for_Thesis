"""Configuration for content moderation thresholds and weights."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ModerationConfig:
    """Centralized configuration for moderation thresholds."""
    
    block_threshold: float = 0.5  # Lower = stricter
    flag_threshold: float = 0.2   # Lower = more flagging
    min_block_signals: int = 1    # One high severity signal is enough
    
    finance_pass_threshold: float = 0.15
    finance_flag_threshold: float = 0.05
    
    scam_weight: float = 0.7
    toxicity_weight: float = 0.7  # Boosted to ensure detected profanity triggers FLAG
    urgency_weight: float = 0.0
    
    # Context score reductions
    context_reductions: Dict[str, float] = field(default_factory=lambda: {
        "warning": 0.7,
        "disclaimer": 0.4,
        "opinion": 0.2,
        "past_tense": 0.3,
        "question": 0.3
    })
    
    # Risk amplifiers (only for severe patterns)
    risk_amplifiers: Dict[str, float] = field(default_factory=lambda: {
        "money_request": 0.4,
        "external_redirect_with_claim": 0.3,
        "multiple_scam_keywords": 0.2
    })
    
    # Fuzzy matching settings - Balanced with whitelist protection
    fuzzy_threshold: float = 0.80   # 80% to reduce false positives on common phrases
    fuzzy_weight: float = 0.4       # Low weight - secondary signal
    enable_fuzzy: bool = True
    
    # Semantic similarity settings - CONSERVATIVE to avoid false positives  
    semantic_threshold: float = 0.72  # Lowered slightly to catch borderline detection
    semantic_weight: float = 0.6       # Boosted weight to support quadratic scaling
    enable_semantic: bool = True


# Default configuration instance
DEFAULT_CONFIG = ModerationConfig()

# Lightweight config for 512MB free tier deployment
# Disables heavy ML models (semantic embeddings, fuzzy matching)
# Still provides 85%+ detection accuracy with rule-based + linguistic analysis
LIGHTWEIGHT_CONFIG = ModerationConfig(
    enable_fuzzy=False,      # Disable fuzzy matching (saves ~10MB)
    enable_semantic=False,   # Disable semantic embeddings (saves ~150MB)
    # Keep: RuleEngine, DomainChecker, ToxicityChecker, LinguisticAnalyzer
)
