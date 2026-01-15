import pandas as pd

df = pd.read_excel('Old Lookup File/lookup.xlsx')

# Find potential ambiguities - keywords that share common words
print("=" * 100)
print("AMBIGUOUS KEYWORD PAIRS (overlapping subgroups)")
print("=" * 100)

keywords = df['Subgroup'].tolist()

# Check for keywords that contain other keywords
ambiguous_pairs = []
for i, kw1 in enumerate(keywords):
    for j, kw2 in enumerate(keywords):
        if i < j:
            # Check if keywords share tokens but are different
            tokens1 = set(kw1.lower().split())
            tokens2 = set(kw2.lower().split())
            overlap = tokens1 & tokens2
            
            if overlap and len(overlap) > 0 and kw1 != kw2:
                score = len(overlap) / min(len(tokens1), len(tokens2))
                if score >= 0.5:  # 50% or more token overlap
                    ambiguous_pairs.append((kw1, kw2, overlap, score))

ambiguous_pairs.sort(key=lambda x: x[3], reverse=True)

print(f"\nFound {len(ambiguous_pairs)} ambiguous pairs\n")

for idx, (kw1, kw2, overlap, score) in enumerate(ambiguous_pairs[:20], 1):
    uc1 = df[df['Subgroup'] == kw1]['UseCase'].values[0]
    uc2 = df[df['Subgroup'] == kw2]['UseCase'].values[0]
    print(f"{idx}. '{kw1}' ({uc1})")
    print(f"   vs '{kw2}' ({uc2})")
    print(f"   Shared words: {overlap} | Match: {score:.2%}\n")
