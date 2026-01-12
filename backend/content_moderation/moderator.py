"""Main content moderation entry point."""

import logging
from typing import Optional
from .config import ModerationConfig, DEFAULT_CONFIG
from .pipeline import (
    TextPreprocessor,
    RuleEngine,
    DomainChecker,
    ToxicityChecker,
    DecisionEngine,
    FuzzyMatcher,
    SemanticChecker,
    LinguisticAnalyzer
)
from .pipeline.content_analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)


class ContentModerator:
    """
    Main entry point for content moderation.
    
    Usage:
        moderator = ContentModerator()
        result = moderator.moderate("Your content here")
    """
    
    def __init__(self, config: Optional[ModerationConfig] = None):
        self.config = config or DEFAULT_CONFIG
        logger.info(f"Initializing ContentModerator with config: {self.config}")
        
        try:
            # Initialize core pipeline components
            self._preprocessor = TextPreprocessor()
            self._linguistic_analyzer = LinguisticAnalyzer() # New component
            self._domain_checker = DomainChecker()
            self._rule_engine = RuleEngine()
            self._toxicity_checker = ToxicityChecker()
            self._decision_engine = DecisionEngine(self.config)
            
            # Initialize advanced detection (lazy loaded)
            self._fuzzy_matcher = None
            self._semantic_checker = None
            self._content_analyzer = None  # World-class content analyzer
            logger.info("ContentModerator initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize ContentModerator: {e}", exc_info=True)
            raise

    def _get_fuzzy_matcher(self):
        """Lazy load fuzzy matcher."""
        try:
            if self._fuzzy_matcher is None and self.config.enable_fuzzy:
                logger.info("Loading FuzzyMatcher...")
                self._fuzzy_matcher = FuzzyMatcher(
                    threshold=self.config.fuzzy_threshold * 100
                )
            return self._fuzzy_matcher
        except Exception as e:
            logger.error(f"Failed to load FuzzyMatcher: {e}", exc_info=True)
            return None
    
    def _get_semantic_checker(self):
        """Lazy load semantic checker."""
        try:
            if self._semantic_checker is None and self.config.enable_semantic:
                logger.info("Loading SemanticChecker...")
                self._semantic_checker = SemanticChecker(
                    threshold=self.config.semantic_threshold,
                    enable=self.config.enable_semantic
                )
            return self._semantic_checker
        except Exception as e:
            logger.error(f"Failed to load SemanticChecker: {e}", exc_info=True)
            return None
    
    def _get_content_analyzer(self):
        """Lazy load the world-class content analyzer."""
        try:
            if self._content_analyzer is None:
                logger.info("Loading ContentAnalyzer...")
                self._content_analyzer = ContentAnalyzer()
            return self._content_analyzer
        except Exception as e:
            logger.error(f"Failed to load ContentAnalyzer: {e}", exc_info=True)
            return None
    
    def moderate(self, content: str) -> dict:
        """
        Moderate content and return decision.
        """
        if not content or not content.strip():
            return {
                "decision": "FLAG",
                "confidence": 1.0,
                "risk_score": 0.0,
                "is_finance_related": False,
                "flags": ["empty_content"],
                "explanation": "Content is empty"
            }
        
        try:
            # Step 1: Preprocess
            cleaned_text, metadata = self._preprocessor.preprocess(content)
            
            # Step 1.5: Linguistic Analysis
            linguistic_result = self._linguistic_analyzer.analyze(content) # Analyze original text
            metadata["linguistic_features"] = {
                "entities": len(linguistic_result.get("entities", [])),
                "is_available": linguistic_result.get("is_available", False)
            }
            
            # Step 2: Check finance domain relevance (pass text for word boundary matching)
            domain_result = self._domain_checker.check(cleaned_text, linguistic_result)
            
            # Step 2.5: WORLD-CLASS CONTENT ANALYSIS (NEW)
            # Run comprehensive multi-dimensional analysis on ALL content
            content_analysis = {"unified_score": 0.0, "is_substantive_finance": False}
            content_analyzer = self._get_content_analyzer()
            if content_analyzer:
                try:
                    content_analysis = content_analyzer.analyze(content, linguistic_result)
                    
                    # Apply content analysis to domain result
                    vocab_score = domain_result.get("score", 0)
                    analysis_score = content_analysis.get("unified_score", 0)
                    
                    # Decision Matrix:
                    # 1. Analysis >= 0.50 → PASS (trust semantic understanding)
                    # 2. Analysis < 0.35 → BLOCK (low substance regardless of vocab)
                    # 3. In between → use weighted combination
                    
                    if analysis_score >= 0.50:
                        # Strong semantic signal → trust it
                        domain_result["score"] = max(vocab_score, analysis_score)
                        domain_result["is_finance"] = True
                    elif analysis_score < 0.35:
                        # Weak content → BLOCK by setting score below threshold
                        # Set to 0.0 to ensure DecisionEngine blocks
                        domain_result["score"] = 0.0
                        domain_result["is_finance"] = False
                        logger.info(f"Content analysis BLOCK: vocab={vocab_score:.3f}, analysis={analysis_score:.3f}")
                    else:
                        # Borderline (0.35-0.50) → require vocab support
                        if vocab_score >= 0.20:
                            domain_result["score"] = (vocab_score + analysis_score) / 2
                            domain_result["is_finance"] = True
                        else:
                            # Low vocab + borderline analysis → BLOCK
                            domain_result["score"] = 0.0
                            domain_result["is_finance"] = False
                    
                    domain_result["content_analysis"] = content_analysis
                        
                except Exception as e:
                    logger.error(f"Content analysis failed: {e}", exc_info=True)
            
            # Step 3: Check for scam patterns (rule-based)
            scam_result = self._rule_engine.check(cleaned_text)
            
            # Step 4: Fuzzy matching for misspellings
            fuzzy_result = {"score": 0.0, "matches": []}
            if self.config.enable_fuzzy:
                matcher = self._get_fuzzy_matcher()
                if matcher:
                    try:
                        fuzzy_result = matcher.check(cleaned_text)
                    except Exception as e:
                        logger.error(f"Fuzzy matching failed: {e}", exc_info=True)
            
            # Step 5: Semantic similarity check
            semantic_result = {"score": 0.0, "matches": []}
            semantic_checker = self._get_semantic_checker()
            if semantic_checker:
                try:
                    semantic_result = semantic_checker.check(content)  # Use original text
                except Exception as e:
                    logger.error(f"Semantic checking failed: {e}", exc_info=True)
            
            # Step 6: Check toxicity
            toxicity_result = self._toxicity_checker.check(cleaned_text, linguistic_result)
            
            # Step 7: Make final decision (combining all signals)
            decision = self._decision_engine.decide(
                domain_result,
                scam_result,
                toxicity_result,
                fuzzy_result,
                semantic_result
            )
            
            # Add preprocessing metadata
            decision["metadata"] = {
                "original_length": metadata.get("original_length", 0),
                "had_obfuscation": metadata.get("had_obfuscation", False),
                "urls_found": len(metadata.get("urls_found", [])),
                "finance_terms_matched": domain_result.get("matched_terms", [])[:5],
                "negative_terms_found": domain_result.get("negative_terms_found", []),
                "fuzzy_matches": len(fuzzy_result.get("matches", [])),
                "semantic_match": semantic_result.get("has_semantic_match", False)
            }
            
            logger.info(f"Moderated content (Decision: {decision['decision']}, Score: {decision['risk_score']:.2f})")
            return decision

        except Exception as e:
            logger.error(f"Unexpected error during moderation: {e}", exc_info=True)
            # Fail safe: Block if critical error? Or Flag? 
            # Production safe: FLAG and alert.
            return {
                "decision": "FLAG",
                "confidence": 0.0,
                "risk_score": 1.0,  # High risk due to error
                "is_finance_related": False,
                "flags": ["system_error"],
                "explanation": "System encountered an error during processing."
            }
    
    def moderate_batch(self, contents: list) -> list:
        """Moderate multiple contents."""
        return [self.moderate(content) for content in contents]

