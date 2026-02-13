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
    
    def __init__(self, config: Optional[ModerationConfig] = None):
        self.config = config or DEFAULT_CONFIG
        logger.info(f"Initializing ContentModerator with config: {self.config}")
        
        try:
            self._preprocessor = TextPreprocessor()
            self._linguistic_analyzer = LinguisticAnalyzer()
            self._domain_checker = DomainChecker()
            self._rule_engine = RuleEngine()
            self._toxicity_checker = ToxicityChecker()
            self._decision_engine = DecisionEngine(self.config)
            
            self._fuzzy_matcher = None
            self._semantic_checker = None
            self._content_analyzer = None
            logger.info("ContentModerator initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize ContentModerator: {e}", exc_info=True)
            raise

    def _get_fuzzy_matcher(self):
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
        try:
            if self._content_analyzer is None:
                logger.info("Loading ContentAnalyzer...")
                self._content_analyzer = ContentAnalyzer()
            return self._content_analyzer
        except Exception as e:
            logger.error(f"Failed to load ContentAnalyzer: {e}", exc_info=True)
            return None
    
    def moderate(self, content: str) -> dict:
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
            cleaned_text, metadata = self._preprocessor.preprocess(content)
            
            linguistic_result = self._linguistic_analyzer.analyze(content)
            metadata["linguistic_features"] = {
                "entities": len(linguistic_result.get("entities", [])),
                "is_available": linguistic_result.get("is_available", False)
            }
            
            domain_result = self._domain_checker.check(cleaned_text, linguistic_result)
            
            content_analysis = {"unified_score": 0.0, "is_substantive_finance": False}
            content_analyzer = self._get_content_analyzer()
            if content_analyzer:
                try:
                    content_analysis = content_analyzer.analyze(content, linguistic_result)
                    
                    vocab_score = domain_result.get("score", 0)
                    analysis_score = content_analysis.get("unified_score", 0)
                    
                    if analysis_score >= 0.50:
                        domain_result["score"] = max(vocab_score, analysis_score)
                        domain_result["is_finance"] = True
                    elif analysis_score < 0.35:
                        domain_result["score"] = 0.0
                        domain_result["is_finance"] = False
                        logger.info(f"Content analysis BLOCK: vocab={vocab_score:.3f}, analysis={analysis_score:.3f}")
                    else:
                        if vocab_score >= 0.20:
                            domain_result["score"] = (vocab_score + analysis_score) / 2
                            domain_result["is_finance"] = True
                        else:
                            domain_result["score"] = 0.0
                            domain_result["is_finance"] = False
                    
                    domain_result["content_analysis"] = content_analysis
                        
                except Exception as e:
                    logger.error(f"Content analysis failed: {e}", exc_info=True)
            
            scam_result = self._rule_engine.check(cleaned_text)
            
            fuzzy_result = {"score": 0.0, "matches": []}
            if self.config.enable_fuzzy:
                matcher = self._get_fuzzy_matcher()
                if matcher:
                    try:
                        fuzzy_result = matcher.check(cleaned_text)
                    except Exception as e:
                        logger.error(f"Fuzzy matching failed: {e}", exc_info=True)
            
            semantic_result = {"score": 0.0, "matches": []}
            semantic_checker = self._get_semantic_checker()
            if semantic_checker:
                try:
                    semantic_result = semantic_checker.check(content)
                except Exception as e:
                    logger.error(f"Semantic checking failed: {e}", exc_info=True)
            
            toxicity_result = self._toxicity_checker.check(cleaned_text, linguistic_result)
            
            decision = self._decision_engine.decide(
                domain_result,
                scam_result,
                toxicity_result,
                fuzzy_result,
                semantic_result
            )
            
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
            return {
                "decision": "FLAG",
                "confidence": 0.0,
                "risk_score": 1.0,
                "is_finance_related": False,
                "flags": ["system_error"],
                "explanation": "System encountered an error during processing."
            }
    
    def moderate_batch(self, contents: list) -> list:
        return [self.moderate(content) for content in contents]

