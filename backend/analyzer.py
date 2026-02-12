"""
Thesis Strength Analyzer - Hybrid ML + LLM Approach

This module analyzes investment theses using:
1. ML preprocessing (spaCy) for feature extraction
2. Pattern matching for quantitative scoring
3. LLM (OpenAI) for qualitative analysis and synthesis
"""

import os
import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env in the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Lazy imports for heavy libraries
_spacy_nlp = None
_openai_client = None
_verbose = True  # Global verbose flag

def get_spacy():
    """Lazy load spaCy model."""
    global _spacy_nlp
    if _spacy_nlp is None:
        import spacy
        try:
            _spacy_nlp = spacy.load("en_core_web_sm")
            if _verbose:
                print("spaCy model loaded.")
        except OSError as e:
            # In production (Docker), model should be pre-downloaded
            # Don't attempt runtime download - fail fast instead
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Ensure it was downloaded during Docker build."
            ) from e
    return _spacy_nlp

def get_openai_client():
    """Lazy load OpenAI client."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if _verbose:
            print("OpenAI client initialized.")
    return _openai_client


try:
    from .models import (
        SentenceType, SupportLevel, SentenceRole,
        SentenceAnalysis, ComponentScore, MLFeatures, StrengthReport,
        AuditEntry, LogicChainNode, WeaknessReport, ConsistencyIssue, BiasAnalysis
    )
    from .vocabularies import (
        EVIDENCE_MARKERS, VAGUE_WORDS, WEASEL_WORDS, CERTAINTY_WORDS,
        RISK_VOCABULARY, ACTIONABILITY_SIGNALS, FACT_INDICATORS,
        OPINION_INDICATORS, ASSUMPTION_INDICATORS, PROJECTION_INDICATORS,
        FINANCIAL_PATTERNS, FINANCIAL_STATEMENT_REFS, CREDIBLE_SOURCES,
        TIME_BOUND_PATTERNS, CAUSAL_CONNECTORS, CERTAINTY_LEVELS,
        OVERCONFIDENCE_INDICATORS
    )
    from .prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE
    from .templates import get_embedding_vote, classify_by_embedding
except ImportError:
    # Fallback for running script directly
    from models import (
        SentenceType, SupportLevel, SentenceRole,
        SentenceAnalysis, ComponentScore, MLFeatures, StrengthReport,
        AuditEntry, LogicChainNode, WeaknessReport, ConsistencyIssue, BiasAnalysis
    )
    from vocabularies import (
        EVIDENCE_MARKERS, VAGUE_WORDS, WEASEL_WORDS, CERTAINTY_WORDS,
        RISK_VOCABULARY, ACTIONABILITY_SIGNALS, FACT_INDICATORS,
        OPINION_INDICATORS, ASSUMPTION_INDICATORS, PROJECTION_INDICATORS,
        FINANCIAL_PATTERNS, FINANCIAL_STATEMENT_REFS, CREDIBLE_SOURCES,
        TIME_BOUND_PATTERNS, CAUSAL_CONNECTORS, CERTAINTY_LEVELS,
        OVERCONFIDENCE_INDICATORS
    )
    from prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE
    from templates import get_embedding_vote, classify_by_embedding


class StrengthAnalyzer:
    """
    Hybrid ML + LLM Thesis Strength Analyzer.
    Designed for API use - creates fresh instance per request.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        # Configure logging
        self.logger = logging.getLogger(__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.info("Initializing Strength Analyzer...")

    
    def _log(self, message: str):
            print(message)
    
    def analyze(self, thesis_text: str) -> StrengthReport:
        """
        Main entry point: Analyze a thesis and return a comprehensive report.
        """
        self._log("\n" + "="*60)
        self._log("THESIS STRENGTH ANALYSIS")
        self._log("="*60)
        
        # Step 1: ML Preprocessing
        self._log("\n[Step 1] ML Preprocessing...")
        sentences, ml_features = self._preprocess(thesis_text)
        self._log(f"   -> Extracted {len(sentences)} sentences")
        self._log(f"   -> Found {ml_features.entity_count} entities")
        
        # Step 2: Sentence Classification
        self._log("\n[Step 2] ML Sentence Classification...")
        sentence_analyses, ambiguous_indices = self._classify_sentences_ml(sentences)
        self._log(f"   -> Classified {len(sentence_analyses) - len(ambiguous_indices)} sentences with high confidence")
        self._log(f"   -> {len(ambiguous_indices)} sentences need LLM validation")
        
        # Step 3: Quantitative Scoring
        self._log("\n[Step 3] ML Quantitative Scoring...")
        evidence_score = self._score_evidence_quality(ml_features, sentence_analyses)
        clarity_score = self._score_clarity(ml_features, thesis_text)
        risk_score = self._score_risk_awareness(thesis_text, ml_features)
        action_score = self._score_actionability(thesis_text, ml_features)
        
        self._log(f"   -> Evidence Quality: {evidence_score.score}/20")
        self._log(f"   -> Clarity: {clarity_score.score}/20")
        self._log(f"   -> Risk Awareness: {risk_score.score}/20")
        self._log(f"   -> Actionability: {action_score.score}/20")
        
        # Step 4: LLM Analysis
        self._log("\n[Step 4] LLM Deep Analysis...")
        llm_result = self._llm_analyze(thesis_text, ml_features, sentence_analyses)
        
        # Extract logical coherence score from LLM
        coherence_score = ComponentScore(
            name="Logical Coherence",
            score=llm_result.get("logical_coherence", {}).get("total", 12),
            breakdown={
                "argument_flow": llm_result.get("logical_coherence", {}).get("argument_flow", 6),
                "cause_effect_validity": llm_result.get("logical_coherence", {}).get("cause_effect_validity", 3),
                "absence_of_fallacies": llm_result.get("logical_coherence", {}).get("absence_of_fallacies", 3)
            },
            notes=llm_result.get("logical_coherence", {}).get("notes", [])
        )
        self._log(f"   -> Logical Coherence: {coherence_score.score}/20")
        
        # Apply LLM corrections
        corrections = llm_result.get("classification_corrections", [])
        if corrections:
            self._log(f"   -> LLM corrected {len(corrections)} sentence classifications")
            self._apply_corrections(sentence_analyses, corrections)
            
        # Apply detected fallacies
        fallacies = llm_result.get("fallacies_detected", [])
        if fallacies:
            self._apply_fallacies(sentence_analyses, fallacies)
        
        # Step 5: Additional Features
        self._log("\n[Step 5] Building Additional Analysis...")
        
        # Build audit table (Step 4)
        audit_table = self._build_audit_table(sentence_analyses, corrections)
        self._log(f"   -> Audit table entries: {len(audit_table)}")
        
        # Build logic chain (Step 5)
        logic_chain = self._build_logic_chain(sentence_analyses, thesis_text)
        self._log(f"   -> Logic chain nodes: {len(logic_chain)}")
        
        # Build weakness report (Step 6)
        weakness_report = self._build_weakness_report(sentence_analyses, ml_features, thesis_text)
        self._log(f"   -> Categorized weaknesses built")
        
        # Check consistency (Rule 6)
        consistency_issues = self._check_consistency(sentence_analyses)
        if consistency_issues:
            self._log(f"   -> Consistency issues: {len(consistency_issues)}")
        
        # Detect bias (Rule 8)
        bias_analysis = self._detect_bias(sentence_analyses, thesis_text)
        self._log(f"   -> Bias analysis: {'Biased' if bias_analysis.is_biased else 'Balanced'}")
        
        # Step 6: Final Report
        self._log("\n[Step 6] Building Final Report...")
        
        # Count sentence types
        type_counts = self._count_sentence_types(sentence_analyses)
        supported_count = sum(1 for s in sentence_analyses if s.support_level == SupportLevel.SUPPORTED)
        
        # Calculate overall score
        overall = (
            evidence_score.score + 
            coherence_score.score + 
            clarity_score.score + 
            risk_score.score + 
            action_score.score
        )
        
        report = StrengthReport(
            overall_score=overall,
            grade=StrengthReport.calculate_grade(overall),
            evidence_quality=evidence_score,
            logical_coherence=coherence_score,
            clarity=clarity_score,
            risk_awareness=risk_score,
            actionability=action_score,
            sentence_analyses=sentence_analyses,
            ml_features=ml_features,
            fact_count=type_counts.get(SentenceType.FACT, 0),
            assumption_count=type_counts.get(SentenceType.ASSUMPTION, 0),
            opinion_count=type_counts.get(SentenceType.OPINION, 0),
            projection_count=type_counts.get(SentenceType.PROJECTION, 0),
            supported_percentage=(supported_count / len(sentence_analyses) * 100) if sentence_analyses else 0,
            top_strengths=llm_result.get("synthesis", {}).get("top_strengths", []),
            top_weaknesses=llm_result.get("synthesis", {}).get("top_weaknesses", []),
            missing_elements=llm_result.get("synthesis", {}).get("missing_elements", []),
            improvement_priorities=llm_result.get("synthesis", {}).get("improvement_priorities", []),
            # NEW FEATURES
            audit_table=audit_table,
            logic_chain=logic_chain,
            weakness_report=weakness_report,
            consistency_issues=consistency_issues,
            bias_analysis=bias_analysis
        )
        
        self._log(f"\n{'='*60}")
        self._log(f"OVERALL SCORE: {overall}/100 (Grade: {report.grade})")
        self._log(f"{'='*60}")
        
        return report

    
    def _preprocess(self, text: str) -> Tuple[List[str], MLFeatures]:
        """Use spaCy for preprocessing and feature extraction."""
        nlp = get_spacy()
        doc = nlp(text)
        
        # Extract sentences
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        
        # Extract entities
        entities = [ent.text for ent in doc.ents]
        companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Count various features
        features = MLFeatures(
            sentence_count=len(sentences),
            entity_count=len(entities),
            companies_mentioned=list(set(companies)),
            source_citation_count=self._count_source_citations(text),
            numerical_data_count=self._count_numerical_data(text),
            date_references=self._extract_dates(text, doc),
            vague_word_count=sum(1 for word in VAGUE_WORDS if word.lower() in text.lower()),
            weasel_word_count=sum(1 for word in WEASEL_WORDS if word.lower() in text.lower()),
            certainty_word_count=sum(1 for word in CERTAINTY_WORDS if word.lower() in text.lower()),
            risk_vocabulary_count=self._count_risk_vocabulary(text),
            actionability_signals=self._count_actionability_signals(text)
        )
        
        return sentences, features
    
    def _count_source_citations(self, text: str) -> int:
        count = 0
        for marker_list in EVIDENCE_MARKERS.values():
            for marker in marker_list:
                count += text.lower().count(marker.lower())
        return count
    
    def _count_numerical_data(self, text: str) -> int:
        count = 0
        for pattern in FINANCIAL_PATTERNS:
            count += len(re.findall(pattern, text))
        return count
    
    def _extract_dates(self, text: str, doc) -> List[str]:
        """Extract date references."""
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        # Also check for year patterns
        year_pattern = r'\b(20\d{2}|19\d{2})\b'
        dates.extend(re.findall(year_pattern, text))
        return list(set(dates))
    
    def _count_risk_vocabulary(self, text: str) -> int:
        """Count risk-related vocabulary."""
        text_lower = text.lower()
        count = 0
        for category in RISK_VOCABULARY.values():
            for term in category:
                count += text_lower.count(term.lower())
        return count
    
    def _count_actionability_signals(self, text: str) -> int:
        """Count actionability signals."""
        text_lower = text.lower()
        count = 0
        for category in ACTIONABILITY_SIGNALS.values():
            for term in category:
                count += text_lower.count(term.lower())
        return count
    
    def _classify_sentences_ml(self, sentences: List[str]) -> Tuple[List[SentenceAnalysis], List[int]]:
        """
        Classify sentences using ML patterns + embedding similarity.
        Uses weighted voting: 60% pattern signals + 40% embedding similarity.
        Returns analyses and indices of ambiguous sentences.
        """
        analyses = []
        ambiguous = []
        
        for i, sentence in enumerate(sentences):
            sent_lower = sentence.lower()
            
            # === PATTERN-BASED SCORING (60% weight) ===
            pattern_scores = {
                SentenceType.FACT: 0,
                SentenceType.OPINION: 0,
                SentenceType.ASSUMPTION: 0,
                SentenceType.PROJECTION: 0,
                SentenceType.CONTEXT: 0
            }
            
            for indicator in FACT_INDICATORS:
                if indicator in sent_lower:
                    pattern_scores[SentenceType.FACT] += 2
            
            for ref in FINANCIAL_STATEMENT_REFS:
                if ref.lower() in sent_lower:
                    pattern_scores[SentenceType.FACT] += 3
            
            for source in CREDIBLE_SOURCES:
                if source.lower() in sent_lower:
                    pattern_scores[SentenceType.FACT] += 2
            
            # Numbers and percentages suggest FACT
            if re.search(r'\d+\.?\d*%', sentence):
                pattern_scores[SentenceType.FACT] += 3
            if re.search(r'\$[\d,]+', sentence) or re.search(r'₹[\d,]+', sentence):
                pattern_scores[SentenceType.FACT] += 2
            
            # Time-bound patterns boost FACT
            for pattern in TIME_BOUND_PATTERNS:
                if re.search(pattern, sentence, re.IGNORECASE):
                    pattern_scores[SentenceType.FACT] += 2
                    break
            
            for indicator in OPINION_INDICATORS:
                if indicator in sent_lower:
                    pattern_scores[SentenceType.OPINION] += 3
            
            for indicator in ASSUMPTION_INDICATORS:
                if indicator in sent_lower:
                    pattern_scores[SentenceType.ASSUMPTION] += 3
            
            for indicator in PROJECTION_INDICATORS:
                if indicator in sent_lower:
                    pattern_scores[SentenceType.PROJECTION] += 2
            
            # Future tense
            if " will " in sent_lower or " would " in sent_lower:
                pattern_scores[SentenceType.PROJECTION] += 1
            
            # Causal connectors
            for conn in CAUSAL_CONNECTORS["strong_causal"]:
                if conn in sent_lower:
                    pattern_scores[SentenceType.CONTEXT] += 1
                    break
            
            pattern_max_type = max(pattern_scores, key=pattern_scores.get)
            pattern_max_score = pattern_scores[pattern_max_type]
            pattern_total = sum(pattern_scores.values())
            
            # === EMBEDDING SCORING (40% weight) ===
            # Optimization: Use embeddings only for low confidence
            use_embeddings = pattern_total < 5 or (pattern_max_score / max(pattern_total, 1)) < 0.7
            
            if use_embeddings and len(sentence.strip()) > 20:
                try:
                    embed_scores = get_embedding_vote(sentence)
                    # Normalize embedding scores
                    embed_max = max(embed_scores.values())
                    embed_normalized = {k: v / embed_max * 5 for k, v in embed_scores.items()}
                    
                    # Weighted combination: 60% pattern + 40% embedding
                    combined_scores = {}
                    for stype in pattern_scores:
                        type_name = stype.value
                        p_score = pattern_scores[stype]
                        e_score = embed_normalized.get(type_name, 0)
                        combined_scores[stype] = (p_score * 0.6) + (e_score * 0.4)
                    
                    max_type = max(combined_scores, key=combined_scores.get)
                    max_score = combined_scores[max_type]
                    total_score = sum(combined_scores.values())
                except Exception:
                    # Fallback to pattern-only on embedding error
                    max_type = pattern_max_type
                    max_score = pattern_max_score
                    total_score = pattern_total
            else:
                max_type = pattern_max_type
                max_score = pattern_max_score
                total_score = pattern_total
            
            # Calculate confidence
            if total_score == 0:
                max_type = SentenceType.CONTEXT
                confidence = 0.5
            else:
                confidence = max_score / max(total_score, 1)
                confidence = min(1.0, confidence * 1.2)  # Boost confidence slightly
            
            # === CERTAINTY ANALYSIS ===
            certainty_level = None
            for level, words in CERTAINTY_LEVELS.items():
                if any(word in sent_lower for word in words):
                    certainty_level = level
                    break
            
            issues = []
            
            # High certainty without evidence = issue
            if certainty_level == "high":
                has_evidence = any(marker in sent_lower for markers in EVIDENCE_MARKERS.values() for marker in markers)
                if not has_evidence:
                    issues.append("High certainty language without supporting evidence")
            
            for indicator in OVERCONFIDENCE_INDICATORS:
                if indicator.lower() in sent_lower:
                    issues.append(f"Overconfident claim: '{indicator}'")
                    break
            
            if any(word in sent_lower for word in VAGUE_WORDS):
                issues.append("Vague quantifier used")
            
            # Determine support level (relaxed criteria for SUPPORTED)
            support = SupportLevel.PARTIAL
            if any(marker in sent_lower for marker in EVIDENCE_MARKERS["strong"]):
                support = SupportLevel.SUPPORTED
            elif any(ref.lower() in sent_lower for ref in FINANCIAL_STATEMENT_REFS):
                support = SupportLevel.SUPPORTED
            elif any(marker in sent_lower for marker in EVIDENCE_MARKERS["moderate"]):
                support = SupportLevel.SUPPORTED
            elif re.search(r'\d+%|\$[\d,]+|₹[\d,]+', sentence):
                support = SupportLevel.PARTIAL
            elif any(word in sent_lower for word in WEASEL_WORDS) and max_type != SentenceType.PROJECTION:
                support = SupportLevel.UNSUPPORTED
            
            # Determine role
            role = SentenceRole.BRIDGE
            if i == 0 or "thesis" in sent_lower:
                role = SentenceRole.FOUNDATION
            elif max_type == SentenceType.FACT:
                role = SentenceRole.EVIDENCE
            elif i == len(sentences) - 1 or any(conn in sent_lower for conn in ["therefore", "thus", "hence"]):
                role = SentenceRole.CONCLUSION
            
            analysis = SentenceAnalysis(
                index=i + 1,
                text=sentence,
                sentence_type=max_type,
                support_level=support,
                role=role,
                confidence=confidence,
                issues=issues
            )
            analyses.append(analysis)
            
            # Mark as ambiguous if low confidence (lowered from 0.7 to 0.55 for better ML coverage)
            if confidence < 0.55:
                ambiguous.append(i)
        
        return analyses, ambiguous
    
    def _score_evidence_quality(self, features: MLFeatures, analyses: List[SentenceAnalysis]) -> ComponentScore:
        """Score evidence quality (0-20)."""
        # Verifiable data points (0-10)
        data_score = min(10, features.numerical_data_count * 1.5 + features.entity_count * 0.5)
        
        # Source attribution (0-5)
        source_score = min(5, features.source_citation_count * 1.5)
        
        # Recency (0-5) - check if recent dates mentioned
        current_year = 2026
        recent_dates = [d for d in features.date_references if any(str(y) in d for y in range(current_year-2, current_year+1))]
        recency_score = min(5, len(recent_dates) * 1.5)
        
        total = data_score + source_score + recency_score
        
        return ComponentScore(
            name="Evidence Quality",
            score=min(20, total),
            breakdown={
                "verifiable_data_points": round(data_score, 1),
                "source_attribution": round(source_score, 1),
                "recency": round(recency_score, 1)
            },
            notes=[
                f"Found {features.numerical_data_count} numerical data points",
                f"Found {features.source_citation_count} source citations",
                f"Date references: {len(features.date_references)}"
            ]
        )
    
    def _score_clarity(self, features: MLFeatures, text: str) -> ComponentScore:
        """Score clarity and specificity (0-20)."""
        word_count = len(text.split())
        
        # Clear position (0-5) - check for stance words
        stance_words = ["bullish", "bearish", "buy", "sell", "long", "short", "invest", "avoid"]
        stance_count = sum(1 for w in stance_words if w in text.lower())
        position_score = min(5, stance_count * 2)
        
        # Specific targets (0-10)
        target_patterns = [r'\$[\d,.]+', r'\d+%', r'Q[1-4]\s*\d{4}', r'\d{4}[-–]\d{2,4}']
        target_count = sum(len(re.findall(p, text)) for p in target_patterns)
        specificity_score = min(10, target_count * 1.5)
        
        # Unambiguous language (0-5)
        vague_ratio = features.vague_word_count / max(word_count / 100, 1)
        ambiguity_score = max(0, 5 - vague_ratio * 2)
        
        total = position_score + specificity_score + ambiguity_score
        
        return ComponentScore(
            name="Clarity & Specificity",
            score=min(20, total),
            breakdown={
                "clear_position": round(position_score, 1),
                "specific_targets": round(specificity_score, 1),
                "unambiguous_language": round(ambiguity_score, 1)
            },
            notes=[
                f"Stance indicators: {stance_count}",
                f"Specific targets/dates: {target_count}",
                f"Vague words: {features.vague_word_count}"
            ]
        )
    
    def _score_risk_awareness(self, text: str, features: MLFeatures) -> ComponentScore:
        """Score risk awareness (0-20)."""
        text_lower = text.lower()
        
        # Downside scenarios (0-10)
        risk_terms = RISK_VOCABULARY["risk_terms"]
        risk_count = sum(1 for term in risk_terms if term in text_lower)
        downside_score = min(10, risk_count * 2)
        
        # Stop loss / exit criteria (0-5)
        exit_terms = RISK_VOCABULARY["mitigation_terms"]
        exit_count = sum(1 for term in exit_terms if term in text_lower)
        exit_score = min(5, exit_count * 2)
        
        # Position sizing (0-5)
        sizing_terms = ["position size", "allocation", "% of portfolio", "weight", "cap"]
        sizing_count = sum(1 for term in sizing_terms if term in text_lower)
        sizing_score = min(5, sizing_count * 2)
        
        total = downside_score + exit_score + sizing_score
        
        return ComponentScore(
            name="Risk Awareness",
            score=min(20, total),
            breakdown={
                "downside_scenarios": round(downside_score, 1),
                "exit_criteria": round(exit_score, 1),
                "position_sizing": round(sizing_score, 1)
            },
            notes=[
                f"Risk terms found: {risk_count}",
                f"Exit/mitigation terms: {exit_count}",
                f"Sizing guidance: {sizing_count > 0}"
            ]
        )
    
    def _score_actionability(self, text: str, features: MLFeatures) -> ComponentScore:
        """Score actionability (0-20)."""
        text_lower = text.lower()
        
        # Executable trade ideas (0-10)
        action_terms = ACTIONABILITY_SIGNALS["strong"]
        action_count = sum(1 for term in action_terms if term in text_lower)
        trade_score = min(10, action_count * 2)
        
        # Entry/exit signals (0-5)
        entry_exit = ACTIONABILITY_SIGNALS["entry_exit"]
        entry_count = sum(1 for term in entry_exit if term in text_lower)
        signal_score = min(5, entry_count * 2)
        
        # Monitoring plan (0-5)
        monitor_terms = ACTIONABILITY_SIGNALS["monitoring"]
        monitor_count = sum(1 for term in monitor_terms if term in text_lower)
        monitor_score = min(5, monitor_count * 2)
        
        total = trade_score + signal_score + monitor_score
        
        return ComponentScore(
            name="Actionability",
            score=min(20, total),
            breakdown={
                "executable_trades": round(trade_score, 1),
                "entry_exit_signals": round(signal_score, 1),
                "monitoring_plan": round(monitor_score, 1)
            },
            notes=[
                f"Action terms: {action_count}",
                f"Entry/exit signals: {entry_count}",
                f"Monitoring triggers: {monitor_count}"
            ]
        )
    
    def _llm_analyze(self, thesis_text: str, features: MLFeatures, analyses: List[SentenceAnalysis]) -> Dict:
        """Use LLM for qualitative analysis."""
        client = get_openai_client()
        
        # Format sentence classifications for LLM
        classifications = "\n".join([
            f"[{a.index}] {a.text[:80]}... → {a.sentence_type.value} (conf: {a.confidence:.2f})"
            for a in analyses[:20]  # Limit to first 20 sentences
        ])
        
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            thesis_text=thesis_text[:3000],  # Limit text length
            sentence_count=features.sentence_count,
            entity_count=features.entity_count,
            source_count=features.source_citation_count,
            numerical_count=features.numerical_data_count,
            risk_vocab=features.risk_vocabulary_count,
            vague_count=features.vague_word_count + features.weasel_word_count,
            sentence_classifications=classifications
        )
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            self._log(f"   -> LLM analysis complete (tokens used: {response.usage.total_tokens})")
            return result
            
        except Exception as e:
            self._log(f"   [!] LLM Error: {e}")
            # Return fallback values
            return {
                "logical_coherence": {"argument_flow": 6, "cause_effect_validity": 3, "absence_of_fallacies": 3, "total": 12, "notes": ["LLM analysis failed"]},
                "classification_corrections": [],
                "fallacies_detected": [],
                "synthesis": {
                    "top_strengths": ["Unable to analyze - LLM error"],
                    "top_weaknesses": ["Unable to analyze - LLM error"],
                    "missing_elements": [],
                    "improvement_priorities": []
                }
            }
    
    def _apply_corrections(self, analyses: List[SentenceAnalysis], corrections: List[Dict]):
        """Apply LLM corrections to sentence classifications."""
        for corr in corrections:
            idx = corr.get("sentence_index", 0) - 1  # Convert to 0-indexed
            if 0 <= idx < len(analyses):
                try:
                    analyses[idx].sentence_type = SentenceType(corr.get("correct_type", analyses[idx].sentence_type.value))
                    analyses[idx].confidence = 0.95  # High confidence after LLM correction
                except ValueError:
                    pass  # Keep original if invalid type

    def _apply_fallacies(self, analyses: List[SentenceAnalysis], fallacies: List[Dict]):
        """Map global fallacies to specific sentence issues."""
        for fallacy in fallacies:
            ref = str(fallacy.get("sentence_reference", ""))
            explanation = fallacy.get("explanation", fallacy.get("type", "Logical issue"))
            
            # Try to match index
            match = re.search(r'\d+', ref)
            if match:
                idx = int(match.group()) - 1
                if 0 <= idx < len(analyses):
                    if analyses[idx].issues is None:
                        analyses[idx].issues = []
                    analyses[idx].issues.append(f"Fallback: {explanation}")
            
            # Also try to match text if ref is a quote
            if len(ref) > 10:
                for a in analyses:
                    if ref.lower() in a.text.lower() or a.text.lower() in ref.lower():
                        if a.issues is None:
                            a.issues = []
                        if f"Fallback: {explanation}" not in a.issues:
                            a.issues.append(f"Fallacy: {explanation}")
    
    def _count_sentence_types(self, analyses: List[SentenceAnalysis]) -> Dict[SentenceType, int]:
        """Count sentences by type."""
        counts = {}
        for a in analyses:
            counts[a.sentence_type] = counts.get(a.sentence_type, 0) + 1
        return counts
    
    # ============================================
    # NEW FEATURES: Steps 4, 5, 6 and Rules 6, 8
    # ============================================
    
    def _build_audit_table(self, analyses: List[SentenceAnalysis], llm_corrections: List[Dict]) -> List[AuditEntry]:
        """
        Build Fact vs Assumption audit table (Step 4).
        
        Per strength_idea spec, the table shows ALL statements with issues:
        
        Example from spec:
        | "Revenue grew 200%" | FACT | FACT | Missing source |
        | "Will dominate market" | FACT | ASSUMPTION | Stated as certainty |
        
        This includes:
        1. FACT → FACT with issue (like "Missing source")
        2. FACT → ASSUMPTION (misclassification - stated as certainty)
        3. FACT → PROJECTION (future prediction presented as fact)
        4. FACT → OPINION (subjective claim without evidence)
        """
        audit_entries = []
        processed_indices = set()
        
        # ========== DETECTION PATTERNS ==========
        
        # Certainty words that indicate assumptions/projections, not facts
        certainty_words = ["will", "shall", "must", "definitely", "certainly", "always", 
                          "never", "guaranteed", "undoubtedly", "inevitably", "surely",
                          "bound to", "destined"]
        
        # Future prediction indicators
        prediction_phrases = ["will be", "will become", "going to", "is expected to", 
                             "projected to", "forecast to", "destined to", "bound to",
                             "will likely", "will probably", "will continue"]
        
        # Opinion/subjective indicators
        opinion_words = ["best", "worst", "greatest", "superior", "inferior", 
                        "optimal", "ideal", "perfect", "excellent", "terrible",
                        "amazing", "outstanding", "remarkable", "exceptional"]
        
        # Evidence/source markers that validate factual claims
        source_markers = ["according to", "research shows", "data indicates", "studies show",
                         "reported by", "source:", "based on", "per ", "as stated in",
                         "as per", "citing", "referenced in", "documented in",
                         "quarterly report", "annual report", "sec filing", "10-k", "10-q"]
        
        # Numerical evidence that supports facts (but may still need source)
        has_numbers_pattern = lambda text: any(c.isdigit() for c in text) and ('%' in text or '$' in text or 'million' in text.lower() or 'billion' in text.lower())
        
        # ========== ANALYZE EACH SENTENCE ==========
        
        for a in analyses:
            text_lower = a.text.lower()
            text_clean = a.text.strip()
            
            # Skip very short sentences (headers, etc.)
            if len(text_clean.split()) < 5:
                continue
            
            # Skip CONTEXT type sentences
            if a.sentence_type == SentenceType.CONTEXT:
                continue
            
            # Check for various markers
            has_source = any(marker in text_lower for marker in source_markers)
            has_numbers = has_numbers_pattern(a.text)
            has_certainty = any(word in text_lower for word in certainty_words)
            has_prediction = any(phrase in text_lower for phrase in prediction_phrases)
            has_opinion = any(word in text_lower for word in opinion_words)
            
            # ========== PATTERN 1: FACT with missing source ==========
            # "Revenue grew 200%" - FACT - FACT - Missing source
            if a.sentence_type == SentenceType.FACT:
                if has_numbers and not has_source:
                    audit_entries.append(AuditEntry(
                        sentence_index=a.index,
                        statement=a.text,
                        classified_as="FACT",
                        should_be="FACT",
                        issue="Contains numerical claim without source citation"
                    ))
                    processed_indices.add(a.index)
                    continue
            
            # ========== PATTERN 2: FACT that should be ASSUMPTION ==========
            # "Will dominate market" - FACT - ASSUMPTION - Stated as certainty
            if a.sentence_type == SentenceType.FACT:
                if has_certainty and not has_source:
                    certainty_used = next((w for w in certainty_words if w in text_lower), "certainty language")
                    audit_entries.append(AuditEntry(
                        sentence_index=a.index,
                        statement=a.text,
                        classified_as="FACT",
                        should_be="ASSUMPTION",
                        issue=f"Stated as certainty using '{certainty_used}' without evidence"
                    ))
                    processed_indices.add(a.index)
                    continue
            
            # ========== PATTERN 3: FACT that should be PROJECTION ==========
            # Future predictions presented as established facts
            if a.sentence_type == SentenceType.FACT:
                if has_prediction:
                    audit_entries.append(AuditEntry(
                        sentence_index=a.index,
                        statement=a.text,
                        classified_as="FACT",
                        should_be="PROJECTION",
                        issue="Future prediction presented as established fact"
                    ))
                    processed_indices.add(a.index)
                    continue
            
            # ========== PATTERN 4: FACT that should be OPINION ==========
            # Subjective claims without objective evidence
            if a.sentence_type == SentenceType.FACT:
                if has_opinion and not has_source and not has_numbers:
                    opinion_used = next((w for w in opinion_words if w in text_lower), "subjective term")
                    audit_entries.append(AuditEntry(
                        sentence_index=a.index,
                        statement=a.text,
                        classified_as="FACT",
                        should_be="OPINION",
                        issue=f"Uses subjective term '{opinion_used}' without objective evidence"
                    ))
                    processed_indices.add(a.index)
                    continue
            
            # ========== PATTERN 5: ASSUMPTION without qualifier ==========
            # Assumptions that are presented too definitively
            if a.sentence_type == SentenceType.ASSUMPTION:
                if has_certainty:
                    audit_entries.append(AuditEntry(
                        sentence_index=a.index,
                        statement=a.text,
                        classified_as="ASSUMPTION",
                        should_be="ASSUMPTION",
                        issue="Assumption stated with high certainty - should include qualifier"
                    ))
                    processed_indices.add(a.index)
                    continue
            
            # ========== PATTERN 6: FACT needing context ==========
            # Facts that are correct but lack context
            if a.sentence_type == SentenceType.FACT:
                if a.support_level.value == "UNSUPPORTED" and a.index not in processed_indices:
                    audit_entries.append(AuditEntry(
                        sentence_index=a.index,
                        statement=a.text,
                        classified_as="FACT",
                        should_be="FACT",
                        issue="Factual claim marked unsupported - needs verification or source"
                    ))
                    processed_indices.add(a.index)
                    continue
        
        # ========== ADD LLM CORRECTIONS ==========
        for corr in llm_corrections:
            idx = corr.get("sentence_index", 0)
            if idx not in processed_indices and 0 < idx <= len(analyses):
                original_type = corr.get("ml_type", "").upper()
                correct_type = corr.get("correct_type", "").upper()
                reason = corr.get("reason", "Classification reviewed by LLM")
                
                if original_type and correct_type:
                    audit_entries.append(AuditEntry(
                        sentence_index=idx,
                        statement=analyses[idx-1].text if idx <= len(analyses) else "",
                        classified_as=original_type,
                        should_be=correct_type,
                        issue=reason
                    ))
        
        # Sort by sentence index and limit
        audit_entries.sort(key=lambda x: x.sentence_index)
        return audit_entries[:15]  # Limit to 15 most significant
    
    def _build_logic_chain(self, analyses: List[SentenceAnalysis], thesis_text: str) -> List[LogicChainNode]:
        """
        Build logic chain visualization (Step 5).
        Maps: Main Claim → Supporting Points → Evidence
        """
        logic_chain = []
        text_lower = thesis_text.lower()
        
        # Find main claim (usually first sentence or sentence with "thesis" keyword)
        main_claim_idx = 0
        best_score = -1
        
        for i, a in enumerate(analyses):
            # Skip very short sentences/headers
            if len(a.text) < 20:
                continue
                
            score = 0
            text_lower = a.text.lower()
            
            if "thesis" in text_lower:
                score += 10
            if a.role == SentenceRole.FOUNDATION:
                score += 5
            if a.sentence_type == SentenceType.FACT and i < 5:
                score += 2
            
            if score > best_score:
                best_score = score
                main_claim_idx = i
        
        if analyses:
            main_claim = analyses[main_claim_idx]
            evidence_refs = [a.index for a in analyses if a.sentence_type == SentenceType.FACT]
            logic_chain.append(LogicChainNode(
                claim=main_claim.text,
                claim_type="main_claim",
                has_evidence=len(evidence_refs) > 0,
                evidence_sentences=evidence_refs[:5],  # Limit to first 5
                confidence=main_claim.confidence
            ))
        
        # Find supporting points (PROJECTION or CONTEXT sentences with evidence)
        for a in analyses:
            if a.role == SentenceRole.EVIDENCE and a.sentence_type == SentenceType.FACT:
                logic_chain.append(LogicChainNode(
                    claim=a.text,
                    claim_type="supporting_evidence",
                    has_evidence=True,
                    evidence_sentences=[a.index],
                    confidence=a.confidence
                ))
        
        # Check for counter-arguments
        counter_patterns = ["however", "but", "on the other hand", "risk", "bear case", "downside"]
        for a in analyses:
            if any(p in a.text.lower() for p in counter_patterns):
                logic_chain.append(LogicChainNode(
                    claim=a.text,
                    claim_type="counter_argument",
                    has_evidence=a.support_level == SupportLevel.SUPPORTED,
                    evidence_sentences=[a.index],
                    confidence=a.confidence
                ))
                break  # Just need to confirm counter-arguments exist
        
        return logic_chain
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple word overlap similarity for circular reasoning detection."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "in", "that", "it"}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0
    
    def _build_weakness_report(self, analyses: List[SentenceAnalysis], features: MLFeatures, thesis_text: str) -> WeaknessReport:
        """
        Build categorized weakness report (Step 6 enhancement).
        Separates into: Language / Logical / Data weaknesses.
        """
        weakness = WeaknessReport()
        text_lower = thesis_text.lower()
        
        # LANGUAGE WEAKNESSES
        for word in VAGUE_WORDS:
            if word in text_lower:
                weakness.vague_terms.append(word)
        
        for word in WEASEL_WORDS:
            if word in text_lower:
                weakness.weasel_words.append(word)
        
        # Find unquantified claims (assertions without numbers)
        for a in analyses:
            if a.sentence_type in [SentenceType.FACT, SentenceType.PROJECTION]:
                if not re.search(r'\d+', a.text) and a.support_level == SupportLevel.UNSUPPORTED:
                    weakness.unquantified_claims.append({"index": a.index, "text": a.text[:60]})
                
                # Rule 7: Check for numerical context (Numbers without context/comparison)
                if a.sentence_type == SentenceType.FACT and re.search(r'\d+', a.text):
                    # Check for context words (growth, decline, compared, margin, yoy, etc.)
                    context_words = ["growth", "decline", "increase", "decrease", "margin", "yoy", "cagr", "compared", "versus", "vs", "from", "to"]
                    has_context = any(w in a.text.lower() for w in context_words)
                    if not has_context:
                        # Append to missing context if not already flagged
                        weakness.missing_context.append(f"Sentence {a.index}: Numerical claim without context/comparison")
        
        # LOGICAL WEAKNESSES
        # Missing connections: claims without causal connectors
        causal_markers = CAUSAL_CONNECTORS.get("strong_causal", [])
        has_connections = any(m in text_lower for m in causal_markers)
        if not has_connections:
            weakness.missing_connections.append("No explicit causal connectors found between claims")
        
        # Check for unstated assumptions
        for a in analyses:
            if a.sentence_type == SentenceType.PROJECTION and "if" not in a.text.lower():
                weakness.unstated_assumptions.append(f"Sentence {a.index}: Projection without stated conditions")
        
        # CIRCULAR REASONING DETECTION
        # Check for sentences that use conclusion keywords as premises
        circular_patterns = [
            (r"because .*(it is|they are|this is) (good|strong|solid|promising)", "Uses conclusion as premise"),
            (r"(proves|shows|demonstrates) that .*(because|since)", "Circular logic: proof references itself"),
            (r"(obviously|clearly|evidently) .*(therefore|thus|hence)", "Assumes conclusion in premise"),
        ]
        for a in analyses:
            text_lower = a.text.lower()
            for pattern, issue_desc in circular_patterns:
                if re.search(pattern, text_lower):
                    weakness.circular_reasoning_flags.append(f"Sentence {a.index}: {issue_desc}")
                    break
        
        # Check for repeated assertions without new evidence
        conclusions = [a for a in analyses if a.role == SentenceRole.CONCLUSION]
        foundations = [a for a in analyses if a.role == SentenceRole.FOUNDATION]
        for conclusion in conclusions:
            for foundation in foundations:
                # If conclusion just restates foundation without evidence chain
                if self._text_similarity(conclusion.text, foundation.text) > 0.6:
                    weakness.circular_reasoning_flags.append(
                        f"Sentences {foundation.index} and {conclusion.index}: Conclusion restates thesis without new evidence"
                    )
        
        # DATA WEAKNESSES
        # Unsourced statistics
        for a in analyses:
            if re.search(r'\d+%|\$[\d,]+', a.text):
                has_source = any(m in a.text.lower() for m in EVIDENCE_MARKERS["strong"])
                if not has_source:
                    weakness.unsourced_statistics.append({"index": a.index, "text": a.text[:60]})
        
        # Outdated info (data older than 2 years)
        current_year = 2026
        for a in analyses:
            years = re.findall(r'\b(20\d{2})\b', a.text)
            for year in years:
                if int(year) < current_year - 2:
                    weakness.outdated_info.append({"index": a.index, "year": year, "text": a.text[:50]})
        
        return weakness
    
    def _check_consistency(self, analyses: List[SentenceAnalysis]) -> List[ConsistencyIssue]:
        """
        Check internal consistency (Rule 6).
        Flags contradictory statements.
        """
        issues = []
        
        bullish_indices = []
        bearish_indices = []
        
        bullish_words = ["bullish", "buy", "long", "upside", "growth", "expand", "positive"]
        bearish_words = ["bearish", "sell", "short", "downside", "contraction", "negative", "decline"]
        
        for a in analyses:
            text_lower = a.text.lower()
            if any(w in text_lower for w in bullish_words):
                bullish_indices.append(a.index)
            if any(w in text_lower for w in bearish_words):
                bearish_indices.append(a.index)
        
        # If same sentence has both bullish and bearish, might be a balanced view
        # But if different sentences contradict without explanation, flag it
        if bullish_indices and bearish_indices:
            # Check if there's a contrast connector between them
            has_contrast = any("however" in a.text.lower() or "but" in a.text.lower() for a in analyses)
            if not has_contrast and len(bullish_indices) > 0 and len(bearish_indices) > 0:
                issues.append(ConsistencyIssue(
                    sentence_a_index=bullish_indices[0],
                    sentence_b_index=bearish_indices[0],
                    sentence_a_text=analyses[bullish_indices[0]-1].text if bullish_indices[0] <= len(analyses) else "",
                    sentence_b_text=analyses[bearish_indices[0]-1].text if bearish_indices[0] <= len(analyses) else "",
                    issue_type="conflicting_stance",
                    explanation="Thesis contains both bullish and bearish sentiments without clear contrast/explanation"
                ))
        
        return issues
    
    def _detect_bias(self, analyses: List[SentenceAnalysis], thesis_text: str) -> BiasAnalysis:
        """
        Detect bias/one-sided analysis (Rule 8).
        Checks sentiment ratio and counter-argument presence.
        """
        text_lower = thesis_text.lower()
        
        # Positive vs negative sentiment words
        positive_words = ["growth", "expand", "profit", "gain", "upside", "bullish", "opportunity", "strong", "success"]
        negative_words = ["risk", "loss", "decline", "downside", "bearish", "threat", "weak", "failure", "challenge"]
        
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        total = pos_count + neg_count if pos_count + neg_count > 0 else 1
        
        positive_ratio = (pos_count / total) * 100
        negative_ratio = (neg_count / total) * 100
        
        # Check for counter-arguments
        counter_patterns = ["however", "but", "on the other hand", "alternatively", "risk", "downside", "bear case"]
        counter_present = any(p in text_lower for p in counter_patterns)
        
        # Calculate bias score (0 = balanced, 1 = extremely one-sided)
        imbalance = abs(positive_ratio - negative_ratio) / 100
        bias_score = imbalance * (0.5 if counter_present else 1.0)
        
        is_biased = bias_score > 0.6 and not counter_present
        
        flags = []
        if positive_ratio > 80:
            flags.append("Overly positive sentiment (>80% positive)")
        if negative_ratio > 80:
            flags.append("Overly negative sentiment (>80% negative)")
        if not counter_present:
            flags.append("No counter-arguments or alternative scenarios presented")
        
        return BiasAnalysis(
            is_biased=is_biased,
            bias_score=bias_score,
            positive_ratio=positive_ratio,
            negative_ratio=negative_ratio,
            counter_arguments_present=counter_present,
            one_sided_flags=flags
        )
    
    def format_report(self, report: StrengthReport) -> str:
        """Format report as readable markdown with all sections."""
        output = []
        output.append("=" * 80)
        output.append("THESIS STRENGTH REPORT")
        output.append("=" * 80)
        output.append(f"OVERALL SCORE: [{report.overall_score}/100]")
        output.append(f"THESIS GRADE:  [{report.grade}]")
        output.append("")
        
        # Component scores
        output.append("### COMPONENT SCORES")
        components = [
            report.evidence_quality,
            report.logical_coherence,
            report.clarity,
            report.risk_awareness,
            report.actionability
        ]
        
        max_len = max(len(c.name) for c in components) if components else 0
        
        for comp in components:
            if comp:
                bar_len = 10
                filled_len = int(comp.score / 2)
                bar = "#" * filled_len + "-" * (bar_len - filled_len)
                output.append(f"  {comp.name:<{max_len + 2}} {bar} [{comp.score}/20]")
        
        output.append("")
        
        # Quick Stats
        output.append("### QUICK STATS")
        output.append(f"  * Total Sentences: {len(report.sentence_analyses)}")
        output.append(f"  * Facts: {report.fact_count} | Assumptions: {report.assumption_count} | Opinions: {report.opinion_count}")
        output.append(f"  * Supported Claims: {report.supported_percentage:.1f}%")
        
        output.append("")
        
        # Synthesis
        output.append("### TOP 3 STRENGTHS")
        for i, s in enumerate(report.top_strengths[:3], 1):
            output.append(f"  {i}. {s}")
        
        output.append("")
        output.append("### TOP 3 WEAKNESSES")
        for i, w in enumerate(report.top_weaknesses[:3], 1):
            output.append(f"  {i}. {w}")
        
        if report.missing_elements:
            output.append("")
            output.append("### CRITICAL MISSING ELEMENTS")
            for m in report.missing_elements:
                output.append(f"  [ ] {m}")
        
        output.append("")
        output.append("### IMPROVEMENT PRIORITIES")
        for i, p in enumerate(report.improvement_priorities[:3], 1):
            output.append(f"  {i}. {p}")
            
        # STEP 3: SENTENCE-LEVEL ANALYSIS (Newly Added)
        output.append("")
        output.append("### STEP 3: SENTENCE-LEVEL ANALYSIS")
        output.append("")
        for a in report.sentence_analyses:
            output.append(f"[Sentence #{a.index}]: \"{a.text}\"")
            output.append(f"  TYPE:    {a.sentence_type.value}")
            output.append(f"  SUPPORT: {a.support_level.value}")
            output.append(f"  ROLE:    {a.role.value}")
            if a.issues:
                output.append(f"  ISSUES:  {', '.join(a.issues)}")
            output.append("")
        
        # STEP 4: FACT VS ASSUMPTION AUDIT (Expanded)
        if report.audit_table:
            output.append("### STEP 4: FACT VS ASSUMPTION AUDIT")
            output.append("")
            # Header
            output.append(f"| {'#':<3} | {'Statement':<60} | {'Classified As':<15} | {'Should Be':<20} | {'Issue':<40} |")
            output.append(f"|{'-'*5}|{'-'*62}|{'-'*17}|{'-'*22}|{'-'*42}|")
            
            for entry in report.audit_table:
                # Truncate statement only for table fit, but keep it readable
                stmt = (entry.statement[:57] + "...") if len(entry.statement) > 60 else entry.statement
                output.append(f"| {entry.sentence_index:<3} | {stmt:<60} | {entry.classified_as:<15} | {entry.should_be:<20} | {entry.issue:<40} |")
            output.append("")
        
        # STEP 5: LOGIC CHAIN VISUALIZATION (Tree Format)
        if report.logic_chain:
            output.append("### STEP 5: LOGIC CHAIN VISUALIZATION")
            output.append("")
            
            # Find main claim
            main_claims = [n for n in report.logic_chain if n.claim_type == "main_claim"]
            if main_claims:
                mc = main_claims[0]
                output.append(f"Main Claim: {mc.claim}")
                
                # Supporting points
                supporting = [n for n in report.logic_chain if n.claim_type == "supporting_evidence"]
                for sp in supporting:
                    check = "[x]" if sp.has_evidence else "[ ]"
                    output.append(f"+-- Supporting Point [{check}]")
                    output.append(f"|   +-- Evidence: {'Present' if sp.has_evidence else 'Missing'} (Sentence #{sp.evidence_sentences[0] if sp.evidence_sentences else '?'})")
                    output.append(f"|       \"{sp.claim[:80]}...\"")
                
                # Counter arguments
                counters = [n for n in report.logic_chain if n.claim_type == "counter_argument"]
                processed = "Yes" if counters else "No"
                output.append(f"+-- Counter-arguments addressed: [{processed}]")
                if counters:
                    for c in counters:
                        output.append(f"    +-- \"{c.claim[:80]}...\"")
            else:
                output.append("No clear main logic chain detected.")
            output.append("")
        
        # STEP 6: WEAKNESS DETECTION (Expanded)
        if report.weakness_report:
            wr = report.weakness_report
            output.append("### STEP 6: CATEGORIZED WEAKNESSES")
            
            output.append("")
            output.append("**LANGUAGE WEAKNESSES:**")
            if wr.vague_terms:
                output.append(f"  - Vague terms: {', '.join(wr.vague_terms)}")
            if wr.weasel_words:
                output.append(f"  - Weasel words: {', '.join(wr.weasel_words)}")
            if wr.unquantified_claims:
                output.append(f"  - Unquantified claims: {len(wr.unquantified_claims)}")
                for item in wr.unquantified_claims:
                     output.append(f"    * Sentence {item['index']}: \"{item['text']}...\"")
            
            output.append("")
            output.append("**LOGICAL WEAKNESSES:**")
            if wr.missing_connections:
                for mc in wr.missing_connections:
                    output.append(f"  - {mc}")
            if wr.unstated_assumptions:
                output.append(f"  - Unstated assumptions: {len(wr.unstated_assumptions)}")
                for ua in wr.unstated_assumptions:
                    output.append(f"    * {ua}")
            if wr.circular_reasoning_flags:
                output.append(f"  - Circular reasoning: {len(wr.circular_reasoning_flags)}")
                for flag in wr.circular_reasoning_flags:
                    output.append(f"    * {flag}")
            
            output.append("")
            output.append("**DATA WEAKNESSES:**")
            if wr.unsourced_statistics:
                output.append(f"  - Unsourced statistics: {len(wr.unsourced_statistics)}")
                for us in wr.unsourced_statistics:
                    output.append(f"    * Sentence {us['index']}: \"{us['text']}...\"")
            if wr.outdated_info:
                output.append(f"  - Outdated information: {len(wr.outdated_info)}")
                for oi in wr.outdated_info:
                    output.append(f"    * Sentence {oi['index']} reference to {oi['year']}")
            if wr.missing_context:
                for mc in wr.missing_context:
                     output.append(f"  - {mc}")
            output.append("")
        
        # RULE 6: CONSISTENCY ISSUES
        if report.consistency_issues:
            output.append("### RULE 6: CONSISTENCY CHECK")
            for issue in report.consistency_issues:
                output.append(f"  [!] {issue.issue_type.replace('_', ' ').title()}:")
                output.append(f"      {issue.explanation}")
                output.append(f"      Conflict between Sentence {issue.sentence_a_index} and {issue.sentence_b_index}")
            output.append("")
            
        # RULE 8: BIAS ANALYSIS
        if report.bias_analysis:
            ba = report.bias_analysis
            output.append("### RULE 8: BIAS ANALYSIS")
            status = "[!] BIASED" if ba.is_biased else "[OK] BALANCED"
            output.append(f"  Status: {status} (Score: {ba.bias_score:.2f})")
            output.append(f"  Sentiment: {ba.positive_ratio:.0f}% Positive / {ba.negative_ratio:.0f}% Negative")
            output.append(f"  Counter-arguments: {'Present' if ba.counter_arguments_present else 'Missing'}")
            if ba.one_sided_flags:
                output.append("  Flags:")
                for flag in ba.one_sided_flags:
                    output.append(f"  - {flag}")
        
        output.append("=" * 80)
        return "\n".join(output)
