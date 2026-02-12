"""Rule-based scam detection engine."""

import json
import re
from pathlib import Path
from typing import List, Dict, Set


class RuleEngine:
    """Pattern-based scam and fraud detection."""
    
    def __init__(self):
        self._patterns: Dict = {}
        self._whitelist: Set[str] = set()
        self._compiled_regex: List = []
        self._load_patterns()
    
    def _load_patterns(self):
        """Load scam patterns from JSON file."""
        data_path = Path(__file__).parent.parent / "data" / "scam_patterns.json"
        
        with open(data_path, 'r', encoding='utf-8') as f:
            self._patterns = json.load(f)
        
        # Build whitelist set
        for term in self._patterns.get("whitelist_contexts", []):
            self._whitelist.add(term.lower())
        
        # Compile regex patterns
        for pattern in self._patterns.get("unrealistic_return_patterns", []):
            try:
                self._compiled_regex.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass
        
        for pattern in self._patterns.get("external_redirect_patterns", []):
            try:
                self._compiled_regex.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass
        
        # Compile solicitation patterns (New)
        self._compiled_solicitation = []
        for pattern in self._patterns.get("solicitation_patterns", []):
            try:
                self._compiled_solicitation.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass
                
        # Compile MLM patterns (New)
        self._compiled_mlm = []
        for pattern in self._patterns.get("mlm_patterns", []):
            try:
                self._compiled_mlm.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass
    
    def check(self, text: str) -> dict:
        """
        Check text for scam patterns.
        Returns score, matched patterns, and context analysis.
        """
        text_lower = text.lower()
        
        result = {
            "score": 0.0,
            "signals": [],
            "severity": "none",
            "has_whitelist_context": False,
            "context_reduction": 0.0
        }
        
        # Check for whitelist context first
        context_reduction = self._check_context(text_lower)
        result["context_reduction"] = context_reduction
        result["has_whitelist_context"] = context_reduction > 0
        
        # If strong whitelist context (educational/warning), skip scam detection
        if context_reduction >= 0.9:
            result["score"] = 0.0
            result["severity"] = "none"
            result["skipped_reason"] = "strong_whitelist_context"
            return result
        
        # Aggregate logic from sub-scanners
        matched_signals = []
        raw_score = 0.0
        
        # 1. Keywords
        k_signals, k_score = self._scan_keywords(text)
        matched_signals.extend(k_signals)
        raw_score += k_score
        
        # 2. Money Requests
        m_signals, m_score = self._scan_money_requests(text)
        matched_signals.extend(m_signals)
        raw_score += m_score
        
        # 3. Regex Patterns
        r_signals, r_score = self._scan_regex_patterns(text)
        matched_signals.extend(r_signals)
        raw_score += r_score
        
        # 4. Solicitation
        s_signals, s_score = self._scan_solicitation(text)
        matched_signals.extend(s_signals)
        raw_score += s_score
        
        # 5. MLM
        mlm_signals, mlm_score = self._scan_mlm(text)
        matched_signals.extend(mlm_signals)
        raw_score += mlm_score
        
        # Apply context reduction as multiplier (stronger effect)
        if context_reduction > 0 and raw_score > 0:
            multiplier = 1.0 - context_reduction
            raw_score = raw_score * multiplier
            # Also reduce signals if context present
            if context_reduction >= 0.5:
                matched_signals = []  # Clear signals if medium+ context
        
        # Normalize score
        final_score = min(1.0, raw_score)
        
        if context_reduction > 0:
            final_score = max(0.0, final_score * (1.0 - context_reduction))
            
            # If context effectively neutralized the risk (score < 0.2), 
            # suppress high severity signals to prevent DecisionEngine from blocking based on signal count logic
            if final_score < 0.2:
                # Keep only low severity info-level signals or clear them
                # Ideally, if it's safe news/edu, we shouldn't pass alarmist flags
                matched_signals = [s for s in matched_signals if s['severity'] == 'low']

        result["score"] = round(final_score, 3)
        result["signals"] = matched_signals
        
        # Determine severity based on final score after context
        if final_score >= 0.7:
            result["severity"] = "high"
        elif final_score >= 0.4:
            result["severity"] = "medium"
        elif final_score > 0:
            result["severity"] = "low"
        
        return result

    def _match_pattern(self, pattern: str, text: str, text_lower: str) -> bool:
        """Match pattern using word boundaries for single words, substring for phrases."""
        pattern_lower = pattern.lower()
        if ' ' in pattern_lower:
            # Multi-word phrase: substring match is acceptable
            return pattern_lower in text_lower
        else:
            # Single word: use word boundary regex to prevent partial matches
            # e.g., "fed" should not match "FedEx"
            return bool(re.search(r'\b' + re.escape(pattern_lower) + r'\b', text, re.IGNORECASE))

    def _scan_keywords(self, text: str) -> tuple:
        """Scan for severity-weighted keywords with proper word boundaries."""
        text_lower = text.lower()
        signals = []
        score = 0.0
        
        for severity in ["high_severity", "medium_severity", "low_severity"]:
            if severity not in self._patterns:
                continue
            
            severity_data = self._patterns[severity]
            keywords = severity_data.get("keywords", [])
            weight = severity_data.get("weight", 0.5)
            
            for keyword in keywords:
                if self._match_pattern(keyword, text, text_lower):
                    signals.append({
                        "pattern": keyword,
                        "severity": severity.replace("_severity", ""),
                        "weight": weight
                    })
                    score += weight
        return signals, score

    def _scan_money_requests(self, text: str) -> tuple:
        """Scan for money request patterns with word boundaries."""
        text_lower = text.lower()
        signals = []
        score = 0.0
        for pattern in self._patterns.get("money_request_patterns", []):
            if self._match_pattern(pattern, text, text_lower):
                signals.append({
                    "pattern": pattern,
                    "severity": "high",
                    "weight": 0.8
                })
                score += 0.8
        return signals, score

    def _scan_regex_patterns(self, text: str) -> tuple:
        """Scan for regex patterns."""
        signals = []
        score = 0.0
        for regex in self._compiled_regex:
            if regex.search(text):
                signals.append({
                    "pattern": regex.pattern,
                    "severity": "high",
                    "weight": 0.7
                })
                score += 0.7
        return signals, score
    
    def _scan_solicitation(self, text: str) -> tuple:
        """Scan for solicitation patterns."""
        signals = []
        score = 0.0
        for regex in self._compiled_solicitation:
            if regex.search(text):
                signals.append({
                    "pattern": "solicitation_detection",
                    "severity": "high",
                    "weight": 0.6
                })
                score += 0.6
        return signals, score

    def _scan_mlm(self, text: str) -> tuple:
        """Scan for MLM patterns."""
        signals = []
        score = 0.0
        for regex in self._compiled_mlm:
            if regex.search(text):
                signals.append({
                    "pattern": "mlm_detection",
                    "severity": "high",
                    "weight": 0.8
                })
                score += 0.8
        return signals, score

    def _check_context(self, text: str) -> float:
        """Check for context that reduces scam score."""
        reduction = 0.0
        
        # Strong warning context - use whitelist from JSON
        # These phrases almost completely negate scam score
        
        # Check loaded whitelist first
        for phrase in self._whitelist:
            if phrase in text:
                return 0.9

        strong_reduction_phrases = [
            "never trust", "don't trust", "avoid", "beware", 
            "scam alert", "fraud alert", "be careful", "stay away",
            "definitely a scam", "is a scam", "are scams", 
            "classic scam", "classic ponzi", "ponzi scheme",
            "red flags", "red flag", "too good to be true",
            "fall for", "don't fall", "falling for", "fell for",
            "lost money to", "expensive lesson", "lesson learned",
            "scam warning", "fraud warning", "scammers say",
            "scammers promise", "scammers often", "fraudsters use",
            "how to identify", "how to spot", "warning signs",
            "sebi warns", "rbi warns", "rbi governor", "sebi circular",
            "report such", "report them", "report immediately",
            "arrested", "ed arrests", "convicted", "fraudster",
            "mastermind of", "investment fraud", "crore fraud",
            "this is not me", "impersonator", "impersonators",
            "we don't allow", "community guidelines", "moderators note",
            "rules are", "will result in ban", "not allowed",
            "we do not allow",
            # News and Reporting
            "breaking news", "police arrested", "gang of", "seized",
            "headline says", "fact check", "hoax", "banned because",
            "received this message", "scam alert", "alert:",
            "found a bug", # Context matters, usually reporting
            # Sarcasm / Rhetorical
            "yeah right", "in your dreams", "as if", "yeah sure",
            "lol", "lmao", "😂", "🙄", "💀",
            "who in their right mind", "seriously people",
            "best financial decision ever. not",
            # Books and movie references
            "just finished reading", "book", "psychology of money",
            "wolf of wall street", "just watched", "documentary",
            "bad boy billionaires",
            # Educational/disclaimer
            "here's the truth", "the truth is", 
            "not bragging", "counter the", "sharing to counter",
            "want to share so others", "know the difference"
        ]
        for phrase in strong_reduction_phrases:
            if phrase in text:
                return 0.9  # Return immediately with max reduction
        
        # Medium reduction - educational/warning context
        medium_reduction_phrases = [
            "not financial advice", "nfa", "dyor", 
            "do your own research", "consult advisor",
            "subject to market risk", "for educational",
            "no guaranteed returns", "there are no guaranteed",
            "past performance", "no guarantee",
            "such things don't exist", "doesn't exist in markets",
            "anyone promising otherwise",
            "let me share my experience", "sharing so others",
            "difference between", "legitimate vs", "vs scam",
            "mutual fund investments are subject to",
            "read all scheme related documents",
            # Legitimate finance terms
            "guaranteed market returns",  # index fund discussion
            "index fund case", "active fund case",
            "my take", "for large caps", "for small-mid caps",
            # Demat and platform discussions
            "comparing platforms", "demat account", "which bank-broker",
            "fund transfers", "fastest fund transfer",
            # Mentorship context
            "looking for a mentor", "willing to pay", "structured learning",
            "not looking for guaranteed", "not looking for tips",
            "verified track record"
        ]
        for phrase in medium_reduction_phrases:
            if phrase in text:
                reduction = max(reduction, 0.7)
        
        # Opinion markers - lighter reduction
        opinion_phrases = ["i think", "in my opinion", "imo", "imho", 
                          "just my opinion", "remember that", "keep in mind"]
        for phrase in opinion_phrases:
            if phrase in text:
                reduction = max(reduction, 0.4)
        
        # Question context
        for pattern in self._patterns.get("question_indicators", []):
            if pattern.lower() in text:
                reduction = max(reduction, 0.3)
                break
        
        # Past tense context
        for pattern in self._patterns.get("past_tense_indicators", []):
            if pattern.lower() in text:
                reduction = max(reduction, 0.3)
                break
        
        return reduction
