# Shared module init
from .model_manager import get_spacy, is_spacy_loaded

__all__ = ['get_spacy', 'is_spacy_loaded']
