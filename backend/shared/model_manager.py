

_spacy_nlp = None
_sentence_transformer = None
_verbose = True

def get_spacy():
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
    return _spacy_nlp is not None

def get_sentence_transformer():
    global _sentence_transformer
    if _sentence_transformer is None:
        from sentence_transformers import SentenceTransformer
        _sentence_transformer = SentenceTransformer("all-MiniLM-L6-v2")
        if _verbose:
            print("[ModelManager] SentenceTransformer loaded (all-MiniLM-L6-v2)")
    return _sentence_transformer

def is_sentence_transformer_loaded():
    return _sentence_transformer is not None
