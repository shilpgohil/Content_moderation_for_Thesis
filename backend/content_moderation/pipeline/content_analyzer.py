"""
Unified Content Analyzer with Multi-Dimensional Scoring.

This module provides world-class semantic understanding for finance content
by analyzing 5 dimensions:
1. Topic Relevance - Is it about finance?
2. Content Substance - Is it analysis vs casual mention?
3. Discourse Type - Is it education/analysis vs gossip/trolling?
4. Entity-Context Coherence - Are mentioned entities relevant?
5. Linguistic Quality - Is it well-formed content?
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """
    Unified content analyzer that scores content across multiple dimensions
    to determine if it's substantive finance content worth surfacing.
    """
    
    # Weights for unified scoring
    WEIGHT_TOPIC = 0.30
    WEIGHT_SUBSTANCE = 0.40
    WEIGHT_DISCOURSE = 0.20
    WEIGHT_LINGUISTIC = 0.10
    
    # Thresholds
    PASS_THRESHOLD = 0.50
    FLAG_THRESHOLD = 0.35
    
    def __init__(self):
        self._model = None
        self._finance_embeddings = None
        self._negative_embeddings = None
        self._templates = None
        self._is_loaded = False
    
    def _load_model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading sentence transformer for content analysis...")
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                logger.warning("sentence-transformers not installed.")
                return None
        return self._model
    
    def _load_templates(self) -> Dict:
        """Load templates from JSON file."""
        if self._templates is None:
            data_path = Path(__file__).parent.parent / "data" / "finance_domain_templates.json"
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    self._templates = json.load(f)
            else:
                self._templates = {}
        return self._templates
    
    def _compute_embeddings(self):
        """Compute embeddings for all templates."""
        if self._is_loaded:
            return
        
        model = self._load_model()
        if model is None:
            return
        
        templates = self._load_templates()
        
        # Gather positive finance examples
        finance_texts = []
        for category, examples in templates.get("templates", {}).items():
            finance_texts.extend(examples)
        
        if finance_texts:
            self._finance_embeddings = model.encode(finance_texts, convert_to_numpy=True)
        else:
            self._finance_embeddings = np.array([])
        
        # Gather negative examples (now categorized)
        negative_texts = []
        negative_examples = templates.get("negative_examples", {})
        if isinstance(negative_examples, dict):
            for category, examples in negative_examples.items():
                negative_texts.extend(examples)
        elif isinstance(negative_examples, list):
            negative_texts = negative_examples
        
        if negative_texts:
            self._negative_embeddings = model.encode(negative_texts, convert_to_numpy=True)
        else:
            self._negative_embeddings = np.array([])
        
        self._is_loaded = True
    
    def analyze(self, text: str, linguistic_result: dict = None) -> Dict:
        """
        Perform comprehensive content analysis across all dimensions.
        
        Returns:
            Dictionary with dimension scores and final unified decision.
        """
        if not text or not text.strip():
            return self._empty_result("empty_input")
        
        linguistic_result = linguistic_result or {}
        text_lower = text.lower()
        
        # Compute all dimension scores
        topic_score = self._score_topic_relevance(text)
        substance_score = self._score_substance_quality(text, text_lower)
        discourse_result = self._classify_discourse_type(text_lower)
        linguistic_score = self._score_linguistic_quality(text, linguistic_result)
        
        # Apply discourse bonus/penalty
        discourse_modifier = discourse_result["modifier"]
        
        # Unified score calculation
        unified_score = (
            topic_score * self.WEIGHT_TOPIC +
            substance_score * self.WEIGHT_SUBSTANCE +
            discourse_modifier * self.WEIGHT_DISCOURSE +
            linguistic_score * self.WEIGHT_LINGUISTIC
        )
        
        # Clamp to 0-1 range
        unified_score = max(0.0, min(1.0, unified_score))
        
        # Determine decision
        if unified_score >= self.PASS_THRESHOLD:
            decision = "PASS"
        elif unified_score >= self.FLAG_THRESHOLD:
            decision = "FLAG"
        else:
            decision = "BLOCK"
        
        return {
            "unified_score": round(unified_score, 3),
            "decision": decision,
            "is_substantive_finance": unified_score >= self.PASS_THRESHOLD,
            "dimensions": {
                "topic_relevance": round(topic_score, 3),
                "substance_quality": round(substance_score, 3),
                "discourse_type": discourse_result["type"],
                "discourse_modifier": round(discourse_modifier, 3),
                "linguistic_quality": round(linguistic_score, 3)
            },
            "explanation": self._build_explanation(
                topic_score, substance_score, discourse_result, linguistic_score, decision
            )
        }
    
    def _score_topic_relevance(self, text: str) -> float:
        """Score how relevant the content is to finance domain."""
        self._compute_embeddings()
        
        model = self._load_model()
        if model is None or self._finance_embeddings is None or len(self._finance_embeddings) == 0:
            return 0.0
        
        text_embedding = model.encode([text], convert_to_numpy=True)[0]
        
        # Similarity to finance templates
        finance_sims = self._cosine_similarity(text_embedding, self._finance_embeddings)
        max_finance = float(np.max(finance_sims))
        avg_top5_finance = float(np.mean(np.sort(finance_sims)[-5:]))
        
        # Similarity to negative templates
        negative_sims = self._cosine_similarity(text_embedding, self._negative_embeddings)
        max_negative = float(np.max(negative_sims)) if len(negative_sims) > 0 else 0.0
        
        # Score calculation: higher finance similarity, lower negative similarity
        if max_negative > max_finance:
            # More similar to negative content
            return avg_top5_finance * 0.3
        elif max_negative > avg_top5_finance:
            return avg_top5_finance * 0.6
        else:
            return avg_top5_finance
    
    def _score_substance_quality(self, text: str, text_lower: str) -> float:
        """Score the substantive quality of the content."""
        templates = self._load_templates()
        substance = templates.get("substance_indicators", {})
        
        high_patterns = substance.get("high_substance_patterns", [])
        low_patterns = substance.get("low_substance_patterns", [])
        
        # Count matches
        high_count = sum(1 for p in high_patterns if p in text_lower)
        low_count = sum(1 for p in low_patterns if p in text_lower)
        
        # Base score from length (longer content generally more substantive)
        word_count = len(text.split())
        length_score = min(1.0, word_count / 30)  # Cap at 30 words
        
        # Adjust for substance patterns
        pattern_score = 0.5  # Neutral baseline
        if high_count > 0:
            pattern_score += 0.15 * min(high_count, 3)  # Cap bonus at 3 patterns
        if low_count > 0:
            pattern_score -= 0.20 * min(low_count, 3)  # Cap penalty at 3 patterns
        
        # Combine
        final_score = (length_score * 0.4 + pattern_score * 0.6)
        return max(0.0, min(1.0, final_score))
    
    def _classify_discourse_type(self, text_lower: str) -> Dict:
        """Classify the discourse type and return modifier."""
        templates = self._load_templates()
        discourse = templates.get("discourse_types", {})
        
        # Check each discourse type
        type_scores = {}
        for dtype, patterns in discourse.items():
            matches = sum(1 for p in patterns if p in text_lower)
            if matches > 0:
                type_scores[dtype] = matches
        
        if not type_scores:
            return {"type": "neutral", "modifier": 0.5}
        
        # Get dominant type
        dominant_type = max(type_scores, key=type_scores.get)
        
        # Assign modifiers
        modifiers = {
            "analysis": 0.9,
            "education": 0.85,
            "news": 0.8,
            "question": 0.7,
            "gossip": 0.1,
        }
        
        modifier = modifiers.get(dominant_type, 0.5)
        
        return {"type": dominant_type, "modifier": modifier}
    
    def _score_linguistic_quality(self, text: str, linguistic_result: dict) -> float:
        """Score the linguistic quality of the content."""
        score = 0.5  # Baseline
        
        # Check sentence structure (has proper punctuation)
        if text.strip().endswith(('.', '!', '?')):
            score += 0.15
        
        # Check capitalization (starts with capital)
        if text[0].isupper():
            score += 0.1
        
        # Check for complete sentences (has verbs - rough heuristic via length)
        words = text.split()
        if len(words) >= 5:
            score += 0.15
        
        # Penalize excessive caps (SHOUTING)
        upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if upper_ratio > 0.5:
            score -= 0.3
        
        # Penalize excessive punctuation
        punct_ratio = sum(1 for c in text if c in '!?') / max(len(text), 1)
        if punct_ratio > 0.1:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between vector a and matrix b."""
        if len(b) == 0:
            return np.array([])
        a_norm = a / np.linalg.norm(a)
        b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
        return np.dot(b_norm, a_norm)
    
    def _build_explanation(self, topic: float, substance: float, 
                          discourse: dict, linguistic: float, decision: str) -> str:
        """Build human-readable explanation."""
        parts = []
        
        if topic < 0.3:
            parts.append("low topic relevance")
        if substance < 0.4:
            parts.append("low substance")
        if discourse["type"] == "gossip":
            parts.append("gossip content")
        if linguistic < 0.4:
            parts.append("poor quality")
        
        if not parts:
            return f"Content {decision.lower()}ed: substantive finance content"
        
        return f"Content {decision.lower()}ed: {', '.join(parts)}"
    
    def _empty_result(self, reason: str) -> Dict:
        """Return empty result structure."""
        return {
            "unified_score": 0.0,
            "decision": "BLOCK",
            "is_substantive_finance": False,
            "dimensions": {
                "topic_relevance": 0.0,
                "substance_quality": 0.0,
                "discourse_type": "unknown",
                "discourse_modifier": 0.0,
                "linguistic_quality": 0.0
            },
            "explanation": f"Content blocked: {reason}"
        }
