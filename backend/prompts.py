
SYSTEM_PROMPT = """You are a professional investment thesis analyzer. Your job is to forensically examine investment theses and provide detailed scoring and analysis.

You will receive:
1. The raw thesis text
2. ML-extracted features (sentence classifications, entity counts, etc.)

Your task is to:
1. Score the LOGICAL COHERENCE component (0-20)
2. Validate/adjust ML sentence classifications for ambiguous cases
3. Detect any logical fallacies
4. Synthesize top strengths, weaknesses, and improvements

Be objective, cite specific sentences, and focus on structure/logic rather than agreement with the thesis."""

ANALYSIS_PROMPT_TEMPLATE = """
## THESIS TEXT:
{thesis_text}

## ML-EXTRACTED FEATURES:
- Total sentences: {sentence_count}
- Entities found: {entity_count}
- Source citations: {source_count}
- Numerical data points: {numerical_count}
- Risk vocabulary present: {risk_vocab}
- Vague/weasel words: {vague_count}

## ML SENTENCE CLASSIFICATIONS (Needs Your Validation):
{sentence_classifications}

## YOUR TASKS:

### 1. LOGICAL COHERENCE SCORE (0-20)
Evaluate:
- Argument flow (0-10): Do claims logically lead to conclusions?
- Cause-effect validity (0-5): Are causal relationships sound?
- Absence of fallacies (0-5): Are there logical errors?

### 2. VALIDATE SENTENCE CLASSIFICATIONS
Review the ML classifications above. For any that seem incorrect, provide corrections.

### 3. FALLACY DETECTION
Identify any logical fallacies present (cherry-picking, circular reasoning, false causation, etc.)

### 4. SYNTHESIS
Provide:
- Top 3 strengths (with specific examples from text)
- Top 3 weaknesses (with sentence references)
- Missing elements (what the thesis lacks)
- Top 3 improvement priorities

## OUTPUT FORMAT (JSON):
{{
    "logical_coherence": {{
        "argument_flow": <0-10>,
        "cause_effect_validity": <0-5>,
        "absence_of_fallacies": <0-5>,
        "total": <0-20>,
        "notes": ["<specific observations>"]
    }},
    "classification_corrections": [
        {{"sentence_index": <n>, "ml_type": "<original>", "correct_type": "<corrected>", "reason": "<why>"}}
    ],
    "fallacies_detected": [
        {{"type": "<fallacy_type>", "sentence_reference": "<quote or index>", "explanation": "<why this is a fallacy>"}}
    ],
    "synthesis": {{
        "top_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
        "top_weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
        "missing_elements": ["<element 1>", "<element 2>"],
        "improvement_priorities": ["<priority 1>", "<priority 2>", "<priority 3>"]
    }}
}}
"""

SENTENCE_BATCH_PROMPT = """
## AMBIGUOUS SENTENCES TO CLASSIFY

The following sentences could not be confidently classified by ML. Please classify each as:
- FACT: Verifiable data, past events, sourced information
- ASSUMPTION: Unstated premises, conditions taken for granted
- OPINION: Subjective views, beliefs, evaluations
- PROJECTION: Future predictions, forecasts, expectations
- CONTEXT: Background information, definitions

Also assess the SUPPORT level:
- SUPPORTED: Has backing evidence in the thesis
- PARTIAL: Some evidence but incomplete
- UNSUPPORTED: No supporting evidence provided

{sentences}

Output as JSON array:
[
    {{"index": <n>, "type": "<TYPE>", "support": "<SUPPORT_LEVEL>", "confidence": <0.0-1.0>, "issues": ["<any problems>"]}}
]
"""
