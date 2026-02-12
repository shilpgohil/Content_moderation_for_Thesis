"""Semantic similarity checking using sentence transformers."""

import json
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np


class SemanticChecker:
    """Detects scam content using semantic similarity with pre-computed embeddings."""
    
    # Similarity threshold for flagging content
    DEFAULT_THRESHOLD = 0.75
    
    def __init__(self, threshold: float = None, enable: bool = True):
        """
        Initialize semantic checker with lazy model loading.
        
        Args:
            threshold: Cosine similarity threshold (0-1)
            enable: Whether semantic checking is enabled
        """
        self.threshold = threshold or self.DEFAULT_THRESHOLD
        self.enable = enable
        
        # Lazy loading
        self._model = None
        self._template_embeddings = None
        self._templates = None
        self.WHITELIST_CONTEXTS = []
        self._load_whitelist()
    
    def _load_model(self):
        """Lazy load the sentence transformer model from shared manager."""
        if self._model is None:
            from shared.model_manager import get_sentence_transformer
            self._model = get_sentence_transformer()
        return self._model
    
    def _load_templates(self) -> List[Dict]:
        """Load scam templates from JSON file or use defaults."""
        if self._templates is None:
            data_path = Path(__file__).parent.parent / "data" / "scam_templates.json"
            
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._templates = data.get("templates", [])
            else:
                # Default templates if file doesn't exist
                self._templates = self._get_default_templates()
        
        return self._templates
    
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

    def _get_default_templates(self) -> List[Dict]:
        """Default scam templates for semantic matching."""
        return [
            # Guaranteed returns scams
            {"text": "Join my group for guaranteed returns every month", "severity": "high"},
            {"text": "I guarantee you will make profit with my tips", "severity": "high"},
            {"text": "Get assured returns on your investment", "severity": "high"},
            {"text": "100 percent guaranteed profit in stock market", "severity": "high"},
            
            # Double money schemes
            {"text": "Double your money in just a few days", "severity": "high"},
            {"text": "Multiply your capital quickly with us", "severity": "high"},
            {"text": "Turn your investment into twice the amount", "severity": "high"},
            {"text": "Your money will grow 2x in short time", "severity": "high"},
            
            # Insider information
            {"text": "I have insider information about a stock", "severity": "high"},
            {"text": "Secret tip that will make you rich", "severity": "high"},
            {"text": "Confidential information from company insiders", "severity": "high"},
            {"text": "This stock will jump because of leaked news", "severity": "high"},
            
            # Risk-free claims
            {"text": "This is a completely risk-free investment", "severity": "high"},
            {"text": "Zero risk way to make money in stocks", "severity": "high"},
            {"text": "There is no chance of losing money here", "severity": "high"},
            {"text": "Safe investment with guaranteed profits", "severity": "high"},
            
            # Money requests
            {"text": "Send money to my account to join", "severity": "high"},
            {"text": "Pay the registration fee to my UPI", "severity": "high"},
            {"text": "Transfer funds to start making money", "severity": "high"},
            {"text": "Deposit amount in our trading pool", "severity": "high"},
            
            # Urgency/FOMO
            {"text": "Last chance to join our exclusive group", "severity": "medium"},
            {"text": "Limited spots available act now", "severity": "medium"},
            {"text": "This opportunity will not come again", "severity": "medium"},
            {"text": "Hurry up before its too late", "severity": "medium"},
            
            # Trading on behalf
            {"text": "We will trade on your behalf and give profits", "severity": "high"},
            {"text": "Just give us your capital we do the rest", "severity": "high"},
            {"text": "Let us handle your money for guaranteed returns", "severity": "high"},
            
            # Unrealistic daily returns
            {"text": "Make thousands of rupees every day from home", "severity": "high"},
            {"text": "Earn daily income through our trading system", "severity": "medium"},
            {"text": "Get fixed daily returns on investment", "severity": "high"},
            
            # VIP/Premium groups
            {"text": "Join our VIP telegram for premium stock tips", "severity": "medium"},
            {"text": "Our premium members make lakhs every month", "severity": "medium"},
            {"text": "Exclusive signals for VIP members only", "severity": "medium"},
        ]
    
    def _compute_embeddings(self):
        """Compute embeddings for all templates."""
        if self._template_embeddings is None:
            model = self._load_model()
            templates = self._load_templates()
            
            texts = [t["text"] for t in templates]
            self._template_embeddings = model.encode(texts, convert_to_numpy=True)
        
        return self._template_embeddings
    

    
    def check(self, text: str) -> Dict:
        """Check text for semantic similarity to known scam patterns."""
        if not self.enable:
            return {
                "score": 0.0,
                "matches": [],
                "enabled": False
            }
        
        text_lower = text.lower()
        
        # Skip if whitelist context is present (educational/warning content)
        for context in self.WHITELIST_CONTEXTS:
            if context in text_lower:
                return {
                    "score": 0.0,
                    "matches": [],
                    "has_semantic_match": False,
                    "enabled": True,
                    "skipped_context": context
                }
        
        try:
            model = self._load_model()
            template_embeddings = self._compute_embeddings()
            templates = self._load_templates()
            
            # Encode input text
            text_embedding = model.encode([text], convert_to_numpy=True)[0]
            
            # Compute cosine similarities
            similarities = self._cosine_similarity(text_embedding, template_embeddings)
            
            # Find matches above threshold
            matches = []
            max_similarity = 0.0
            
            for i, sim in enumerate(similarities):
                if sim >= self.threshold:
                    matches.append({
                        "template": templates[i]["text"],
                        "similarity": round(float(sim), 3),
                        "severity": templates[i]["severity"]
                    })
                max_similarity = max(max_similarity, sim)
            
            # Sort by similarity
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Calculate score based on best match
            if max_similarity >= self.threshold:
                # Scale score: threshold->1.0 maps to 0.5->1.0
                score = 0.5 + (max_similarity - self.threshold) / (1 - self.threshold) * 0.5
            else:
                # Quadratic scaling for sub-threshold matches to suppress noise while keeping weak signals
                # Sim 0.3 (market) -> ~0.08 score (Safe)
                # Sim 0.65 -> ~0.37 score (Flag)
                score = (max_similarity / self.threshold) ** 2 * 0.5
            
            high_severity_count = sum(1 for m in matches if m["severity"] == "high")
            
            return {
                "score": round(float(score), 3),
                "max_similarity": round(float(max_similarity), 3),
                "matches": matches[:5],  # Top 5 matches
                "has_semantic_match": len(matches) > 0,
                "high_severity_count": high_severity_count,
                "enabled": True
            }
            
        except Exception as e:
            # Graceful degradation if model fails
            return {
                "score": 0.0,
                "matches": [],
                "error": str(e),
                "enabled": False
            }
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between vector a and matrix b."""
        a_norm = a / np.linalg.norm(a)
        b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
        return np.dot(b_norm, a_norm)
