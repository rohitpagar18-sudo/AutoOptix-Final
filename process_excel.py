import pandas as pd
import json
import sys
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')


def convert_to_mmm_yyyy(date_value):
    """
    Convert any date format to 'mmm-yyyy' format (e.g., Jan-2025, Feb-2024)
    Handles:
    - DateTime objects
    - Strings in various formats: mm-yyyy, mmm-yyyy, yyyy-mm, dd/mm/yyyy, etc.
    - Timestamps
    
    Returns: 'mmm-yyyy' format or original value if conversion fails
    """
    if pd.isna(date_value) or date_value is None:
        return ""
    
    try:
        # If it's already a datetime, format it
        if isinstance(date_value, (pd.Timestamp, datetime)):
            return date_value.strftime('%b-%Y')
        
        # If it's a string, try to parse it
        if isinstance(date_value, str):
            date_str = str(date_value).strip()
            
            # Try common date formats
            formats = [
                '%m-%Y',        # 01-2025
                '%m-%y',        # 01-25
                '%b-%Y',        # Jan-2025
                '%b-%y',        # Jan-25
                '%B-%Y',        # January-2025
                '%B-%y',        # January-25
                '%Y-%m',        # 2025-01
                '%Y-%b',        # 2025-Jan
                '%m/%Y',        # 01/2025
                '%d/%m/%Y',     # 01/01/2025
                '%m/%d/%Y',     # 01/01/2025
                '%Y/%m/%d',     # 2025/01/01
                '%d-%m-%Y',     # 01-01-2025
                '%Y-%m-%d',     # 2025-01-01
            ]
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%b-%Y')
                except:
                    pass
            
            # If no format matched, return as-is
            return date_str
        
        # If it's numeric (timestamp), convert
        if isinstance(date_value, (int, float)):
            return pd.Timestamp(date_value).strftime('%b-%Y')
        
        return str(date_value)
    
    except Exception as e:
        # If all conversions fail, return original
        return str(date_value)


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
    # Debug: Print available columns
    import sys
    print(f"\n[DEBUG] Available columns in merged_df: {list(df.columns)}", file=sys.stderr)
    
    # Find required columns - with smart detection for various spellings
    # Check for L1/L2 in original columns OR enriched L1_L2 column from lookup
    col_l1l2 = find_column(df, ["L1/L2", "L1_L2", "Level", "Ticket Level", "l1/l2", "l1_l2"])
    if not col_l1l2:
        print(f"[DEBUG] Column search failed. Available: {list(df.columns)}", file=sys.stderr)
        # If L1/L2 not found, create a default column with all "L1.5" values
        print("[WARNING] L1/L2 column not found. Creating default L1.5 classification.", file=sys.stderr)
        df['L1/L2'] = 'L1.5'
        col_l1l2 = 'L1/L2'

    col_elim = find_column(df, ["Elimination", "Elimination_Feasibility", "Elimination Feasibility", "elimination", "elimination_feasibility"])
    if not col_elim:
        print("[WARNING] Elimination column not found. Creating default 'Not feasible'.", file=sys.stderr)
        df['Elimination_Feasibility'] = 'Not feasible'
        col_elim = 'Elimination_Feasibility'

    col_usecase = find_column(df, ["UseCase", "Use Case", "Case Name", "Usecase", "usecase", "use case"])
    if not col_usecase:
        print("[WARNING] UseCase column not found. Creating default 'Unknown'.", file=sys.stderr)
        df['UseCase'] = 'Unknown'
        col_usecase = 'UseCase'

    col_closed_month = find_column(df, ["Closed Month", "Month", "Month Resolved", "closed month", "month"])
    # closed month may be optional; if missing, treat num_months = 1
    num_months = 1
    if col_closed_month:
        unique_months = df[col_closed_month].dropna().unique()
        num_months = len(unique_months) or 1

    col_automation = find_column(df, ["Automation_Feasibility", "Automation Feasibility", "Automation", "automation_feasibility", "automation"])
    if not col_automation:
        print("[WARNING] Automation_Feasibility column not found. Creating default 'Unknown'.", file=sys.stderr)
        df['Automation_Feasibility'] = 'Unknown'
        col_automation = 'Automation_Feasibility'

    col_std_agentic = find_column(df, ["Automation_Approach", "Automation Approach", "Std/Agentic", "Automation Type", "automation_approach", "automation approach"])
    if not col_std_agentic:
        print("[WARNING] Automation_Approach column not found. Creating default 'Unknown'.", file=sys.stderr)
        df['Automation_Approach'] = 'Unknown'
        col_std_agentic = 'Automation_Approach'

    col_left_shift = find_column(df, ["Left_Shift_Feasibility", "Left Shift", "Left Shift Feasibility", "Can Left Shift", "left_shift_feasibility", "left shift"])
    if not col_left_shift:
        print("[WARNING] Left_Shift_Feasibility column not found. Creating default 'Unknown'.", file=sys.stderr)
        df['Left_Shift_Feasibility'] = 'Unknown'
        col_left_shift = 'Left_Shift_Feasibility'

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
    auto_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
    std_agentic_normalized = auto_df[col_std_agentic].apply(normalize_value)
    auto_std_df = auto_df[std_agentic_normalized.eq("standard") | std_agentic_normalized.eq("standard/agentic ai")]
    auto_usecases = int(auto_std_df[col_usecase].nunique())
    auto_ticket_volume = len(auto_std_df) / num_months if num_months > 0 else 0
    auto_fte = round(auto_ticket_volume / 140, 2)
    automation_array = [auto_usecases, round(auto_ticket_volume, 2), auto_fte]

    # Agentic
    agentic_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & (df[col_std_agentic].apply(normalize_value).eq("agentic ai")) & (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
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
