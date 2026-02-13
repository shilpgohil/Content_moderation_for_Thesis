from typing import Dict, List
from rapidfuzz import fuzz, process


class FuzzyMatcher:
    
    DEFAULT_THRESHOLD = 75
    
    def __init__(self, threshold: float = None):
        self.threshold = threshold if threshold is not None else self.DEFAULT_THRESHOLD
        self._scam_phrases = self._load_scam_phrases()
        self._load_whitelist()
    
    def _load_scam_phrases(self) -> List[str]:
        return [
            "guaranteed returns",
            "guaranteed profit", 
            "guaranteed monthly returns",
            "double your money",
            "triple your money",
            "risk free profit",
            "risk free investment",
            "no risk investment",
            "sure shot profit",
            "fixed returns daily",
            "get rich quick",
            "easy money scheme",
            "secret formula",
            "insider tip only",
            "insider information",
            "leaked information",
            "foolproof system",
            "foolproof trading",
            "never lose money",
            "always make profit",
            "daily profit guaranteed",
            "hundred percent accurate",
            "hundred percent returns",
            "join my telegram",
            "join my whatsapp",
            "join my premium",
            "deposit in our account",
            "trade on your behalf",
            "send money to my upi",
            "send to my account",
            "pay registration fee",
            "pay joining fee",
            "double yor moni",
            "doubel your money",
            "garanteed returns",
            "guaranted returns",
            "gauranted profit",
            "insyder tips",
            "sekret tips",
            "premium telegraam",
            "premium telegram group",
            "zero risk profit",
            "lakhs daily",
            "earn lakhs",
            "make lakhs",
            "crores monthly",
            "laaast chaance",
            "opshuns traading groop",
            "registrashun closing",
        ]
    WHITELIST_CONTEXTS = []

    def _load_whitelist(self):
        import json
        from pathlib import Path
        try:
            data_path = Path(__file__).parent.parent / "data" / "scam_patterns.json"
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.WHITELIST_CONTEXTS = data.get("whitelist_contexts", [])
        except Exception as e:
            print(f"Error loading whitelist: {e}")
            self.WHITELIST_CONTEXTS = []
    
    def _match_context(self, context: str, text: str) -> bool:
        import re
        context_lower = context.lower()
        text_lower = text.lower()
        if ' ' in context_lower:
            return context_lower in text_lower
        else:
            return bool(re.search(r'\b' + re.escape(context_lower) + r'\b', text, re.IGNORECASE))
    
    def check(self, text: str) -> Dict:
        text_lower = text.lower()
        
        for context in self.WHITELIST_CONTEXTS:
            if self._match_context(context, text):
                return {
                    "score": 0.0,
                    "matches": [],
                    "has_fuzzy_match": False,
                    "skipped_context": context
                }
        
        matches = []
        max_score = 0.0
        
        words = text_lower.split()
        ngrams = self._generate_ngrams(words, min_n=2, max_n=4)
        
        seen_matches = set()
        
        for ngram in ngrams:
            if len(ngram) < 10:
                continue
                
            result = process.extractOne(
                ngram,
                self._scam_phrases,
                scorer=fuzz.ratio
            )
            
            if result and result[1] >= self.threshold:
                matched_phrase, score, _ = result
                
                len_ratio = len(ngram) / len(matched_phrase)
                if len_ratio < 0.7 or len_ratio > 1.5:
                    continue
                
                if matched_phrase in seen_matches:
                    continue
                seen_matches.add(matched_phrase)
                
                matches.append({
                    "input": ngram,
                    "matched": matched_phrase,
                    "similarity": score / 100.0,
                    "severity": self._get_severity(matched_phrase)
                })
                max_score = max(max_score, score / 100.0)
        
        if not matches:
            return {
                "score": 0.0,
                "matches": [],
                "has_fuzzy_match": False
            }
        
        high_severity_count = sum(1 for m in matches if m["severity"] == "high")
        
        final_score = max_score
        
        return {
            "score": round(final_score, 3),
            "matches": matches,
            "has_fuzzy_match": True,
            "high_severity_count": high_severity_count
        }
    
    def _generate_ngrams(self, words: List[str], min_n: int = 2, max_n: int = 5) -> List[str]:
        ngrams = []
        for n in range(min_n, min(max_n + 1, len(words) + 1)):
            for i in range(len(words) - n + 1):
                ngrams.append(" ".join(words[i:i+n]))
        return ngrams
    
    def _get_severity(self, phrase: str) -> str:
        high_severity_phrases = {
            "guaranteed returns", "guaranteed profit", "guaranteed monthly",
            "double your money", "triple your money", "risk free profit",
            "risk-free investment", "no risk investment", "sure shot profit",
            "fixed returns daily", "get rich quick", "easy money scheme",
            "insider information", "leaked information", "foolproof system",
            "100% accurate", "100% returns", "never lose money"
        }
        
        if phrase in high_severity_phrases:
            return "high"
        return "medium"
