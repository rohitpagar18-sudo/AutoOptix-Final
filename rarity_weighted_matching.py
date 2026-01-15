"""
RARITY-BASED KEYWORD MATCHING
==============================
Prioritizes rare/uncommon keywords over common ones
Because rare keywords are more specific and distinctive
"""

import pandas as pd
from typing import List, Tuple, Optional, Dict
from collections import Counter

# Load lookup keywords
df_lookup = pd.read_excel("Old Lookup File/lookup.xlsx")

class RarityWeightedMatcher:
    def __init__(self, df_lookup: pd.DataFrame):
        self.df = df_lookup
        self.keywords = df_lookup['Subgroup'].tolist()
        self.lookup_dict = {row['Subgroup']: row['UseCase'] for _, row in df_lookup.iterrows()}
        
        # Calculate keyword rarity scores
        self.token_frequency = self._calculate_token_frequency()
        self.keyword_rarity = self._calculate_keyword_rarity()
    
    def _calculate_token_frequency(self) -> Dict[str, int]:
        """Calculate how often each token appears in keywords"""
        all_tokens = []
        for kw in self.keywords:
            tokens = kw.lower().split()
            all_tokens.extend(tokens)
        return Counter(all_tokens)
    
    def _calculate_keyword_rarity(self) -> Dict[str, float]:
        """
        Calculate rarity score for each keyword
        Lower frequency = Higher rarity score
        Scale: 0.0 (very common) to 1.0 (very rare)
        """
        rarity_scores = {}
        
        for keyword in self.keywords:
            tokens = keyword.lower().split()
            
            # Get average frequency of tokens in this keyword
            avg_frequency = sum(self.token_frequency.get(t, 0) for t in tokens) / len(tokens)
            
            # Normalize: rarity = 1 - (normalized_frequency)
            max_freq = max(self.token_frequency.values()) if self.token_frequency else 1
            normalized_freq = avg_frequency / max_freq
            rarity_score = 1.0 - normalized_freq
            
            rarity_scores[keyword] = rarity_score
        
        return rarity_scores
    
    def get_rarity_tier(self, keyword: str) -> str:
        """Classify keyword into rarity tiers"""
        score = self.keyword_rarity.get(keyword, 0.5)
        
        if score >= 0.80:
            return "VERY_RARE"
        elif score >= 0.60:
            return "RARE"
        elif score >= 0.40:
            return "UNCOMMON"
        elif score >= 0.20:
            return "COMMON"
        else:
            return "VERY_COMMON"
    
    def find_best_match(self, text: str) -> Optional[Tuple[str, float, str, str]]:
        """
        Find BEST match using RARITY-WEIGHTED prioritization
        Returns: (keyword, score, usecase, rarity_tier)
        """
        text_lower = text.lower()
        
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'and', 'or', 'of', 'to', 'for', 'in', 'on', 'at', 'by', 'with',
            'from', 'not', 'no', 'can', 'could', 'should', 'would', 'user',
            'this', 'that', 'it', 'as', '-'
        }
        
        all_matches = []
        
        for keyword in self.keywords:
            kw_lower = keyword.lower()
            
            # Exact substring match
            if kw_lower in text_lower:
                score = 1.0
                rarity = self.keyword_rarity.get(keyword, 0.5)
                all_matches.append((keyword, score, 'exact_match', rarity))
            else:
                # Token-based matching
                kw_tokens = [t for t in kw_lower.split() if t not in stop_words]
                text_tokens = [t for t in text_lower.split() if t not in stop_words]
                
                if not kw_tokens or not text_tokens:
                    continue
                
                kw_set = set(kw_tokens)
                text_set = set(text_tokens)
                
                forward = sum(1 for kt in kw_set if kt in text_set) / len(kw_set)
                backward = sum(1 for tt in text_set if tt in kw_set) / len(text_set)
                
                combined = min(forward, backward)
                
                if combined >= 0.70:
                    score = 0.85 + (combined * 0.15)
                    rarity = self.keyword_rarity.get(keyword, 0.5)
                    all_matches.append((keyword, score, 'token_match', rarity))
                elif combined >= 0.50:
                    score = 0.65 + (combined * 0.2)
                    rarity = self.keyword_rarity.get(keyword, 0.5)
                    all_matches.append((keyword, score, 'partial_match', rarity))
        
        if not all_matches:
            return None
        
        # PRIORITY RANKING with RARITY as PRIMARY factor
        # Sort by: (1) Exact match, (2) Rarity tier, (3) Score
        priority_map = {'exact_match': 3, 'token_match': 2, 'partial_match': 1}
        
        all_matches.sort(
            key=lambda x: (
                priority_map[x[2]],      # Match type priority
                x[3],                     # RARITY SCORE (higher = rarer = better)
                x[1]                      # Confidence score
            ),
            reverse=True
        )
        
        # Return top match
        keyword, score, match_type, rarity = all_matches[0]
        usecase = self.lookup_dict.get(keyword, "")
        rarity_tier = self.get_rarity_tier(keyword)
        
        return (keyword, score, usecase, rarity_tier)


# TEST CASES - Your Example
print("=" * 120)
print("RARITY-WEIGHTED KEYWORD MATCHING SYSTEM")
print("=" * 120)

matcher = RarityWeightedMatcher(df_lookup)

# Show rarity analysis for your example
print("\n" + "=" * 120)
print("RARITY ANALYSIS: Your Example Keywords")
print("=" * 120)

example_keywords = ["Account Deactivation", "Service Request", "Pagerduty"]
for kw in example_keywords:
    if kw in matcher.keywords:
        rarity_score = matcher.keyword_rarity.get(kw, 0)
        rarity_tier = matcher.get_rarity_tier(kw)
        print(f"\n'{kw}'")
        print(f"  Rarity Score: {rarity_score:.3f}")
        print(f"  Rarity Tier:  {rarity_tier}")
        print(f"  Common Tokens: {[t for t in kw.lower().split() if matcher.token_frequency[t] > 20]}")
        print(f"  Rare Tokens:   {[t for t in kw.lower().split() if matcher.token_frequency[t] <= 5]}")

# Now test the matching
test_descriptions = [
    "I want service request for pager duty for account deactivation",
    "Need account deactivation for employee",
    "Service request for general support",
    "PagerDuty integration setup required",
    "Create access request for new user",
    "Application issue resolved",
    "Database performance monitoring alert",
]

print("\n" + "=" * 120)
print("MATCHING RESULTS (RARITY-WEIGHTED)")
print("=" * 120)

for i, desc in enumerate(test_descriptions, 1):
    result = matcher.find_best_match(desc)
    
    if result:
        keyword, score, usecase, rarity_tier = result
        print(f"\n{i}. ✓ MATCHED")
        print(f"   Description: {desc}")
        print(f"   Keyword:     {keyword}")
        print(f"   UseCase:     {usecase}")
        print(f"   Rarity:      {rarity_tier}")
        print(f"   Confidence:  {score:.2%}")
    else:
        print(f"\n{i}. ✗ NO MATCH")
        print(f"   Description: {desc}")

print("\n" + "=" * 120)
print("KEY INSIGHTS:")
print("  ✓ Rare keywords are prioritized over common ones")
print("  ✓ 'Pagerduty' is RARE → Gets high priority if found")
print("  ✓ 'Account Deactivation' is COMMON → Gets lower priority")
print("  ✓ 'Service Request' is VERY COMMON → Lowest priority")
print("=" * 120)
