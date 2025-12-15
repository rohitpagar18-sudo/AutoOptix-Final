# Automation Utility Dashboard

A Streamlit-based analytics dashboard for Excel data processing and visualization.

## Project Structure

\\\
 app.py                          # Main Streamlit entry point
 pages/
    01_Home.py                  # File upload and data processing
    02_Dashboard.py             # Analytics visualization
 merge_by_subgroup_final.py      # Data matching and merging logic
 process_excel.py                # Excel processing and calculations
 other_recommended_tools.py       # Tool recommendation calculations
 rl_calculations.py              # RL (Remaining Load) calculations
 utilization_graphs.py           # Utilization graph calculations
 lookup.xlsx                     # Lookup data for matching
 requirements.txt                # Python dependencies
 README.md                       # This file
\\\

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Install dependencies:
\\\ash
pip install -r requirements.txt
\\\

2. Run the application:
\\\ash
streamlit run app.py
\\\

3. Open your browser to \http://localhost:8501\

## Usage

### Home Page
- Upload your Excel file
- Preview merged and unmatched data
- View processing logs

### Dashboard Page
- **Utilization Graphs**: Three donut charts showing Elimination, Automation Standard, and Automation Agentic AI
- **Optimization Summary**: Lever analysis with Volume and FTE metrics
- **Overall RL**: Three-period analysis (H1Y1, H2Y1, H1Y2) with minimum value of 7
- **Other Recommended Tools**: Conditional tool recommendations based on thresholds
- **GradeWise MnM RL**: 18-month performance matrix by grade

## Key Calculations

### Volume & FTE
- Volume = Total tickets / Number of months
- FTE = Volume / 140

### Overall RL (Remaining Load)
- Base RL = L1.5 per month / 140
- H1Y1 = Base RL - FTE_Elimination
- H2Y1 = Base RL - FTE_Elimination - ((FTE_Automation + FTE_Agentic)  50%)
- H1Y2 = Base RL - FTE_Elimination - FTE_Automation - FTE_Agentic
- Minimum RL value: 7

### Utilization Graphs
- Lever Value = FTE_Lever / (L1.5 per month / 140)
- Percentages = (Lever Value / Total)  100

## Data Format

### Expected Columns in Excel
- \L1_L2\ or \L1/L2\: Ticket level classification
- \Closed Month\: Month when ticket was closed
- \Elimination_Feasibility\: Feasibility flag
- \Automation_Feasibility\: Feasibility flag
- \Automation_Approach\: Standard/Agentic AI classification
- \Left_Shift_Feasibility\: Feasibility flag
- \UseCase\: Use case classification
- \Priority\: P1 or P2 classification

## Output Formatting

All numeric values are displayed with exactly **2 decimal places** across:
- Process Excel calculations
- Utilization graph values and percentages
- RL calculations
- All Dashboard tables

## Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: pandas, openpyxl
- **Visualization**: matplotlib
- **Language**: Python 3.8+
