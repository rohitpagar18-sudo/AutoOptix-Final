"""
SMART TEXT CLEANING: Remove Generic Filler Phrases
====================================================
Cleans ticket descriptions by removing common filler words/phrases
Then applies rarity-weighted matching on cleaned text
"""

import pandas as pd
from typing import List, Tuple, Optional, Dict
from collections import Counter
import re

df_lookup = pd.read_excel("lookup.xlsx")  # Use MAIN folder lookup

class TextCleaner:
    """Remove generic filler phrases and keep only meaningful keywords"""
    
    def __init__(self):
        # Generic filler phrases that don't contribute to categorization
        self.filler_phrases = {
            # Greetings
            'hi', 'hello', 'hey', 'hi there', 'hello there',
            
            # Polite requests
            'please', 'kindly', 'can you', 'could you', 'would you', 'will you',
            'can i', 'could i', 'would i', 'will i',
            'give me', 'get me', 'provide me', 'send me',
            'i need', 'i want', 'i require', 'i request',
            
            # Generic actions
            'for', 'thank you', 'thanks', 'thank you for',
            'do', 'does', 'doing', 'done', 'get', 'getting',
            
            # Common connecting words
            'and', 'or', 'but', 'the', 'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by', 'from',
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'this', 'that', 'these', 'those', 'it', 'they', 'them', 'that',
            
            # Filler words
            'help', 'assistance', 'support', 'issue', 'problem', 'help with',
            'with', 'regarding', 'about', 'as', 'also', 'as well',
        }
        
        # Stop words (keep but lower priority)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must',
            'not', 'no', 'yes', 'if', 'else', 'while', 'for', 'to', 'of', 'in',
            'on', 'at', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'with', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'them', 'their', 'what', 'which', 'who', 'when',
            'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'as', 'also', 'or', 'an'
        }
    
    def clean_description(self, text: str) -> Tuple[str, str, List[str]]:
        """
        Clean and extract meaningful keywords from description
        Returns: (cleaned_text, original_text, removed_phrases)
        """
        original = text
        text_lower = text.lower()
        
        # Remove extra whitespace
        text_lower = ' '.join(text_lower.split())
        
        # Track removed phrases
        removed = []
        
        # Remove filler phrases
        for phrase in self.filler_phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            if re.search(pattern, text_lower):
                text_lower = re.sub(pattern, '', text_lower, flags=re.IGNORECASE)
                removed.append(phrase)
        
        # Remove extra spaces again
        cleaned = ' '.join(text_lower.split())
        
        return cleaned, original, removed


class RarityWeightedMatcherWithCleaning:
    def __init__(self, df_lookup: pd.DataFrame):
        self.df = df_lookup
        self.keywords = df_lookup['Subgroup'].tolist()
        self.lookup_dict = {row['Subgroup']: row['UseCase'] for _, row in df_lookup.iterrows()}
        self.cleaner = TextCleaner()
        
        # Calculate keyword rarity scores
        self.token_frequency = self._calculate_token_frequency()
        self.keyword_rarity = self._calculate_keyword_rarity()
    
    def _calculate_token_frequency(self) -> Dict[str, int]:
        """Calculate how often each token appears in keywords"""
        all_tokens = []
        for kw in self.keywords:
            if pd.notna(kw):  # Skip NaN values
                tokens = str(kw).lower().split()
                all_tokens.extend(tokens)
        return Counter(all_tokens)
    
    def _calculate_keyword_rarity(self) -> Dict[str, float]:
        """Calculate rarity score for each keyword"""
        rarity_scores = {}
        
        for keyword in self.keywords:
            if pd.notna(keyword):  # Skip NaN values
                tokens = str(keyword).lower().split()
                avg_frequency = sum(self.token_frequency.get(t, 0) for t in tokens) / len(tokens)
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
    
    def find_best_match(self, text: str) -> Optional[Tuple[str, float, str, str, str, str]]:
        """
        Find BEST match with text cleaning + rarity weighting
        Returns: (keyword, score, usecase, rarity_tier, original_text, cleaned_text)
        """
        # Clean the text first
        cleaned_text, original_text, removed_phrases = self.cleaner.clean_description(text)
        
        # Use cleaned text for matching
        text_lower = cleaned_text
        
        all_matches = []
        
        for keyword in self.keywords:
            if pd.notna(keyword):  # Skip NaN values
                kw_lower = str(keyword).lower()
            
            # Exact substring match
            if kw_lower in text_lower:
                score = 1.0
                rarity = self.keyword_rarity.get(keyword, 0.5)
                all_matches.append((keyword, score, 'exact_match', rarity))
            else:
                # Token-based matching
                kw_tokens = [t for t in kw_lower.split() if t not in self.cleaner.stop_words]
                text_tokens = [t for t in text_lower.split() if t not in self.cleaner.stop_words]
                
                if not kw_tokens or not text_tokens:
                    continue
                
                kw_set = set(kw_tokens)
                text_set = set(text_tokens)
                
                forward = sum(1 for kt in kw_set if kt in text_set) / len(kw_set) if kw_set else 0
                backward = sum(1 for tt in text_set if tt in kw_set) / len(text_set) if text_set else 0
                
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
        
        # Priority ranking: rarity first, then match type, then score
        priority_map = {'exact_match': 3, 'token_match': 2, 'partial_match': 1}
        
        all_matches.sort(
            key=lambda x: (x[3], priority_map[x[2]], x[1]),
            reverse=True
        )
        
        # Return top match
        keyword, score, match_type, rarity = all_matches[0]
        usecase = self.lookup_dict.get(keyword, "")
        rarity_tier = self.get_rarity_tier(keyword)
        
        return (keyword, score, usecase, rarity_tier, original_text, cleaned_text)


# TEST CASES with generic filler phrases
print("=" * 140)
print("SMART TEXT CLEANING + RARITY-WEIGHTED MATCHING")
print("=" * 140)

matcher = RarityWeightedMatcherWithCleaning(df_lookup)

test_cases = [
    "Hi please give me access for account deletion",
    "Hello can you provide account deactivation for my user",
    "I need help with access removal request please",
    "Could you please grant me database access and create a new account",
    "I want deployment request for my service",
    "Hi there, please help me with alert configuration",
    "Account unlock needed for user john@company.com",
    "Can I get file access for the shared drive",
]

print("\nProcessing tickets with text cleaning:\n")

for i, desc in enumerate(test_cases, 1):
    result = matcher.find_best_match(desc)
    
    if result:
        keyword, score, usecase, rarity_tier, original, cleaned = result
        
        print(f"{i}. {'─' * 135}")
        print(f"   Original:     {original}")
        print(f"   Cleaned:      {cleaned}")
        print(f"   Match:        {keyword}")
        print(f"   UseCase:      {usecase}")
        print(f"   Rarity:       {rarity_tier}")
        print(f"   Confidence:   {score:.2%}")
    else:
        print(f"{i}. NO MATCH")
        print(f"   Original: {desc}")
        result = matcher.find_best_match(desc)

print("\n" + "=" * 140)
print("TEXT CLEANING STATISTICS")
print("=" * 140)

cleaner = TextCleaner()
print(f"\nTotal filler phrases: {len(cleaner.filler_phrases)}")
print(f"Total stop words: {len(cleaner.stop_words)}")

print("\nFiller phrases removed:")
categories = {
    'Greetings': ['hi', 'hello', 'hey'],
    'Polite requests': ['please', 'can you', 'could you', 'give me'],
    'Generic actions': ['help', 'support', 'for'],
    'Connecting words': ['and', 'or', 'the', 'with'],
}

for category, phrases in categories.items():
    print(f"\n{category}:")
    for phrase in phrases:
        if phrase in cleaner.filler_phrases:
            print(f"  • {phrase}")

print("\n" + "=" * 140)
print("KEY BENEFITS")
print("=" * 140)

benefits = """
✓ REMOVES FILLER:
  "Hi please give me access for account deletion"
  →  "account deletion"
  
✓ FINDS CORE INTENT:
  Generic phrases removed, meaningful keywords remain
  
✓ IMPROVES MATCHING:
  Less noise = more accurate categorization
  
✓ WORKS WITH RARITY WEIGHTING:
  - Clean text extracted
  - Rarity-weighted matching applied
  - Result: Best, most specific keyword selected
"""

print(benefits)
print("=" * 140)
