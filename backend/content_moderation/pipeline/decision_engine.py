from typing import Dict, Optional
from ..config import ModerationConfig, DEFAULT_CONFIG


class DecisionEngine:
    
    DECISION_BLOCK = "BLOCK"
    DECISION_FLAG = "FLAG"
    DECISION_PASS = "PASS"
    
    def __init__(self, config: ModerationConfig = None):
        self.config = config or DEFAULT_CONFIG
    
    def decide(
        self,
        domain_result: dict,
        scam_result: dict,
        toxicity_result: dict,
        fuzzy_result: Optional[dict] = None,
        semantic_result: Optional[dict] = None
    ) -> dict:
        
        fuzzy_result = fuzzy_result or {"score": 0.0, "matches": []}
        semantic_result = semantic_result or {"score": 0.0, "matches": []}
        
        result = {
            "decision": self.DECISION_PASS,
            "confidence": 1.0,
            "risk_score": 0.0,
            "is_finance_related": domain_result.get("is_finance", False),
            "flags": [],
            "explanation": ""
        }
        
        finance_score = domain_result.get("score", 0)
        is_finance = domain_result.get("is_finance", False)
        
        if finance_score < self.config.finance_flag_threshold or (finance_score < 0.15 and not is_finance):
            result["decision"] = self.DECISION_BLOCK
            result["flags"].append("off_topic")
            result["explanation"] = "Content is not related to finance"
            result["confidence"] = 1.0 - finance_score
            return result
        
        if finance_score < self.config.finance_pass_threshold:
            result["flags"].append("low_finance_relevance")
        
        risk_score = self._calculate_risk_score(
            scam_result, toxicity_result, fuzzy_result, semantic_result
        )
        result["risk_score"] = risk_score
        
        flags, high_sev_count = self._collect_flags(
            scam_result, toxicity_result, fuzzy_result, semantic_result
        )
        result["flags"].extend(flags)
        
        self._determine_verdict(result, risk_score, high_sev_count)
        
        return result

    def _calculate_risk_score(self, scam: dict, toxic: dict, fuzzy: dict, semantic: dict) -> float:
        rule_score = (
            scam.get("score", 0) * self.config.scam_weight +
            toxic.get("score", 0) * self.config.toxicity_weight
        )
        fuzzy_w = fuzzy.get("score", 0) * self.config.fuzzy_weight
        semantic_w = semantic.get("score", 0) * self.config.semantic_weight
        
        return round(max(rule_score, fuzzy_w, semantic_w), 3)

    def _collect_flags(self, scam: dict, toxic: dict, fuzzy: dict, semantic: dict) -> tuple:
        flags = []
        high_severity_count = 0
        
        s_flags, s_cnt = self._get_scam_flags(scam)
        flags.extend(s_flags)
        high_severity_count += s_cnt
        
        f_flags, f_cnt = self._get_fuzzy_flags(fuzzy)
        flags.extend(f_flags)
        high_severity_count += f_cnt
        
        sem_flags, sem_cnt = self._get_semantic_flags(semantic)
        flags.extend(sem_flags)
        high_severity_count += sem_cnt
        
        t_flags, t_cnt = self._get_toxic_flags(toxic)
        flags.extend(t_flags)
        high_severity_count += t_cnt
                    
        return flags, high_severity_count

    def _get_scam_flags(self, result: dict) -> tuple:
        flags = []
        count = 0
        if result.get("score", 0) >= 0.2:
            for signal in result.get("signals", []):
                if signal.get("severity") == "high":
                    count += 1
                flags.append(f"scam:{signal.get('pattern', 'unknown')[:30]}")
        return flags, count

    def _get_fuzzy_flags(self, result: dict) -> tuple:
        flags = []
        count = 0
        for match in result.get("matches", [])[:3]:
            if match.get("severity") == "high":
                count += 1
            flags.append(f"fuzzy:{match.get('matched', '')[:30]}")
        return flags, count

    def _get_semantic_flags(self, result: dict) -> tuple:
        flags = []
        count = 0
        for match in result.get("matches", [])[:2]:
            if match.get("severity") == "high":
                count += 1
            flags.append(f"semantic:{match.get('similarity', 0):.0%}")
        return flags, count

    def _get_toxic_flags(self, result: dict) -> tuple:
        flags = []
        count = 0
        if result.get("is_toxic"):
            categories = result.get("categories", [])
            matched_terms = result.get("matched", [])
            
            for i, term in enumerate(matched_terms):
                category = categories[i] if i < len(categories) else categories[0] if categories else "toxicity"
                flags.append(f"toxic:{category}:{term}")
                
                if category in ["hate_speech", "personal_attack", "severe_profanity", "threat", "harassment", "doxxing", "defamation"]:
                    count += 1
            
            if not matched_terms and categories:
                for category in categories:
                    flags.append(f"toxic:{category}")
                    if category in ["hate_speech", "personal_attack", "severe_profanity", "threat", "harassment", "doxxing", "defamation"]:
                        count += 1
        return flags, count

    def _determine_verdict(self, result: dict, score: float, severity_count: int):
        if score >= self.config.block_threshold or severity_count >= self.config.min_block_signals:
            result["decision"] = self.DECISION_BLOCK
            result["explanation"] = self._build_explanation(result["flags"], "blocked")
            result["confidence"] = min(0.99, score)
        
        elif score >= self.config.flag_threshold or (severity_count >= 1 and score >= 0.1):
            result["decision"] = self.DECISION_FLAG
            result["explanation"] = self._build_explanation(result["flags"], "flagged")
            result["confidence"] = score
        
        else:
            result["explanation"] = "Content appears safe"
        return result
    
    def _build_explanation(self, flags: list, action: str) -> str:
        if not flags:
            return f"Content {action} based on risk score"
        
        reasons = []
        for flag in flags[:3]:
            if flag.startswith("scam:"):
                reasons.append("scam pattern detected")
            elif flag.startswith("fuzzy:"):
                reasons.append("misspelled scam phrase detected")
            elif flag.startswith("semantic:"):
                reasons.append("similar to known scam")
            elif flag.startswith("toxic:"):
                category = flag.replace("toxic:", "")
                reasons.append(f"{category} content")
            elif flag == "off_topic":
                reasons.append("not finance related")
            elif flag == "low_finance_relevance":
                reasons.append("low finance relevance")
        
        unique_reasons = list(dict.fromkeys(reasons))
        return f"Content {action}: {', '.join(unique_reasons)}"

