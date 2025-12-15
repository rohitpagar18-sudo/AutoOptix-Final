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


def calculate_utilization_graph(df: pd.DataFrame, verbose: bool = False) -> dict:
    """
    Calculate utilization graph data with three levers:
    - Elimination: FTE_Elimination / (L1.5_per_month / 140)
    - Automation Standard: FTE_Automation / (L1.5_per_month / 140)
    - Automation Agentic AI: FTE_Agentic / (L1.5_per_month / 140)
    
    Where:
    - L1.5_per_month = Total L1.5 tickets / number of months
    - (L1.5_per_month / 140) = base divisor
    
    Args:
        df: Input DataFrame
        verbose: If True, print debug information to terminal
    
    Returns a dictionary with values and percentages for each category.
    """
    
    # Find required columns
    col_l1l2 = find_column(df, ["L1_L2", "L1/L2", "L1/l2", "L1_l2"])
    if not col_l1l2:
        raise ValueError("Column 'L1_L2' not found")
    
    col_closed_month = find_column(df, ["Closed Month", "ClosedMonth"])
    num_months = 1
    if col_closed_month:
        unique_months = df[col_closed_month].dropna().unique()
        num_months = len(unique_months) or 1
    
    col_elim = find_column(df, ["Elimination_Feasibility", "Elimination"])
    col_usecase = find_column(df, ["UseCase", "Usecase", "Use Case"])
    col_automation = find_column(df, ["Automation_Feasibility", "Automation"])
    col_std_agentic = find_column(df, ["Automation_Approach", "Std/Agentic"])
    
    # Calculate L1.5 tickets per month
    total_l1_5 = df[col_l1l2].apply(normalize_value).eq("l1.5").sum()
    l1_5_per_month = total_l1_5 / num_months if num_months > 0 else 0
    
    # Calculate base divisor: L1.5 per month / 140
    base_divisor = l1_5_per_month / 140 if l1_5_per_month > 0 else 1
    
    if verbose:
        print("\n" + "="*70)
        print("UTILIZATION GRAPH DEBUG - CALCULATION")
        print("="*70)
        print(f"Total rows in DataFrame: {len(df)}")
        print(f"Unique months: {num_months}")
        print(f"Total L1.5 tickets: {total_l1_5}")
        print(f"L1.5 per month: {l1_5_per_month}")
        print(f"Base divisor (L1.5_per_month / 140): {base_divisor}")
    
    # Calculate FTE values for each lever (from process_excel logic)
    # Elimination: L1.5 & Elimination=feasible
    elim_df = df[(df[col_elim].apply(normalize_value).eq("feasible")) & 
                 (df[col_l1l2].apply(normalize_value).eq("l1.5"))] if col_elim else df[df[col_l1l2].apply(normalize_value).eq("l1.5")].head(0)
    elim_count = len(elim_df)
    fte_elimination = (elim_count / num_months) / 140 if num_months > 0 else 0
    
    # Automation Standard: L1.5 & Automation=feasible & Approach=standard or standard/agentic ai
    if col_automation and col_std_agentic:
        auto_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & 
                     (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
        std_agentic_normalized = auto_df[col_std_agentic].apply(normalize_value)
        auto_std_df = auto_df[std_agentic_normalized.eq("standard") | std_agentic_normalized.eq("standard/agentic ai")]
        auto_count = len(auto_std_df)
    else:
        auto_count = 0
    fte_automation = (auto_count / num_months) / 140 if num_months > 0 else 0
    
    # Automation Agentic AI: L1.5 & Automation=feasible & Approach=agentic ai
    if col_automation and col_std_agentic:
        agentic_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & 
                        (df[col_std_agentic].apply(normalize_value).eq("agentic ai")) & 
                        (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
        agentic_count = len(agentic_df)
    else:
        agentic_count = 0
    fte_agentic = (agentic_count / num_months) / 140 if num_months > 0 else 0
    
    if verbose:
        print(f"\n--- FTE CALCULATION ---")
        print(f"Elimination: {elim_count} tickets / {num_months} months / 140 = {fte_elimination}")
        print(f"Automation Standard: {auto_count} tickets / {num_months} months / 140 = {fte_automation}")
        print(f"Automation Agentic AI: {agentic_count} tickets / {num_months} months / 140 = {fte_agentic}")
    
    # Calculate utilization values: FTE / base_divisor
    elimination_value = fte_elimination / base_divisor if base_divisor > 0 else 0
    automation_std_value = fte_automation / base_divisor if base_divisor > 0 else 0
    agentic_ai_value = fte_agentic / base_divisor if base_divisor > 0 else 0
    
    if verbose:
        print(f"\n--- UTILIZATION VALUES (FTE / base_divisor) ---")
        print(f"Elimination: {fte_elimination} / {base_divisor} = {elimination_value}")
        print(f"Automation Standard: {fte_automation} / {base_divisor} = {automation_std_value}")
        print(f"Automation Agentic AI: {fte_agentic} / {base_divisor} = {agentic_ai_value}")
    
    # Calculate total
    total_value = elimination_value + automation_std_value + agentic_ai_value
    
    # Calculate percentages
    if total_value > 0:
        elimination_percentage = (elimination_value / total_value) * 100
        automation_std_percentage = (automation_std_value / total_value) * 100
        agentic_ai_percentage = (agentic_ai_value / total_value) * 100
    else:
        elimination_percentage = 0
        automation_std_percentage = 0
        agentic_ai_percentage = 0
    
    if verbose:
        print(f"\n--- TOTAL AND PERCENTAGES ---")
        print(f"Total: {elimination_value} + {automation_std_value} + {agentic_ai_value} = {total_value}")
        print(f"Elimination: {elimination_value:.2f} ({elimination_percentage:.2f}%)")
        print(f"Automation Standard: {automation_std_value:.2f} ({automation_std_percentage:.2f}%)")
        print(f"Automation Agentic AI: {agentic_ai_value:.2f} ({agentic_ai_percentage:.2f}%)")
        print("="*70 + "\n")
    
    return {
        "elimination": {
            "value": round(elimination_value, 2),
            "percentage": round(elimination_percentage, 2)
        },
        "automation_standard": {
            "value": round(automation_std_value, 2),
            "percentage": round(automation_std_percentage, 2)
        },
        "automation_agentic": {
            "value": round(agentic_ai_value, 2),
            "percentage": round(agentic_ai_percentage, 2)
        },
        "total": round(total_value, 2),
        "raw_data": {
            "l1_5_per_month": round(l1_5_per_month, 2),
            "base_divisor": round(base_divisor, 2),
            "num_months": int(num_months),
            "fte_elimination": round(fte_elimination, 2),
            "fte_automation": round(fte_automation, 2),
            "fte_agentic": round(fte_agentic, 2)
        }
    }


def get_graph_data_for_display(utilization_data: dict) -> dict:
    """
    Format utilization data for graph display with labels and colors.
    Returns a dictionary suitable for Streamlit pie/bar charts.
    """
    
    categories = {
        "Elimination": {
            "value": utilization_data["elimination"]["value"],
            "percentage": utilization_data["elimination"]["percentage"],
            "color": "#2E8CA8"  # Teal
        },
        "Automation Standard": {
            "value": utilization_data["automation_standard"]["value"],
            "percentage": utilization_data["automation_standard"]["percentage"],
            "color": "#BFE2EA"  # Light Teal
        },
        "Automation Agentic AI": {
            "value": utilization_data["automation_agentic"]["value"],
            "percentage": utilization_data["automation_agentic"]["percentage"],
            "color": "#1F6C86"  # Dark Teal
        }
    }
    
    # Create lists for graph
    labels = list(categories.keys())
    values = [categories[label]["value"] for label in labels]
    percentages = [categories[label]["percentage"] for label in labels]
    colors = [categories[label]["color"] for label in labels]
    
    return {
        "categories": categories,
        "labels": labels,
        "values": values,
        "percentages": percentages,
        "colors": colors,
        "total": utilization_data["total"]
    }


def main(file_path):
    df = pd.read_excel(file_path, sheet_name=0)
    print(f"Loaded {len(df)} rows from {file_path}")
    
    utilization_data = calculate_utilization_graph(df, verbose=True)
    
    print("\n=== Utilization Graph Data ===")
    print(json.dumps({
        "Elimination": f"{utilization_data['elimination']['value']} ({utilization_data['elimination']['percentage']}%)",
        "Automation Standard": f"{utilization_data['automation_standard']['value']} ({utilization_data['automation_standard']['percentage']}%)",
        "Automation Agentic AI": f"{utilization_data['automation_agentic']['value']} ({utilization_data['automation_agentic']['percentage']}%)",
        "Total": utilization_data['total']
    }, indent=2))
    
    graph_data = get_graph_data_for_display(utilization_data)
    print("\n=== Graph Display Data ===")
    for label, percentage in zip(graph_data["labels"], graph_data["percentages"]):
        print(f"{label}: {percentage}%")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python utilization_graphs.py <excel_file_path>")
        sys.exit(1)
    main(sys.argv[1])
