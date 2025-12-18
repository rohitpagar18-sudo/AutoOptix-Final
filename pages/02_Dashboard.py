import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import pandas as pd
import threading
import json
import os
import base64
import plotly.graph_objects as go

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
_lock = threading.Lock()

# Constants for colors and fonts
TEAL_START = "#2E8CA8"
TEAL_END = "#1F6C86"
TEAL = "#2E8CA8"
LIGHT_TEAL = "#BFE2EA"
GRID_LINE_COLOR = "#D9D9D9"
FONT_FAMILY = "Segoe UI, Calibri, sans-serif"
PRIMARY_COLOR = "#0066cc"
SECONDARY_COLOR = "#00a8e8"
ACCENT_COLOR = "#00d9ff"
SUCCESS_COLOR = "#00b894"
WARNING_COLOR = "#fdcb6e"

st.set_page_config(
    page_title="📈 Dashboard - Analytics",
    layout="wide",
)

# Add logo to sidebar
with st.sidebar:
    st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{LOGO_BASE65}" alt="AutoOptix Logo" style="height: 150px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));"></div>', unsafe_allow_html=True)
    # st.markdown('---')

# Add page styling with modern 3D table design
st.markdown("""
<style>
    /* Clean, Professional Background */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #f5f7fa 100%);
    }
    
    /* Remove extra padding and margins from main container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Smooth transitions for interactive elements */
    button {
        transition: all 0.3s ease !important;
    }
    
    /* Modern 3D Table Design */
    [data-testid="stDataFrame"] {
        background-color: transparent !important;
    }
    
    /* Main table wrapper with 3D effect */
    [data-testid="stDataFrame"] > div {
        background: #ffffff !important;
        border-radius: 12px;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(46, 140, 168, 0.1);
        overflow: hidden;
        padding: 2px;
    }
    
    /* Table element */
    [data-testid="stDataFrame"] table {
        background-color: #ffffff;
        border-collapse: separate !important;
        border-spacing: 0;
        width: 100%;
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Header row - 3D gradient effect */
    [data-testid="stDataFrame"] table thead tr {
        background: linear-gradient(135deg, #2E8CA8 0%, #1F6C86 100%);
        box-shadow: 0 4px 12px rgba(46, 140, 168, 0.25), inset 0 1px 0 rgba(255,255,255,0.2);
    }
    
    /* Header cells - Modern styling */
    [data-testid="stDataFrame"] table thead th {
        color: white !important;
        font-weight: 700 !important;
        padding: 16px 18px !important;
        text-align: center !important;
        letter-spacing: 0.4px;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        background: transparent !important;
        font-size: 12px !important;
        text-transform: uppercase;
        box-shadow: none !important;
    }
    
    /* Body rows - Grid style with 3D depth */
    [data-testid="stDataFrame"] table tbody tr {
        border-bottom: 2px solid rgba(46, 140, 168, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: #ffffff;
    }
    
    /* Body cells - Grid with borders */
    [data-testid="stDataFrame"] table tbody td {
        padding: 14px 18px !important;
        border-right: 2px solid rgba(46, 140, 168, 0.12) !important;
        color: #2C3E50 !important;
        font-family: 'Segoe UI', sans-serif;
        font-size: 11px !important;
        text-align: center;
        background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(248,249,250,0.5) 100%);
    }
    
    /* Last cell in row - no right border */
    [data-testid="stDataFrame"] table tbody td:last-child {
        border-right: none !important;
    }
    
    /* Alternating row colors - subtle 3D effect */
    [data-testid="stDataFrame"] table tbody tr:nth-child(even) td {
        background: linear-gradient(180deg, rgba(248,249,250,1) 0%, rgba(245,247,250,0.5) 100%);
    }
    
    /* Hover effect - 3D lift */
    [data-testid="stDataFrame"] table tbody tr:hover {
        background: linear-gradient(180deg, rgba(219,237,245,1) 0%, rgba(219,237,245,0.5) 100%);
        box-shadow: inset 0 0 0 2px rgba(46, 140, 168, 0.2);
        transform: translateY(-2px);
    }
    
    [data-testid="stDataFrame"] table tbody tr:hover td {
        background: linear-gradient(180deg, rgba(219,237,245,1) 0%, rgba(219,237,245,0.5) 100%);
        box-shadow: inset 1px 0 0 rgba(46, 140, 168, 0.1);
    }
    
    /* First column - highlight */
    [data-testid="stDataFrame"] table tbody td:first-child {
        font-weight: 600;
        color: #2E8CA8;
        background: linear-gradient(90deg, rgba(46, 140, 168, 0.08) 0%, rgba(46, 140, 168, 0.02) 100%);
    }
    
    /* Last row - special styling */
    [data-testid="stDataFrame"] table tbody tr:last-child {
        border-bottom: none !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: linear-gradient(90deg, #f1f3f5 0%, #e9ecef 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #2E8CA8 0%, #1F6C86 100%);
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(46, 140, 168, 0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #1F6C86 0%, #154360 100%);
    }
</style>
""", unsafe_allow_html=True)

# Check if data is processed
if 'processed' not in st.session_state or not st.session_state.processed:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #d32f2f;
        animation: slideInLeft 0.5s ease-out;
    ">
        <h3 style="color: #c62828; margin-top: 0;">⚠️ No Data Processed Yet</h3>
        <p>Please go to <b>Home page</b>, upload an Excel file, and click <b>Process & Go to Dashboard</b></p>
    </div>
    """, unsafe_allow_html=True)
    st.info("Navigate using the sidebar: Home → Upload Excel → Click 'Process & Go to Dashboard'")
    st.stop()

# Check if we have results or summary data
if ('results_df' not in st.session_state or st.session_state.results_df is None) and \
   ('summary_data' not in st.session_state or st.session_state.summary_data is None):
    st.error("❌ No results data found. Please process a file first.")
    st.stop()

# Helper functions



def gradient_header(title):
    """Render a clean header bar with gradient background and centered title text using Streamlit container."""
    # Use Streamlit's native container to avoid column-related layout issues
    st.write("")  # Add spacing
    
    # Create custom HTML without using CSS classes that might conflict
    header_html = f"""
    <div style="
        background: linear-gradient(135deg, #2e8ca8 0%, #1f6c86 100%);
        color: white;
        font-weight: 500;
        font-size: 24px;
        padding: 12px 24px;
        text-align: center;
        border-radius: 10px;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(46, 140, 168, 0.25);
        margin: 16px 0;
        font-family: {FONT_FAMILY};
        border: 2px solid #1f6c86;
    ">
        {title}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def donut_chart(label, value, alt_text):
    """Create a stunning neomorphic donut chart with soft, embedded appearance."""
    # Unified purple neomorphic color scheme for all charts
    primary_color = "#CE93D8"  # Soft purple
    accent_color = "#9B59B6"  # Deeper purple for accents
    base_color = "#F8F0FF"  # Very light purple background

    remainder = 100 - value
    sizes = [value, remainder]
    colors = [primary_color, base_color]  # Soft background color

    # Neomorphic figure with soft appearance
    fig, ax = plt.subplots(figsize=(4.2, 4.2), dpi=150, subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor('#F5F5F5')  # Soft gray background
    ax.set_facecolor('#F5F5F5')

    # Create neomorphic donut chart with soft, embedded effects
    wedges, texts = ax.pie(sizes,
                       colors=colors,
                       startangle=90,
                       wedgeprops=dict(width=0.5, edgecolor='white', linewidth=6, alpha=0.9),
                       counterclock=False)

    # Neomorphic shadow effects - soft and subtle
    # Outer shadow (bottom-right)
    shadow_outer = Circle((0.015, -0.015), 1.05, fc='none', ec=(0.8, 0.8, 0.8, 0.4), linewidth=12, alpha=0.6, zorder=3)
    ax.add_artist(shadow_outer)

    # Inner shadow (top-left) for embedded effect
    shadow_inner = Circle((-0.01, 0.01), 0.98, fc='none', ec=(1, 1, 1, 0.8), linewidth=8, alpha=0.7, zorder=4)
    ax.add_artist(shadow_inner)

    # Main outer ring - soft and smooth
    outer_circle = Circle((0, 0), 1.0, fc='none', ec=primary_color, linewidth=8, alpha=0.95, zorder=7)
    ax.add_artist(outer_circle)

    # Inner highlight for neomorphic effect
    highlight_inner = Circle((0, 0), 0.52, fc='none', ec=(1, 1, 1, 0.9), linewidth=4, alpha=0.8, zorder=8)
    ax.add_artist(highlight_inner)

    # Soft inner circle with subtle border
    inner_circle = Circle((0, 0), 0.55, fc=base_color, ec=(0.9, 0.9, 0.9, 0.5), linewidth=2, alpha=0.8, zorder=9)
    ax.add_artist(inner_circle)

    # Neomorphic percentage text with soft shadows
    # Soft shadow text
    ax.text(
        0.03, -0.03, f"{value}%",
        ha='center',
        va='center',
        fontsize=44,
        fontweight='800',
        fontfamily='Arial',
        color=(0, 0, 0, 0.08),
        zorder=10
    )

    # Main text with soft color
    ax.text(
        0, 0, f"{value}%",
        ha='center',
        va='center',
        fontsize=44,
        fontweight='800',
        fontfamily='Arial',
        color=accent_color,
        zorder=11
    )

    # Neomorphic label with soft typography
    # Soft shadow for label
    ax.text(
        0.02, -1.48, label,
        ha='center',
        va='center',
        fontsize=14,
        fontweight='700',
        fontfamily='Arial',
        color=(0, 0, 0, 0.08),
        zorder=10
    )

    # Main label text
    ax.text(
        0, -1.45, label,
        ha='center',
        va='center',
        fontsize=14,
        fontweight='700',
        fontfamily='Arial',
        color='#374151',
        zorder=11
    )

    ax.axis('equal')
    plt.tight_layout()

    # Display the neomorphic chart
    st.pyplot(fig, use_container_width=False)

    plt.close(fig)

def plotly_donut_chart(label, value, color):
    """Create a single circle gauge with glue-type color overlay effect."""
    fig = go.Figure()
    
    # Main gauge circle with glue-type overlay
    fig.add_trace(go.Pie(
        labels=["Progress", "Remaining"],
        values=[value, 100 - value],
        hole=0.65,
        marker=dict(
            colors=[color, "#E8E8E8"],
            line=dict(color=color, width=3)
        ),
        textinfo='none',
        sort=False,
        hoverinfo='skip'
    ))
    
    # Add center text annotation
    fig.add_annotation(
        text=f"<b>{value}%</b>",
        x=0.5, y=0.5,
        font=dict(size=28, color=color, family="Arial"),
        showarrow=False,
        xref="paper", yref="paper"
    )
    
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=140, 
        height=140,
        font=dict(family="Arial, sans-serif")
    )
    return fig

# Convert this to a function to avoid repetition
def render_donut_charts_section():
    """Render the top section donut charts for three metrics."""
    if 'results_df' in st.session_state and 'summary_data' in st.session_state:
        col1, col2, col3 = st.columns(3)
        
        # Define distinct glue-type colors for each metric
        color_reduction = "#FF6B6B"      # Warm red/coral
        color_adoption = "#4ECDC4"       # Teal/turquoise
        color_ai_automation = "#FFD93D"  # Golden yellow
        
        with col1:
            st.plotly_chart(plotly_donut_chart("Manual Task Reduction", 0, color_reduction), use_container_width=True)
            st.markdown("<center><b>Manual Task Reduction</b><br>0%</center>", unsafe_allow_html=True)
        with col2:
            st.plotly_chart(plotly_donut_chart("Core Automation Adoption", 0, color_adoption), use_container_width=True)
            st.markdown("<center><b>Core Automation Adoption</b><br>0%</center>", unsafe_allow_html=True)
        with col3:
            st.plotly_chart(plotly_donut_chart("AI-Driven Automation", 3, color_ai_automation), use_container_width=True)
            st.markdown("<center><b>AI-Driven Automation</b><br>3%</center>", unsafe_allow_html=True)

def render_donut_section(donut_data=None):
    """Render donut charts section with calculated utilization data."""
    gradient_header("Automation Performance Overview")
    
    # Define distinct glue-type colors for each metric
    color_reduction = "#FF6B6B"      # Warm red/coral
    color_adoption = "#4ECDC4"       # Teal/turquoise
    color_ai_automation = "#FFD93D"  # Golden yellow
    colors = [color_reduction, color_adoption, color_ai_automation]
    
    try:
        from utilization_graphs import calculate_utilization_graph, get_graph_data_for_display
        
        if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
            merged_df = st.session_state.merged_df
            
            # Calculate utilization graph data
            graph_data = calculate_utilization_graph(merged_df)
            display_data = get_graph_data_for_display(graph_data)
            
            # Extract percentages for donut charts from the display_data
            # display_data has: labels, percentages, values lists and categories dict
            donut_data = [
                ("Manual Task Reduction", int(round(display_data['categories']['Elimination']['percentage'])), color_reduction),
                ("Core Automation Adoption", int(round(display_data['categories']['Automation Standard']['percentage'])), color_adoption),
                ("AI Driven Automation", int(round(display_data['categories']['Automation Agentic AI']['percentage'])), color_ai_automation),
            ]
        else:
            # Fallback to default data if no merged_df
            donut_data = [
                ("Manual Task Reduction", 33, color_reduction),
                ("Core Automation Adoption", 33, color_adoption),
                ("AI Driven Automation", 34, color_ai_automation),
            ]
    except ImportError:
        st.error("utilization_graphs module not found.")
        donut_data = [
            ("Manual Task Reduction", 33, color_reduction),
            ("Core Automation Adoption", 33, color_adoption),
            ("AI Driven Automation", 34, color_ai_automation),
        ]
    except Exception as e:
        st.error(f"Error calculating utilization graphs: {e}")
        donut_data = [
            ("Manual Task Reduction", 33, color_reduction),
            ("Core Automation Adoption", 33, color_adoption),
            ("AI Driven Automation", 34, color_ai_automation),
        ]
    
    cols = st.columns(3, gap="medium")
    for col, (label, value, color) in zip(cols, donut_data):
        with col:
            st.plotly_chart(plotly_donut_chart(label, value, color), use_container_width=True)
            st.markdown(f"<center><b>{label}</b><br>{value}%</center>", unsafe_allow_html=True)

def styled_table(df, col_widths, remark_align='left', row_heights=None):
    """Render a clean, professional table with proper styling."""
    styled = df.style.set_table_styles([
        {'selector': 'th', 'props': [
            ('background', 'linear-gradient(90deg, #2e8ca8, #1f6c86)'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('font-family', FONT_FAMILY),
            ('text-align', 'center'),
            ('padding', '10px 12px'),
            ('border', f'1px solid #ddd'),
            ('height', '24px')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '8px 12px'),
            ('border', f'1px solid #eee'),
            ('font-family', FONT_FAMILY),
            ('font-size', '10pt'),
            ('text-align', 'center')
        ]},
        {'selector': 'tbody tr:hover', 'props': [
            ('background-color', '#f5f5f5')
        ]}
    ])

    if 'Remarks/information icon' in df.columns:
        styled = styled.set_properties(subset=['Remarks/information icon'], **{'text-align': remark_align})

    return styled

def render_overall_rl_section(data=None):
    """Render Resource Load and Productivity trends section with calculated values from RL module."""
    gradient_header("Resource Load And Productivity Trends")
    
    try:
        from rl_calculations import calculate_rl_tables, adjust_rl_for_non_ticketed
        
        if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
            merged_df = st.session_state.merged_df
            overall_rl, gradewise_df, metrics = calculate_rl_tables(merged_df)
            
            # Check if non-ticketed activities are configured and adjust RL accordingly
            total_non_ticketed_pct = st.session_state.get('total_non_ticketed_percent', 0)
            has_non_ticketed = st.session_state.get('has_non_ticketed', False)
            
            # Apply non-ticketed adjustment if applicable
            if has_non_ticketed and total_non_ticketed_pct > 0:
                adjusted_rl = adjust_rl_for_non_ticketed(overall_rl, total_non_ticketed_pct)
            else:
                adjusted_rl = overall_rl
            
            # Add clean minimal table CSS
            st.markdown("""
            <style>
                .rl-table-container {
                    background: transparent;
                    border-radius: 0;
                    overflow: visible;
                    box-shadow: none;
                    border: none;
                    padding: 0;
                    margin: 0;
                }
                
                .rl-row {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 0;
                    border-bottom: 1px solid rgba(46, 140, 168, 0.4);
                    margin-bottom: 0;
                    margin-top: -8px;
                }
                
                .rl-row.separator {
                    border-bottom: 3px solid rgba(46, 140, 168, 0.6) !important;
                }
                
                .rl-row:last-child {
                    border-bottom: none;
                }
                
                .rl-cell {
                    padding: 12px 16px;
                    border-right: 1px solid rgba(46, 140, 168, 0.08);
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    background: transparent;
                }
                
                .rl-cell:nth-child(2n) {
                    border-right: none;
                }
                
                .rl-cell-label {
                    font-size: 9px;
                    color: #7F8C95;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.4px;
                    margin-bottom: 8px;
                    display: block;
                }
                
                .rl-cell-value {
                    font-size: 20px;
                    font-weight: 800;
                    color: #2E8CA8;
                    font-family: 'Courier New', monospace;
                    letter-spacing: 0.5px;
                }
                
                .rl-tooltip {
                    position: relative;
                    cursor: help;
                }
                
                .rl-tooltip:hover {
                    background-color: transparent;
                }
                
                .rl-tooltip-text {
                    visibility: hidden;
                    width: max-content;
                    background-color: #2E8CA8;
                    color: white;
                    text-align: center;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 16px;
                    font-weight: 600;
                    position: absolute;
                    z-index: 1000;
                    bottom: 120%;
                    left: 50%;
                    margin-left: -60px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    white-space: nowrap;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                }
                
                .rl-tooltip .rl-tooltip-text::after {
                    content: "";
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    margin-left: -5px;
                    border-width: 5px;
                    border-style: solid;
                    border-color: #2E8CA8 transparent transparent transparent;
                }
                
                .rl-tooltip:hover .rl-tooltip-text {
                    visibility: visible;
                    opacity: 1;
                }
                
                .rl-header-cell {
                    background: transparent;
                    color: #2E8CA8;
                    font-weight: 700;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    padding: 16px;
                    border-right: 1px solid rgba(46, 140, 168, 0.08);
                    border-bottom: 2px solid rgba(46, 140, 168, 0.15);
                    text-align: center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .rl-header-cell:nth-child(2n) {
                    border-right: none;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Render as a clean 2-column table
            st.markdown("""
            <div class="rl-table-container">
                <div class="rl-row">
                    <div class="rl-header-cell">Timeline</div>
                    <div class="rl-header-cell">Resource Load Value</div>
                </div>
            """, unsafe_allow_html=True)
            
            # # Row 1: H1Y1
            # st.markdown(f"""
            # <div class="rl-row separator">
            #     <div class="rl-cell rl-tooltip">
            #         <span class="rl-cell-value">H1Y1</span>
            #         <span class="rl-tooltip-text" style="opacity:0.8;">140 Tickets productivity No automation</span>
            #     </div>
            #     <div class="rl-cell">
            #         <span class="rl-cell-value">{adjusted_rl.get('H1Y1', 0):.2f}</span>
            #     </div>
            # </div>
            # """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="rl-row separator" style="text-align:center;">
                <div class="rl-cell rl-tooltip" style="display:inline-block;">
                    <span class="rl-cell-value" style="font-weight:bold;">H1Y1</span>
                    <span class="rl-tooltip-text" style="opacity:0.8;">140 Tickets productivity No automation</span>
                </div>
                <div class="rl-cell" style="display:inline-block; margin-left:20px;">
                    <span class="rl-cell-value">{adjusted_rl.get('H1Y1', 0):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Row 2: H2Y1

            st.markdown(f"""
            <div class="rl-row separator" style="text-align:center;">
                <div class="rl-cell rl-tooltip" style="display:inline-block;">
                    <span class="rl-cell-value" style="font-weight:bold;">H2Y1</span>
                    <span class="rl-tooltip-text" style="opacity:0.8;">140 Tickets productivity No automation</span>
                </div>
                <div class="rl-cell" style="display:inline-block; margin-left:20px;">
                    <span class="rl-cell-value">{adjusted_rl.get('H2Y1', 0):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # st.markdown(f"""
            # <div class="rl-row separator">
            #     <div class="rl-cell rl-tooltip">
            #         <span class="rl-cell-value">H2Y1</span>
            #         <span class="rl-tooltip-text"style="opacity:0.8;">160 Tickets productivity 50% automation</span>
            #     </div>
            #     <div class="rl-cell">
            #         <span class="rl-cell-value">{adjusted_rl.get('H2Y1', 0):.2f}</span>
            #     </div>
            # </div>
            # """, unsafe_allow_html=True)
            
            # Row 3: H1Y2
            st.markdown(f"""
            <div class="rl-row separator" style="text-align:center;">
                <div class="rl-cell rl-tooltip" style="display:inline-block;">
                    <span class="rl-cell-value" style="font-weight:bold;">H1Y2</span>
                    <span class="rl-tooltip-text" style="opacity:0.8;">140 Tickets productivity No automation</span>
                </div>
                <div class="rl-cell" style="display:inline-block; margin-left:20px;">
                    <span class="rl-cell-value">{adjusted_rl.get('H1Y2', 0):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # st.markdown(f"""
            # <div class="rl-row">
            #     <div class="rl-cell rl-tooltip">
            #         <span class="rl-cell-value">H1Y2</span>
            #         <span class="rl-tooltip-text">160 Tickets productivity, 100% Automation + Left Shift</span>
            #     </div>
            #     <div class="rl-cell">
            #         <span class="rl-cell-value">{adjusted_rl.get('H1Y2', 0):.2f}</span>
            #     </div>
            # </div>
            # </div>
            # """, unsafe_allow_html=True)

            # Conditional visible note below the Resource Load and Productivity Trends table
            if has_non_ticketed and total_non_ticketed_pct is not None and isinstance(total_non_ticketed_pct, (int, float)):
                if total_non_ticketed_pct <= 15:
                    # Less than or equal to 15% - already considered in RL
                    note = f"✅ Non-ticketed activities: {total_non_ticketed_pct:.1f}% - Already included in the RL calculation (≤15% baseline)"
                    bg_color = "#e8f5e9"
                    border_color = "#4caf50"
                    text_color = "#2e7d32"
                    
                else:
                    # Greater than 15% - need to adjust RL
                    excess_pct = total_non_ticketed_pct - 15
                    note = f"⚠️ Non-ticketed activities: {total_non_ticketed_pct:.1f}% - Excess {excess_pct:.1f}% has to be added to RL values above (15% baseline already included). Recommended to review capacity planning."
                    bg_color = "#fff3e0"
                    border_color = "#ff9800"
                    text_color = "#e65100"

                st.markdown(f"""
                <div style="background-color:{bg_color}; border-left:6px solid {border_color}; padding:10px 12px; border-radius:4px; color:{text_color}; margin-top:8px; font-weight:600; font-size:18px;">
                    {note}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No merged data available. Please process a file first.")
    except ImportError:
        st.error("rl_calculations module not found.")
    except Exception as e:
        st.error(f"Error calculating Resource Load And Productivity Trends: {e}")

def styled_table(df, col_widths, remark_align='left', row_heights=None):
    """Render a clean, professional table with proper styling."""

def professional_bar_chart(title, categories, values, colors=None):
    """Create a professional bar chart with conditional coloring and styling."""
    if colors is None:
        # Default professional colors
        colors = ['#27AE60', '#3498DB', '#9B59B6', '#E67E22']
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#F8F9FA')
    
    # Create bars with professional styling
    bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2, width=0.6)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom',
                fontweight='bold',
                fontfamily='Segoe UI',
                fontsize=11,
                color='#2C3E50')
    
    # Professional styling
    ax.set_ylabel('Value', fontsize=11, fontweight='bold', fontfamily='Segoe UI', color='#2C3E50')
    ax.set_xlabel('Category', fontsize=11, fontweight='bold', fontfamily='Segoe UI', color='#2C3E50')
    ax.set_title(title, fontsize=13, fontweight='bold', fontfamily='Segoe UI', color='#2C3E50', pad=15)
    
    # Add grid for better readability
    ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.5, color='#BDC3C7')
    ax.set_axisbelow(True)
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#BDC3C7')
    ax.spines['bottom'].set_color('#BDC3C7')
    
    # Style tick labels
    ax.tick_params(axis='x', labelsize=10, colors='#2C3E50')
    ax.tick_params(axis='y', labelsize=10, colors='#2C3E50')
    
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

def modern_table_style(df, highlight_column=None):
    """Apply modern, clean Tailwind-inspired styling to dataframes - no grids, professional look."""
    styled = df.style.set_table_styles([
        # Header styling - gradient background with no borders
        {
            'selector': 'th',
            'props': [
                ('background', 'linear-gradient(90deg, #2e8ca8, #1f6c86) !important'),
                ('color', 'white !important'),
                ('font-weight', '600 !important'),
                ('font-family', f'{FONT_FAMILY} !important'),
                ('text-align', 'center !important'),
                ('padding', '14px 16px !important'),
                ('border', 'none !important'),
                ('letter-spacing', '0.3px'),
                ('height', '24px')
            ]
        },
        # Row styling - alternating backgrounds, no visible borders
        {
            'selector': 'tbody tr',
            'props': [
                ('background-color', '#ffffff !important'),
                ('border', 'none !important'),
            ]
        },
        {
            'selector': 'tbody tr:hover',
            'props': [
                ('background-color', '#F5F7FA !important'),
                ('transition', 'background-color 0.2s ease'),
            ]
        },
        {
            'selector': 'tbody tr:nth-child(even)',
            'props': [
                ('background-color', '#F8F9FA !important'),
            ]
        },
        # Cell styling - no grids, clean spacing
        {
            'selector': 'td',
            'props': [
                ('padding', '14px 16px !important'),
                ('border', 'none !important'),
                ('font-family', f'{FONT_FAMILY} !important'),
                ('font-size', '10pt !important'),
                ('text-align', 'center !important'),
                ('color', '#2C3E50 !important'),
                ('border-bottom', '1px solid #E8EAED !important')
            ]
        },
        # Last row - no bottom border
        {
            'selector': 'tbody tr:last-child td',
            'props': [
                ('border-bottom', 'none !important')
            ]
        }
    ])
    
    # Highlight specific column if requested
    if highlight_column and highlight_column in df.columns:
        styled = styled.set_properties(subset=[highlight_column], **{
            'font-weight': 'bold',
            'color': TEAL_START,
            'text-align': 'left'
        })
    
    return styled

def render_optimization_summary_section(data=None):
    """Render Efficiency Gains Breakdown with option to use custom data."""
    gradient_header("Efficiency Gains Breakdown")
    
    if data is None:
        # Try to load from session state first
        if 'summary_data' in st.session_state and st.session_state.summary_data:
            summary_data = st.session_state.summary_data
        # Otherwise try to load from summary_output.json
        elif os.path.exists("summary_output.json"):
            try:
                with open("summary_output.json", "r") as f:
                    summary_data = json.load(f)
            except Exception as e:
                st.error(f"Error loading summary data: {e}")
                summary_data = None
        else:
            summary_data = None
        
        if summary_data:
            data = {
                "Optimization Approach": [
                    "Manual task Reduction",
                    "Core Automation Adoption",
                    "AI Driven Automation",
                    "Left Shift"
                ],
                "UseCase Count": [
                    summary_data.get("elimination_array", [0, 0, 0])[0],
                    summary_data.get("automation_array", [0, 0, 0])[0],
                    summary_data.get("automation_agent_array", [0, 0, 0])[0],
                    summary_data.get("left_shift_array", [0, 0, 0])[0]
                ],
                "Ticket Volume": [
                    f"{summary_data.get('elimination_array', [0, 0, 0])[1]:.2f}",
                    f"{summary_data.get('automation_array', [0, 0, 0])[1]:.2f}",
                    f"{summary_data.get('automation_agent_array', [0, 0, 0])[1]:.2f}",
                    f"{summary_data.get('left_shift_array', [0, 0, 0])[1]:.2f}"
                ],
                "Effort Saved (FTE)": [
                    f"{summary_data.get('elimination_array', [0, 0, 0])[2]:.2f}",
                    f"{summary_data.get('automation_array', [0, 0, 0])[2]:.2f}",
                    f"{summary_data.get('automation_agent_array', [0, 0, 0])[2]:.2f}",
                    f"{summary_data.get('left_shift_array', [0, 0, 0])[2]:.2f}"
                ]
            }
        else:
            data = {
                "Optimization Approach": [
                    "Manual task Reduction",
                    "Core Automation Adoption",
                    "AI Driven Automation",
                    "Left Shift"
                ],
                "UseCase Count": ["", "", "", ""],
                "Ticket Volume": ["", "", "", ""],
                "Effort Saved (FTE)": ["", "", "", ""]
            }
    
    df = pd.DataFrame(data)
    styled = modern_table_style(df, highlight_column='Optimization Approach')
    st.dataframe(styled.hide(axis='index'), use_container_width=True, hide_index=True)

def render_other_tools_section(data=None):
    """Render Additional recommended tools with conditional tool recommendations."""
    gradient_header("Additional Recommended Tools")
    
    try:
        from other_recommended_tools import calculate_other_recommended_tools
        
        # Get the merged DataFrame from session state
        if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
            merged_df = st.session_state.merged_df
            tools_df, raw_data = calculate_other_recommended_tools(merged_df)
            
            # Build a 1-column display: Only Tools (if condition met)
            tools_mapping = {
                "P1/P2": "CRTSIT Assist",
                "FLR": "SOP Genius Recommended",
                "Triaging Effort": "Auto Ticket Triaging"
            }
            
            tool_recommendations = []
            
            # P1/P2
            if raw_data["conditions_met"]["p1_p2_show"]:
                tool_recommendations.append(tools_mapping["P1/P2"])
            
            # FLR
            if raw_data["conditions_met"]["flr_show"]:
                tool_recommendations.append(tools_mapping["FLR"])
            
            # Triaging Effort
            if raw_data["conditions_met"]["triaging_effort_show"]:
                tool_recommendations.append(tools_mapping["Triaging Effort"])
            
            # Service Improvement (always shown)
            tool_recommendations.append("Ticket Quality Audit Tool")
            
            # Create display DataFrame with only Tools column
            display_data = {
                "Recommended Tools": tool_recommendations
            }
            
            df_display = pd.DataFrame(display_data)
            
            # Apply modern styling
            styled = modern_table_style(df_display)
            st.dataframe(styled.hide(axis='index'), use_container_width=True, hide_index=True)
            
            # Show condition thresholds in expander
            with st.expander("ℹ️ Condition Thresholds"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Metric Thresholds:**")
                    st.markdown("""
                    - **P1/P2**: >= 10
                    - **FLR**: < 30%
                    - **Triaging Effort**: > 1 Effort Saved (FTE)
                    """)
                with col2:
                    st.write("**Current Status:**")
                    status_text = f"""
                    - P1/P2: {raw_data['p1_p2']:.2f} {'✓ meets threshold' if raw_data['conditions_met']['p1_p2_show'] else '✗ below threshold'}
                    - FLR: {raw_data['flr_percentage']:.2f}% {'✓ meets threshold' if raw_data['conditions_met']['flr_show'] else '✗ above threshold'}
                    - Triaging: {raw_data['triaging_effort']:.2f} {'✓ meets threshold' if raw_data['conditions_met']['triaging_effort_show'] else '✗ below threshold'}
                    """
                    st.markdown(status_text)
        else:
            st.warning("No merged data available. Please process a file first.")
            
    except ImportError:
        st.error("calculate_other_recommended_tools module not found. Please ensure other_recommended_tools.py exists.")
    except Exception as e:
        st.error(f"Error rendering Additional recommended tools: {e}")

def render_gradewise_mnm_rl_section(data=None):
    """Render Grade-level Resource section with calculated values from RL module."""
    
    # Add CSS for Final Productivity section
    st.markdown("""
    <style>
        .productivity-header {
            background: linear-gradient(135deg, #00b894 0%, #27ae60 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            box-shadow: 0 4px 15px rgba(0, 184, 148, 0.25);
        }
        
        .productivity-column {
            background: linear-gradient(135deg, #E8F4F8 0%, #D4E9F0 100%);
            border: 2px solid #2E8CA8;
            border-radius: 8px;
            padding:0;
            text-align: center;
            box-shadow: 0 2px 8px rgba(46, 140, 168, 0.1);
            position: relative;
        }
        
        .productivity-tooltip {
            position: relative;
            cursor: help;
            display: inline-block;
        }
        
        .productivity-tooltip .tooltip-text {
            visibility: hidden;
            width: max-content;
            background-color: #2E8CA8;
            color: white;
            text-align: center;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        
        .productivity-tooltip .tooltip-text::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #2E8CA8 transparent transparent transparent;
        }
        
        .productivity-tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }
        
        .productivity-label {
            display:none;
            font-size: 10px;
            color: #1F6C86;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 8px;
        }
        
        .productivity-value {
            font-size: 24px;
            color: #2E8CA8;
            font-weight: 800;
            font-family: 'Courier New', monospace;
        }
        
        .productivity-subheader {
            font-size: 14px;
            color: #1F6C86;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 12px;
        }
        
        .productivity-item {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .tooltip-container {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        
        .tooltip-container .tooltiptext {
            visibility: hidden;
            background-color: #1F6C86;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 10px 12px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 11px;
            white-space: normal;
            width: 140px;
            word-wrap: break-word;
            line-height: 1.3;
        }
        
        .tooltip-container .tooltiptext::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #1F6C86 transparent transparent transparent;
        }
        
        .tooltip-container:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        .productivity-container {
            display: flex;
            width: 100%;
            gap: 20px;
            align-items: center;
            justify-content: space-between;
        }
        
        .productivity-section {
            flex: 1;
            text-align: center;
        }

        .productivity-section:nth-child(2) {
            border-left: 1px solid #2E8CA8;
        }
        
        .productivity-section-header {
            font-size: 12px;
            color: #1F6C86;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="productivity-header">✨ Final Productivity after Optimization</div>', unsafe_allow_html=True)
    
    try:
        from rl_calculations import calculate_rl_tables
        
        if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
            merged_df = st.session_state.merged_df
            overall_rl, gradewise_df, metrics = calculate_rl_tables(merged_df)
            
            # Get left shift volume and H1Y2 FTE (use actual calculated value)
            left_shift_volume = metrics.get('fte_left_shift', 0) * 140
            h1y2_fte = overall_rl.get('H1Y2', 0)
            
            # Calculate productivity
            productivity_value = left_shift_volume / h1y2_fte if h1y2_fte > 0 else 0
            
            st.markdown(f"""
            <div class="productivity-container">
                <div class="productivity-section">
                    <div class="productivity-section-header">Before Automation</div>
                    <div class="tooltip-container">
                        <div class="productivity-value">140</div>
                        <span class="tooltiptext">Initial Productivity</span>
                    </div>
                </div>
                <div class="productivity-section">
                    <div class="productivity-section-header">After Automation</div>
                    <div class="tooltip-container">
                        <div class="productivity-value">{productivity_value:.2f}</div>
                        <span class="tooltiptext">Final productivity after transformation (elimination, automation and optimization)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No merged data available. Please process a file first.")
    except ImportError:
        st.error("rl_calculations module not found.")
    except Exception as e:
        st.error(f"Error calculating Final Productivity: {e}")
    
    gradient_header("Grade-Level Resource Load")
    
    try:
        from rl_calculations import calculate_rl_tables
        
        if 'merged_df' in st.session_state and st.session_state.merged_df is not None:
            merged_df = st.session_state.merged_df
            overall_rl, gradewise_df, metrics = calculate_rl_tables(merged_df)
            
            # Rename Grade column for display
            display_df = gradewise_df.copy()
            
            # Format all numeric columns to 2 decimal places
            numeric_cols = display_df.select_dtypes(include=['float64', 'float32']).columns
            for col in numeric_cols:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
            
            # Apply modern styling
            styled = modern_table_style(display_df, highlight_column='Grade')
            st.dataframe(styled.hide(axis='index'), use_container_width=True, hide_index=True)
        else:
            st.warning("No merged data available. Please process a file first.")
    except ImportError:
        st.error("rl_calculations module not found.")
    except Exception as e:
        st.error(f"Error calculating Grade-level Resource: {e}")

def render_non_ticketed_summary_section():
    """Render Non-Ticketed Activities Summary section if data is available."""
    # Check if non-ticketed data exists and has been submitted
    total_pct = st.session_state.get('total_non_ticketed_percent', 0)
    has_non_ticketed = st.session_state.get('has_non_ticketed', False)
    selected_activities = st.session_state.get('selected_activities', {})
    
    # Don't render if no non-ticketed data or total is 0
    if not has_non_ticketed or total_pct == 0 or not selected_activities:
        return
    
    gradient_header("Non-Ticketed Activities Summary")
    
    # Collect selected activities with percentages > 0
    activities_list = []
    
    for activity_name, activity_data in selected_activities.items():
        percentage = activity_data.get('percentage', 0)
        
        # Only include activities with non-zero percentages
        if percentage > 0:
            # Get feasibility from activity_data
            feasibility = activity_data.get('feasibility', 'Not Feasible')
            
            activities_list.append({
                "Activity Type": activity_name,
                "% Allocation": f"{percentage}%",
                "Efforts": feasibility
            })
    
    if activities_list:
        # Create DataFrame
        df = pd.DataFrame(activities_list)
        
        # Apply modern styling
        styled = modern_table_style(df, highlight_column='Activity Type')
        st.dataframe(styled.hide(axis='index'), use_container_width=True, hide_index=True)

def main():
    # Apply global CSS with professional styling and animations
    st.markdown(f"""
    <style>
        /* Dashboard container styling */
        .block-container {{
            padding: 0.5in 0.5in 0.5in 0.5in;
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Calibri, sans-serif;
            font-size: 10pt;
            color: #333;
        }}

        .section-spacing {{
            margin-top: 20px;
            margin-bottom: 20px;
            animation: fadeIn 0.6s ease-out;
        }}

        .header-bar {{
            height: 28px;
            line-height: 28px;
            font-weight: 700;
            font-size: 14pt;
            color: white;
            text-align: center;
            font-family: 'Segoe UI', Calibri, sans-serif;
            border-radius: 4px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0, 102, 204, 0.15);
            animation: slideInLeft 0.5s ease-out;
        }}

        /* Dashboard title styling */
        .dashboard-title {{
            background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
            padding: 30px;
            border-radius: 8px;
            color: white;
            text-align: center;
            animation: fadeIn 0.6s ease-out;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
            margin-bottom: 20px;
        }}
        
        .dashboard-title h1 {{
            margin: 0;
            font-size: 36px;
            font-weight: 900;
            letter-spacing: -0.5px;
        }}
        
        .dashboard-title p {{
            margin: 8px 0 0 0;
            font-size: 14px;
            opacity: 0.95;
            letter-spacing: 0.5px;
        }}

        .stDataFrame, .stTable {{
            max-width: 100%;
            animation: fadeIn 0.5s ease-out;
        }}
        
        /* Section wrapper */
        .section-wrapper {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #0066cc;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            animation: slideInRight 0.5s ease-out;
        }}
        
        /* Professional card styling */
        .metric-card {{
            background: linear-gradient(135deg, rgba(0, 102, 204, 0.05) 0%, rgba(0, 168, 232, 0.05) 100%);
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #e0e7ff;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            border-color: #0066cc;
            box-shadow: 0 2px 8px rgba(0, 102, 204, 0.12);
            transform: translateY(-2px);
        }}
        
        /* Button styling */
        .stButton > button {{
            background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 102, 204, 0.2);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 102, 204, 0.3);
        }}
        
        /* Info/Warning/Success boxes styling */
        .stAlert {{
            animation: slideInLeft 0.4s ease-out;
            border-radius: 6px;
        }}
        
        /* Divider styling */
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, rgba(0, 102, 204, 0) 0%, rgba(0, 102, 204, 0.3) 50%, rgba(0, 102, 204, 0) 100%);
            margin: 25px 0;
        }}
        
        /* Column layout styling */
        .stColumns {{
            animation: fadeIn 0.6s ease-out;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Professional Dashboard Header with animation
    st.markdown("""
    <div class="dashboard-title">
        <h1> 📊Dashboard Analytics</h1>
        <p>Real-time Resource Estimation & Automation Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
    
    # Header with file info and controls
    col1, col2, col3 = st.columns([3, 1, 1], gap="large")
    with col1:
        if 'file_name' in st.session_state and st.session_state.file_name:
            st.markdown(f"""
            <div class="metric-card">
                <strong>📁 File:</strong> {st.session_state.file_name}
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.write("")
    with col3:
        if st.button("🔄 Clear & Re-upload", help="Clear data and upload a new file", key="clear_btn"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown("---")

    # Layout with left and right columns for first 4 sections
    left_col, right_col = st.columns([1,1], gap="large")
    with left_col:
        render_donut_section()
        st.write("")
        render_overall_rl_section()
    with right_col:
        render_optimization_summary_section()
        st.write("")
        render_other_tools_section()

    # Full width section
    st.write("")
    render_gradewise_mnm_rl_section()
    
    # Non-Ticketed Activities Summary section (if data exists)
    st.write("")
    render_non_ticketed_summary_section()
    
    st.markdown("---")
    st.info("💡 To update the data, go back to Home page and upload a new Excel file.")

if __name__ == "__main__":
    main()
