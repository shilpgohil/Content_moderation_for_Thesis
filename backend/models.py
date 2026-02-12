"""
Data models for Thesis Strength Analysis results.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class SentenceType(Enum):
    FACT = "FACT"
    ASSUMPTION = "ASSUMPTION"
    OPINION = "OPINION"
    PROJECTION = "PROJECTION"
    CONTEXT = "CONTEXT"


class SupportLevel(Enum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    UNSUPPORTED = "UNSUPPORTED"


class SentenceRole(Enum):
    FOUNDATION = "Foundation"
    EVIDENCE = "Evidence"
    BRIDGE = "Bridge"
    CONCLUSION = "Conclusion"
    TANGENT = "Tangent"


@dataclass
class AuditEntry:
    """Entry for Fact vs Assumption audit table (Step 4)."""
    sentence_index: int
    statement: str
    classified_as: str
    should_be: str
    issue: str
    
    def to_dict(self) -> Dict:
        return {
            "sentence_index": self.sentence_index,
            "statement": self.statement[:80] + "..." if len(self.statement) > 80 else self.statement,
            "classified_as": self.classified_as,
            "should_be": self.should_be,
            "issue": self.issue
        }


@dataclass
class LogicChainNode:
    """Node in the logic chain visualization (Step 5)."""
    claim: str
    claim_type: str  # "main_claim", "supporting_point", "counter_argument"
    has_evidence: bool
    evidence_sentences: List[int] = field(default_factory=list)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "claim": self.claim[:100] + "..." if len(self.claim) > 100 else self.claim,
            "type": self.claim_type,
            "has_evidence": self.has_evidence,
            "evidence_refs": self.evidence_sentences,
            "confidence": round(self.confidence, 2)
        }


@dataclass
class WeaknessReport:
    """Categorized weaknesses (Step 6 enhancement)."""
    vague_terms: List[str] = field(default_factory=list)
    weasel_words: List[str] = field(default_factory=list)
    unquantified_claims: List[Dict] = field(default_factory=list)
    missing_connections: List[str] = field(default_factory=list)
    circular_reasoning_flags: List[str] = field(default_factory=list)
    unstated_assumptions: List[str] = field(default_factory=list)
    unsourced_statistics: List[Dict] = field(default_factory=list)
    outdated_info: List[Dict] = field(default_factory=list)
    missing_context: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "language": {"vague_terms": self.vague_terms, "weasel_words": self.weasel_words, "unquantified_claims": self.unquantified_claims},
            "logical": {"missing_connections": self.missing_connections, "circular_reasoning": self.circular_reasoning_flags, "unstated_assumptions": self.unstated_assumptions},
            "data": {"unsourced_statistics": self.unsourced_statistics, "outdated_info": self.outdated_info, "missing_context": self.missing_context}
        }


@dataclass
class ConsistencyIssue:
    """Internal consistency issue (Rule 6)."""
    sentence_a_index: int
    sentence_b_index: int
    sentence_a_text: str
    sentence_b_text: str
    issue_type: str
    explanation: str
    
    def to_dict(self) -> Dict:
        return {"sentences": [self.sentence_a_index, self.sentence_b_index], "issue_type": self.issue_type, "explanation": self.explanation}


@dataclass
class BiasAnalysis:
    """Bias detection result (Rule 8)."""
    is_biased: bool
    bias_score: float
    positive_ratio: float
    negative_ratio: float
    counter_arguments_present: bool
    one_sided_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {"is_biased": self.is_biased, "bias_score": round(self.bias_score, 2), "sentiment": {"positive": round(self.positive_ratio, 1), "negative": round(self.negative_ratio, 1)}, "counter_arguments_present": self.counter_arguments_present, "flags": self.one_sided_flags}


@dataclass
class SentenceAnalysis:
    """Analysis result for a single sentence."""
    index: int
    text: str
    sentence_type: SentenceType
    support_level: SupportLevel
    role: SentenceRole
    confidence: float  # 0.0 - 1.0
    issues: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)  # Extracted entities
    
    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "text": self.text,
            "type": self.sentence_type.value,
            "support": self.support_level.value,
            "role": self.role.value,
            "confidence": round(self.confidence, 2),
            "issues": self.issues,
            "entities": self.entities
        }


@dataclass
class ComponentScore:
    """Score for one of the 5 main components."""
    name: str
    score: float  # 0-20
    max_score: float = 20.0
    confidence: float = 1.0  # How confident we are in this score
    breakdown: Dict = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    
    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "score": round(self.score, 1),
            "max": self.max_score,
            "percentage": round(self.percentage, 1),
            "confidence": round(self.confidence, 2),
            "breakdown": self.breakdown,
            "notes": self.notes
        }


@dataclass
class MLFeatures:
    """Features extracted by ML preprocessing."""
    sentence_count: int = 0
    entity_count: int = 0
    source_citation_count: int = 0
    numerical_data_count: int = 0
    date_references: List[str] = field(default_factory=list)
    vague_word_count: int = 0
    weasel_word_count: int = 0
    certainty_word_count: int = 0
    risk_vocabulary_count: int = 0
    actionability_signals: int = 0
    companies_mentioned: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "sentence_count": self.sentence_count,
            "entity_count": self.entity_count,
            "source_citations": self.source_citation_count,
            "numerical_data": self.numerical_data_count,
            "date_references": self.date_references,
            "vague_words": self.vague_word_count,
            "weasel_words": self.weasel_word_count,
            "certainty_words": self.certainty_word_count,
            "risk_vocabulary": self.risk_vocabulary_count,
            "actionability_signals": self.actionability_signals,
            "companies": self.companies_mentioned
        }


@dataclass
class StrengthReport:
    """Complete thesis strength analysis report."""
    # Overall
    overall_score: float  # 0-100
    grade: str  # A/B/C/D/F
    
    # Component scores
    evidence_quality: ComponentScore = None
    logical_coherence: ComponentScore = None
    clarity: ComponentScore = None
    risk_awareness: ComponentScore = None
    actionability: ComponentScore = None
    
    # Sentence-level analysis
    sentence_analyses: List[SentenceAnalysis] = field(default_factory=list)
    
    # ML extracted features
    ml_features: MLFeatures = None
    
    # Quick stats
    fact_count: int = 0
    assumption_count: int = 0
    opinion_count: int = 0
    projection_count: int = 0
    supported_percentage: float = 0.0
    
    # Synthesis
    top_strengths: List[str] = field(default_factory=list)
    top_weaknesses: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    improvement_priorities: List[str] = field(default_factory=list)
    
    # NEW: Audit table (Step 4)
    audit_table: List[AuditEntry] = field(default_factory=list)
    
    # NEW: Logic chain (Step 5)
    logic_chain: List[LogicChainNode] = field(default_factory=list)
    
    # NEW: Categorized weaknesses (Step 6)
    weakness_report: WeaknessReport = None
    
    # NEW: Consistency issues (Rule 6)
    consistency_issues: List[ConsistencyIssue] = field(default_factory=list)
    
    # NEW: Bias analysis (Rule 8)
    bias_analysis: BiasAnalysis = None
    
    def to_dict(self) -> Dict:
        return {
            "overall_score": round(self.overall_score, 1),
            "grade": self.grade,
            "component_scores": {
                "evidence_quality": self.evidence_quality.to_dict() if self.evidence_quality else None,
                "logical_coherence": self.logical_coherence.to_dict() if self.logical_coherence else None,
                "clarity": self.clarity.to_dict() if self.clarity else None,
                "risk_awareness": self.risk_awareness.to_dict() if self.risk_awareness else None,
                "actionability": self.actionability.to_dict() if self.actionability else None,
            },
            "quick_stats": {
                "total_sentences": len(self.sentence_analyses),
                "facts": self.fact_count,
                "assumptions": self.assumption_count,
                "opinions": self.opinion_count,
                "projections": self.projection_count,
                "supported_percentage": round(self.supported_percentage, 1)
            },
            "ml_features": self.ml_features.to_dict() if self.ml_features else None,
            "sentence_analyses": [s.to_dict() for s in self.sentence_analyses],
            "synthesis": {
                "top_strengths": self.top_strengths,
                "top_weaknesses": self.top_weaknesses,
                "missing_elements": self.missing_elements,
                "improvement_priorities": self.improvement_priorities
            },
            "audit_table": [a.to_dict() for a in self.audit_table],
            "logic_chain": [n.to_dict() for n in self.logic_chain],
            "weakness_report": self.weakness_report.to_dict() if self.weakness_report else None,
            "consistency_issues": [c.to_dict() for c in self.consistency_issues],
            "bias_analysis": self.bias_analysis.to_dict() if self.bias_analysis else None
        }

    
    @staticmethod
    def calculate_grade(score: float) -> str:
        """Calculate letter grade from numerical score."""
        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 45:
            return "D"
        else:
            return "F"
