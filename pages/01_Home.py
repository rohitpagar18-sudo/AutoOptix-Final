import streamlit as st
import pandas as pd
import io
import json
from pathlib import Path
import traceback
import os
import base64

# Logo configuration
LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'logo2.png')
LOGO_PATH1 = os.path.join(os.path.dirname(__file__), '..', 'logo3.png')
# Function to convert image to base64
def get_image_as_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode()

# Convert logo to base64
LOGO_BASE64 = get_image_as_base64(LOGO_PATH)
LOGO_BASE65 = get_image_as_base64(LOGO_PATH1)

# Try importing the new APIs if present
try:
    from merge_by_subgroup_final import merge_file
except Exception:
    merge_file = None

try:
    from process_excel import process_dataframe
except Exception:
    process_dataframe = None

try:
    from dashboard import populate_dashboard
except Exception:
    populate_dashboard = None

st.set_page_config(
    page_title="AutoOptix - Home",
    layout="wide",
)

# Add logo to sidebar
with st.sidebar:
    st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{LOGO_BASE65}" alt="AutoOptix Logo" style="height: 150px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));"></div>', unsafe_allow_html=True)
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
                st.dataframe(df.reset_index(drop=True), use_container_width=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
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
                    st.dataframe(df.reset_index(drop=True), use_container_width=True)

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

# Button is enabled if: has_uploaded AND (non-ticketed step is complete OR user never entered non-ticketed)
button_enabled = has_uploaded and (is_non_ticketed_complete or st.session_state.has_non_ticketed is None)

# Show button
if st.button("✅ Process & Go to Dashboard", key="process_btn_main", use_container_width=True, disabled=not button_enabled):
    if not button_enabled:
        st.error("Please complete non-ticketed configuration first (or select 'NO').")
    else:
        # Choose data to process
        try:
            if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
                df_to_process = st.session_state.merged_df
            elif 'df_uploaded' in st.session_state and st.session_state.df_uploaded:
                sheet_names = list(st.session_state.df_uploaded.keys())
                df_to_process = st.session_state.df_uploaded[sheet_names[0]]
            else:
                try:
                    excel_file = pd.ExcelFile(uploaded_file)
                    df_to_process = pd.read_excel(uploaded_file, sheet_name=excel_file.sheet_names[0])
                except Exception as e:
                    st.error(f"❌ Unable to find data to process: {e}")
                    df_to_process = None

            if df_to_process is None:
                st.stop()

            # If merge API is available and we don't have merged_df yet, attempt merge
            if merge_file is not None and ('merged_df' not in st.session_state or st.session_state.merged_df is None):
                with st.spinner("Matching records using lookup keywords..."):
                    merged_df_local, unmatched_df_local, log_info_local = merge_file(df_to_process, source_filename=st.session_state.get('file_name'))
                st.session_state.merged_df = merged_df_local
                st.session_state.unmatched_df = unmatched_df_local
                st.session_state.log_info = log_info_local

            # Run calculations (preferred API, otherwise fallback)
            if process_dataframe is not None:
                with st.spinner("Running calculations..."):
                    results_df_local = process_dataframe(st.session_state.merged_df if 'merged_df' in st.session_state and st.session_state.merged_df is not None else df_to_process)
                st.session_state.results_df = results_df_local
                st.session_state.processed = True
                st.success("✓ Calculations complete")
            else:
                output, error = process_excel_file(st.session_state.merged_df if 'merged_df' in st.session_state and st.session_state.merged_df is not None else df_to_process)
                if error:
                    st.error(f"❌ Processing Error: {error}")
                else:
                    st.session_state.processed = True
                    st.session_state.summary_data = output
                    st.success("✓ File processed successfully (fallback)!")
        except Exception as e:
            st.error(f"❌ Error during processing: {e}")
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
    st.subheader("📥 Download All Results")
    st.info("📊 **Download your optimization output files** containing merged enriched data, unmatched records, and analysis results.")
    
    merged_df = st.session_state.merged_df
    unmatched_df = st.session_state.unmatched_df
    results_df = st.session_state.results_df

    try:
        buf_all = io.BytesIO()
        with pd.ExcelWriter(buf_all, engine='openpyxl') as writer:
            # Sheet 1: Merged Data
            if merged_df is not None:
                merged_df.to_excel(writer, index=False, sheet_name='Output Result')
            
            # Sheet 2: Unmatched Data
            if unmatched_df is not None:
                unmatched_df.to_excel(writer, index=False, sheet_name='Unmatched')
            
            # Sheet 3: Results Data
            if results_df is not None:
                results_df.to_excel(writer, index=False, sheet_name='Calculated Output')
        
        buf_all.seek(0)
        st.download_button(
            "⬇️ Download All Results",
            data=buf_all.getvalue(),
            file_name='Complete_Results.xlsx',
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
