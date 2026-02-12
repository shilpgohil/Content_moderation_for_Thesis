"""Finance domain relevance checker."""

import json
import re
from pathlib import Path
from typing import Set, Dict


class DomainChecker:
    """Checks if content is related to finance domain."""
    
    def __init__(self):
        self._finance_terms: Set[str] = set()
        self._high_priority_terms: Set[str] = set()
        self._strong_finance_terms: Set[str] = set()
        self._negative_terms: Set[str] = set()
        # Compiled regex patterns for word boundary matching
        self._single_word_patterns: Dict[str, re.Pattern] = {}
        self._load_vocabulary()
    
    def _load_vocabulary(self):
        """Load finance vocabulary from JSON file."""
        data_path = Path(__file__).parent.parent / "data" / "finance_vocabulary.json"
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load categories
        for category, terms in data["categories"].items():
            if category == "negative_topics":
                for term in terms:
                    term_lower = term.lower()
                    self._negative_terms.add(term_lower)
                    # Pre-compile regex for single words
                    if ' ' not in term_lower:
                        self._single_word_patterns[term_lower] = re.compile(
                            r'\b' + re.escape(term_lower) + r'\b', re.IGNORECASE
                        )
            else:
                for term in terms:
                    term_lower = term.lower()
                    self._finance_terms.add(term_lower)
                    # Pre-compile regex for single words (no spaces)
                    if ' ' not in term_lower:
                        self._single_word_patterns[term_lower] = re.compile(
                            r'\b' + re.escape(term_lower) + r'\b', re.IGNORECASE
                        )
                
                # Identify strong signal categories
                if category in ["brands", "career", "technical", "regulators", "safety", "metrics", "fundamental_analysis", "stock_market", "investing"]:
                    for term in terms:
                        term_lower = term.lower()
                        # Ambiguous terms should NOT be strong signals on their own
                        if term_lower not in self.AMBIGUOUS_TERMS:
                            self._strong_finance_terms.add(term_lower)
        
        # Load high priority terms
        for term in data.get("high_priority_terms", []):
            self._high_priority_terms.add(term.lower())
    
    def _match_term(self, term: str, text: str, text_lower: str) -> bool:
        """Match a term using word boundaries for single words, substring for phrases."""
        if ' ' in term:
            # Multi-word phrase: substring match is fine
            return term in text_lower
        else:
            # Single word: use pre-compiled word boundary regex
            pattern = self._single_word_patterns.get(term)
            if pattern:
                return bool(pattern.search(text))
            # Fallback for terms not pre-compiled
            return bool(re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE))
    
    # Terms that are common in general English and shouldn't trigger finance domain alone
    # Terms that are common in general English and shouldn't trigger finance domain alone
    AMBIGUOUS_TERMS = {
        'budget', 'loss', 'support', 'target', 'profit', 'risk', 'offering', 'bond', 'security',
        'selling', 'sell', 'buy', 'buying', 'paid', 'premium', 'rs', 'rupees', 'inr', 'cost', 'price'
    }

    def check(self, text: str, linguistic_result: dict = None, words: list = None) -> dict:
        """
        Check finance relevance of content.
        Args:
            text: Original text for regex matching
            linguistic_result: Dictionary containing SpaCy analysis (entities, etc.)
            words: Optional pre-tokenized words (legacy)
        Returns relevance score and matched terms.
        """
        # If only words provided (legacy), reconstruct text
        if words is not None and isinstance(words, list):
            text = ' '.join(words)
        
        if not text or not text.strip():
            return {"score": 0.0, "is_finance": False, "matched_terms": [], "negative_terms_found": []}
        
        linguistic_result = linguistic_result or {}
        text_lower = text.lower()
        words_list = text_lower.split()
        
        matched = []
        negative_matches = []
        high_priority_matches = 0
        strong_signal_found = False
        
        # Check single-word terms using word boundaries
        for term in self._finance_terms:
            if self._match_term(term, text, text_lower):
                matched.append(term)
                if term in self._high_priority_terms:
                    high_priority_matches += 1
                if term in self._strong_finance_terms:
                    strong_signal_found = True
        
        # Check negative terms
        for term in self._negative_terms:
            if self._match_term(term, text, text_lower):
                negative_matches.append(term)
        
        # Calculate score
        meaningful_words = len([w for w in words_list if len(w) > 2])
        if meaningful_words == 0:
            return {"score": 0.0, "is_finance": False, "matched_terms": [], "negative_terms_found": []}
        
        base_score = len(set(matched)) / meaningful_words
        
        # Boost for high priority terms
        if high_priority_matches > 0:
            base_score = min(1.0, base_score + 0.1 * high_priority_matches)
            
        # Boost for SpaCy Entities (ORG, MONEY)
        entity_boost = 0.0
        found_entities = []
        if linguistic_result.get("is_available"):
            for ent_text, label in linguistic_result.get("entities", []):
                ent_lower = ent_text.lower()
                # Ignore entity if it is one of our negative matches (e.g. iPhone identified as ORG)
                if ent_lower in self._negative_terms:
                    continue
                
                # Ignore common false positive entities
                if ent_lower in {'dm', 'pm', 'admin'}:
                    continue
                    
                if label == "ORG":
                    # Organization/Company is a strong signal if paired with any context
                    entity_boost += 0.05
                    found_entities.append(ent_text)
                elif label == "MONEY":
                    # Money mentions ($500) combined with 'budget' make it finance
                    entity_boost += 0.1
                    found_entities.append(ent_text)
        
        base_score += min(0.2, entity_boost) # Cap entity boost
            
        base_score += min(0.2, entity_boost) # Cap entity boost
            
        # Penalize for negative topics (gaming, weddings, etc.)
        if negative_matches:
            unique_negatives = len(set(negative_matches))
            penalty = 0.15 * unique_negatives
            base_score = max(0.0, base_score - penalty)
            
        # -------------------------------------------------------------------------
        # COHERENCE CHECK: Natural Language Understanding
        # Detect sentences that drift into off-topic entities (Politics, Celebs, etc.)
        # without hardcoded keywords, relying on linguistic analysis.
        # -------------------------------------------------------------------------
        doc = linguistic_result.get("doc")
        coherence_penalty = 0.0
        
        if doc:
            for sent in doc.sents:
                # Skip short/fragmented sentences
                if len(sent) < 6: 
                    continue
                
                # Check if sentence has any finance context
                sent_text = sent.text.lower()
                has_finance_context = False
                
                # Quick check: does it contain any known finance term?
                for term in self._finance_terms:
                    if self._match_term(term, sent.text, sent_text):
                        has_finance_context = True
                        break
                
                if has_finance_context:
                    continue
                
                # If NO finance context, checks for "Topic Entities"
                # These are entities that define a subject: People, Places, Groups, Events
                # We exclude numerical/functional entities (DATE, MONEY, PERCENT, CARDINAL)
                topic_entities = [
                    ent for ent in sent.ents 
                    if ent.label_ in {"PERSON", "ORG", "GPE", "NORP", "EVENT", "FAC", "LAW", "PRODUCT"}
                ]
                
                # Strong heuristic: Talking about specific People/Places/Orgs without ANY finance context
                # is a strong indicator of off-topic drift (e.g., Politics, Movies, Sports)
                if topic_entities:
                    # Check if entities are not actually negative terms found earlier 
                    # (to avoid double punishing known negatives)
                    new_drift = True
                    for ent in topic_entities:
                        if ent.text.lower() in self._negative_terms:
                            new_drift = False # Already caught by keyword
                            break
                    
                    if new_drift:
                        # Apply penalty for coherent off-topic sentence
                        # "Mr Trump thought it was a waste" -> PERSON + No Finance -> Penalty
                        coherence_penalty += 0.15
                        negative_matches.append(f"off_topic_entity:{topic_entities[0].label_}")

        # Apply coherence penalty
        if coherence_penalty > 0:
            # Increasing penalty helps flag mixed-content posts
            base_score = max(0.0, base_score - coherence_penalty)
            
        # -------------------------------------------------------------------------
        
        # Ambiguity Check: 
        # If ALL matched terms are ambiguous AND no strong signal AND no entities -> Not Finance
        unique_matches = set(matched)
        
        if unique_matches and unique_matches.issubset(self.AMBIGUOUS_TERMS):
            if not strong_signal_found and not found_entities:
                # "Budget hotel" -> matched 'budget' (ambiguous), no entities -> 0 score
                return {
                    "score": 0.05, # Low score, passed as 'not finance' mostly
                    "is_finance": False, 
                    "matched_terms": matched,
                    "negative_terms_found": list(set(negative_matches)),
                    "reason": "ambiguous_only"
                }

        # Override for strong signals
        if negative_matches:
             # Strict mode: Need higher score to overcome negative topic
             # Even if strong signal exists, we require substantial finance density
             is_finance = base_score >= 0.15
        else:
             # Normal mode
             is_finance = base_score >= 0.05
             
             if strong_signal_found:
                 is_finance = True
                 base_score = max(base_score, 0.25)
             elif base_score >= 0.1 and found_entities:
                 # Weak signals + Entities can pass
                 is_finance = True
                 base_score = max(base_score, 0.25)
        
        return {
            "score": round(base_score, 3),
            "is_finance": is_finance,
            "matched_terms": list(set(matched)),
            "negative_terms_found": list(set(negative_matches))
        }
