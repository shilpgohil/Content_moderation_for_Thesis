

import re
import unicodedata
from typing import Tuple, List

class TextPreprocessor:
    
    # L33t speak mappings
    LEET_MAP = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '7': 't', '8': 'b', '@': 'a', '$': 's', '!': 'i'
    }
    
    # Patterns to extract
    URL_PATTERN = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
    MENTION_PATTERN = re.compile(r'@\w+')
    
    def preprocess(self, text: str) -> Tuple[str, dict]:
        """
        Clean and normalize text.
        Returns cleaned text and extracted metadata.
        """
        metadata = {
            "original_length": len(text),
            "urls_found": [],
            "mentions_found": [],
            "had_obfuscation": False
        }
        
        # Extract URLs before cleaning
        metadata["urls_found"] = self.URL_PATTERN.findall(text)
        text = self.URL_PATTERN.sub(" [URL] ", text)
        
        # Extract mentions
        metadata["mentions_found"] = self.MENTION_PATTERN.findall(text)
        text = self.MENTION_PATTERN.sub(" [MENTION] ", text)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Decode l33t speak
        decoded = self._decode_leet(text)
        if decoded != text.lower():
            metadata["had_obfuscation"] = True
            text = decoded
        else:
            text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text, metadata
    
    def _decode_leet(self, text: str) -> str:
        """Convert l33t speak to normal text, preserving standalone numbers."""
        # Split into words, decode each word separately
        words = re.findall(r'\S+', text.lower())
        result = []
        
        for word in words:
            # Matches: 100, 100%, $100, 100$, ₹100, 100,000, $1,000
            if re.match(r'^[$₹]?[\d,]+[%$]?$', word):
                result.append(word)
            else:
                # Decode l33t speak in alphanumeric words
                decoded_word = ''.join(self.LEET_MAP.get(c, c) for c in word)
                result.append(decoded_word)
        
        return ' '.join(result)
    

