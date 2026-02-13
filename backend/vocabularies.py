


EVIDENCE_MARKERS = {
    "strong": [
        "according to", "reported", "data shows", "SEC filing", 
        "financial statements", "confirmed", "announced", "disclosed",
        "quarterly report", "annual report", "10-K", "10-Q"
    ],
    "moderate": [
        "suggests", "indicates", "based on", "research shows",
        "analysis indicates", "historically"
    ],
    "weak": [
        "seems", "appears", "might indicate", "could suggest"
    ]
}


SOURCE_PATTERNS = [
    r"according to\s+\w+",
    r"as per\s+\w+",
    r"reported by\s+\w+",
    r"\(\d{4}\)",  # Year citations
    r"Q[1-4]\s*\d{4}",  # Quarter references
    r"FY\d{2,4}",  # Fiscal year
]


VAGUE_WORDS = [
    "some", "many", "most", "often", "usually", "significant",
    "substantial", "considerable", "various", "numerous"
]

WEASEL_WORDS = [
    "might", "could", "possibly", "potentially", "arguably",
    "perhaps", "probably", "likely", "tend to", "generally"
]

CERTAINTY_WORDS = [
    "definitely", "certainly", "always", "never", "absolutely",
    "guaranteed", "undoubtedly", "without doubt"
]


RISK_VOCABULARY = {
    "risk_terms": [
        "risk", "downside", "bear case", "if fails", "could break",
        "what could go wrong", "threats", "challenges", "headwinds"
    ],
    "mitigation_terms": [
        "stop loss", "exit if", "position size", "limit exposure",
        "hedge", "diversify", "cap allocation", "monitor"
    ],
    "scenario_terms": [
        "if", "scenario", "in case", "should", "worst case",
        "bear case", "stress test"
    ]
}


ACTIONABILITY_SIGNALS = {
    "strong": [
        "buy", "sell", "enter", "exit", "allocate", "position",
        "trade", "invest", "accumulate", "book profits"
    ],
    "entry_exit": [
        "entry point", "exit when", "target price", "stop loss at",
        "buy at", "sell at", "take profit"
    ],
    "monitoring": [
        "watch for", "monitor", "track", "reassess if", "review when",
        "catalyst", "trigger", "signal"
    ],
    "sizing": [
        "position size", "allocation", "% of portfolio", "weight",
        "exposure", "cap at", "limit to"
    ]
}


FACT_INDICATORS = [
    "reported", "announced", "disclosed", "confirmed", "released",
    "grew", "increased", "decreased", "fell", "rose", "expanded"
]

OPINION_INDICATORS = [
    "I think", "I believe", "in my view", "in my opinion",
    "we expect", "we believe", "appears to be", "seems"
]

ASSUMPTION_INDICATORS = [
    "assuming", "if", "given that", "provided that", "contingent on",
    "depends on", "relies on", "based on the assumption"
]

PROJECTION_INDICATORS = [
    "will", "expected to", "forecast", "projected", "anticipated",
    "likely to", "set to", "poised to", "on track to"
]


FINANCIAL_PATTERNS = [
    r"\$[\d,]+\.?\d*[BMK]?",  # Dollar amounts
    r"₹[\d,]+\.?\d*[LCK]?",  # Rupee amounts
    r"\d+\.?\d*%",  # Percentages
    r"\d+\.?\d*x",  # Multiples (P/E, EV/EBITDA)
    r"Q[1-4]\s*\d{4}",  # Quarter references
    r"\d{4}[-–]\d{2,4}",  # Year ranges
]


SECTOR_KEYWORDS = [
    "IT services", "auto", "banking", "FMCG", "pharma", "infra",
    "defense", "capital goods", "chemicals", "energy", "telecom"
]

THESIS_STRUCTURE_MARKERS = {
    "thesis_statement": ["thesis", "core idea", "investment thesis", "main argument"],
    "evidence_section": ["real-life context", "evidence", "supporting data", "proof"],
    "rationale_section": ["why", "rationale", "reason", "allocated because"],
    "risk_section": ["risk", "what could break", "downside", "bear case"],
    "action_section": ["how", "action", "strategy", "execution"]
}




FINANCIAL_STATEMENT_REFS = [
    "10-K", "10-Q", "annual report", "quarterly report", "SEC filing",
    "balance sheet", "income statement", "cash flow statement",
    "earnings call", "investor presentation", "management commentary",
    "financial statements", "audited report", "proxy statement"
]


CREDIBLE_SOURCES = [
    "Bloomberg", "Reuters", "Wall Street Journal", "Financial Times",
    "SEC", "SEBI", "management guidance", "analyst estimates", "consensus",
    "company filings", "official announcement", "press release",
    "quarterly earnings", "annual general meeting", "investor day"
]


TIME_BOUND_PATTERNS = [
    r"in Q[1-4]\s*\d{4}",           # Q3 2024
    r"FY\d{2,4}",                    # FY24, FY2024
    r"(H1|H2)\s*\d{4}",              # H1 2024
    r"\d{4}[-–]\d{2,4}",             # 2023-24, 2023-2024
    r"over the (past|last|next) \d+ (years?|quarters?|months?)",
    r"(YoY|QoQ|MoM)",                # Year-over-year, etc.
    r"CAGR of \d+%",                 # Compound annual growth rate
    r"(since|from) \d{4}",           # since 2020
]


CAUSAL_CONNECTORS = {
    "strong_causal": ["because", "therefore", "thus", "hence", "as a result", 
                      "consequently", "due to", "caused by", "leading to"],
    "conditional": ["if", "when", "unless", "provided that", "in case"],
    "contrast": ["however", "but", "although", "despite", "nevertheless", "yet"],
    "additive": ["moreover", "furthermore", "additionally", "also", "in addition"]
}




CERTAINTY_LEVELS = {
    "high": [
        "definitely", "certainly", "always", "never", "absolutely",
        "guaranteed", "undoubtedly", "without doubt", "must", "will definitely"
    ],
    "medium": [
        "likely", "probably", "should", "expected", "typically",
        "generally", "usually", "tends to", "often"
    ],
    "low": [
        "might", "could", "possibly", "may", "perhaps",
        "potentially", "conceivably", "arguably"
    ],
    "hedged": [
        "assuming", "if", "provided that", "contingent on", "depends on",
        "subject to", "given that", "in the event"
    ]
}


OVERCONFIDENCE_INDICATORS = [
    "will definitely", "guaranteed to", "certainly will", "must happen",
    "no doubt", "100%", "impossible to fail", "cannot lose"
]


APPROPRIATE_HEDGE_WORDS = [
    "likely", "expected", "projected", "anticipated", "may",
    "could", "potential", "possible", "estimated"
]
