import pandas as pd
import json
import sys
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')


def normalize_column_name(col_name):
    """Normalize column name for comparison - removes all special chars and spaces."""
    # Convert to lowercase and remove all non-alphanumeric characters
    normalized = re.sub(r'[^a-z0-9]', '', str(col_name).strip().lower())
    return normalized


def find_column(df, search_terms):
    """
    Find a column by searching for any of the search terms.
    Handles various spellings, spaces, special characters, and abbreviations.
    """
    normalized_cols = {normalize_column_name(col): col for col in df.columns}
    
    # Expand search terms to include common variations
    expanded_terms = []
    for term in search_terms:
        expanded_terms.append(normalize_column_name(term))
        # Add variations for common misspellings and formats
        norm = normalize_column_name(term)
        
        # Handle L1/L2 variations
        if 'l1' in norm and 'l2' in norm:
            expanded_terms.extend(['l1l2', 'l1l2level', 'ticketlevel', 'tickettype'])
        
        # Handle Closed Month variations
        if 'closed' in norm and 'month' in norm:
            expanded_terms.extend(['closedmonth', 'closemonth', 'month', 'monthclosed', 'monthresolved'])
        
        # Handle Elimination variations
        if 'elim' in norm:
            expanded_terms.extend(['eliminationfeasibility', 'eliminationfeasible', 'caneliminate'])
        
        # Handle Automation variations
        if 'autom' in norm and 'feasib' in norm:
            expanded_terms.extend(['automationfeasibility', 'automationfeasible', 'canautomated'])
        
        # Handle Std/Agentic variations
        if 'std' in norm or 'agentic' in norm or 'approach' in norm:
            expanded_terms.extend(['stdagentic', 'automationapproach', 'automationtype', 'standardagentic'])
        
        # Handle Left Shift variations
        if 'left' in norm and 'shift' in norm:
            expanded_terms.extend(['leftshift', 'leftshiftfeasibility', 'leftshiftfeasible', 'canleftshift'])
        
        # Handle UseCase variations
        if 'use' in norm and 'case' in norm:
            expanded_terms.extend(['usecase', 'usecases', 'casename', 'caseid'])
    
    # Remove duplicates and search
    expanded_terms = list(set(expanded_terms))
    
    for term in expanded_terms:
        if term in normalized_cols:
            return normalized_cols[term]
    
    return None


def normalize_value(val):
    """Normalize a cell value for comparison."""
    if pd.isna(val):
        return None
    return str(val).strip().lower()


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Accept merged DataFrame and perform calculations. Returns a summary DataFrame
    with rows for each lever (Elimination, Automation, Standard Automation, Agentic AI, Left Shift)
    and top-level totals in JSON form stored to disk as `summary_output.json`.
    """
    # Find required columns - with smart detection for various spellings
    col_l1l2 = find_column(df, ["L1/L2", "Level", "Ticket Level"])
    if not col_l1l2:
        raise ValueError("Column 'L1/L2' (Ticket Level) not found in merged DataFrame")

    col_elim = find_column(df, ["Elimination", "Elimination Feasibility", "Can Eliminate"])
    if not col_elim:
        raise ValueError("Column 'Elimination' not found in merged DataFrame")

    col_usecase = find_column(df, ["UseCase", "Use Case", "Case Name"])
    if not col_usecase:
        raise ValueError("Column 'UseCase' not found in merged DataFrame")

    col_closed_month = find_column(df, ["Closed Month", "Month", "Month Resolved"])
    # closed month may be optional; if missing, treat num_months = 1
    num_months = 1
    if col_closed_month:
        unique_months = df[col_closed_month].dropna().unique()
        num_months = len(unique_months) or 1

    col_automation = find_column(df, ["Automation_Feasibility", "Automation"])
    if not col_automation:
        raise ValueError("Column 'Automation' not found in merged DataFrame")

    col_autom = find_column(df, ["Automation", "Automation Feasibility", "Can Automate"])
    if not col_autom:
        raise ValueError("Column 'Automation' not found in merged DataFrame")

    col_std_agentic = find_column(df, ["Automation Approach", "Std/Agentic", "Automation Type"])
    if not col_std_agentic:
        raise ValueError("Column 'Automation Approach' (Std/Agentic) not found in merged DataFrame")

    col_left_shift = find_column(df, ["Left Shift", "Left Shift Feasibility", "Can Left Shift"])
    if not col_left_shift:
        raise ValueError("Column 'Left Shift' not found in merged DataFrame")

    # Total counts for L1.5 and L2
    total_count_ofL1_5 = df[col_l1l2].apply(normalize_value).eq("l1.5").sum()
    total_count_ofL2 = df[col_l1l2].apply(normalize_value).eq("l2").sum()

    # Elimination
    elim_df = df[(df[col_elim].apply(normalize_value).eq("feasible")) & (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    elim_usecases = int(elim_df[col_usecase].nunique())
    elim_ticket_volume = len(elim_df) / num_months if num_months > 0 else 0
    elim_fte = round(elim_ticket_volume / 140, 2)
    elimination_array = [elim_usecases, round(elim_ticket_volume, 2), elim_fte]

    # Automation
    auto_df = df[(df[col_autom].apply(normalize_value).eq("feasible")) & (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    std_agentic_normalized = auto_df[col_std_agentic].apply(normalize_value)
    auto_std_df = auto_df[std_agentic_normalized.eq("standard") | std_agentic_normalized.eq("standard/agentic ai")]
    auto_usecases = int(auto_std_df[col_usecase].nunique())
    auto_ticket_volume = len(auto_std_df) / num_months if num_months > 0 else 0
    auto_fte = round(auto_ticket_volume / 140, 2)
    automation_array = [auto_usecases, round(auto_ticket_volume, 2), auto_fte]

    # Agentic
    agentic_df = df[(df[col_autom].apply(normalize_value).eq("feasible")) & (df[col_std_agentic].apply(normalize_value).eq("agentic ai")) & (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    agentic_usecases = int(agentic_df[col_usecase].nunique())
    agentic_ticket_volume = len(agentic_df) / num_months if num_months > 0 else 0
    agentic_fte = round(agentic_ticket_volume / 140, 2)
    automation_agent_array = [agentic_usecases, round(agentic_ticket_volume, 2), agentic_fte]

    # Left shift
    left_df = df[(df[col_left_shift].apply(normalize_value).eq("feasible")) & (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    left_usecases = int(left_df[col_usecase].nunique())
    left_ticket_volume = len(left_df) / num_months if num_months > 0 else 0
    left_fte = round(left_ticket_volume / 140, 2)
    left_shift_array = [left_usecases, round(left_ticket_volume, 2), left_fte]

    output = {
        "total_count_ofL1.5": int(total_count_ofL1_5),
        "total_count_ofL2": int(total_count_ofL2),
        "elimination_array": elimination_array,
        "automation_array": automation_array,
        "automation_agent_array": automation_agent_array,
        "left_shift_array": left_shift_array
    }

    # Save JSON summary for compatibility
    with open("summary_output.json", "w") as f:
        json.dump(output, f, indent=4)

    # Create a pandas DataFrame for dashboard consumption (lever rows)
    summary_rows = [
        {"Lever": "Elimination", "# of UseCases": elimination_array[0], "Volume": round(elim_ticket_volume, 2), "FTE": round(elim_ticket_volume / 140, 2)},
        {"Lever": "Automation", "# of UseCases": auto_usecases, "Volume": round(auto_ticket_volume, 2), "FTE": round(auto_ticket_volume / 140, 2)},
        {"Lever": "Agentic AI", "# of UseCases": agentic_usecases, "Volume": round(agentic_ticket_volume, 2), "FTE": round(agentic_ticket_volume / 140, 2)},
        {"Lever": "Left Shift", "# of UseCases": left_usecases, "Volume": round(left_ticket_volume, 2), "FTE": round(left_ticket_volume / 140, 2)},
    ]

    results_df = pd.DataFrame(summary_rows)
    return results_df
