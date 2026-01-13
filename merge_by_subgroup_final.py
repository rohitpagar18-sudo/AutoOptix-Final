"""
merge_by_subgroup_final.py - stable DataFrame API implementation

Provides `merge_file(df_input, source_filename=None)`.
"""

import os
import json
import traceback
import sys
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from rapidfuzz import fuzz


def find_column_case_insensitive(df: pd.DataFrame, names: List[str]) -> Optional[str]:
    lower_map = {str(col).strip().lower(): col for col in df.columns}
    for n in names:
        key = str(n).strip().lower()
        if key in lower_map:
            return lower_map[key]
    return None


def load_excel_file(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    return pd.read_excel(path, sheet_name=0)

# Define stop words (shared across functions)
STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'and', 'or', 'of', 'to', 'for', 'in', 'on', 'at', 'by', 'with', 'from',
    'not', 'no', 'can', 'could', 'should', 'would', 'must', 'may', 'might',
    'user', 'request', 'issue', 'this', 'that', 'it', 'as', 'all', 'has', 'have',
    'will', 'do', 'does', 'did', 'done', 'get', 'got', 'need', 'help', 'support',
    'ticket', 'description', 'problem', 'error', 'bug', 'fail', 'failed'
}


def match_keyword_in_text_rapidfuzz(text: str, keywords: List[str]) -> Optional[Tuple[str, float, Dict]]:
    """
    PASS 1: FAST KEYWORD MATCHING using word-based pre-filtering
    
    Algorithm:
    1. Extract significant words from text
    2. Pre-filter keywords that share words with text
    3. Score only top candidates with RapidFuzz
    4. Threshold: 40% - catches obvious matches quickly
    
    Returns: (keyword, score, details) or None if no match found
    """
    if not text or not keywords:
        return None
    
    text_lower = text.lower().strip()
    if not text_lower:
        return None
    
    # Extract significant words from text
    text_words = [w for w in text_lower.split() if w and w not in STOP_WORDS and len(w) >= 3]
    if not text_words:
        text_words = [w for w in text_lower.split() if w and w not in STOP_WORDS and len(w) >= 2]
    
    if not text_words:
        return None
    
    text_word_set = set(text_words)
    
    # PRE-FILTER: Only check keywords that share words with text
    candidate_keywords = []
    for kw in keywords:
        kw_lower = kw.lower()
        kw_words = [w for w in kw_lower.split() if w and w not in STOP_WORDS and len(w) >= 2]
        matched_words = sum(1 for kw_w in kw_words if kw_w in text_word_set)
        
        if matched_words > 0:
            candidate_keywords.append((kw, matched_words))
    
    # If we have candidates, score them
    if not candidate_keywords:
        return None  # No word overlap - will be handled by Pass 2
    
    # Score candidates with RapidFuzz
    best_match = None
    best_score = 0.40  # Pass 1 threshold
    best_matched_words = 0
    
    for original_kw, word_count in sorted(candidate_keywords, key=lambda x: -x[1])[:250]:  # Increased to 250
        kw_lower = original_kw.lower()
        score = fuzz.token_set_ratio(text_lower, kw_lower) / 100.0
        
        if score > best_score or (score == best_score and word_count > best_matched_words):
            best_score = score
            best_match = original_kw
            best_matched_words = word_count
    
    if best_match is None:
        return None
    
    verification_details = {
        'step1_passed': True,
        'step1_reason': f'Pass 1: Keyword match with {best_matched_words} words',
        'step2_passed': True,
        'step2_reason': f'RapidFuzz fuzzy score: {best_score:.2f}',
        'algorithm': 'pass1_word_filtering',
        'matched_words': best_matched_words,
        'description_words': len(text_words)
    }
    
    return (best_match, best_score, verification_details)


def match_keyword_in_text_pass2(text: str, keywords: List[str]) -> Optional[Tuple[str, float, Dict]]:
    """
    PASS 2: THOROUGH KEYWORD MATCHING for unmatched records
    
    Algorithm:
    1. Check ALL keywords with RapidFuzz (no pre-filtering)
    2. Use moderate threshold (45%) to catch more fuzzy matches
    3. Only invoked for records that didn't match in Pass 1
    
    Returns: (keyword, score, details) or None
    """
    if not text or not keywords:
        return None
    
    text_lower = text.lower().strip()
    if not text_lower:
        return None
    
    # Pass 2: Check all keywords with moderate threshold (45% - more lenient)
    best_match = None
    best_score = 0.45  # Lowered from 50% to 45% to catch more matches
    
    # Score all keywords
    scores = []
    for kw in keywords:
        kw_lower = kw.lower()
        score = fuzz.token_set_ratio(text_lower, kw_lower) / 100.0
        if score >= best_score:
            scores.append((score, kw))
    
    if not scores:
        return None
    
    # Get the best match
    best_score, best_match = max(scores, key=lambda x: x[0])
    
    text_words = [w for w in text_lower.split() if w and w not in STOP_WORDS and len(w) >= 2]
    
    verification_details = {
        'step1_passed': False,
        'step1_reason': 'No word overlap in Pass 1',
        'step2_passed': True,
        'step2_reason': f'Pass 2: RapidFuzz score: {best_score:.2f}',
        'algorithm': 'pass2_fuzzy_matching',
        'matched_words': 0,
        'description_words': len(text_words)
    }
    
    return (best_match, best_score, verification_details)


def match_keyword_in_text_pass3(text: str, keywords: List[str]) -> Optional[Tuple[str, float, Dict]]:
    """
    PASS 3: ULTRA-LENIENT KEYWORD MATCHING for stubborn unmatched records
    
    Algorithm:
    1. Check ALL keywords with RapidFuzz (no pre-filtering)
    2. Use very low threshold (35%) to catch even loose matches
    3. Only invoked for records that didn't match in Pass 1 or Pass 2
    
    Returns: (keyword, score, details) or None
    """
    if not text or not keywords:
        return None
    
    text_lower = text.lower().strip()
    if not text_lower:
        return None
    
    # Pass 3: Check all keywords with lenient threshold (35%)
    best_match = None
    best_score = 0.35  # Very lenient - catches even loose associations
    
    # Score all keywords
    scores = []
    for kw in keywords:
        kw_lower = kw.lower()
        score = fuzz.token_set_ratio(text_lower, kw_lower) / 100.0
        if score >= best_score:
            scores.append((score, kw))
    
    if not scores:
        return None
    
    # Get the best match
    best_score, best_match = max(scores, key=lambda x: x[0])
    
    text_words = [w for w in text_lower.split() if w and w not in STOP_WORDS and len(w) >= 2]
    
    verification_details = {
        'step1_passed': False,
        'step1_reason': 'No word overlap in Pass 1',
        'step2_passed': False,
        'step2_reason': 'No match in Pass 2 (45% threshold)',
        'step3_passed': True,
        'step3_reason': f'Pass 3: Ultra-lenient RapidFuzz score: {best_score:.2f}',
        'algorithm': 'pass3_ultra_lenient_matching',
        'matched_words': 0,
        'description_words': len(text_words)
    }
    
    return (best_match, best_score, verification_details)


def find_best_keyword_match(text: str, keywords: List[str]) -> Optional[Tuple[str, float, dict]]:
    """
    ULTRA-FAST KEYWORD MATCHING - MAIN ENTRY POINT
    
    Uses RapidFuzz C++ optimized fuzzy matching.
    Expected performance: 70-80% ticket match in <1 minute for large datasets.
    
    Returns: (keyword, score, verification_details) or None
    """
    return match_keyword_in_text_rapidfuzz(text, keywords)


def merge_file(df_input: pd.DataFrame, source_filename: str = None) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Process input DataFrame by matching subgroup keywords.

    Returns: (merged_df, unmatched_df, log_info)
    """
    # Look for lookup.xlsx in multiple locations
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        "lookup.xlsx",
        os.path.join(script_dir, "lookup.xlsx"),
        os.path.join(os.getcwd(), "lookup.xlsx")
    ]
    
    lookup_path = None
    for path in possible_paths:
        if os.path.exists(path):
            lookup_path = path
            break
    
    if not lookup_path:
        print(f"[ERROR] lookup.xlsx not found. Searched in:", file=sys.stderr)
        for p in possible_paths:
            print(f"  - {p}", file=sys.stderr)
        raise FileNotFoundError(f"lookup.xlsx not found. Searched in: {possible_paths}")
    
    df_lookup = load_excel_file(lookup_path)

    df_input = df_input.copy()
    total_input_rows = len(df_input)
    input_cols = list(df_input.columns)

    desc_col = find_column_case_insensitive(df_input, ["description"])
    if desc_col is None:
        print(f"[DEBUG] Available columns: {list(df_input.columns)}", file=sys.stderr)
        raise ValueError(f"Input DataFrame missing 'description' column. Available columns: {list(df_input.columns)}")

    subgroup_col = find_column_case_insensitive(df_lookup, ["subgroup"])
    if subgroup_col is None:
        raise ValueError("Lookup file missing 'subgroup' column")

    # Enrichment lookup columns (best-effort)
    usecase_col = find_column_case_insensitive(df_lookup, ["usecase", "use case"])
    automation_col = find_column_case_insensitive(df_lookup, ["automation feasibility"])
    approach_col = find_column_case_insensitive(df_lookup, ["automation approach"])
    leftshift_col = find_column_case_insensitive(df_lookup, ["left shift feasibility"])
    elimination_col = find_column_case_insensitive(df_lookup, ["elimination feasibility"])
    l1l2_col = find_column_case_insensitive(df_lookup, ["l1/l2", "l1", "l2"])

    lookup_cols = {
        'usecase': usecase_col,
        'automation': automation_col,
        'approach': approach_col,
        'leftshift': leftshift_col,
        'elimination': elimination_col,
        'l1l2': l1l2_col
    }

    lookup_subgroups_raw = df_lookup[subgroup_col].fillna("").astype(str).map(lambda s: s.strip()).tolist()
    keywords_unique = list(dict.fromkeys([s.strip().lower() for s in lookup_subgroups_raw if s.strip() != ""]))

    keyword_to_row = {}
    for idx in df_lookup.index:
        raw = str(df_lookup.at[idx, subgroup_col]).strip()
        norm = raw.lower()
        if norm == "":
            continue
        if norm not in keyword_to_row:
            keyword_to_row[norm] = {
                "lookup_index": int(idx),
                "lookup_row": df_lookup.loc[idx],
                "original_keyword": raw
            }

    # TWO-PASS MATCHING: Enhanced to catch more records
    # Extract all descriptions at once
    descriptions = df_input[desc_col].fillna("").astype(str).map(lambda s: s.strip())
    
    all_results = []
    
    # PASS 1: Fast word-based matching
    print(f"[DEBUG] Pass 1: Word-based matching on {len(descriptions)} rows", file=sys.stderr)
    for in_idx, desc_str in zip(descriptions.index, descriptions.values):
        # Try Pass 1 matching (word-based filtering)
        match = match_keyword_in_text_rapidfuzz(desc_str, keywords_unique)

        result = {
            "input_index": int(in_idx),
            "description": desc_str,
            "matched": match is not None,
            "keyword": None,
            "score": 0.0,
            "lookup_data": {},
            "verification": {
                "step1_passed": False,
                "step1_reason": "",
                "step2_passed": False,
                "step2_reason": ""
            }
        }

        if match:
            keyword_norm, score, verification = match
            result["keyword"] = keyword_norm
            result["score"] = score
            result["verification"] = verification
            lookup_entry = keyword_to_row.get(keyword_norm)
            if lookup_entry:
                result["lookup_data"] = {
                    "lookup_index": lookup_entry["lookup_index"],
                    "lookup_row": lookup_entry["lookup_row"],
                    "original_keyword": lookup_entry["original_keyword"]
                }

        all_results.append(result)
    
    # PASS 2: Thorough fuzzy matching for unmatched records
    unmatched_indices = [r["input_index"] for r in all_results if not r["matched"]]
    print(f"[DEBUG] Pass 2: Fuzzy matching on {len(unmatched_indices)} unmatched records", file=sys.stderr)
    
    for result in all_results:
        if result["matched"]:
            continue  # Already matched in Pass 1
        
        in_idx = result["input_index"]
        desc_str = result["description"]
        
        # Try Pass 2 matching (full fuzzy search with high threshold)
        match = match_keyword_in_text_pass2(desc_str, keywords_unique)
        
        if match:
            keyword_norm, score, verification = match
            result["keyword"] = keyword_norm
            result["score"] = score
            result["verification"] = verification
            result["matched"] = True
            lookup_entry = keyword_to_row.get(keyword_norm)
            if lookup_entry:
                result["lookup_data"] = {
                    "lookup_index": lookup_entry["lookup_index"],
                    "lookup_row": lookup_entry["lookup_row"],
                    "original_keyword": lookup_entry["original_keyword"]
                }

    matched_count = sum(1 for r in all_results if r["matched"])
    unmatched_count = len(all_results) - matched_count
    
    # PASS 3: Ultra-lenient matching for remaining stubborn unmatched records
    unmatched_indices = [r["input_index"] for r in all_results if not r["matched"]]
    print(f"[DEBUG] Pass 3: Ultra-lenient matching on {len(unmatched_indices)} stubborn unmatched records", file=sys.stderr)
    
    for result in all_results:
        if result["matched"]:
            continue  # Already matched in Pass 1 or 2
        
        in_idx = result["input_index"]
        desc_str = result["description"]
        
        # Try Pass 3 matching (ultra-lenient fuzzy search at 35% threshold)
        match = match_keyword_in_text_pass3(desc_str, keywords_unique)
        
        if match:
            keyword_norm, score, verification = match
            result["keyword"] = keyword_norm
            result["score"] = score
            result["verification"] = verification
            result["matched"] = True
            lookup_entry = keyword_to_row.get(keyword_norm)
            if lookup_entry:
                result["lookup_data"] = {
                    "lookup_index": lookup_entry["lookup_index"],
                    "lookup_row": lookup_entry["lookup_row"],
                    "original_keyword": lookup_entry["original_keyword"]
                }
    
    # Update match counts after all 3 passes
    matched_count = sum(1 for r in all_results if r["matched"])
    unmatched_count = len(all_results) - matched_count
    print(f"[DEBUG] After Pass 3: {matched_count} matched, {unmatched_count} unmatched", file=sys.stderr)
    first_matches = []
    for result in all_results:
        in_idx = result["input_index"]
        input_row = df_input.loc[in_idx]
        
        # Start with ALL original input columns
        enriched = {}
        for col in input_cols:
            enriched[col] = input_row.get(col)

        if result["matched"] and result["lookup_data"]:
            lookup_row = result["lookup_data"]["lookup_row"]
            enriched["Matched_Keyword"] = result["lookup_data"].get("original_keyword", result["keyword"])
            enriched["Match_Score"] = round(result["score"], 2)
            enriched["Verification_Step1"] = result["verification"]["step1_reason"]
            enriched["Verification_Step2"] = result["verification"]["step2_reason"]
            enriched["UseCase"] = lookup_row.get(usecase_col) if usecase_col else ""
            enriched["Automation_Feasibility"] = lookup_row.get(automation_col) if automation_col else ""
            enriched["Automation_Approach"] = lookup_row.get(approach_col) if approach_col else ""
            enriched["Left_Shift_Feasibility"] = lookup_row.get(leftshift_col) if leftshift_col else ""
            enriched["Elimination_Feasibility"] = lookup_row.get(elimination_col) if elimination_col else ""
            enriched["L1_L2"] = lookup_row.get(l1l2_col) if l1l2_col else ""
            first_matches.append({
                "input_index": in_idx,
                "matched_subgroup": enriched.get("Matched_Keyword"),
                "match_score": enriched.get("Match_Score"),
                "lookup_row_id": result["lookup_data"].get("lookup_index"),
                "verification_step1": result["verification"]["step1_reason"],
                "verification_step2": result["verification"]["step2_reason"]
            })
        else:
            enriched["Matched_Keyword"] = ""
            enriched["Match_Score"] = 0.0
            enriched["UseCase"] = "Others"
            enriched["Automation_Feasibility"] = "Unknown"
            enriched["Automation_Approach"] = "Unknown"
            enriched["Left_Shift_Feasibility"] = "Unknown"
            enriched["Elimination_Feasibility"] = "Unknown"
            enriched["L1_L2"] = "Unknown"
            unmatched_rows.append(enriched)

        output_rows.append(enriched)

    enriched_df = pd.DataFrame(output_rows)
    unmatched_df = pd.DataFrame(unmatched_rows)

    log_info = {
        "total_rows": total_input_rows,
        "matched_count": matched_count,
        "unmatched_count": unmatched_count,
        "distinct_subgroups": len(keywords_unique),
        "first_matches": first_matches[:10]
    }

    return enriched_df, unmatched_df, log_info


def main():
    try:
        input_path = "input.xlsx"
        print("=" * 80)
        print("TICKET PROCESSING & OPTIMIZATION ANALYSIS (CLI)")
        print("=" * 80)

        df_input = load_excel_file(input_path)
        enriched_df, unmatched_df, log_info = merge_file(df_input, source_filename=input_path)

        total_input_rows = log_info.get("total_rows", len(df_input))
        matched_count = log_info.get("matched_count", enriched_df.shape[0] - unmatched_df.shape[0])
        unmatched_count = log_info.get("unmatched_count", unmatched_df.shape[0])

        summary_data = []
        elimination_count = sum(1 for _, row in enriched_df.iterrows() if str(row.get("Elimination_Feasibility", "")).strip().lower() == "feasible")
        summary_data.append({"Lever": "Elimination", "# of UseCases": elimination_count, "Volume": total_input_rows, "FTE": round(elimination_count / 140, 2)})

        automation_count = sum(1 for _, row in enriched_df.iterrows() if str(row.get("Automation_Feasibility", "")).strip().lower() == "feasible")
        summary_data.append({"Lever": "Automation", "# of UseCases": automation_count, "Volume": total_input_rows, "FTE": round(automation_count / 140, 2)})

        standard_count = sum(1 for _, row in enriched_df.iterrows() if str(row.get("Automation_Approach", "")).strip().lower() == "standard")
        summary_data.append({"Lever": "Standard Automation", "# of UseCases": standard_count, "Volume": total_input_rows, "FTE": round(standard_count / 140, 2)})

        agentic_count = sum(1 for _, row in enriched_df.iterrows() if "agentic" in str(row.get("Automation_Approach", "")).strip().lower())
        summary_data.append({"Lever": "Agentic AI", "# of UseCases": agentic_count, "Volume": total_input_rows, "FTE": round(agentic_count / 140, 2)})

        leftshift_count = sum(1 for _, row in enriched_df.iterrows() if str(row.get("Left_Shift_Feasibility", "")).strip().lower() == "feasible")
        summary_data.append({"Lever": "Left Shift", "# of UseCases": leftshift_count, "Volume": total_input_rows, "FTE": round(leftshift_count / 140, 2)})

        summary_df = pd.DataFrame(summary_data)

        output_filename = f"processed_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            enriched_df.to_excel(writer, sheet_name='Enriched Data', index=False)
            summary_df.to_excel(writer, sheet_name='Optimization Summary', index=False)

        summary_json = {
            "generated_at": datetime.now().isoformat(),
            "total_tickets": total_input_rows,
            "matched": matched_count,
            "unmatched": unmatched_count,
            "match_rate": f"{(matched_count/total_input_rows*100):.1f}%",
            "summary": summary_data
        }
        with open("summary.json", "w") as f:
            json.dump(summary_json, f, indent=2)

        print(f"Saved: {output_filename} and summary.json")
        print("Processing complete.")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
