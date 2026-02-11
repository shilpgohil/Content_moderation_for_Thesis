

import numpy as np
from typing import Dict, List, Tuple, Optional

from shared.model_manager import get_sentence_transformer

# Cache for template embeddings
_template_embeddings = None
# GOLD-STANDARD SENTENCE TEMPLATES
FACT_TEMPLATES = [
    "Revenue increased 23% in Q3 2024.",
    "According to SEC filings, the company reported net income of $5.2 billion.",
    "The company announced earnings of $2.45 per share.",
    "EBIT margins expanded from 8% to 12% over the last two years.",
    "As disclosed in the 10-K filing, cash reserves stand at $15 billion.",
    "The quarterly report confirmed debt reduction of 20%.",
    "Operating cash flow grew by 15% year-over-year.",
    "The company has 45,000 employees across 30 countries.",
    "Net debt-to-EBITDA ratio improved to 1.5x from 2.3x.",
    "Dividend yield stands at 3.2% based on current price.",
    "JLR EBIT margins expanded, confirming operational improvement.",
    "Net automotive debt started falling consistently.",
]

OPINION_TEMPLATES = [
    "I believe this stock is significantly undervalued.",
    "In my view, management has demonstrated excellent capital allocation.",
    "I think the market is overreacting to short-term concerns.",
    "This appears to be a compelling buying opportunity.",
    "We believe the company is well-positioned for growth.",
    "In my opinion, the risk-reward is highly favorable.",
    "Management seems competent and shareholder-friendly.",
    "I consider this to be one of the best opportunities in the sector.",
    "The valuation looks attractive relative to peers.",
    "We expect strong performance over the next few years.",
]

ASSUMPTION_TEMPLATES = [
    "Assuming market conditions remain stable, growth should continue.",
    "If the company maintains current margins, profitability will improve.",
    "This thesis relies on management executing their stated strategy.",
    "Given that interest rates stay low, financing costs will remain manageable.",
    "Provided regulatory approval is obtained, expansion can proceed.",
    "The analysis assumes no major disruption from new competitors.",
    "Contingent on successful product launches, revenue targets are achievable.",
    "Based on the assumption that demand remains strong through 2025.",
    "If global enterprises materially cut core IT budgets, earnings visibility would weaken.",
    "This assumes no protectionist regulations restrict outsourcing.",
]

PROJECTION_TEMPLATES = [
    "The company will likely reach $10 billion in revenue by 2026.",
    "Expected to deliver 15% annual EPS growth over the next three years.",
    "Revenue is forecast to grow at a CAGR of 12% through 2027.",
    "Margins are projected to expand to 18% by Q4 2025.",
    "The stock is set to outperform the broader market.",
    "Analysts anticipate earnings of $5.00 per share next year.",
    "On track to achieve carbon neutrality by 2030.",
    "Poised to capture significant market share in the emerging EV segment.",
    "Management guides for 20% revenue growth in the coming fiscal year.",
    "The turnaround will likely result in improved free cash flow.",
]

CONTEXT_TEMPLATES = [
    "The company operates in the software-as-a-service industry.",
    "Founded in 1985, the firm has a long history of innovation.",
    "The global market for electric vehicles is estimated at $500 billion.",
    "This sector typically experiences cyclical demand patterns.",
    "Background: The company underwent restructuring in 2019.",
    "For context, the industry average P/E ratio is 25x.",
    "The thesis is structured around three key investment themes.",
    "Indian IT firms benefited as companies replaced high-cost in-house teams.",
    "Between 2018-2020, Tata Motors suffered from high debt and weak margins.",
    "From 2022 onward, Indian markets experienced high retail participation.",
]

def get_template_embeddings() -> Dict[str, np.ndarray]:
    global _template_embeddings
    
    if _template_embeddings is not None:
        return _template_embeddings
    
    model = get_sentence_transformer()
    
    _template_embeddings = {
        "FACT": model.encode(FACT_TEMPLATES, convert_to_numpy=True),
        "OPINION": model.encode(OPINION_TEMPLATES, convert_to_numpy=True),
        "ASSUMPTION": model.encode(ASSUMPTION_TEMPLATES, convert_to_numpy=True),
        "PROJECTION": model.encode(PROJECTION_TEMPLATES, convert_to_numpy=True),
        "CONTEXT": model.encode(CONTEXT_TEMPLATES, convert_to_numpy=True),
    }
    
    try:
        import analyzer
        if getattr(analyzer, '_verbose', True):
            print(f"Template embeddings computed: {sum(len(v) for v in _template_embeddings.values())} templates.")
    except (ImportError, AttributeError):
        pass  # Silent in API mode
    return _template_embeddings

def classify_by_embedding(sentence: str) -> Tuple[str, float]:
    """
    Classify a sentence by comparing its embedding to template embeddings.
    Returns (predicted_type, confidence_score).
    
    confidence = max_similarity - second_max_similarity (margin-based)
    """
    model = get_sentence_transformer()
    templates = get_template_embeddings()
    
    sent_embedding = model.encode([sentence], convert_to_numpy=True)[0]
    
    type_scores = {}
    for sent_type, template_embeds in templates.items():
        # Cosine similarity = dot product for normalized vectors
        similarities = np.dot(template_embeds, sent_embedding) / (
            np.linalg.norm(template_embeds, axis=1) * np.linalg.norm(sent_embedding)
        )
        type_scores[sent_type] = float(np.max(similarities))
    
    sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
    best_type, best_score = sorted_types[0]
    second_score = sorted_types[1][1] if len(sorted_types) > 1 else 0
    
    # Confidence based on margin between top two
    margin = best_score - second_score
    # Normalize confidence: margin of 0.1+ = high confidence
    confidence = min(1.0, margin * 5 + 0.5)  # Scale margin to 0.5-1.0 range
    
    return best_type, confidence

def get_embedding_vote(sentence: str) -> Dict[str, float]:
    """
    Get similarity scores for all types (for voting system).
    Returns dict mapping type to similarity score.
    """
    model = get_sentence_transformer()
    templates = get_template_embeddings()
    
    sent_embedding = model.encode([sentence], convert_to_numpy=True)[0]
    
    scores = {}
    for sent_type, template_embeds in templates.items():
        similarities = np.dot(template_embeds, sent_embedding) / (
            np.linalg.norm(template_embeds, axis=1) * np.linalg.norm(sent_embedding)
        )
        scores[sent_type] = float(np.max(similarities))
    
    return scores
