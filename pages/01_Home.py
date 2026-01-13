import streamlit as st
import pandas as pd
import io
import json
from pathlib import Path
import traceback
import os
import base64
import time
import sys
import importlib.util

# Add parent directory to path so we can import from there
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print(f"[DEBUG] Parent directory: {parent_dir}", file=sys.stderr)
print(f"[DEBUG] sys.path: {sys.path[:3]}", file=sys.stderr)

# Logo configuration
LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'logo2.png')
LOGO_PATH1 = os.path.join(os.path.dirname(__file__), '..', 'logo3.png')
# Function to convert image to base64
def get_image_as_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode()

# Convert logo to base64
LOGO_BASE64 = get_image_as_base64(LOGO_PATH)
LOGO_BASE64_2 = get_image_as_base64(LOGO_PATH1)

# Import the required functions - with detailed error handling
merge_file = None
process_dataframe = None
populate_dashboard = None

# Method 1: Try direct import (normal case)
try:
    print(f"[DEBUG] Attempting direct import of merge_file...", file=sys.stderr)
    from merge_by_subgroup_final import merge_file as merge_file_direct
    merge_file = merge_file_direct
    print(f"[SUCCESS] Imported merge_file directly", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] Direct import failed: {type(e).__name__}: {e}", file=sys.stderr)
    
    # Method 2: Try using importlib with absolute path
    try:
        print(f"[DEBUG] Attempting importlib import...", file=sys.stderr)
        import importlib.util
        spec = importlib.util.spec_from_file_location("merge_by_subgroup_final", os.path.join(parent_dir, "merge_by_subgroup_final.py"))
        if spec and spec.loader:
            merge_module = importlib.util.module_from_spec(spec)
            sys.modules['merge_by_subgroup_final'] = merge_module
            spec.loader.exec_module(merge_module)
            merge_file = getattr(merge_module, 'merge_file', None)
            if merge_file:
                print(f"[SUCCESS] Imported merge_file via importlib", file=sys.stderr)
            else:
                print(f"[ERROR] merge_file not found in module", file=sys.stderr)
    except Exception as e2:
        print(f"[ERROR] importlib import also failed: {type(e2).__name__}: {e2}", file=sys.stderr)
        print(f"[ERROR] Full traceback:\n{traceback.format_exc()}", file=sys.stderr)
        merge_file = None

try:
    print(f"[DEBUG] Attempting to import process_dataframe...", file=sys.stderr)
    from process_excel import process_dataframe
    print(f"[SUCCESS] Imported process_dataframe", file=sys.stderr)
except Exception as e:
    print(f"[ERROR] Failed to import process_dataframe: {type(e).__name__}: {e}", file=sys.stderr)
    
    # Fallback: Try importlib
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("process_excel", os.path.join(parent_dir, "process_excel.py"))
        if spec and spec.loader:
            process_module = importlib.util.module_from_spec(spec)
            sys.modules['process_excel'] = process_module
            spec.loader.exec_module(process_module)
            process_dataframe = getattr(process_module, 'process_dataframe', None)
            if process_dataframe:
                print(f"[SUCCESS] Imported process_dataframe via importlib", file=sys.stderr)
    except Exception as e2:
        print(f"[ERROR] importlib also failed: {type(e2).__name__}", file=sys.stderr)
    
    process_dataframe = None

try:
    print(f"[DEBUG] Attempting to import populate_dashboard...", file=sys.stderr)
    from dashboard import populate_dashboard
    print(f"[SUCCESS] Imported populate_dashboard", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] populate_dashboard not available (optional): {type(e).__name__}", file=sys.stderr)
    populate_dashboard = None

st.set_page_config(
    page_title="AutoOptix - Home",
    layout="wide",
)

# Add logo to sidebar
with st.sidebar:
    st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{LOGO_BASE64_2}" alt="AutoOptix Logo" style="height: 150px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));"></div>', unsafe_allow_html=True)
    # st.markdown('---')

st.markdown("""
<style>
    /* Page transition and animation keyframes */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 2px 8px rgba(0, 102, 204, 0.1);
        }
        50% {
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
        }
    }
    
    /* Apply animations globally */
    .main {
        animation: fadeIn 0.6s ease-out;
    }
    
    [data-testid="stMarkdownContainer"] {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Smooth transitions for all elements */
    * {
        transition: all 0.3s ease;
    }
    
    button {
        transition: all 0.3s ease !important;
    }
    
    /* Professional styling for AutoOptix */
    .header-title {
        text-align: center;
        font-size: 42pt;
        font-weight: 900;
        background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: opaque;
        background-clip: text;
        margin-bottom: 10px;
        letter-spacing: -1px;
        animation: slideDown 0.6s ease-out;
    }
    
    .header-subtitle {
        text-align: center;
        font-size: 16pt;
        color: #666;
        margin-bottom: 30px;
        font-weight: 500;
        animation: fadeIn 0.7s ease-out 0.1s both;
    }
    
    .upload-section {
        background: white;
        padding: 30px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 102, 204, 0.1);
        border-top: 4px solid #0066cc;
        transition: all 0.3s ease;
        animation: slideInRight 0.5s ease-out;
    }
    
    .upload-section:hover {
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.15);
        border-top-color: #00a8e8;
        transform: translateY(-2px);
    }
    
    .upload-section h3 {
        color: #0066cc;
        margin-top: 0;
        font-weight: 600;
        animation: fadeIn 0.5s ease-out;
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.05) 0%, rgba(0, 168, 232, 0.05) 100%);
        padding: 20px;
        border-left: 4px solid #0066cc;
        margin-bottom: 15px;
        border-radius: 6px;
        font-size: 14px;
        line-height: 1.6;
        animation: slideInLeft 0.5s ease-out;
    }
    
    .step-header {
        font-size: 18px;
        font-weight: 600;
        color: #0066cc;
        margin: 20px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
        animation: slideInLeft 0.5s ease-out;
    }
    
    .activity-table-header {
        background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
        color: white;
        padding: 15px;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
        margin-top: 15px;
        animation: slideDown 0.5s ease-out;
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #0066cc, transparent);
        margin: 30px 0;
        animation: scaleIn 0.6s ease-out;
    }
    
    .validation-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        animation: scaleIn 0.4s ease-out;
    }
    
    .badge-valid {
        background-color: #d4edda;
        color: #155724;
    }
    
    .badge-invalid {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .badge-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    
    /* Process button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #004499 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 102, 204, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Alert styling with animations */
    .stAlert {
        animation: slideInLeft 0.4s ease-out;
        border-radius: 6px;
    }
    
    /* Table styling */
    .stDataFrame {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Column layouts */
    .stColumns {
        gap: 20px;
    }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        animation: scaleIn 0.5s ease-out;
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        box-shadow: 0 2px 4px rgba(0, 102, 204, 0.08);
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div style="text-align: center; margin-bottom: 0;"><img src="data:image/png;base64,{LOGO_BASE64}" alt="AutoOptix Logo" style="height: 240px;"></div>', unsafe_allow_html=True)
#st.markdown('<div class="header-subtitle" style="margin-bottom: 0;">Analyze tickets. Optimize operations. Forecast resources.</div>', unsafe_allow_html=True)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with st.expander("📌 **Required columns**: Ticket ID, Description, Assignment Group, Closed Month, Priority"):
    st.markdown(
        """
<div style="
  background:#eef6ff;
  border:1px solid #d8e4f0;
  border-radius:10px;
  padding:12px 14px;
  font-size:0.95rem;
">
  <ul style="margin:0 0 6px 22px;">
    <li>Headers must match exactly</li>
    <li>File format: <code>.xlsx</code></li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )



# Initialize session state with all necessary variables
if 'df_uploaded' not in st.session_state:
    st.session_state.df_uploaded = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'summary_data' not in st.session_state:
    st.session_state.summary_data = None
if 'merged_df' not in st.session_state:
    st.session_state.merged_df = None
if 'unmatched_df' not in st.session_state:
    st.session_state.unmatched_df = None
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'log_info' not in st.session_state:
    st.session_state.log_info = None

# Initialize non-ticketed data session variables
if 'has_non_ticketed' not in st.session_state:
    st.session_state.has_non_ticketed = None
if 'selected_range' not in st.session_state:
    st.session_state.selected_range = None
if 'selected_activities' not in st.session_state:
    st.session_state.selected_activities = {}
if 'total_non_ticketed_percent' not in st.session_state:
    st.session_state.total_non_ticketed_percent = 0
if 'show_warning' not in st.session_state:
    st.session_state.show_warning = False

# Fixed data mapping for activities
ACTIVITIES_DATA = {
    "Monitoring": {"default": 10, "feasibility": "Automation Feasible"},
    "Health Check": {"default": 5, "feasibility": "Elimination"},
    "Reporting": {"default": 5, "feasibility": "Automation Feasible"},
    "Coordination": {"default": 2, "feasibility": "Not Feasible"},
    "MIM / Defect mgmt / Release Mgmt Calls": {"default": 5, "feasibility": "Partial Automation"},
    "Others": {"default": 2, "feasibility": "Not Feasible"}
}

RANGE_OPTIONS = ["0%-5%", "5%-10%", "10%-20%", "20%-30%", "30%-50%", "50%-100%"]

def normalize_value(val):
    """Normalize a cell value for comparison."""
    if pd.isna(val):
        return None
    return str(val).strip().lower()

def find_column(df, search_terms):
    """Find a column by searching for any of the search terms (case-insensitive, trimmed)."""
    normalized_cols = {normalize_value(col): col for col in df.columns}
    search_terms_lower = [normalize_value(term) for term in search_terms]
    
    for term in search_terms_lower:
        if term in normalized_cols:
            return normalized_cols[term]
    return None

def get_range_limits(range_str):
    """Extract min and max from range string like '30%-50%'."""
    parts = range_str.replace('%', '').split('-')
    return int(parts[0]), int(parts[1])

def calculate_total_percentage():
    """Calculate total percentage from selected activities."""
    total = 0
    for activity_name, data in st.session_state.selected_activities.items():
        if data.get('checked', False):
            total += data.get('percentage', 0)
    return total

def validate_against_range(total_pct, range_str):
    """Check if total is within range limits."""
    min_pct, max_pct = get_range_limits(range_str)
    return total_pct <= max_pct

def toggle_activity_checkbox(activity_name):
    """Callback to handle checkbox toggle"""
    current_state = st.session_state.selected_activities[activity_name]['checked']
    st.session_state.selected_activities[activity_name]['checked'] = not current_state
    # When unchecking, reset percentage
    if current_state:  # was checked, now unchecking
        st.session_state.selected_activities[activity_name]['percentage'] = 0

def process_excel_file(df):
    """Process Excel file and generate optimization summary."""
    try:
        # If new merge/process APIs exist, prefer using them (but here df is already the uploaded sheet)
        if process_dataframe is not None:
            # process_dataframe expects merged/enriched DF. If the uploaded sheet is already merged, call directly.
            output = process_dataframe(df)
            return output, None

        # Find required columns (case-insensitive, trimmed search)
        col_l1l2 = find_column(df, ["L1/L2", "L1/l2"])
        if not col_l1l2:
            raise ValueError("Column 'L1/L2' not found")

        col_elim = find_column(df, ["Elimination"])
        if not col_elim:
            raise ValueError("Column 'Elimination' not found")

        col_usecase = find_column(df, ["Usecase", "Use Case"])
        if not col_usecase:
            raise ValueError("Column 'Usecase' not found")

        col_closed_month = find_column(df, ["Closed Month", "ClosedMonth"])
        if not col_closed_month:
            raise ValueError("Column 'Closed Month' not found")

        col_automation = find_column(df, ["Automation"])
        if not col_automation:
            raise ValueError("Column 'Automation' not found")

        col_std_agentic = find_column(df, ["Std/Agentic", "Std/agentic", "Standard/Agentic"])
        if not col_std_agentic:
            raise ValueError("Column 'Std/Agentic' not found")

        col_left_shift = find_column(df, ["Left Shift", "LeftShift", "left shift"])
        if not col_left_shift:
            raise ValueError("Column 'Left Shift' not found")

        # Get number of unique months
        unique_months = df[col_closed_month].dropna().unique()
        num_months = len(unique_months)
        
        if num_months == 0:
            raise ValueError("No valid months found in 'Closed Month' column")

        # Total counts for L1.5 and L2 (entire sheet)
        total_count_ofL1_5 = df[col_l1l2].apply(normalize_value).eq("l1.5").sum()
        total_count_ofL2 = df[col_l1l2].apply(normalize_value).eq("l2").sum()

        # ===== Elimination array =====
        elim_df = df[(df[col_elim].apply(normalize_value).eq("feasible")) & 
                     (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
        
        elim_usecases = int(elim_df[col_usecase].nunique())
        elim_ticket_volume = len(elim_df) / num_months if num_months > 0 else 0
        elim_fte = elim_ticket_volume / 140
        elimination_array = [elim_usecases, round(elim_ticket_volume, 4), round(elim_fte, 4)]

        # ===== Automation array =====
        auto_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & 
                     (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
        
        std_agentic_normalized = auto_df[col_std_agentic].apply(normalize_value)
        auto_std_df = auto_df[std_agentic_normalized.eq("standard") | std_agentic_normalized.eq("standard/agentic ai")]
        
        auto_usecases = int(auto_std_df[col_usecase].nunique())
        auto_ticket_volume = len(auto_std_df) / num_months if num_months > 0 else 0
        auto_fte = auto_ticket_volume / 140
        automation_array = [auto_usecases, round(auto_ticket_volume, 4), round(auto_fte, 4)]

        # ===== Automation agent array =====
        agentic_df = df[(df[col_automation].apply(normalize_value).eq("feasible")) & 
                        (df[col_std_agentic].apply(normalize_value).eq("agentic ai")) &
                        (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
        
        agentic_usecases = int(agentic_df[col_usecase].nunique())
        agentic_ticket_volume = len(agentic_df) / num_months if num_months > 0 else 0
        agentic_fte = agentic_ticket_volume / 140
        automation_agent_array = [agentic_usecases, round(agentic_ticket_volume, 4), round(agentic_fte, 4)]

        # ===== Left shift array =====
        left_df = df[(df[col_left_shift].apply(normalize_value).eq("feasible")) & 
                     (df[col_l1l2].apply(normalize_value).eq("l1.5"))]
        
        left_usecases = int(left_df[col_usecase].nunique())
        left_ticket_volume = len(left_df) / num_months if num_months > 0 else 0
        left_fte = left_ticket_volume / 140
        left_shift_array = [left_usecases, round(left_ticket_volume, 4), round(left_fte, 4)]

        # ===== Generate output JSON =====
        output = {
            "total_count_ofL1.5": int(total_count_ofL1_5),
            "total_count_ofL2": int(total_count_ofL2),
            "elimination_array": elimination_array,
            "automation_array": automation_array,
            "automation_agent_array": automation_agent_array,
            "left_shift_array": left_shift_array
        }

        # Save to file
        with open("summary_output.json", "w") as f:
            json.dump(output, f, indent=4)
        
        return output, None
    except Exception as e:
        return None, str(e)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="upload-section" style="padding:0;margin:0;"><h3>📁 Step 1: Upload Ticket Data</h3></div>', unsafe_allow_html=True)
    #st.markdown('### 📁 Step 1: Upload Ticket Data')
    


    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx, .xls)",
        type=["xlsx", "xls"],
        help="Upload your ticket data in Excel format. File should contain columns: L1/L2, Usecase, Closed Month, Elimination, Automation, Std/Agentic, Left Shift"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# with col2:
#     st.markdown('<div class="info-box">', unsafe_allow_html=True)
#     st.markdown("**✅ Required Columns:**")
#     st.markdown("- Ticket ID")
#     st.markdown("- Description")
#     st.markdown("- Assignment Group")
#     st.markdown("- Closed Month")
#     st.markdown("- Priority")
#     st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div class="info-box">
            <strong>✅ Required Columns:</strong>
            <ul>
                <li>Ticket ID</li>
                <li>Description</li>
                <li>Assignment Group</li>
                <li>Closed Month</li>
                <li>Priority</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

#st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

if uploaded_file is not None:
    st.markdown('### 📋 Step 2: Preview & Verify Data')
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        st.write(f"**Sheets Found:** {', '.join(excel_file.sheet_names)}")
        sheet_tabs = st.tabs(excel_file.sheet_names)
        sheet_data = {}
        for idx, sheet_name in enumerate(excel_file.sheet_names):
            with sheet_tabs[idx]:
                # read each sheet
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                sheet_data[sheet_name] = df
                # Show only first 10 rows for faster preview loading
                st.dataframe(df.head(10).reset_index(drop=True), use_container_width=True)
                st.caption(f"Showing first 10 rows of {len(df)} total rows")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        
        # NEW: Column Selection UI with sheet selector
        st.markdown('### 🔧 Step 2B: Map Columns to Required Fields')
        st.info("1. Select the sheet containing ticket data, 2. Map the 5 mandatory columns, 3. Click Proceed")
        
        # Get sheet names
        first_sheet = excel_file.sheet_names[0]
        
        # Initialize session state for sheet selection
        if 'selected_sheet_for_mapping' not in st.session_state:
            st.session_state.selected_sheet_for_mapping = first_sheet
        
        # Sheet selector if multiple sheets - use form to prevent rerun on selection
        if len(excel_file.sheet_names) > 1:
            with st.form("sheet_selection_form", border=False):
                selected_sheet = st.selectbox(
                    "Select Sheet",
                    excel_file.sheet_names,
                    index=excel_file.sheet_names.index(st.session_state.selected_sheet_for_mapping),
                    key="sheet_selector_unique"
                )
                sheet_submitted = st.form_submit_button("✓ Load Sheet", use_container_width=False)
            
            # Update only if sheet form submitted
            if sheet_submitted and selected_sheet != st.session_state.selected_sheet_for_mapping:
                st.session_state.selected_sheet_for_mapping = selected_sheet
                st.rerun()  # Rerun only when user explicitly submits
        else:
            selected_sheet = first_sheet
            st.session_state.selected_sheet_for_mapping = selected_sheet
            st.write(f"**Sheet Selected:** {selected_sheet}")
        
        # Get columns from selected sheet
        df_for_mapping = pd.read_excel(uploaded_file, sheet_name=st.session_state.selected_sheet_for_mapping)
        available_columns = list(df_for_mapping.columns)
        
        st.write(f"**Columns in '{st.session_state.selected_sheet_for_mapping}':** {len(available_columns)} columns")
        
        # Initialize session state for column mapping
        if 'column_mapping' not in st.session_state:
            st.session_state.column_mapping = {
                'ticket_id': None,
                'description': None,
                'assignment_group': None,
                'closed_month': None,
                'priority': None
            }
        
        # Use a form to prevent rerun on every selectbox change
        st.markdown("**Map the 5 mandatory columns:**")
        with st.form("column_mapping_form", border=False):
            col_map_cols = st.columns(2)
            
            with col_map_cols[0]:
                ticket_id_col = st.selectbox(
                    "🔹 Ticket ID Column",
                    [None] + available_columns,
                    index=0 if st.session_state.column_mapping['ticket_id'] is None else (available_columns.index(st.session_state.column_mapping['ticket_id']) + 1 if st.session_state.column_mapping['ticket_id'] in available_columns else 0),
                    key="ticket_id_col_form"
                )
                
                description_col = st.selectbox(
                    "🔹 Description Column",
                    [None] + available_columns,
                    index=0 if st.session_state.column_mapping['description'] is None else (available_columns.index(st.session_state.column_mapping['description']) + 1 if st.session_state.column_mapping['description'] in available_columns else 0),
                    key="description_col_form"
                )
                
                assignment_group_col = st.selectbox(
                    "🔹 Assignment Group Column",
                    [None] + available_columns,
                    index=0 if st.session_state.column_mapping['assignment_group'] is None else (available_columns.index(st.session_state.column_mapping['assignment_group']) + 1 if st.session_state.column_mapping['assignment_group'] in available_columns else 0),
                    key="assignment_group_col_form"
                )
            
            with col_map_cols[1]:
                closed_month_col = st.selectbox(
                    "🔹 Date/Closed Month Column",
                    [None] + available_columns,
                    index=0 if st.session_state.column_mapping['closed_month'] is None else (available_columns.index(st.session_state.column_mapping['closed_month']) + 1 if st.session_state.column_mapping['closed_month'] in available_columns else 0),
                    key="closed_month_col_form"
                )
                
                priority_col = st.selectbox(
                    "🔹 Priority Column",
                    [None] + available_columns,
                    index=0 if st.session_state.column_mapping['priority'] is None else (available_columns.index(st.session_state.column_mapping['priority']) + 1 if st.session_state.column_mapping['priority'] in available_columns else 0),
                    key="priority_col_form"
                )
            
            # Submit button - only rerun when user clicks this
            form_submitted = st.form_submit_button("✓ Confirm Column Mapping", use_container_width=True)
        
        # Update session state only when form is submitted
        if form_submitted:
            st.session_state.column_mapping['ticket_id'] = ticket_id_col
            st.session_state.column_mapping['description'] = description_col
            st.session_state.column_mapping['assignment_group'] = assignment_group_col
            st.session_state.column_mapping['closed_month'] = closed_month_col
            st.session_state.column_mapping['priority'] = priority_col
            st.session_state.ready_to_process = True
            st.rerun()
        
        # Validate mappings and show status
        mapped_columns = [v for v in st.session_state.column_mapping.values() if v is not None]
        all_mapped = all(st.session_state.column_mapping.values())
        
        if all_mapped:
            st.success("✅ All 5 columns mapped successfully!")
        else:
            st.warning(f"⚠️ {len(mapped_columns)}/5 columns selected. Select all 5 mandatory columns.")
        
        # persist
        st.session_state.df_uploaded = sheet_data
        st.session_state.file_name = uploaded_file.name
        file_display_name = uploaded_file.name
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.session_state.df_uploaded = None
else:
    # No fresh upload — check session_state for previous upload
    if 'df_uploaded' in st.session_state and st.session_state.df_uploaded:
        sheet_data = st.session_state.df_uploaded
        file_display_name = st.session_state.get('file_name', None)
        st.markdown('### 📋 Step 2: Preview & Verify Data (Loaded)')
        try:
            sheet_names = list(sheet_data.keys())
            st.write(f"**Sheets Found:** {', '.join(sheet_names)}")
            sheet_tabs = st.tabs(sheet_names)
            for idx, sheet_name in enumerate(sheet_names):
                with sheet_tabs[idx]:
                    df = sheet_data[sheet_name]
                    # Show only first 10 rows for faster preview loading
                    st.dataframe(df.head(10).reset_index(drop=True), use_container_width=True)
                    st.caption(f"Showing first 10 rows of {len(df)} total rows")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", len(df))
                    with col2:
                        st.metric("Columns", len(df.columns))
                    with col3:
                        st.metric("Status", "✅ Ready")
        except Exception as e:
            st.error(f"❌ Error displaying stored file: {e}")
            st.session_state.df_uploaded = None
            sheet_data = None

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# NON-TICKETED DATA SECTION
st.markdown('### 🎯 Step 3: Non-Ticketed Activities Configuration')
st.markdown("*Optional: Configure non-ticketed effort allocation (e.g., meetings, ad-hoc work)*")

# Step 1: Ask if user has non-ticketed data
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("**Do you have non-ticketed data to account for?**")
    col_yes, col_no = st.columns(2)
    
    with col_yes:
        if st.button("✅ YES", key="has_non_ticketed_yes", use_container_width=True):
            st.session_state.has_non_ticketed = True
            st.rerun()
    
    with col_no:
        if st.button("❌ NO", key="has_non_ticketed_no", use_container_width=True):
            st.session_state.has_non_ticketed = False
            # Clear non-ticketed data
            st.session_state.selected_range = None
            st.session_state.selected_activities = {}
            st.session_state.total_non_ticketed_percent = 0
            st.session_state.show_warning = False
            st.rerun()

# If user selected YES, show range selection
if st.session_state.has_non_ticketed:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Step 1: Select range first
    st.markdown('<div class="step-header">📊 Step 1: Select Non-Ticketed Effort Range</div>', unsafe_allow_html=True)
    st.write("**Select the range that best represents your non-ticketed efforts:**")
    
    selected_range = st.selectbox(
        "Choose range:",
        options=RANGE_OPTIONS,
        key="range_selectbox",
        label_visibility="collapsed"
    )
    st.session_state.selected_range = selected_range
    
    if selected_range:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Step 2: Select from 5 categories
        st.markdown('<div class="step-header">📋 Step 2: Distribute Across 5 Categories</div>', unsafe_allow_html=True)
        st.write(f"**For the range {selected_range}, distribute the effort across these categories:**")
        
        min_val, max_val = get_range_limits(selected_range)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        # Select top 5 activities (excluding "Others" initially)
        activities_list = [act for act in ACTIVITIES_DATA.keys() if act != "Others"][:5]
        
        total_entered = 0
        for idx, activity in enumerate(activities_list):
            col = [col1, col2, col3][idx % 3]
            with col:
                percentage = st.number_input(
                    f"{activity}",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.selected_activities.get(activity, {}).get('percentage', 0),
                    step=1,
                    key=f"activity_{activity}"
                )
                st.session_state.selected_activities[activity] = {
                    'percentage': percentage,
                    'feasibility': ACTIVITIES_DATA[activity]['feasibility']
                }
                total_entered += percentage
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Step 3: Show total and validation
        st.markdown('<div class="step-header">📈 Step 3: Review Total</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.metric("Range", selected_range)
        with col2:
            st.metric("Total Entered %", f"{total_entered}%")
        
        # Validation
        if min_val <= total_entered <= max_val:
            st.success(f"✅ Total {total_entered}% is within range {selected_range}")
            st.session_state.total_non_ticketed_percent = total_entered
            st.session_state.non_ticketed_step_complete = True
        elif total_entered == 0:
            st.warning("⚠️ Please enter values for the categories")
        else:
            st.error(f"❌ Total {total_entered}% is outside range {selected_range}. Please adjust values.")
        
        # Display details
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        if total_entered > 0:
            if total_entered <= 15:
                st.markdown(f"""
                <div style="background:#e8f5e9; border-left:6px solid #4caf50; padding:14px; border-radius:6px; font-weight:600; color:#2e7d32; margin-top:12px;">
                    ✅ <strong>Included in RL:</strong> The entered {total_entered}% is within the baseline 0-15% that is already factored into Resource Load calculations.
                </div>
                """, unsafe_allow_html=True)
            else:
                excess_pct = total_entered - 15
                st.markdown(f"""
                <div style="background:#fff3e0; border-left:6px solid #ff8800; padding:14px; border-radius:6px; font-weight:600; color:#e65100; margin-top:12px;">
                    ⚠️ <strong>Excess Non-Ticketed Work:</strong> Out of {total_entered}%, we've included 15% in baseline RL. The additional {excess_pct}% will be added to H1Y1 RL in the dashboard.
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.has_non_ticketed is False:
    st.info("ℹ️ Proceeding without non-ticketed data. Skip to main dashboard section.")

# Add flag to track if non-ticketed step is complete
if 'non_ticketed_step_complete' not in st.session_state:
    st.session_state.non_ticketed_step_complete = False

# Mark step complete when user says NO
if st.session_state.has_non_ticketed is False:
    st.session_state.non_ticketed_step_complete = True

# Mark step complete when user submits non-ticketed data successfully
# (this happens inside the submit button callback above)

st.markdown("---")

# ===== PROCESS & GO TO DASHBOARD BUTTON (placed here, after non-ticketed section) =====
st.markdown('### ✅ Step 4: Process Data')

# Determine if button should be enabled
has_uploaded = (uploaded_file is not None) or ('df_uploaded' in st.session_state and st.session_state.df_uploaded)
is_non_ticketed_complete = st.session_state.get('non_ticketed_step_complete', False)
is_column_mapping_complete = st.session_state.get('ready_to_process', False)

# Button is enabled if: column mapping done AND (non-ticketed step is complete OR user never entered non-ticketed)
button_enabled = is_column_mapping_complete and (is_non_ticketed_complete or st.session_state.has_non_ticketed is None)

# Show button
if st.button("✅ Process & Go to Dashboard", key="process_btn_main", use_container_width=True, disabled=not button_enabled):
    if not button_enabled:
        st.error("Please complete column mapping and non-ticketed configuration first.")
    else:
        # Create progress container
        progress_container = st.container()
        status_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            progress_text = st.empty()
        
        try:
            # ===== PHASE 1: DATA LOADING & VALIDATION (0-20%) =====
            progress_text.text("🔄 Phase 1: Loading and validating data... (0%)")
            progress_bar.progress(0)
            
            if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
                df_to_process = st.session_state.merged_df
            elif 'df_uploaded' in st.session_state and st.session_state.df_uploaded:
                sheet_names = list(st.session_state.df_uploaded.keys())
                df_to_process = st.session_state.df_uploaded[sheet_names[0]].copy()
            else:
                try:
                    excel_file = pd.ExcelFile(uploaded_file)
                    df_to_process = pd.read_excel(uploaded_file, sheet_name=excel_file.sheet_names[0])
                except Exception as e:
                    st.error(f"❌ Unable to find data to process: {e}")
                    df_to_process = None

            if df_to_process is None:
                st.stop()
            
            # ===== APPLY COLUMN MAPPING & DATE CONVERSION =====
            # If user has selected column mappings, rename columns
            if 'column_mapping' in st.session_state and st.session_state.column_mapping:
                col_mapping = st.session_state.column_mapping
                rename_dict = {}
                
                # Create rename mapping (old_col -> new_col)
                if col_mapping.get('ticket_id'):
                    rename_dict[col_mapping['ticket_id']] = 'Ticket ID'
                if col_mapping.get('description'):
                    rename_dict[col_mapping['description']] = 'Description'
                if col_mapping.get('assignment_group'):
                    rename_dict[col_mapping['assignment_group']] = 'Assignment Group'
                if col_mapping.get('closed_month'):
                    rename_dict[col_mapping['closed_month']] = 'Closed Month'
                if col_mapping.get('priority'):
                    rename_dict[col_mapping['priority']] = 'Priority'
                
                # Rename columns
                if rename_dict:
                    df_to_process = df_to_process.rename(columns=rename_dict)
                    
                    # Convert date column to mmm-yyyy format
                    if 'Closed Month' in df_to_process.columns:
                        from process_excel import convert_to_mmm_yyyy
                        df_to_process['Closed Month'] = df_to_process['Closed Month'].apply(convert_to_mmm_yyyy)

            progress_text.text("✓ Data loaded successfully (20%)")
            progress_bar.progress(20)
            
            # ===== PHASE 2: INITIAL CHECKS (20-35%) =====
            progress_text.text("🔍 Phase 2: Running initial validation checks... (20%)")
            progress_bar.progress(25)
            
            # Validate required columns exist
            required_cols = ['Description']
            for col in required_cols:
                if col not in df_to_process.columns:
                    st.error(f"❌ Required column '{col}' not found. Please check column mapping.")
                    st.stop()
            
            progress_bar.progress(35)
            progress_text.text("✓ Initial validation complete (35%)")
            
            
            # ===== PHASE 3: ULTRA-FAST KEYWORD MATCHING WITH RAPIDFUZZ (35-80%) =====
            progress_text.text("⚡ Phase 3: RAPIDFUZZ KEYWORD MATCHING - Ultra-fast C++ optimized engine... (35%)")
            progress_bar.progress(40)
            
            # Always try to do keyword matching
            if 'merged_df' not in st.session_state or st.session_state.merged_df is None:
                total_rows = len(df_to_process)
                
                progress_text.text("🚀 RAPIDFUZZ MATCHING IN PROGRESS: Using C++ optimized fuzzy matching with 32 parallel workers...\nThis will complete in 30-60 seconds. Please wait... (45%)")
                progress_bar.progress(45)
                
                import sys
                print(f"[DEBUG] Starting keyword matching with {total_rows} rows", file=sys.stderr)
                
                try:
                    if merge_file is None:
                        raise RuntimeError("merge_file function not imported")
                    
                    print(f"[DEBUG] Calling merge_file function", file=sys.stderr)
                    result = merge_file(df_to_process, source_filename=st.session_state.get('file_name'))
                    
                    if result is None or len(result) != 3:
                        raise ValueError(f"merge_file returned unexpected result: {type(result)}")
                    
                    merged_df_local, unmatched_df_local, log_info_local = result
                    
                    print(f"[DEBUG] merge_file success. merged_df shape: {merged_df_local.shape if hasattr(merged_df_local, 'shape') else 'N/A'}", file=sys.stderr)
                    
                    # Store in session state immediately
                    st.session_state.merged_df = merged_df_local
                    st.session_state.unmatched_df = unmatched_df_local if unmatched_df_local is not None else pd.DataFrame()
                    st.session_state.log_info = log_info_local if log_info_local is not None else {}
                    
                    print(f"[DEBUG] Session state updated successfully", file=sys.stderr)
                    
                    # Get matched count
                    matched_count = len(merged_df_local) if hasattr(merged_df_local, '__len__') else 0
                    
                    progress_bar.progress(75)
                    progress_text.text(f"✓ RAPIDFUZZ MATCHING COMPLETE!\n  - Total Records Processed: {total_rows}\n  - Records Matched: {matched_count} (75%)")
                    time.sleep(0.5)
                    
                    progress_bar.progress(80)
                    progress_text.text("✓ All keyword matching complete - Ready for calculations (80%)")
                    
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"[ERROR] Keyword matching failed:\n{error_trace}", file=sys.stderr)
                    
                    # Show error to user
                    st.error(f"❌ Keyword matching error: {str(e)}")
                    with st.expander("📋 Error Details"):
                        st.code(error_trace)
                    st.stop()
            
            # Verify merged_df exists before proceeding
            if 'merged_df' not in st.session_state or st.session_state.merged_df is None:
                st.error("❌ Critical: merged_df not found in session state after keyword matching")
                st.stop()
            
            # ===== PHASE 4: CALCULATIONS (80-95%) =====
            progress_text.text("⚙️ Phase 4: Running calculations... (80%)")
            progress_bar.progress(85)
            
            try:
                # Double-check we have merged_df
                if 'merged_df' not in st.session_state:
                    raise ValueError("Session state missing 'merged_df'")
                
                if st.session_state.merged_df is None:
                    raise ValueError("merged_df is None")
                
                merged_data = st.session_state.merged_df
                
                import sys
                print(f"[DEBUG] Starting calculations with merged_df shape: {merged_data.shape}", file=sys.stderr)
                
                # Run process_dataframe
                results_df_local = process_dataframe(merged_data)
                
                print(f"[DEBUG] process_dataframe returned shape: {results_df_local.shape if hasattr(results_df_local, 'shape') else 'N/A'}", file=sys.stderr)
                
                st.session_state.results_df = results_df_local
                st.session_state.processed = True
                
                progress_bar.progress(95)
                progress_text.text("✓ Calculations complete (95%)")
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"[ERROR] Calculations failed:\n{error_trace}", file=sys.stderr)
                
                st.error(f"❌ Error during calculations: {str(e)}")
                with st.expander("📋 Error Details"):
                    st.code(error_trace)
                st.stop()
            
            # ===== PHASE 5: FINALIZATION (95-100%) =====
            progress_text.text("🎯 Phase 5: Finalizing data... (95%)")
            progress_bar.progress(98)
            
            # Verify session state is set
            import sys
            print(f"[DEBUG] Session state processed flag: {st.session_state.get('processed', False)}", file=sys.stderr)
            print(f"[DEBUG] Session state has results_df: {'results_df' in st.session_state}", file=sys.stderr)
            print(f"[DEBUG] Session state has merged_df: {'merged_df' in st.session_state}", file=sys.stderr)
            
            progress_bar.progress(100)
            progress_text.text("✅ Processing complete! (100%)")
            
            # Clear progress after completion
            import time
            time.sleep(1)
            progress_container.empty()
            
            with status_container:
                st.success("✅ All processing complete! Preparing to navigate to Dashboard...")
                st.info("📊 Your data is ready. You will be redirected to the Dashboard.")
                time.sleep(2)
                st.rerun()
                
        except Exception as e:
            progress_container.empty()
            st.error(f"❌ Error during processing: {e}")
            import sys
            print(f"[ERROR] Top-level exception: {traceback.format_exc()}", file=sys.stderr)
            st.exception(traceback.format_exc())

if not button_enabled:
    if not has_uploaded:
        st.info("💡 Upload a file to proceed.")
    elif st.session_state.has_non_ticketed is True and not is_non_ticketed_complete:
        st.warning("⚠️ Please complete the non-ticketed activities configuration above (select activities and click 'Submit Non-Ticketed Data').")

# Display status — show persisted info even when `uploaded_file` is None
st.markdown("---")
if 'file_name' in st.session_state and st.session_state.file_name:
    st.success(f"✓ File loaded: **{st.session_state.file_name}**")
elif uploaded_file is not None:
    st.success(f"✓ File loaded: **{uploaded_file.name}**")

if 'processed' in st.session_state and st.session_state.processed:
    st.info("✓ Ready to view dashboard. Use the sidebar to navigate to Dashboard page.")

# Persistent outputs: if processing has been done earlier, keep download buttons and summary visible
if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
    st.markdown("---")
    st.subheader("📥 Download Results")
    st.info("📊 **Download your optimization output** - L1.5 data (Sheets 1-2) and complete merged dataset (Sheet 3).")
    
    merged_df = st.session_state.merged_df
    unmatched_df = st.session_state.unmatched_df
    results_df = st.session_state.results_df

    try:
        buf_all = io.BytesIO()
        with pd.ExcelWriter(buf_all, engine='openpyxl') as writer:
            # Sheet 1: L1.5 Summary (Filtered Results)
            if results_df is not None and len(results_df) > 0:
                l1_5_summary = results_df[results_df.get('L1_L2', '') == 'L1.5'].copy() if 'L1_L2' in results_df.columns else results_df.copy()
                l1_5_summary.to_excel(writer, index=False, sheet_name='L1.5 Summary')
            
            # Sheet 2: Merged Data (L1.5 Only)
            if merged_df is not None and len(merged_df) > 0:
                l1_5_merged = merged_df[merged_df.get('L1_L2', '') == 'L1.5'].copy() if 'L1_L2' in merged_df.columns else merged_df.copy()
                l1_5_merged.to_excel(writer, index=False, sheet_name='L1.5 Merged Data')
            
            # Sheet 3: All Merged Data (Complete)
            if merged_df is not None:
                merged_df.to_excel(writer, index=False, sheet_name='All Merged Data')
        
        buf_all.seek(0)
        st.download_button(
            "⬇️ Download Results (L1.5 + All Data)",
            data=buf_all.getvalue(),
            file_name='Results_L1.5_Complete.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key="download-all-results-btn",
            use_container_width=True
        )
    except Exception as e:
        st.warning(f"Could not prepare download: {e}")
    
    # if st.button("⬇️ Download Complete Results (All Sheets)", use_container_width=True, key="download_all_results"):
    #     try:
    #         buf_all = io.BytesIO()
    #         with pd.ExcelWriter(buf_all, engine='openpyxl') as writer:
    #             # Sheet 1: Merged Data (Enriched Data)
    #             if merged_df is not None:
    #                 merged_df.to_excel(writer, index=False, sheet_name='Enriched Data')
                
    #             # Sheet 2: Optimization Summary (from summary_output.json)
    #             if os.path.exists("summary_output.json"):
    #                 try:
    #                     with open("summary_output.json", "r") as f:
    #                         summary_data = json.load(f)
                        
    #                     summary_df = pd.DataFrame({
    #                         "Lever": ["Elimination", "Automation", "Automation-Agentic AI", "Left Shift"],
    #                         "# of Usecases": [
    #                             summary_data.get("elimination_array", [0, 0, 0])[0],
    #                             summary_data.get("automation_array", [0, 0, 0])[0],
    #                             summary_data.get("automation_agent_array", [0, 0, 0])[0],
    #                             summary_data.get("left_shift_array", [0, 0, 0])[0]
    #                         ],
    #                         "Ticket Volume": [
    #                             summary_data.get('elimination_array', [0, 0, 0])[1],
    #                             summary_data.get('automation_array', [0, 0, 0])[1],
    #                             summary_data.get('automation_agent_array', [0, 0, 0])[1],
    #                             summary_data.get('left_shift_array', [0, 0, 0])[1]
    #                         ],
    #                         "FTE": [
    #                             summary_data.get('elimination_array', [0, 0, 0])[2],
    #                             summary_data.get('automation_array', [0, 0, 0])[2],
    #                             summary_data.get('automation_agent_array', [0, 0, 0])[2],
    #                             summary_data.get('left_shift_array', [0, 0, 0])[2]
    #                         ]
    #                     })
    #                     summary_df.to_excel(writer, index=False, sheet_name='Optimization Summary')
    #                 except Exception as e:
    #                     st.warning(f"Could not add Optimization Summary sheet: {e}")
                
    #             # Sheet 3: Non-Ticketed Activities (if data exists)
    #             if (st.session_state.has_non_ticketed and 
    #                 st.session_state.selected_activities and
    #                 any(data.get('checked', False) for data in st.session_state.selected_activities.values())):
                    
    #                 non_ticketed_list = []
    #                 total_non_ticketed = 0
                    
    #                 for activity_name, activity_data in st.session_state.selected_activities.items():
    #                     if activity_data.get('checked', False):
    #                         percentage = activity_data.get('percentage', 0)
    #                         feasibility_mapping = {
    #                             "Monitoring": "Automation Feasible",
    #                             "Health Check": "Elimination",
    #                             "Reporting": "Automation Feasible",
    #                             "Coordination": "Not Feasible",
    #                             "MIM / Defect mgmt / Release Mgmt Calls": "Partial Automation",
    #                             "Others": "Not Feasible"
    #                         }
    #                         feasibility = feasibility_mapping.get(activity_name, "Not Feasible")
                            
    #                         non_ticketed_list.append({
    #                             "Activity Type": activity_name,
    #                             "% Allocation": percentage,
    #                             "Automation Feasibility": feasibility,
    #                             "Range Selected": st.session_state.selected_range or "",
    #                             "Total %": ""
    #                         })
    #                         total_non_ticketed += percentage
                    
    #                 # Add total row
    #                 if non_ticketed_list:
    #                     non_ticketed_df = pd.DataFrame(non_ticketed_list)
    #                     # Update Total % for first row
    #                     if len(non_ticketed_df) > 0:
    #                         non_ticketed_df.loc[0, "Total %"] = total_non_ticketed
                        
    #                     non_ticketed_df.to_excel(writer, index=False, sheet_name='Non-Ticketed Activities')
            
    #         buf_all.seek(0)
    #         st.download_button(
    #             "⬇️ Download All Results",
    #             data=buf_all.getvalue(),
    #             file_name='Complete_Results.xlsx',
    #             mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #             key="download-all-results-btn"
    #         )
    #         st.success("✅ File ready for download!")
    #     except Exception as e:
    #         st.error(f"❌ Error preparing complete results: {e}")
    
    # Prepare the buffer before rendering the download button
    buf_all = io.BytesIO()
    with pd.ExcelWriter(buf_all, engine='openpyxl') as writer:
        # Sheet 1: Merged Data (Enriched Data)
        if merged_df is not None:
            merged_df.to_excel(writer, index=False, sheet_name='Enriched Data')
        # Sheet 2: Optimization Summary (from summary_output.json)
        if os.path.exists("summary_output.json"):
            try:
                with open("summary_output.json", "r") as f:
                    summary_data = json.load(f)
                summary_df = pd.DataFrame({
                    "Lever": ["Elimination", "Automation", "Automation-Agentic AI", "Left Shift"],
                    "# of Usecases": [
                        summary_data.get("elimination_array", [0, 0, 0])[0],
                        summary_data.get("automation_array", [0, 0, 0])[0],
                        summary_data.get("automation_agent_array", [0, 0, 0])[0],
                        summary_data.get("left_shift_array", [0, 0, 0])[0]
                    ],
                    "Ticket Volume": [
                        summary_data.get('elimination_array', [0, 0, 0])[1],
                        summary_data.get('automation_array', [0, 0, 0])[1],
                        summary_data.get('automation_agent_array', [0, 0, 0])[1],
                        summary_data.get('left_shift_array', [0, 0, 0])[1]
                    ],
                    "FTE": [
                        summary_data.get('elimination_array', [0, 0, 0])[2],
                        summary_data.get('automation_array', [0, 0, 0])[2],
                        summary_data.get('automation_agent_array', [0, 0, 0])[2],
                        summary_data.get('left_shift_array', [0, 0, 0])[2]
                    ]
                })
                summary_df.to_excel(writer, index=False, sheet_name='Optimization Summary')
            except Exception as e:
                st.warning(f"Could not add Optimization Summary sheet: {e}")
        # Sheet 3: Non-Ticketed Activities (if data exists)
        if (st.session_state.has_non_ticketed and 
            st.session_state.selected_activities and
            any(data.get('checked', False) for data in st.session_state.selected_activities.values())):
            non_ticketed_list = []
            total_non_ticketed = 0
            for activity_name, activity_data in st.session_state.selected_activities.items():
                if activity_data.get('checked', False):
                    percentage = activity_data.get('percentage', 0)
                    feasibility_mapping = {
                        "Monitoring": "Automation Feasible",
                        "Health Check": "Elimination",
                        "Reporting": "Automation Feasible",
                        "Coordination": "Not Feasible",
                        "MIM / Defect mgmt / Release Mgmt Calls": "Partial Automation",
                        "Others": "Not Feasible"
                    }
                    feasibility = feasibility_mapping.get(activity_name, "Not Feasible")
                    non_ticketed_list.append({
                        "Activity Type": activity_name,
                        "% Allocation": percentage,
                        "Automation Feasibility": feasibility,
                        "Range Selected": st.session_state.selected_range or "",
                        "Total %": ""
                    })
                    total_non_ticketed += percentage
            # Add total row
            if non_ticketed_list:
                non_ticketed_df = pd.DataFrame(non_ticketed_list)
                # Update Total % for first row
                if len(non_ticketed_df) > 0:
                    non_ticketed_df.loc[0, "Total %"] = total_non_ticketed
                non_ticketed_df.to_excel(writer, index=False, sheet_name='Non-Ticketed Activities')
    buf_all.seek(0)
    # st.download_button(
    #     "⬇️ Download Complete Results (All Sheets)",
    #     data=buf_all.getvalue(),
    #     file_name='Complete_Results.xlsx',
    #     mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #     use_container_width=True,
    #     key="download_all_results"
    # )
    # st.success("✅ File ready for download!")


# Instructions section
# st.markdown("---")
st.subheader("📖 Instructions")

with st.expander("How to Use", expanded=False):
    st.markdown("""
    1. **Upload File**: Click the upload button above and select your Excel file
    2. **Configure Non-Ticketed Data**: Answer if you have non-ticketed activities
    3. **Select Activities**: If YES, select range and activities with custom percentages
    4. **Process**: Click the "Process & Go to Dashboard" button
    5. **View Dashboard**: Navigate to the Dashboard page using the sidebar
    6. **Download Results**: Use "Download All Results" to get a complete Excel file with:
       - Sheet 1: Enriched Data (processed ticket data)
       - Sheet 2: Optimization Summary (levers analysis)
       - Sheet 3: Non-Ticketed Activities (if configured)
    
    ### Expected Excel Format:
    - Sheet 1: Main data with columns matching dashboard fields
    - Ensure headers are in the first row
    - Data should be structured and clean
    """)
