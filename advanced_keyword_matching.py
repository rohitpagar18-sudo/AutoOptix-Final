"""
Advanced Keyword Matching with Ambiguity Validation
Handles cases where multiple keywords match similarly
"""

import pandas as pd
from typing import List, Tuple, Optional, Dict

# Load lookup keywords
df_lookup = pd.read_excel("Old Lookup File/lookup.xlsx")

class AmbiguityValidator:
    def __init__(self, df_lookup: pd.DataFrame):
        self.df = df_lookup
        self.keywords = df_lookup['Subgroup'].tolist()
        self.lookup_dict = {row['Subgroup']: row['UseCase'] for _, row in df_lookup.iterrows()}
        
    def resolve_ambiguity(self, matches: List[Tuple[str, float, str]], text: str) -> Tuple[str, float]:
        """
        Resolve ambiguous matches using multiple validation strategies
        matches: List of (keyword, score, match_type) tuples
        """
        if not matches:
            return None, 0.0
        
        if len(matches) == 1:
            return (matches[0][0], matches[0][1])
        
        # Strategy 1: Filter by specificity (word count)
        max_word_count = max(len(m[0].split()) for m in matches)
        specific_matches = [(m[0], m[1]) for m in matches if len(m[0].split()) == max_word_count]
        
        if len(specific_matches) == 1:
            return specific_matches[0]
        
        # Strategy 2: Check for substring relationships
        for keyword, score in matches:
            # Check if this keyword contains all tokens from the text description
            keyword_tokens = set(keyword.lower().split())
            text_tokens = set(text.lower().split())
            
            # Filter common words
            stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'for', 'and', 'or'}
            keyword_tokens -= stop_words
            text_tokens -= stop_words
            
            # If keyword is fully represented in text, boost score
            if keyword_tokens.issubset(text_tokens):
                return (keyword, min(score + 0.1, 1.0))
        
        # Strategy 3: Rank by UseCase presence in text
        text_lower = text.lower()
        ranked = []
        for keyword, score in specific_matches:
            usecase = self.lookup_dict.get(keyword, "")
            # Check if UseCase words appear in text
            usecase_words = set(usecase.lower().split())
            usecase_match = sum(1 for w in usecase_words if w in text_lower)
            ranked.append((keyword, score, usecase_match))
        
        # Sort by UseCase match count, then score
        ranked.sort(key=lambda x: (x[2], x[1]), reverse=True)
        return (ranked[0][0], ranked[0][1])
    
    def find_best_match(self, text: str) -> Optional[Tuple[str, float, str]]:
        """
        Find BEST match with ambiguity validation
        Returns: (keyword, score, usecase)
        """
        text_lower = text.lower()
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'and', 'or', 'of', 'to', 'for', 'in', 'on', 'at', 'by', 'with',
            'from', 'not', 'no', 'can', 'could', 'should', 'would', 'user',
            'request', 'issue', 'this', 'that', 'it', 'as'
        }
        
        all_matches = []
        
        for keyword in self.keywords:
            kw_lower = keyword.lower()
            
            # Exact substring match (highest priority)
            if kw_lower in text_lower:
                score = 1.0
                all_matches.append((keyword, score, 'exact_match'))
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
                    all_matches.append((keyword, score, 'token_match'))
                elif combined >= 0.50:
                    score = 0.65 + (combined * 0.2)
                    all_matches.append((keyword, score, 'partial_match'))
        
        if not all_matches:
            return None
        
        # Sort by match type (exact > token > partial), then by score
        priority = {'exact_match': 3, 'token_match': 2, 'partial_match': 1}
        all_matches.sort(key=lambda x: (priority[x[2]], x[1]), reverse=True)
        
        # If multiple high-confidence matches, resolve ambiguity
        high_score_matches = [m for m in all_matches if m[1] >= 0.80]
        
        if len(high_score_matches) > 1:
            keyword, score = self.resolve_ambiguity(high_score_matches, text)
        else:
            keyword, score = all_matches[0][0], all_matches[0][1]
        
        usecase = self.lookup_dict.get(keyword, "")
        return (keyword, score, usecase)


# TEST CASES
test_descriptions = [
    "I want service request for pager duty for account deactivation",
    "Account Merge needed for duplicate records",
    "Adhoc report request for sales data",
    "Application issue with login functionality",
    "Deployment request for code changes",
    "Access removal from previous role",
    "Monitor batch job execution",
    "Card payment request processing",
    "Cancel order request for customer",
    "Configuration management issue",
]

print("=" * 120)
print("ADVANCED KEYWORD MATCHING WITH AMBIGUITY VALIDATION")
print("=" * 120)

validator = AmbiguityValidator(df_lookup)

for i, desc in enumerate(test_descriptions, 1):
    result = validator.find_best_match(desc)
    
    if result:
        keyword, score, usecase = result
        print(f"\n{i}. MATCHED ✓")
        print(f"   Description: {desc}")
        print(f"   Keyword:     {keyword}")
        print(f"   UseCase:     {usecase}")
        print(f"   Confidence:  {score:.2%}")
    else:
        print(f"\n{i}. NO MATCH ✗")
        print(f"   Description: {desc}")

print("\n" + "=" * 120)
print("VALIDATION STRATEGY APPLIED:")
print("  1. Exact substring matches (priority: HIGH)")
print("  2. Token-based bidirectional matching (priority: MEDIUM)")
print("  3. Partial matches (priority: LOW)")
print("  4. Ambiguity resolution:")
print("     - Prefer longest/most specific keywords")
print("     - Check substring relationships")
print("     - Validate UseCase consistency")
print("=" * 120)
