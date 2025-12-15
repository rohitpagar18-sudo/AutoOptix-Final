import streamlit as st
import os
import base64

# Logo configuration
LOGO_PATH = os.path.join(os.path.dirname(__file__), 'logo2.png')
LOGO_PATH1 = os.path.join(os.path.dirname(__file__), 'logo3.png')
# Function to convert image to base64
def get_image_as_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode()

# Convert logo to base64
LOGO_BASE64 = get_image_as_base64(LOGO_PATH)
LOGO_BASE65 = get_image_as_base64(LOGO_PATH1)

# Page configuration
st.set_page_config(
    page_title="AutoOptix",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/help',
        'Report a bug': None,
        'About': "# AutoOptix V1.0\nAnalyze tickets. Optimize operations. Forecast resources."
    }
)



# Professional Custom Styling with Page Transitions & Animations
st.markdown("""
<style>
    /* Animation keyframes */
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
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-5px);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 2px 8px rgba(0, 102, 204, 0.1);
        }
        50% {
            box-shadow: 0 4px 16px rgba(0, 102, 204, 0.2);
        }
    }
    
    /* Global animations */
    .main {
        animation: fadeIn 0.8s ease-out;
        background-color: #f8f9fa;
    }
    
    [data-testid="stMarkdownContainer"] {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Smooth transitions for all interactive elements */
    * {
        transition: all 0.3s ease;
    }
    
    button {
        transition: all 0.3s ease !important;
    }
    
    /* Main theme colors */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00a8e8;
        --accent-color: #00d9ff;
        --success-color: #00b894;
        --warning-color: #fdcb6e;
        --danger-color: #d63031;
    }
    
    /* Sidebar styling with animation */
    [data-testid="stSidebar"] {
        background: #fafaf7;;
        animation: slideInLeft 0.6s ease-out;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white;
    }
    
    /* Professional headers with animation */
    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: opaque;
        background-clip: text;
        margin-bottom: 10px;
        letter-spacing: -1px;
        animation: slideDown 0.7s ease-out;
    }
    
    .main-subtitle {
        text-align: center;
        font-size: 18px;
        color: #555;
        margin-bottom: 30px;
        font-weight: 500;
        letter-spacing: 0.5px;
        animation: fadeIn 0.8s ease-out 0.1s both;
    }
    
    .feature-box {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 15px;
        transition: all 0.3s ease;
        animation: slideInRight 0.5s ease-out;
    }
    
    .feature-box:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        border-left-color: #00a8e8;
        transform: translateY(-2px);
    }
    
    .feature-box h3 {
        color: #0066cc;
        margin-top: 0;
        font-size: 16px;
        font-weight: 600;
        animation: fadeIn 0.5s ease-out;
    }
    
    .feature-box p {
        color: #666;
        margin: 8px 0;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .status-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 10px;
        animation: scaleIn 0.4s ease-out;
    }
    
    .status-ready {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .footer {
        text-align: center;
        color: #999;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 20px;
        animation: fadeIn 1s ease-out 0.3s both;
        border-top: 1px solid #e0e0e0;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
        animation: fadeIn 0.6s ease-out;
    }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-top: 3px solid #0066cc;
        animation: scaleIn 0.5s ease-out;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 16px rgba(0, 102, 204, 0.15);
    }
    
    .stat-card .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #0066cc;
        margin: 10px 0;
        animation: slideDown 0.5s ease-out;
    }
    
    .stat-card .stat-label {
        font-size: 13px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        animation: fadeIn 0.5s ease-out;
    }
    
    .divider-premium {
        height: 2px;
        background: linear-gradient(90deg, transparent, #0066cc, transparent);
        margin: 30px 0;
        border: none;
    }
    
    .welcome-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .welcome-card {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
    }
    
    .welcome-card-icon {
        font-size: 40px;
        margin-bottom: 15px;
    }
    
    .welcome-card h3 {
        color: #0066cc;
        margin: 10px 0;
        font-size: 18px;
    }
    
    .welcome-card p {
        color: #666;
        font-size: 14px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df_uploaded' not in st.session_state:
    st.session_state.df_uploaded = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'processed' not in st.session_state:
    st.session_state.processed = False

# Main Title - Logo only
st.markdown(f'<div style="text-align: center; margin-bottom: 0.1px;"><img src="data:image/png;base64,{LOGO_BASE64}" alt="AutoOptix Logo" style="height: 200px;"></div>', unsafe_allow_html=True)

st.markdown('<div class="divider-premium"></div>', unsafe_allow_html=True)

# Welcome Section with Features
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### AutoOptix! 🎯
    
    **Analyze tickets. Optimize operations. Forecast resources.**
    
    AutoOptix is an enterprise-grade platform designed to help organizations:
    - 📊 **Analyze** ticket data and identify automation opportunities
    - 🤖 **Optimize** resource allocation across elimination, automation, and left-shift strategies
    - 📈 **Forecast** resource efficiency gains through data-driven insights
    - 💡 **Account for** non-ticketed activities in comprehensive resource planning
    - 📋 **Generate** professional reports with actionable recommendations
    """)

# with col2:
#     st.markdown("""
#     #### Key Metrics    
#     - **Enterprise Ready**: Secure & scalable
#     - **Multi-language**: Global support
#     - **24/7 Support**: Dedicated team
#     """)

st.markdown('<div class="divider-premium"></div>', unsafe_allow_html=True)

# Features Grid
st.markdown("### Platform Capabilities")

col1, col3 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>📁 Data Upload & Processing</h3>
        <p>Upload Excel files with ticket data. Intelligent parsing and automatic data enrichment with lookup keywords.</p>
    </div>
    """, unsafe_allow_html=True)

# with col2:
#     st.markdown("""
#     <div class="feature-box">
#         <h3>🔍 Smart Analysis Engine</h3>
#         <p>Automated categorization of tickets by feasibility (Elimination, Automation, Left-Shift). Real-time metric calculation.</p>
#     </div>
#     """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>📊 Advanced Dashboards</h3>
        <p>Interactive visualizations including donut charts, RL calculations, grade-wise MnM analysis, and optimization summaries.</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>⚙️ Non-Ticketed Activities</h3>
        <p>Configure and track non-ticketed work allocations with intelligent percentage validation and range-based constraints.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>📥 Multi-Sheet Export</h3>
        <p>Export comprehensive results including enriched data, optimization summary, and non-ticketed activities analysis.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>🎯 Resource Planning</h3>
        <p>Calculate FTE requirements, identify optimization opportunities, and generate actionable insights for resource allocation.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider-premium"></div>', unsafe_allow_html=True)

# Quick Start Section
st.markdown("### Quick Start Guide")

with st.expander("▶ Step 1: Upload Your Data", expanded=False):
    st.info("""
    1. Click on **Home** in the left sidebar
    2. Upload your Excel file containing ticket data
    3. Preview the data to ensure it's correct
    """)

with st.expander("▶ Step 2: Configure Settings", expanded=False):
    st.info("""
    1. Indicate if you have non-ticketed activities (YES/NO)
    2. If YES: Select effort allocation range (0%-50%)
    3. Select activities and enter custom percentages
    """)

with st.expander("▶ Step 3: Process & Analyze", expanded=False):
    st.info("""
    1. Click **Process & Go to Dashboard**
    2. View comprehensive analytics and insights
    3. Review GradeWise MnM RL and optimization recommendations
    """)

with st.expander("▶ Step 4: Download Results", expanded=False):
    st.info("""
    1. Click **Download Complete Results**
    2. Receive Excel file with all analysis
    3. Share insights with stakeholders
    """)

st.markdown('<div class="divider-premium"></div>', unsafe_allow_html=True)

# Status Section
st.markdown("### Current Status")

col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.df_uploaded is not None:
        st.markdown('<span class="status-badge status-ready">✅ DATA READY</span>', unsafe_allow_html=True)
        st.success(f"📁 File: {st.session_state.file_name}")
    else:
        st.markdown('<span class="status-badge status-pending">⏳ AWAITING DATA</span>', unsafe_allow_html=True)
        st.warning("No data uploaded yet")

with col2:
    if st.session_state.processed:
        st.markdown('<span class="status-badge status-ready">✅ PROCESSED</span>', unsafe_allow_html=True)
        st.success("Ready for analysis")
    else:
        st.markdown('<span class="status-badge status-pending">⏳ PENDING</span>', unsafe_allow_html=True)
        st.warning("Awaiting processing")

with col3:
    st.markdown('<span class="status-badge status-ready">✅ SYSTEM ACTIVE</span>', unsafe_allow_html=True)
    st.success("All systems operational")

st.markdown('<div class="divider-premium"></div>', unsafe_allow_html=True)

# Call to Action
# st.markdown("""
# <div style="background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%); padding: 30px; border-radius: 10px; text-align: center; color: white; margin: 20px 0;">
#     <h2 style="margin: 0; color: white;">Ready to optimize your resource allocation?</h2>
#     <p style="margin: 10px 0; font-size: 16px;">Click <b>Home</b> in the sidebar to get started</p>
# </div>
# """, unsafe_allow_html=True)

# st.page_link("pages/01_Home.py", label="Home", help="Go to Home page")
# st.markdown(
#     """
#     <div style="background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
#                 padding: 30px; border-radius: 10px; text-align: center; color: white; margin: 20px 0;">
#         <h2 style="margin: 0; color: white;">Ready to optimize your resource allocation?</h2>
#         <p style="margin: 10px 0; font-size: 16px;">
#             Click st.page_link("pages/01_Home.py", label="Home", help="Go to Home page")
#  in the sidebar to get started""",
#     unsafe_allow_html=True
# )




# Home link button
#button1 = st.page_link("pages/01_Home.py", label="Home", help="Go to Home page")



# Footer
st.markdown("""
<div class="footer">
    <p><strong>AutoOptix v1.0</strong> | Analyze tickets. Optimize operations. Forecast resources.</p>
    <p>Powered by Streamlit | © 2025 Enterprise Solutions</p>
</div>
""", unsafe_allow_html=True)
