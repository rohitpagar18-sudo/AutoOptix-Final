"""
COMPREHENSIVE KEYWORD MATCHING VALIDATION GUIDE
===============================================

This system handles ambiguous keyword matching through multiple validation layers:
"""

VALIDATION_RULES = """

╔══════════════════════════════════════════════════════════════════════════════╗
║                  4-TIER AMBIGUITY VALIDATION SYSTEM                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

TIER 1: MATCH TYPE PRIORITIZATION
─────────────────────────────────
Priority Order:
  1. EXACT MATCH (keyword appears as exact substring in text)
     Score: 1.0 (100% confidence)
     Example: "account deactivation" found in "I want account deactivation"
  
  2. TOKEN MATCH (bidirectional word matching)
     Score: 0.85-0.95 (85-95% confidence)
     Requires: Min 70% of keyword tokens present in text AND vice versa
     Example: "Account Deactivation" tokens {account, deactivation} found
  
  3. PARTIAL MATCH (some word overlap)
     Score: 0.65-0.85 (65-85% confidence)
     Requires: Min 50% of keyword tokens in text
     Example: "Access" found but not "Request"


TIER 2: SPECIFICITY RESOLUTION
────────────────────────────────
When multiple keywords score HIGH (≥0.80):
  
  ✓ RULE 1: Prefer LONGER keywords
    Why: More specific keywords are more valuable than generic ones
    Example: 
      - "Account Merge Request" (3 words) > "Merge Request" (2 words)
      - "Application Issue - Incomplete" > "Application Issue"
  
  ✓ RULE 2: Check substring relationships
    Why: Longer keyword might contain all tokens of shorter one
    Example:
      - If "Application Performance Issue" and "Application Issue" both match,
      - Choose "Application Performance Issue" (more specific)
  
  ✓ RULE 3: Stop word filtering
    Why: Common words inflate similarity scores
    Excluded: 'the', 'a', 'is', 'and', 'or', 'for', 'request', 'issue', etc.


TIER 3: USECASE CONSISTENCY CHECK
──────────────────────────────────
When still ambiguous:
  
  ✓ RULE 4: Match UseCase context with text
    Why: Related keywords in same UseCase category might be wrong match
    Example:
      Text: "configure database settings"
      Options:
        - "Configuration Request" (UseCase: Configuration Management) ✓
        - "Configuration Issue" (UseCase: Configuration Management) ✓
      → Choose based on text keywords ("request" vs "issue")
  
  ✓ RULE 5: Token depth analysis
    Why: More keywords tokens vs stop words = better match quality
    Example:
      Text: "adhoc report request for sales"
      Options:
        - "Adhoc Report Request" (3 meaningful tokens) ✓✓✓
        - "Adhoc Request" (2 meaningful tokens) ✓✓
      → Choose "Adhoc Report Request"


TIER 4: CONFIDENCE SCORE TUNING
─────────────────────────────────
Score Calculation:
  
  Exact Substring Match:        1.0   (use immediately)
  Bidirectional High Match:     0.95  (if 80%+ overlap)
  Bidirectional Good Match:     0.90  (if 70%+ overlap)
  Partial Match:                0.75  (if 50%+ overlap)
  Single Word Match:            0.50  (fallback, may reject)

Ambiguity Boost (+0.10):
  - When keyword tokens are subset of text tokens
  - Example: "Request" found in "I want request for..."


╔══════════════════════════════════════════════════════════════════════════════╗
║                        REAL-WORLD EXAMPLES                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

EXAMPLE 1: Exact Match + Disambiguation
─────────────────────────────────────────
Input: "I need account deactivation for employee"

Analysis:
  ✓ Exact match: "Account Deactivation" (1.0)
  ✓ Token match: "Account" + "deactivation" both present
  ✓ UseCase: Account Management
  
Result: "Account Deactivation" (100% confidence)
Why this works: Exact substring match takes priority


EXAMPLE 2: Multiple High-Scoring Matches
──────────────────────────────────────────
Input: "adhoc report request for Q4 sales"

Candidates:
  1. "Adhoc Report Request" (3 words, token match: 100%, score: 0.95)
  2. "Report Request" (2 words, token match: 100%, score: 0.95)
  3. "Adhoc Request" (2 words, token match: 100%, score: 0.95)

Disambiguation Process:
  Step 1: Filter by specificity → "Adhoc Report Request" (3 words longest) ✓
  Step 2: Confirm substring → All tokens in "Adhoc Report Request" found ✓
  Step 3: Validate UseCase → Report Management (matches intent) ✓

Result: "Adhoc Report Request" (100% confidence)
Why this works: Longest keyword is more specific


EXAMPLE 3: Partial Match + UseCase Validation
────────────────────────────────────────────────
Input: "monitoring batch job execution"

Candidates:
  1. "Batch Monitoring" (2 words, token match: 100%, score: 0.95)
  2. "Job Execution Request" (3 words, token match: 66%, score: 0.75)
  3. "Monitoring" (1 word, token match: 100%, score: 0.95)

Disambiguation Process:
  Step 1: High scorers: #1 (0.95) and #3 (0.95)
  Step 2: Apply specificity → "Batch Monitoring" (2 words) > "Monitoring" (1 word) ✓
  Step 3: Validate UseCase → Batch Job Management ✓

Result: "Batch Monitoring" (95% confidence)
Why this works: 2-word match beats 1-word generic match


EXAMPLE 4: Same UseCase, Different Keywords
──────────────────────────────────────────────
Input: "application launch performance issue"

Candidates (all same UseCase - Application Issue):
  1. "Application Issue" (2 words, 100% match, score: 0.95)
  2. "Application Launch Issue" (3 words, 100% match, score: 0.95)
  3. "Application Performance Issue" (3 words, 100% match, score: 0.95)

Disambiguation Process:
  Step 1: Filter by specificity → #2 and #3 (both 3 words) win
  Step 2: Check text alignment:
    - Text tokens: {application, launch, performance, issue}
    - "Application Launch Issue" matches: 3/4 tokens ✓✓✓
    - "Application Performance Issue" matches: 3/4 tokens ✓✓✓
  Step 3: Match primary action word:
    - "launch" more specific in context
    - Choose "Application Launch Issue"

Result: "Application Launch Issue" (95% confidence)
Why this works: Most tokens from description are covered


╔══════════════════════════════════════════════════════════════════════════════╗
║                      IMPLEMENTATION CHECKLIST                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

When integrating this validation system:

☐ Step 1: Exact substring matching first (highest priority)
☐ Step 2: Token-based bidirectional matching (filter by thresholds)
☐ Step 3: Group matches by score tier
☐ Step 4: Apply specificity rules to disambiguate
☐ Step 5: Validate using UseCase context
☐ Step 6: Return highest confidence match with score
☐ Step 7: Log ambiguous matches for monitoring
☐ Step 8: Add manual override option for edge cases


THRESHOLDS TO TUNE:
  - Exact match score: 1.0 (fixed)
  - High confidence threshold: 0.80+ (triggers disambiguation)
  - Minimum token overlap: 0.70 (70% bidirectional)
  - Partial match threshold: 0.50 (50% minimum)
  - Ambiguity boost: +0.10 when keyword subset of text
"""

print(VALIDATION_RULES)
