import json
import re
from pathlib import Path
from typing import List, Set


class ToxicityChecker:
    
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
        data_path = Path(__file__).parent.parent / "data" / "toxic_terms.json"
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for term in data.get("severe_profanity", []):
            self._severe_profanity.add(term.lower())
        
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
        
        for term in data.get("defamation_patterns", []):
            self._defamation_patterns.add(term.lower())
        
        for pattern in data.get("hate_speech_patterns", []):
            try:
                self._hate_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass
    
    def _check_defamation(self, text_lower: str, result: dict, linguistic_result: dict = None):
        linguistic_result = linguistic_result or {}
        
        mentioned_entities = self._find_target_entities(linguistic_result)
        
        if not mentioned_entities:
            return
        
        self._detect_defamation_patterns(
            text_lower, 
            mentioned_entities, 
            result, 
            linguistic_result
        )

    def _find_target_entities(self, linguistic_result: dict) -> List[str]:
        mentioned_entities = []
        
        if linguistic_result.get("is_available"):
            for entity_text, label in linguistic_result.get("entities", []):
                if label in ("PERSON", "ORG", "GPE"):
                    mentioned_entities.append(entity_text.lower())
        
        return mentioned_entities

    def _detect_defamation_patterns(self, text_lower: str, entities: List[str], 
                                   result: dict, linguistic_result: dict):
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
                return
    
    def _is_pattern_negated(self, pattern: str, text_lower: str, 
                          doc, negation_map: dict) -> bool:
        if self._check_spacy_negation(pattern, doc, negation_map):
            return True
        
        return self._check_string_negation(pattern, text_lower)

    def _check_spacy_negation(self, pattern: str, doc, negation_map: dict) -> bool:
        if doc and negation_map:
            pattern_words = set(pattern.split())
            for token in doc:
                if token.text.lower() in pattern_words:
                    if token.i in negation_map:
                        return True
        return False

    def _check_string_negation(self, pattern: str, text_lower: str) -> bool:
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
        import re
        matched_any = False
        for term in patterns:
            if ' ' not in term and len(term) <= 8:
                if self._match_single_word(term, text_lower):
                    self._add_match(result, category, term, score if not matched_any else 0)
                    matched_any = True
            else:
                if self._match_phrase(term, text_lower):
                    self._add_match(result, category, term, score if not matched_any else 0)
                    matched_any = True
    
    def _match_single_word(self, term: str, text: str) -> bool:
        import re
        pattern = r'\b' + re.escape(term) + r'\b'
        return bool(re.search(pattern, text))

    def _match_phrase(self, term: str, text: str) -> bool:
        return term in text

    def _add_match(self, result: dict, category: str, term: str, score: float):
        if category not in result["categories"]:
            result["categories"].append(category)
        result["matched"].append(term)
        result["score"] += score
    
    def _load_whitelist(self):
        data_path = Path(__file__).parent.parent / "data" / "scam_patterns.json"
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.WHITELIST_CONTEXTS = data.get("whitelist_contexts", [])
        except Exception:
            self.WHITELIST_CONTEXTS = []

    WHITELIST_CONTEXTS = []
    
    def check(self, text: str, linguistic_result: dict = None) -> dict:
        text_lower = text.lower()
        linguistic_result = linguistic_result or {}
        
        result = {
            "score": 0.0,
            "is_toxic": False,
            "categories": [],
            "matched": []
        }
        
        is_whitelisted = False
        for context in self.WHITELIST_CONTEXTS:
            if context in text_lower:
                result["skipped_context"] = context
                is_whitelisted = True
                break
        
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
        
        self._check_defamation(text_lower, result, linguistic_result)
        
        for pattern in self._hate_patterns:
            if pattern.search(text):
                if "hate_speech" not in result["categories"]:
                    result["categories"].append("hate_speech")
                result["score"] += 0.6
                break
        
        spam_count = sum(1 for ind in self._spam_indicators if ind in text_lower)
        if spam_count >= 2:
            result["categories"].append("spam")
            result["score"] += 0.3
        
        result["score"] = min(1.0, round(result["score"], 3))
        result["is_toxic"] = result["score"] >= 0.3
        
        return result
