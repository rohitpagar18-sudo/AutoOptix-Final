"""
RARITY-WEIGHTED KEYWORD MATCHING v2
====================================
Prioritizes rare/uncommon keywords over common ones

KEY CONCEPT:
If a rare keyword is found in the text, it gets HIGH priority.
If only common keywords are found, select the rarest of those.
"""

import pandas as pd
from typing import List, Tuple, Optional, Dict
from collections import Counter

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
    
    def find_best_match_with_details(self, text: str) -> Optional[Tuple[str, float, str, str, List]]:
        """
        Find BEST match using RARITY-WEIGHTED prioritization
        Returns: (keyword, score, usecase, rarity_tier, all_matches_found)
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
        # Sort by: (1) Rarity tier (rarest first), (2) Exact match, (3) Score
        priority_map = {'exact_match': 3, 'token_match': 2, 'partial_match': 1}
        
        all_matches.sort(
            key=lambda x: (
                x[3],                     # RARITY SCORE (higher = rarer = better) - PRIMARY
                priority_map[x[2]],       # Match type priority - SECONDARY
                x[1]                      # Confidence score - TERTIARY
            ),
            reverse=True
        )
        
        # Return top match + all matches for analysis
        keyword, score, match_type, rarity = all_matches[0]
        usecase = self.lookup_dict.get(keyword, "")
        rarity_tier = self.get_rarity_tier(keyword)
        
        # Get top 5 matches for comparison
        top_matches = []
        for kw, sc, mt, rar in all_matches[:5]:
            top_matches.append({
                'keyword': kw,
                'score': sc,
                'rarity': rar,
                'rarity_tier': self.get_rarity_tier(kw),
                'match_type': mt
            })
        
        return (keyword, score, usecase, rarity_tier, top_matches)


# TEST WITH YOUR EXAMPLE
print("=" * 130)
print("RARITY-WEIGHTED MATCHING: DEMONSTRATING RARE KEYWORD PRIORITY")
print("=" * 130)

matcher = RarityWeightedMatcher(df_lookup)

test_cases = [
    ("I want service request for pager duty for account deactivation", "Should prioritize RARE keywords if found"),
    ("Alert notification for service issue", "Alert is RARE, Service/Issue are COMMON"),
    ("Account deactivation needed", "Account Deactivation is RARE"),
    ("Service deployment request", "Deployment is RARE vs Service/Request"),
]

for desc, explanation in test_cases:
    print(f"\n{'─' * 130}")
    print(f"Input: {desc}")
    print(f"Explanation: {explanation}")
    print(f"{'─' * 130}")
    
    result = matcher.find_best_match_with_details(desc)
    
    if result:
        keyword, score, usecase, rarity_tier, top_matches = result
        
        print(f"\n🏆 SELECTED (BEST MATCH):")
        print(f"   Keyword:     {keyword}")
        print(f"   UseCase:     {usecase}")
        print(f"   Rarity:      {rarity_tier}")
        print(f"   Confidence:  {score:.2%}")
        
        print(f"\n📊 TOP 5 CANDIDATES (Sorted by Rarity):")
        for i, match in enumerate(top_matches, 1):
            rarity_bar = "█" * int(match['rarity'] * 20)
            print(f"   {i}. {match['keyword']:<40} | Rarity: {rarity_bar:<20} {match['rarity']:.2f} ({match['rarity_tier']}) | {match['score']:.2%}")
    else:
        print(f"✗ NO MATCH")

# SHOW RARITY TIERS
print("\n" + "=" * 130)
print("KEYWORD RARITY DISTRIBUTION")
print("=" * 130)

# Get samples from each tier
for tier_name, min_score, max_score in [
    ("VERY_RARE", 0.80, 1.0),
    ("RARE", 0.60, 0.80),
    ("UNCOMMON", 0.40, 0.60),
    ("COMMON", 0.20, 0.40),
    ("VERY_COMMON", 0.0, 0.20),
]:
    tier_keywords = [
        (kw, score) for kw, score in matcher.keyword_rarity.items()
        if min_score <= score < max_score
    ]
    
    print(f"\n{tier_name} ({len(tier_keywords)} keywords):")
    tier_keywords.sort(key=lambda x: x[1], reverse=True)
    for kw, score in tier_keywords[:5]:
        print(f"  • {kw:<45} (Rarity: {score:.2f})")
    if len(tier_keywords) > 5:
        print(f"  ... and {len(tier_keywords) - 5} more")

print("\n" + "=" * 130)
print("KEY ADVANTAGES OF RARITY-WEIGHTED MATCHING:")
print("=" * 130)
print("""
✓ RARE keywords are prioritized (e.g., Alert, Deployment, Escalation)
✓ COMMON keywords are deprioritized (e.g., Request, Issue, Service)
✓ If multiple keywords match, the rarest one is selected
✓ Prevents generic keywords from drowning out specific ones
✓ Example: "alert notification" → Selects "Alert" (VERY_RARE) over "Notification"

WHY THIS MATTERS:
- "Service Request" appears in 100+ different tickets → LOW specificity
- "PagerDuty Alert" (if it existed) would be RARE → HIGH specificity
- Rare keywords are more distinctive = more reliable for categorization
""")

print("=" * 130)
