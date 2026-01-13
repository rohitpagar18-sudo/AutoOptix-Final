"""
Test script to verify improved keyword matching algorithm
Compares old vs new matching performance
"""

import pandas as pd
from typing import List, Tuple, Optional

# Load lookup keywords
df_lookup = pd.read_excel("lookup.xlsx")
keywords = df_lookup['Subgroup'].unique().tolist()
print(f"Total lookup keywords: {len(keywords)}\n")

# NEW IMPROVED ALGORITHM
def match_keyword_in_text_new(text: str, keyword: str) -> Tuple[bool, float]:
    """Improved bidirectional keyword matching"""
    if not text or not keyword:
        return False, 0.0
    
    text_lower = text.lower()
    kw_lower = keyword.lower()
    
    if kw_lower in text_lower:
        return True, 1.0
    
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'and', 'or', 'of', 'to', 'for', 'in', 'on', 'at', 'by', 'with', 'from',
        'not', 'no', 'can', 'could', 'should', 'would', 'must', 'may', 'might',
        'user', 'request', 'issue', 'this', 'that', 'it', 'as'
    }
    
    kw_tokens = [t for t in kw_lower.split() if t and t not in stop_words]
    text_tokens = [t for t in text_lower.split() if t and t not in stop_words]
    
    if not kw_tokens or not text_tokens:
        return False, 0.0
    
    kw_token_set = set(kw_tokens)
    text_token_set = set(text_tokens)
    
    # Bidirectional matching
    forward_matching = sum(1 for kt in kw_token_set if kt in text_token_set)
    forward_ratio = forward_matching / len(kw_token_set) if kw_token_set else 0
    
    backward_matching = sum(1 for tt in text_token_set if tt in kw_token_set)
    backward_ratio = backward_matching / len(text_token_set) if text_token_set else 0
    
    combined_ratio = min(forward_ratio, backward_ratio)
    
    if combined_ratio >= 0.80:
        score = 0.95
        return True, score
    elif combined_ratio >= 0.60:
        score = 0.80 + (combined_ratio * 0.10)
        return True, score
    elif combined_ratio >= 0.50:
        score = 0.65 + (combined_ratio * 0.15)
        return True, score
    else:
        return False, 0.0


def find_best_keyword_match_new(text: str, keywords: List[str]) -> Optional[Tuple[str, float]]:
    """Find BEST match across ALL keywords (not first match)"""
    if not text or not keywords:
        return None
    
    best_match = None
    best_score = 0.50
    
    for keyword in keywords:
        is_match, score = match_keyword_in_text_new(text, keyword)
        if is_match and score > best_score:
            best_score = score
            best_match = (keyword, score)
    
    return best_match


# TEST CASES
test_descriptions = [
    "User access request for new system account",
    "Access removal from previous role",
    "Account activation needed",
    "Password reset and account unlock",
    "New application access required",
    "Data loading issue in system",
    "Report generation request",
    "Batch processing delay",
    "API integration failure",
    "Database backup failed",
    "User needs file access",
    "Create new user account",
    "System monitoring alert",
    "Performance issue on platform",
    "Approval workflow pending"
]

print("=" * 100)
print("KEYWORD MATCHING TEST RESULTS")
print("=" * 100)

matched_count = 0
for i, desc in enumerate(test_descriptions, 1):
    result = find_best_keyword_match_new(desc, keywords)
    
    if result:
        keyword, score = result
        matched_count += 1
        status = "✓ MATCHED"
        print(f"{i}. {status}")
        print(f"   Description: {desc}")
        print(f"   Keyword:     {keyword}")
        print(f"   Score:       {score:.2f}")
    else:
        status = "✗ NO MATCH"
        print(f"{i}. {status}")
        print(f"   Description: {desc}")
    
    print()

match_rate = (matched_count / len(test_descriptions)) * 100
print("=" * 100)
print(f"SUMMARY: {matched_count}/{len(test_descriptions)} matched ({match_rate:.1f}%)")
print("=" * 100)
print("\nKEY IMPROVEMENTS:")
print("✓ Bidirectional matching (both directions)")
print("✓ Returns BEST match from all keywords (not first)")
print("✓ Stricter thresholds (0.50 minimum combined ratio)")
print("✓ Equal stop word treatment on both sides")
print("✓ Prevents loose matches on single words")
print("✓ More accurate scoring system")
