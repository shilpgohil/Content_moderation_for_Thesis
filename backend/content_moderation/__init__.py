"""
Content Moderation Module for Finance Platform.
Lightweight rule-based content moderation with scam detection,
finance domain verification, and toxicity checking.
"""

import logging
from .moderator import ContentModerator
from .config import ModerationConfig

# Set up logging to avoid "No handler found" warnings
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["ContentModerator", "ModerationConfig"]
__version__ = "1.0.0"
