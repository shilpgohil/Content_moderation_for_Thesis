"""
Shared Model Manager - Singleton for ML models across modules.
Optimized for 512MB free tier deployment.
"""

_spacy_nlp = None
_verbose = True


def get_spacy():
    """
    Lazy load spaCy model - shared across Content Moderation and Thesis Analyzer.
    Uses en_core_web_sm (smaller) for 512MB deployment.
    """
    global _spacy_nlp
    if _spacy_nlp is None:
        import spacy
        try:
            _spacy_nlp = spacy.load("en_core_web_sm")
            if _verbose:
                print("[ModelManager] spaCy model loaded (en_core_web_sm)")
        except OSError as e:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            ) from e
    return _spacy_nlp


def is_spacy_loaded():
    """Check if spaCy is already loaded."""
    return _spacy_nlp is not None
