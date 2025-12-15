import pandas as pd
import json


def normalize_column_name(col_name):
    """Normalize column name for comparison."""
    return str(col_name).strip().lower()


def find_column(df, search_terms):
    """Find a column by searching for any of the search terms (case-insensitive, trimmed)."""
    normalized_cols = {normalize_column_name(col): col for col in df.columns}
    search_terms_lower = [normalize_column_name(term) for term in search_terms]

    for term in search_terms_lower:
        if term in normalized_cols:
            return normalized_cols[term]
    return None


def normalize_value(val):
    """Normalize a cell value for comparison."""
    if pd.isna(val):
        return None
    return str(val).strip().lower()


def get_optimization_metrics(df: pd.DataFrame) -> dict:
    """
    Extract FTE values from the merged DataFrame for use in RL calculations.
    Returns: {
        "fte_elimination": float,
        "fte_automation": float,
        "fte_agentic": float,
        "fte_left_shift": float,
        "l1_5_per_month": float,
        "num_months": int
    }
    """
    
    # Find required columns
    col_l1l2 = find_column(df, ["L1_L2", "L1/L2", "L1/l2", "L1_l2"])
    if not col_l1l2:
        raise ValueError("Column 'L1_L2' not found")
    
    col_elim = find_column(df, ["Elimination_Feasibility", "Elimination"])
    if not col_elim:
        raise ValueError("Column 'Elimination' not found")
    
    col_usecase = find_column(df, ["UseCase", "Usecase", "Use Case"])
    if not col_usecase:
        raise ValueError("Column 'Usecase' not found")
    
    col_closed_month = find_column(df, ["Closed Month", "ClosedMonth"])
    num_months = 1
    if col_closed_month:
        unique_months = df[col_closed_month].dropna().unique()
        num_months = len(unique_months) or 1
    
    col_automation = find_column(df, ["Automation_Feasibility", "Automation"])
    if not col_automation:
        raise ValueError("Column 'Automation' not found")
    
    col_std_agentic = find_column(df, ["Automation_Approach", "Std/Agentic"])
    if not col_std_agentic:
        raise ValueError("Column 'Automation Approach' not found")
    
    col_left_shift = find_column(df, ["Left_Shift_Feasibility", "Left Shift", "LeftShift"])
    if not col_left_shift:
        raise ValueError("Column 'Left Shift' not found")
    
    # Calculate L1.5 tickets per month
    total_l1_5 = df[col_l1l2].apply(normalize_value).eq("l1.5").sum()
    total_l2 = df[col_l1l2].apply(normalize_value).eq("l2").sum()
    l1_5_per_month = total_l1_5 / num_months if num_months > 0 else 0
    
    # Debug output
    print("\n" + "="*70)
    print("RL CALCULATION DEBUG - OPTIMIZATION METRICS")
    print("="*70)
    print(f"Total rows in DataFrame: {len(df)}")
    print(f"Unique months: {num_months}")
    print(f"Total L1.5 tickets: {total_l1_5}")
    print(f"Total L2 tickets: {total_l2}")
    print(f"L1.5 tickets per month: {l1_5_per_month}")
    
    # Elimination: L1.5 & Elimination=feasible
    elim_df = df[(df[col_elim].apply(normalize_value).eq("feasible")) & 
                 (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    elim_count = len(elim_df)
    elim_volume = len(elim_df) / num_months if num_months > 0 else 0
    fte_elimination = elim_volume / 140
    
    print(f"\n--- ELIMINATION ---")
    print(f"Filter: L1.5 & Elimination_Feasibility = 'feasible'")
    print(f"Matching tickets: {elim_count}")
    print(f"Volume per month (tickets/months): {elim_count}/{num_months} = {elim_volume}")
    print(f"FTE (volume/140): {elim_volume}/140 = {fte_elimination}")
    
    # Automation (standard or standard/agentic ai): L1.5 & Automation=feasible & Approach=standard or standard/agentic ai
    auto_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & 
                 (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    std_agentic_normalized = auto_df[col_std_agentic].apply(normalize_value)
    auto_std_df = auto_df[std_agentic_normalized.eq("standard") | std_agentic_normalized.eq("standard/agentic ai")]
    auto_count = len(auto_std_df)
    auto_volume = len(auto_std_df) / num_months if num_months > 0 else 0
    fte_automation = auto_volume / 140
    
    print(f"\n--- AUTOMATION (Standard + Standard/Agentic) ---")
    print(f"Filter: L1.5 & Automation_Feasibility = 'feasible' & Approach in ('standard', 'standard/agentic ai')")
    print(f"Matching tickets: {auto_count}")
    print(f"Volume per month (tickets/months): {auto_count}/{num_months} = {auto_volume}")
    print(f"FTE (volume/140): {auto_volume}/140 = {fte_automation}")
    
    # Agentic AI: L1.5 & Automation=feasible & Approach=agentic ai
    agentic_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & 
                    (df[col_std_agentic].apply(normalize_value).eq("agentic ai")) & 
                    (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    agentic_count = len(agentic_df)
    agentic_volume = len(agentic_df) / num_months if num_months > 0 else 0
    fte_agentic = agentic_volume / 140
    
    print(f"\n--- AGENTIC AI (Only) ---")
    print(f"Filter: L1.5 & Automation_Feasibility = 'feasible' & Approach = 'agentic ai'")
    print(f"Matching tickets: {agentic_count}")
    print(f"Volume per month (tickets/months): {agentic_count}/{num_months} = {agentic_volume}")
    print(f"FTE (volume/140): {agentic_volume}/140 = {fte_agentic}")
    
    # Left Shift: L1.5 & Left Shift=feasible
    left_df = df[(df[col_left_shift].apply(normalize_value).eq("feasible")) & 
                 (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    left_count = len(left_df)
    left_volume = len(left_df) / num_months if num_months > 0 else 0
    fte_left_shift = left_volume / 140
    
    print(f"\n--- LEFT SHIFT ---")
    print(f"Filter: L1.5 & Left_Shift_Feasibility = 'feasible'")
    print(f"Matching tickets: {left_count}")
    print(f"Volume per month (tickets/months): {left_count}/{num_months} = {left_volume}")
    print(f"FTE (volume/140): {left_volume}/140 = {fte_left_shift}")
    print("="*70 + "\n")
    
    return {
        "fte_elimination": round(fte_elimination, 4),
        "fte_automation": round(fte_automation, 4),
        "fte_agentic": round(fte_agentic, 4),
        "fte_left_shift": round(fte_left_shift, 4),
        "l1_5_per_month": round(l1_5_per_month, 4),
        "num_months": int(num_months)
    }


def calculate_overall_rl(metrics: dict) -> dict:
    """
    Calculate Overall RL for three periods:
    - H1Y1: (L1.5 per month / 140) - FTE_Elimination
    - H2Y1: (L1.5 per month / 140) - FTE_Elimination - ((FTE_Automation + FTE_Agentic) * 50%)
    - H1Y2: (L1.5 per month / 140) - FTE_Elimination - FTE_Automation - FTE_Agentic
    """
    
    l1_5_per_month = metrics["l1_5_per_month"]
    fte_elim = metrics["fte_elimination"]
    fte_auto = metrics["fte_automation"]
    fte_agentic = metrics["fte_agentic"]
    
    # Base: L1.5 per month / 140
    base_rl = l1_5_per_month / 140 if l1_5_per_month > 0 else 0
    
    # Debug output
    print("\n" + "="*70)
    print("RL CALCULATION DEBUG - OVERALL RL")
    print("="*70)
    print(f"Base RL = L1.5_per_month / 140 = {l1_5_per_month} / 140 = {base_rl}")
    print(f"\nFTE Values:")
    print(f"  FTE_Elimination: {fte_elim}")
    print(f"  FTE_Automation: {fte_auto}")
    print(f"  FTE_Agentic: {fte_agentic}")
    
    # H1Y1: 140 productivity, no automation
    # = (L1.5 per month / 140) - FTE_Elimination
    h1y1_rl = base_rl - fte_elim
    print(f"\n--- H1Y1 (140 productivity, no automation) ---")
    print(f"Formula: Base_RL - FTE_Elimination = {base_rl} - {fte_elim} = {h1y1_rl}")
    
    # H2Y1: 160 productivity, 100% elimination, 50% automation
    # = (L1.5 per month / 140) - FTE_Elimination - ((FTE_Automation + FTE_Agentic) * 50%)
    automation_50pct = (fte_auto + fte_agentic) * 0.5
    h2y1_rl = base_rl - fte_elim - automation_50pct
    h2y1_rl = max(0, h2y1_rl)  # Ensure non-negative
    print(f"\n--- H2Y1 (160 productivity, 100% elimination, 50% automation) ---")
    print(f"Formula: Base_RL - FTE_Elimination - ((FTE_Automation + FTE_Agentic) * 50%)")
    print(f"       = {base_rl} - {fte_elim} - ({fte_auto} + {fte_agentic}) * 0.5")
    print(f"       = {base_rl} - {fte_elim} - {automation_50pct}")
    print(f"       = {h2y1_rl}")
    
    # H1Y2: 160 productivity, 100% elimination, 100% automation
    # = (L1.5 per month / 140) - FTE_Elimination - FTE_Automation - FTE_Agentic
    h1y2_rl = base_rl - fte_elim - fte_auto - fte_agentic
    h1y2_rl = max(0, h1y2_rl)  # Ensure non-negative
    print(f"\n--- H1Y2 (160 productivity, 100% elimination, 100% automation) ---")
    print(f"Formula: Base_RL - FTE_Elimination - FTE_Automation - FTE_Agentic")
    print(f"       = {base_rl} - {fte_elim} - {fte_auto} - {fte_agentic}")
    print(f"       = {h1y2_rl}")
    print("="*70 + "\n")
    
    # Keep the original calculated values (no minimum constraint applied)
    print(f"\nFINAL OVERALL RL (actual calculated values): H1Y1={h1y1_rl:.4f}, H2Y1={h2y1_rl:.4f}, H1Y2={h1y2_rl:.4f}")
    print("="*70 + "\n")
    
    return {
        "H1Y1": round(h1y1_rl, 4),
        "H2Y1": round(h2y1_rl, 4),
        "H1Y2": round(h1y2_rl, 4)
    }


def adjust_rl_for_non_ticketed(overall_rl: dict, non_ticketed_percent: float) -> dict:
    """
    Adjust H1Y1 RL value based on non-ticketed activity percentage.
    
    Logic:
    - Base non-ticketed = 15% (already included in H1Y1)
    - If non_ticketed_percent > 15:
        1. Calculate excess: excess = non_ticketed_percent - 15
        2. Calculate additional FTE: additional_fte = H1Y1 * (excess / 100)
        3. Adjust H1Y1: adjusted_H1Y1 = H1Y1 + additional_fte
    - If non_ticketed_percent <= 15: No adjustment needed
    
    Example:
    - H1Y1 = 20, non_ticketed_percent = 30%
    - excess = 30 - 15 = 15%
    - additional_fte = 20 * (15 / 100) = 3
    - adjusted_H1Y1 = 20 + 3 = 23
    
    Args:
        overall_rl: dict with keys "H1Y1", "H2Y1", "H1Y2"
        non_ticketed_percent: float value from 0-100
    
    Returns:
        dict with adjusted H1Y1 value
    """
    
    if non_ticketed_percent <= 15:
        # No adjustment needed, 15% is baseline
        return overall_rl
    
    # Calculate excess non-ticketed percentage above baseline
    excess_pct = non_ticketed_percent - 15
    
    # Calculate additional FTE needed for excess non-ticketed work
    # additional_fte = H1Y1 * (excess / 100)
    h1y1_original = overall_rl["H1Y1"]
    additional_fte = h1y1_original * (excess_pct / 100)
    
    # Adjusted H1Y1 = original H1Y1 + additional FTE
    adjusted_h1y1 = h1y1_original + additional_fte
    
    # Return adjusted RL with H1Y1 updated, H2Y1 and H1Y2 unchanged
    adjusted_rl = {
        "H1Y1": round(adjusted_h1y1, 4),
        "H2Y1": overall_rl["H2Y1"],  # No adjustment
        "H1Y2": overall_rl["H1Y2"]   # No adjustment
    }
    
    return adjusted_rl


def calculate_gradewise_mnm_rl(overall_rl: dict) -> pd.DataFrame:
    """
    Calculate GradeWise MnM RL table based on Overall RL values.
    
    Rows: Grade, PAT/PT, PA/P, A, SA, M, SM
    Columns: M1-M6 (H1Y1), M7-M12 (H2Y1), M13-M18 (H1Y2)
    
    Logic:
    - SM: IF(Total RL >= 150, 1, 0)
    - M: IF(Total RL >= 100, 2, IF(Total RL >= 50, 1, 0))
    - SA: IF(Total RL >= 150, 4, IF(Total RL >= 100, 3, IF(Total RL > 50, 2, IF(Total RL > 25, 1, 0))))
    - A: 10% of Total RL
    - PA/P: 60% of Total RL
    - PAT/PT: 30% of Total RL
    """
    
    h1y1_rl = overall_rl["H1Y1"]
    h2y1_rl = overall_rl["H2Y1"]
    h1y2_rl = overall_rl["H1Y2"]
    
    # Helper function to calculate grades
    def sm_logic(rl_value):
        return 1 if rl_value >= 150 else 0
    
    def m_logic(rl_value):
        if rl_value >= 100:
            return 2
        elif rl_value >= 50:
            return 1
        else:
            return 0
    
    def sa_logic(rl_value):
        if rl_value >= 150:
            return 4
        elif rl_value >= 100:
            return 3
        elif rl_value > 50:
            return 2
        elif rl_value > 25:
            return 1
        else:
            return 0
    
    def a_logic(rl_value):
        return round(rl_value * 0.10, 2)
    
    def pa_logic(rl_value):
        return round(rl_value * 0.60, 2)
    
    def pat_logic(rl_value):
        return round(rl_value * 0.30, 2)
    
    # Calculate values for each period
    data = {
        "Grade": ["PAT/PT", "PA/P", "A", "SA", "M", "SM"]
    }
    
    # H1Y1 columns (M1-M6)
    for i in range(1, 7):
        data[f"M{i}"] = [
            pat_logic(h1y1_rl),
            pa_logic(h1y1_rl),
            a_logic(h1y1_rl),
            sa_logic(h1y1_rl),
            m_logic(h1y1_rl),
            sm_logic(h1y1_rl)
        ]
    
    # H2Y1 columns (M7-M12)
    for i in range(7, 13):
        data[f"M{i}"] = [
            pat_logic(h2y1_rl),
            pa_logic(h2y1_rl),
            a_logic(h2y1_rl),
            sa_logic(h2y1_rl),
            m_logic(h2y1_rl),
            sm_logic(h2y1_rl)
        ]
    
    # H1Y2 columns (M13-M18)
    for i in range(13, 19):
        data[f"M{i}"] = [
            pat_logic(h1y2_rl),
            pa_logic(h1y2_rl),
            a_logic(h1y2_rl),
            sa_logic(h1y2_rl),
            m_logic(h1y2_rl),
            sm_logic(h1y2_rl)
        ]
    
    df = pd.DataFrame(data)
    return df


def calculate_rl_tables(df: pd.DataFrame) -> tuple:
    """
    Main function to calculate both RL tables.
    Returns: (overall_rl_dict, gradewise_df)
    """
    
    # Get optimization metrics
    metrics = get_optimization_metrics(df)
    
    # Calculate Overall RL
    overall_rl = calculate_overall_rl(metrics)
    
    # Calculate GradeWise MnM RL
    gradewise_df = calculate_gradewise_mnm_rl(overall_rl)
    
    return overall_rl, gradewise_df, metrics


def main(file_path):
    df = pd.read_excel(file_path, sheet_name=0)
    print(f"Loaded {len(df)} rows from {file_path}")
    
    overall_rl, gradewise_df, metrics = calculate_rl_tables(df)
    
    print("\n=== Optimization Metrics ===")
    print(json.dumps(metrics, indent=2))
    
    print("\n=== Overall RL ===")
    print(json.dumps(overall_rl, indent=2))
    
    print("\n=== GradeWise MnM RL ===")
    print(gradewise_df.to_string(index=False))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python rl_calculations.py <excel_file_path>")
        sys.exit(1)
    main(sys.argv[1])
