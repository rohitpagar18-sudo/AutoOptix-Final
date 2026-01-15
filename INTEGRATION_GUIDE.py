"""
INTEGRATION GUIDE: Text Cleaning + Rarity-Weighted Matching
===========================================================

This shows WHERE and HOW to integrate text cleaning into AutoOptix data pipeline
"""

WORKFLOW_DIAGRAM = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         AutoOptix Data Pipeline                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Step 1: USER UPLOADS EXCEL FILE
   │
   ├─ File: "ticket_data.xlsx"
   └─ Location: 01_Home.py → st.file_uploader()
                │
                ▼
Step 2: READ FILE
   │
   ├─ Load Excel file into DataFrame
   └─ Location: read_excel("uploaded_file")
                │
                ▼
Step 3: ⭐ TEXT CLEANING (NEW) ⭐ ← INSERT HERE
   │
   ├─ For each ticket description:
   │  1. Remove filler phrases
   │  2. Apply synonym normalization
   │  3. Return cleaned text
   │
   └─ Location: Insert in process_excel_file() function
                │
                ▼
Step 4: KEYWORD MATCHING (NEW)
   │
   ├─ Use cleaned text
   ├─ Apply rarity-weighted matching
   └─ Return: keyword, usecase, confidence
                │
                ▼
Step 5: PROCESS & ENRICH
   │
   ├─ Add matched keyword as new column
   ├─ Add usecase as new column
   ├─ Add confidence score
   └─ Location: process_excel.py
                │
                ▼
Step 6: GENERATE DASHBOARD
   │
   ├─ Visualize matched keywords
   ├─ Show categorization accuracy
   └─ Location: 02_Dashboard.py

╔═══════════════════════════════════════════════════════════════════════════════╗
║                    Implementation Details                                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

OPTION A: SIMPLE INTEGRATION (Minimal changes)
═════════════════════════════════════════════════

File: pages/01_Home.py (line ~460)

def process_excel_file(df):
    \"\"\"Process Excel file with text cleaning.\"\"\"
    
    # 1. Initialize matcher
    from PRODUCTION_MATCHER import RarityWeightedMatcher
    import pandas as pd
    df_lookup = pd.read_excel("lookup.xlsx")
    matcher = RarityWeightedMatcher(df_lookup)
    
    # 2. Find description column
    desc_col = find_column(df, ["Description", "Ticket Description", "Summary"])
    
    if not desc_col:
        raise ValueError("Description column not found")
    
    # 3. CLEAN TEXT & MATCH KEYWORDS
    df['Cleaned_Description'] = ""
    df['Matched_Keyword'] = ""
    df['UseCase'] = ""
    df['Match_Confidence'] = 0.0
    
    for idx, row in df.iterrows():
        ticket_desc = row[desc_col]
        
        if pd.notna(ticket_desc):
            result = matcher.find_best_match(str(ticket_desc))
            
            if result:
                df.at[idx, 'Cleaned_Description'] = result['cleaned_text']
                df.at[idx, 'Matched_Keyword'] = result['keyword']
                df.at[idx, 'UseCase'] = result['usecase']
                df.at[idx, 'Match_Confidence'] = result['confidence']
    
    return df


OPTION B: ADVANCED INTEGRATION (Batch processing)
═════════════════════════════════════════════════

File: process_excel.py

from PRODUCTION_MATCHER import RarityWeightedMatcher
import pandas as pd

class TicketProcessor:
    def __init__(self):
        df_lookup = pd.read_excel("lookup.xlsx")
        self.matcher = RarityWeightedMatcher(df_lookup)
    
    def process_dataframe(self, df):
        \"\"\"Process entire dataframe with text cleaning.\"\"\"
        
        # Find description column
        desc_col = self._find_desc_column(df)
        
        # Add new columns
        df['Cleaned_Description'] = ""
        df['Matched_Keyword'] = ""
        df['UseCase'] = ""
        df['Match_Confidence'] = 0.0
        df['Rarity_Tier'] = ""
        
        # Process each row
        for idx, row in df.iterrows():
            ticket_desc = row[desc_col]
            
            if pd.notna(ticket_desc):
                result = self.matcher.find_best_match(str(ticket_desc))
                
                if result:
                    df.at[idx, 'Cleaned_Description'] = result['cleaned_text']
                    df.at[idx, 'Matched_Keyword'] = result['keyword']
                    df.at[idx, 'UseCase'] = result['usecase']
                    df.at[idx, 'Match_Confidence'] = result['confidence']
                    df.at[idx, 'Rarity_Tier'] = result['rarity_tier']
        
        return df


OPTION C: WITH PROGRESS TRACKING (Best for UI)
═══════════════════════════════════════════════

File: pages/01_Home.py

def process_excel_file(df):
    \"\"\"Process with progress bar for Streamlit UI.\"\"\"
    
    from PRODUCTION_MATCHER import RarityWeightedMatcher
    
    # Initialize
    df_lookup = pd.read_excel("lookup.xlsx")
    matcher = RarityWeightedMatcher(df_lookup)
    
    # Find description column
    desc_col = find_column(df, ["Description", "Summary"])
    
    # Add columns
    df['Cleaned_Description'] = ""
    df['Matched_Keyword'] = ""
    df['UseCase'] = ""
    df['Match_Confidence'] = 0.0
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_rows = len(df)
    
    for idx, row in df.iterrows():
        ticket_desc = row[desc_col]
        
        if pd.notna(ticket_desc):
            result = matcher.find_best_match(str(ticket_desc))
            
            if result:
                df.at[idx, 'Cleaned_Description'] = result['cleaned_text']
                df.at[idx, 'Matched_Keyword'] = result['keyword']
                df.at[idx, 'UseCase'] = result['usecase']
                df.at[idx, 'Match_Confidence'] = result['confidence']
        
        # Update progress
        progress = (idx + 1) / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Processing: {idx + 1}/{total_rows} tickets")
    
    status_text.text("✓ Processing complete!")
    
    return df

╔═══════════════════════════════════════════════════════════════════════════════╗
║                    Input Data Structure Example                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

BEFORE (Raw upload):
┌─────────────────────────────────────────────┐
│ Description                                 │
├─────────────────────────────────────────────┤
│ Hi please give me access for account deletion│
│ Hello can you provide account deactivation  │
│ I need help with access removal request     │
│ Could you please grant me database access   │
└─────────────────────────────────────────────┘

AFTER (After text cleaning + matching):
┌──────────────────────┬────────────────────┬──────────────────────┬──────────────┐
│ Cleaned_Description  │ Matched_Keyword    │ UseCase              │ Confidence   │
├──────────────────────┼────────────────────┼──────────────────────┼──────────────┤
│ access deactivation  │ Account Deactivation│ Account Management   │ 1.00         │
│ provide deactivation │ Account Deactivation│ Account Management   │ 1.00         │
│ access remove req    │ Access Removal     │ Access Control       │ 0.75         │
│ database access      │ Database Access    │ Data Management      │ 0.85         │
└──────────────────────┴────────────────────┴──────────────────────┴──────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                    Dashboard Impact                                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

NEW METRICS TO SHOW:

1. Keyword Distribution (Pie Chart)
   ✓ Show matched keywords and their frequencies
   ✓ Visualize UseCase distribution

2. Text Cleaning Effectiveness
   ✓ % of tickets successfully cleaned
   ✓ % of tickets with high confidence (>80%)

3. Average Confidence Score
   ✓ Overall accuracy metric
   ✓ Per-UseCase accuracy

4. Comparison: Before vs After
   ✓ Raw description vs cleaned
   ✓ Show filler phrases removed
   ✓ Show synonyms applied

"""

if __name__ == "__main__":
    print(WORKFLOW_DIAGRAM)
