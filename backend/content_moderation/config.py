from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ModerationConfig:
    
    block_threshold: float = 0.5
    flag_threshold: float = 0.2
    min_block_signals: int = 1
    
    finance_pass_threshold: float = 0.15
    finance_flag_threshold: float = 0.05
    
    scam_weight: float = 0.7
    toxicity_weight: float = 0.7
    urgency_weight: float = 0.0
    
    context_reductions: Dict[str, float] = field(default_factory=lambda: {
        "warning": 0.7,
        "disclaimer": 0.4,
        "opinion": 0.2,
        "past_tense": 0.3,
        "question": 0.3
    })
    
    risk_amplifiers: Dict[str, float] = field(default_factory=lambda: {
        "money_request": 0.4,
        "external_redirect_with_claim": 0.3,
        "multiple_scam_keywords": 0.2
    })
    
    fuzzy_threshold: float = 0.80
    fuzzy_weight: float = 0.4
    enable_fuzzy: bool = True
    
    semantic_threshold: float = 0.72
    semantic_weight: float = 0.6
    enable_semantic: bool = True


DEFAULT_CONFIG = ModerationConfig()

LIGHTWEIGHT_CONFIG = ModerationConfig(
    enable_fuzzy=False,
    enable_semantic=False,
)
