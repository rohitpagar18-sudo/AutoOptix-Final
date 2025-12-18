# AutoOptix: Ticket Optimization & Resource Forecasting Platform

A comprehensive Streamlit-based analytics platform designed to analyze ticket data, optimize resource allocation, and forecast operational efficiency gains through data-driven insights.

## Project Overview

AutoOptix solves the critical business problem of inefficient resource allocation in ticket management operations. By analyzing historical ticket data, the platform identifies automation opportunities across multiple levers (Elimination, Automation, and Left Shift), calculates precise resource requirements, and provides actionable recommendations for operational improvements.

The platform serves organizations by:
- **Analyzing** ticket patterns and identifying optimization opportunities
- **Optimizing** resource allocation through evidence-based FTE calculations
- **Forecasting** efficiency gains across different implementation timelines
- **Generating** professional reports with clear business impact metrics

## Business Concepts & Terminology

### Full-Time Equivalent (FTE)
FTE represents the workload equivalent of one full-time employee. In this project, FTE is calculated as:

**FTE = Volume / 140**

Where:
- **Volume** = Total eligible tickets per month
- **140** represents the standard monthly ticket handling capacity per FTE (based on industry benchmarks for L1.5 ticket resolution)

This formula assumes a baseline productivity of 140 tickets per month per FTE, which is derived from standard service desk metrics and historical performance data.

### Why FTE = 140?
The value 140 is based on:
- Industry-standard ticket resolution rates for L1.5 support
- Historical performance data showing average monthly ticket volumes
- Standard working hours and productivity assumptions
- Conservative estimates accounting for non-ticket activities

### How FTE is Used in Calculations
FTE values drive all optimization calculations:
- **Resource Planning**: Determines staffing requirements after automation
- **Cost Analysis**: Enables budget forecasting for optimization initiatives
- **ROI Calculations**: Measures efficiency gains in FTE terms
- **Capacity Planning**: Identifies resource gaps or surpluses

## Detailed Logic Explanation

### Data Processing Flow
1. **Upload**: Excel file containing ticket data with required columns
2. **Merge**: Data enrichment using keyword matching against lookup.xlsx
3. **Calculate**: FTE values for each optimization lever
4. **Analyze**: RL (Remaining Load) calculations for different scenarios
5. **Visualize**: Interactive dashboards with charts and tables

### Volume & FTE Calculation
For each optimization lever (Elimination, Automation, Left Shift):

```
Volume = Total eligible tickets / Number of months
FTE = Volume / 140
```

**Example:**
- 840 tickets over 6 months = 140 tickets/month
- FTE = 140 / 140 = 1.0 FTE

### Overall RL (Remaining Load) Calculations
RL represents the resource load remaining after applying optimizations:

**Base RL = L1.5 tickets per month / 140**

**H1Y1 (Year 1, Half 1)**: 140 productivity, elimination only
```
H1Y1 = Base RL - FTE_Elimination
```

**H2Y1 (Year 1, Half 2)**: 160 productivity, elimination + 50% automation
```
H2Y1 = Base RL - FTE_Elimination - ((FTE_Automation + FTE_Agentic) × 50%)
```

**H1Y2 (Year 2, Half 1)**: 160 productivity, full optimization
```
H1Y2 = Base RL - FTE_Elimination - FTE_Automation - FTE_Agentic
```

**Minimum RL**: All calculations are floored at 7 FTE to ensure minimum staffing levels.

### Utilization Graphs
Three donut charts showing optimization distribution:

**Lever Value = FTE_Lever / (L1.5 per month / 140)**

**Percentage = (Lever Value / Total) × 100**

### GradeWise MnM RL
18-month resource planning matrix by grade level:
- **PAT/PT**: 30% of Total RL
- **PA/P**: 60% of Total RL
- **A**: 10% of Total RL
- **SA**: Tiered logic (4 FTE if RL ≥150, 3 if ≥100, etc.)
- **M**: Binary logic (2 FTE if RL ≥100, 1 if ≥50)
- **SM**: Binary logic (1 FTE if RL ≥150)

## File-by-File Breakdown

### Core Application Files
- **`AutoOptix_Overview.py`**: Main Streamlit application entry point with overview dashboard, styling, and navigation
- **`pages/01_Home.py`**: File upload interface, data preview, non-ticketed activity configuration, and processing triggers
- **`pages/02_Dashboard.py`**: Analytics visualization with charts, tables, and downloadable reports

### Processing Modules
- **`process_excel.py`**: Core calculation engine for FTE, volumes, and optimization arrays
- **`merge_by_subgroup_final.py`**: Data enrichment via keyword matching against lookup.xlsx
- **`rl_calculations.py`**: Remaining Load calculations for H1Y1/H2Y1/H1Y2 scenarios and grade-wise planning
- **`utilization_graphs.py`**: Utilization percentage calculations for optimization levers
- **`other_recommended_tools.py`**: Conditional tool recommendations based on threshold analysis

### Configuration & Data Files
- **`lookup.xlsx`**: Reference data for ticket categorization and feasibility flags
- **`requirements.txt`**: Python dependencies (Streamlit, pandas, openpyxl, matplotlib)
- **`summary_output.json`**: Calculation results storage
- **`styles_*.css`**: UI styling for different application sections

## Automation Flow

1. **Data Upload** (Home Page)
   - Upload Excel file with ticket data
   - Preview sheets and validate columns
   - Configure non-ticketed activities (optional)

2. **Data Processing**
   - Keyword matching against lookup.xlsx
   - Enrichment with feasibility flags and use cases
   - Calculation of optimization metrics

3. **Analysis & Visualization** (Dashboard)
   - Utilization graphs (Elimination/Automation/Agentic AI)
   - Overall RL analysis (H1Y1/H2Y1/H1Y2)
   - GradeWise MnM RL matrix
   - Tool recommendations

4. **Report Generation**
   - Multi-sheet Excel export
   - JSON summary output
   - Interactive visualizations

## Configurations & Assumptions

### Hardcoded Values
- **FTE Divisor**: 140 tickets per month per FTE
- **RL Minimum**: 7 FTE (floor value for calculations)
- **Automation Productivity**: 50% for H2Y1, 100% for H1Y2
- **Grade Distribution**: PAT/PT (30%), PA/P (60%), A (10%)

### Assumptions
- L1.5 tickets only for optimization calculations
- Monthly volume averaging for FTE calculations
- Standard feasibility flags in lookup data
- Non-ticketed activities ≤50% of total effort
- Base non-ticketed inclusion of 15% in RL calculations

### Environmental Expectations
- Excel files with consistent column naming
- UTF-8 encoding for text data
- Minimum 1 month of historical data
- Lookup.xlsx in working directory

## How to Run the Project

### Prerequisites
- Python 3.8+
- pip package manager
- Modern web browser

### Installation
```bash
# Clone or download the project
cd python_automation_utility

# Install dependencies
pip install -r requirements.txt
```

### Execution
```bash
# Launch the Streamlit application
streamlit run AutoOptix_Overview.py
```

### Usage Steps
1. Open browser to http://localhost:8501
2. Navigate to Home page
3. Upload Excel file with ticket data
4. Configure non-ticketed activities (optional)
5. Click "Process & Go to Dashboard"
6. Review analytics and download reports

## Outputs & Interpretation

### Generated Files
- **`summary_output.json`**: Raw calculation results
- **`Complete_Results.xlsx`**: Multi-sheet analysis export
  - Sheet 1: Enriched Data (processed tickets)
  - Sheet 2: Optimization Summary (lever analysis)
  - Sheet 3: Non-Ticketed Activities (if configured)

### Dashboard Visualizations
- **Utilization Graphs**: Three donut charts showing optimization distribution percentages
- **Overall RL**: Three-period analysis with FTE requirements
- **GradeWise MnM RL**: 18-month staffing matrix by grade
- **Optimization Summary**: Lever-by-lever FTE and volume metrics

### Business Interpretation
- **FTE Values**: Direct staffing impact (negative = reduction opportunity)
- **RL Values**: Required headcount after optimizations
- **Percentages**: Relative contribution of each optimization lever
- **Grade Matrix**: Long-term resource planning by seniority level

## Error Handling & Edge Cases

### Known Limitations
- Requires minimum 1 month of historical data
- Lookup matching accuracy depends on keyword quality
- Calculations assume consistent data formatting
- Non-ticketed adjustments limited to 50% range

### Common Error Scenarios
- **Missing Columns**: Clear error messages with required field lists
- **Empty Data**: Validation checks prevent processing invalid files
- **Lookup Not Found**: Graceful fallback with default categorizations
- **Division by Zero**: Protected calculations with minimum value floors

### Data Quality Issues
- Inconsistent column naming handled via fuzzy matching
- Missing values normalized to prevent calculation errors
- Invalid dates filtered out during month aggregation

## Improvements & Extensibility

### Potential Enhancements
- **Machine Learning**: Automated feasibility prediction models
- **Real-time Integration**: API connections to live ticket systems
- **Multi-language Support**: Internationalization for global teams
- **Advanced Analytics**: Trend analysis and forecasting algorithms
- **Custom Reporting**: User-configurable dashboard layouts

### Extensibility Options
- **New Levers**: Easy addition of custom optimization categories
- **Additional Metrics**: Extensible calculation framework
- **Plugin Architecture**: Modular analysis components
- **API Endpoints**: RESTful interfaces for integration
- **Database Integration**: Persistent storage for historical analysis

### Future Development
- Containerization with Docker
- Cloud deployment options
- Batch processing capabilities
- Advanced visualization libraries
- Mobile-responsive design

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Data Processing**: pandas, openpyxl
- **Visualization**: matplotlib, Streamlit native charts
- **Language**: Python 3.8+
- **Deployment**: Local execution or cloud platforms

---

**AutoOptix v1.0** | Analyze tickets. Optimize operations. Forecast resources.
