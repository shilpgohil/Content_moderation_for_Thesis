"""Linguistic analysis using SpaCy for deep text understanding."""

import re
import logging
from typing import Dict, List, Optional, Tuple, Set

try:
    import spacy
    from spacy.tokens import Doc, Span
    # Define custom attributes if needed (extensions)
    if not Doc.has_extension("negated_terms"):
        Doc.set_extension("negated_terms", default=[])
except ImportError:
    spacy = None

logger = logging.getLogger(__name__)


class LinguisticAnalyzer:
    """Provides deep linguistic analysis including NER, negation, and dependencies."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self._nlp = None
        self._disabled = False
        
        if spacy is None:
            logger.error("SpaCy is not installed. Linguistic analysis will be disabled.")
            self._disabled = True

    def _load_model(self):
        """Lazy load the SpaCy model."""
        if self._nlp is None and not self._disabled:
            try:
                logger.info(f"Loading SpaCy model: {self.model_name}")
                # Disable components we don't strictly need for speed, if necessary.
                # Here we need: toc2vec (if MD), tagger, parser, ner, attribute_ruler, lemmatizer.
                # We can disable 'senter' if parser provides sentences.
                self._nlp = spacy.load(self.model_name)
                logger.info("SpaCy model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load SpaCy model '{self.model_name}': {e}", exc_info=True)
                self._disabled = True

    def analyze(self, text: str) -> Dict:
        """
        Perform comprehensive linguistic analysis.
        
        Returns a dictionary containing:
        - entities: List of (text, label) tuples
        - sentences: List of sentence strings
        - tokens: List of token strings
        - negation_map: Dictionary mapping token indices to their negating words
        - pos_tags: List of (token, pos) tuples
        - dependencies: List of (subject, verb, object) triples (simplified)
        """
        if self._disabled:
            return self._get_empty_result()
        
        self._load_model()
        if self._disabled or self._nlp is None:
            return self._get_empty_result()
        
        try:
            doc = self._nlp(text)
            
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            sentences = [sent.text.strip() for sent in doc.sents]
            tokens = [token.text for token in doc]
            pos_tags = [(token.text, token.pos_) for token in doc]
            
            # Negation and Dependency Analysis
            negation_map = self._detect_negation(doc)
            dependencies = self._extract_dependencies(doc)
            
            return {
                "doc": doc, # Keep the doc for advanced users
                "entities": entities,
                "sentences": sentences,
                "tokens": tokens,
                "pos_tags": pos_tags,
                "negation_map": negation_map,
                "dependencies": dependencies,
                "is_available": True
            }
        except Exception as e:
            logger.error(f"Error during linguistic analysis: {e}", exc_info=True)
            return self._get_empty_result()

    def _detect_negation(self, doc) -> Dict[int, str]:
        """
        Map token indices to the negation word affecting them.
        Example: "not a fraud" -> {index_of_fraud: "not"}
        """
        negation_map = {}
        for token in doc:
            if token.dep_ == "neg":
                head_idx = token.head.i
                negation_map[head_idx] = token.text
                
                # Propagate negation to children of the head (adjectives, objects)
                # e.g. "is not a bad person" -> not -> bad
                for child in token.head.children:
                    if child.dep_ in ("attr", "dobj", "acomp", "amod") and child.i != token.i:
                        negation_map[child.i] = token.text
                        
        return negation_map

    def _extract_dependencies(self, doc) -> List[Dict]:
        """Extract simplified Subject-Verb-Object triples."""
        triples = []
        for token in doc:
            if token.pos_ == "VERB":
                subj = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                obj = [w for w in token.rights if w.dep_ in ("dobj", "pobj")]
                
                if subj:
                    subject_text = subj[0].text
                    object_text = obj[0].text if obj else None
                    triples.append({
                        "subject": subject_text,
                        "verb": token.text,
                        "object": object_text,
                        "negated": token.i in self._detect_negation(doc) # Simple check
                    })
        return triples

    def _get_empty_result(self) -> Dict:
        """Return a safe empty result structure."""
        return {
            "doc": None,
            "entities": [],
            "sentences": [],
            "tokens": [],
            "pos_tags": [],
            "negation_map": {},
            "dependencies": [],
            "is_available": False
        }
