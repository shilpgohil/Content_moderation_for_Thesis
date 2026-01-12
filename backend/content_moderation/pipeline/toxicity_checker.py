"""Toxicity and inappropriate content detection."""

import json
import re
from pathlib import Path
from typing import List, Set


class ToxicityChecker:
    """Detects profanity, hate speech, personal attacks, and defamation."""
    
    def __init__(self):
        self._severe_profanity: Set[str] = set()
        self._mild_profanity: Set[str] = set()
        self._personal_attacks: Set[str] = set()
        self._hate_patterns: List = []
        self._spam_indicators: Set[str] = set()
        self._threat_patterns: Set[str] = set()
        self._harassment_patterns: Set[str] = set()
        self._mockery_patterns: Set[str] = set()
        self._doxxing_patterns: Set[str] = set()
        self._defamation_patterns: Set[str] = set()
        self._load_patterns()
        self._load_whitelist()
    
    def _load_patterns(self):
        """Load toxicity patterns from JSON file."""
        data_path = Path(__file__).parent.parent / "data" / "toxic_terms.json"
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load severe profanity (BLOCK-worthy)
        for term in data.get("severe_profanity", []):
            self._severe_profanity.add(term.lower())
        
        # Load mild profanity (FLAG-worthy)
        for term in data.get("mild_profanity", []):
            self._mild_profanity.add(term.lower())
        
        for term in data.get("personal_attacks", []):
            self._personal_attacks.add(term.lower())
        
        for term in data.get("spam_indicators", []):
            self._spam_indicators.add(term.lower())
        
        for term in data.get("threat_patterns", []):
            self._threat_patterns.add(term.lower())
        
        for term in data.get("harassment_patterns", []):
            self._harassment_patterns.add(term.lower())
        
        for term in data.get("mockery_patterns", []):
            self._mockery_patterns.add(term.lower())
        
        for term in data.get("doxxing_patterns", []):
            self._doxxing_patterns.add(term.lower())
        
        # Load defamation patterns
        for term in data.get("defamation_patterns", []):
            self._defamation_patterns.add(term.lower())
        
        for pattern in data.get("hate_speech_patterns", []):
            try:
                self._hate_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass
    

    
    def _check_defamation(self, text_lower: str, result: dict, linguistic_result: dict = None):
        """
        Check for defamation patterns directed at known entities.
        Uses linguistic analysis for smarter detection (negation, precise entity match).
        """
        linguistic_result = linguistic_result or {}
        
        # 1. Identify Target Entities
        mentioned_entities = self._find_target_entities(linguistic_result)
        
        if not mentioned_entities:
            return
        
        # 2. Check for Attack Patterns (with Negation)
        self._detect_defamation_patterns(
            text_lower, 
            mentioned_entities, 
            result, 
            linguistic_result
        )

    def _find_target_entities(self, linguistic_result: dict) -> List[str]:
        """Identify mentioned public figures/brands."""
        mentioned_entities = []
        
        # Use SpaCy entities (PERSON, ORG, GPE)
        if linguistic_result.get("is_available"):
            for entity_text, label in linguistic_result.get("entities", []):
                if label in ("PERSON", "ORG", "GPE"):
                    mentioned_entities.append(entity_text.lower())
        
        return mentioned_entities

    def _detect_defamation_patterns(self, text_lower: str, entities: List[str], 
                                  result: dict, linguistic_result: dict):
        """Detect attack patterns while handling negation."""
        doc = linguistic_result.get("doc")
        negation_map = linguistic_result.get("negation_map", {})
        
        for pattern in self._defamation_patterns:
            if pattern not in text_lower:
                continue
                
            is_negated = self._is_pattern_negated(pattern, text_lower, doc, negation_map)

            if not is_negated:
                result["categories"].append("defamation")
                result["matched"].append(f"{entities[0]} + '{pattern}'")
                result["score"] += 0.7
                return  # One match is enough
    
    def _is_pattern_negated(self, pattern: str, text_lower: str, 
                          doc, negation_map: dict) -> bool:
        """Check if a pattern is negated using SpaCy or rules."""
        # 1. SpaCy Token-based Negation
        if self._check_spacy_negation(pattern, doc, negation_map):
            return True
        
        # 2. String-based Heuristic Fallback
        return self._check_string_negation(pattern, text_lower)

    def _check_spacy_negation(self, pattern: str, doc, negation_map: dict) -> bool:
        """Check specific tokens for negation mapping."""
        if doc and negation_map:
            pattern_words = set(pattern.split())
            for token in doc:
                if token.text.lower() in pattern_words:
                    if token.i in negation_map:
                        return True
        return False

    def _check_string_negation(self, pattern: str, text_lower: str) -> bool:
        """Check for negation words or phrases near pattern."""
        if f"not {pattern}" in text_lower or \
           f"no {pattern}" in text_lower or \
           f"never {pattern}" in text_lower:
            return True
        
        if "is not " in text_lower and pattern.startswith("is "):
            if text_lower.replace("is not ", "is ").find(pattern) != -1:
                return True
                
        return False

    
    def _check_pattern_set(self, text_lower: str, patterns: Set[str], 
                           category: str, score: float, result: dict):
        """Helper to check a set of patterns and update result."""
        import re
        for term in patterns:
            # For single words (no spaces), use word boundary matching
            if ' ' not in term and len(term) <= 8:
                if self._match_single_word(term, text_lower):
                    self._add_match(result, category, term, score)
                    break
            else:
                # For multi-word phrases, substring match is fine
                if self._match_phrase(term, text_lower):
                    self._add_match(result, category, term, score)
                    break
    
    def _match_single_word(self, term: str, text: str) -> bool:
        """Check for single word with word boundaries."""
        import re
        pattern = r'\b' + re.escape(term) + r'\b'
        return bool(re.search(pattern, text))

    def _match_phrase(self, term: str, text: str) -> bool:
        """Check for multi-word phrase."""
        return term in text

    def _add_match(self, result: dict, category: str, term: str, score: float):
        """Update result with match."""
        if category not in result["categories"]:
            result["categories"].append(category)
        result["matched"].append(term)
        result["score"] += score
    
    def _load_whitelist(self):
        """Load whitelist contexts from shared JSON configuration."""
        data_path = Path(__file__).parent.parent / "data" / "scam_patterns.json"
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.WHITELIST_CONTEXTS = data.get("whitelist_contexts", [])
        except Exception:
            # Fallback to empty
            self.WHITELIST_CONTEXTS = []

    # Whitelist contexts (loaded dynamically)
    WHITELIST_CONTEXTS = []
    
    def check(self, text: str, linguistic_result: dict = None) -> dict:
        """
        Check text for toxic content.
        Returns score and matched patterns.
        """
        text_lower = text.lower()
        linguistic_result = linguistic_result or {}
        
        result = {
            "score": 0.0,
            "is_toxic": False,
            "categories": [],
            "matched": []
        }
        
        # Skip if whitelist context is present (news/educational content)
        for context in self.WHITELIST_CONTEXTS:
            if context in text_lower:
                result["skipped_context"] = context
                return result
        
        # Check standard toxicity categories
        # Config format: (pattern_set, category_name, toxicity_score)
        checks = [
            (self._severe_profanity, "severe_profanity", 0.6),
            (self._mild_profanity, "mild_profanity", 0.3),  
            (self._personal_attacks, "personal_attack", 0.5),
            (self._threat_patterns, "threat", 0.6),
            (self._harassment_patterns, "harassment", 0.6),
            (self._mockery_patterns, "mockery", 0.4),
            (self._doxxing_patterns, "doxxing", 0.7)
        ]

        for patterns, category, score in checks:
            self._check_pattern_set(text_lower, patterns, category, score, result)
        
        # Check defamation (entity + attack pattern)
        self._check_defamation(text_lower, result, linguistic_result)
        
        # Check hate speech patterns (regex)
        for pattern in self._hate_patterns:
            if pattern.search(text):
                if "hate_speech" not in result["categories"]:
                    result["categories"].append("hate_speech")
                result["score"] += 0.6
                break
        
        # Check spam indicators
        spam_count = sum(1 for ind in self._spam_indicators if ind in text_lower)
        if spam_count >= 2:
            result["categories"].append("spam")
            result["score"] += 0.3
        
        # Normalize and finalize
        result["score"] = min(1.0, round(result["score"], 3))
        result["is_toxic"] = result["score"] >= 0.3
        
        return result
