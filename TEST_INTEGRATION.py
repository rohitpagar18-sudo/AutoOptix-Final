"""
QUICK TEST: Verify Text Cleaning Integration
==============================================
"""

import pandas as pd
import sys
import os

# Add to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

print("="*100)
print("INTEGRATION TEST: Text Cleaning + Keyword Matching")
print("="*100)

# Test 1: Verify PRODUCTION_MATCHER can be imported
print("\n✓ Test 1: Importing PRODUCTION_MATCHER...")
try:
    from PRODUCTION_MATCHER import RarityWeightedMatcher, TextCleaner
    print("  ✅ SUCCESS: RarityWeightedMatcher imported")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Verify lookup.xlsx exists
print("\n✓ Test 2: Checking lookup.xlsx...")
lookup_path = os.path.join(parent_dir, "lookup.xlsx")
if os.path.exists(lookup_path):
    print(f"  ✅ Found at: {lookup_path}")
else:
    print(f"  ❌ Not found at: {lookup_path}")
    sys.exit(1)

# Test 3: Initialize matcher
print("\n✓ Test 3: Initializing RarityWeightedMatcher...")
try:
    df_lookup = pd.read_excel(lookup_path)
    matcher = RarityWeightedMatcher(df_lookup)
    print(f"  ✅ Matcher initialized with {len(matcher.keywords)} keywords")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 4: Test text cleaning and matching
print("\n✓ Test 4: Testing text cleaning and matching...")
test_cases = [
    "Hi please give me access for account deletion",
    "Hello can you provide account deactivation",
    "I need help with access removal request please",
]

all_passed = True
for i, ticket in enumerate(test_cases, 1):
    result = matcher.find_best_match(ticket)
    if result:
        print(f"\n  Test 4.{i}: ✅ PASS")
        print(f"    Original:  {ticket[:50]}...")
        print(f"    Cleaned:   {result['cleaned_text']}")
        print(f"    Keyword:   {result['keyword']}")
        print(f"    Confidence: {result['confidence']:.0%}")
    else:
        print(f"\n  Test 4.{i}: ⚠️  NO MATCH")
        all_passed = False

# Test 5: Test with DataFrame (like in 01_Home.py)
print("\n✓ Test 5: Testing DataFrame integration...")
try:
    test_df = pd.DataFrame({
        'Description': test_cases,
        'Other_Column': ['A', 'B', 'C']
    })
    
    test_df['Cleaned_Description'] = ""
    test_df['Matched_Keyword'] = ""
    test_df['Matched_UseCase'] = ""
    test_df['Match_Confidence'] = 0.0
    
    for idx, row in test_df.iterrows():
        result = matcher.find_best_match(row['Description'])
        if result:
            test_df.at[idx, 'Cleaned_Description'] = result['cleaned_text']
            test_df.at[idx, 'Matched_Keyword'] = result['keyword']
            test_df.at[idx, 'Matched_UseCase'] = result['usecase']
            test_df.at[idx, 'Match_Confidence'] = result['confidence']
    
    print(f"  ✅ SUCCESS: Processed {len(test_df)} rows")
    print("\n  Sample output:")
    print(test_df[['Description', 'Matched_Keyword', 'Match_Confidence']].to_string())
    
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    all_passed = False

print("\n" + "="*100)
if all_passed:
    print("✅ ALL TESTS PASSED - Integration Ready!")
    print("="*100)
    print("\nNEXT STEPS:")
    print("1. Run: streamlit run AutoOptix_Overview.py")
    print("2. Upload Excel file with Description column")
    print("3. Check Dashboard for new columns:")
    print("   - Cleaned_Description")
    print("   - Matched_Keyword")
    print("   - Matched_UseCase")
    print("   - Match_Confidence")
else:
    print("⚠️  SOME TESTS FAILED - Check output above")
    
print("="*100)
