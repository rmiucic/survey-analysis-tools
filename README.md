# Survey Analysis Tools

A collection of Python tools for analyzing maternity survey data, built with Streamlit for interactive data visualization and statistical analysis.

## Overview

This repository contains specialized tools for analyzing survey data related to maternity experiences, mental health, education, and support systems. The tools are designed to provide both basic visualization and advanced statistical analysis of survey responses.

## Files

### Main Applications
- **`survey_analyzer.py`** - Basic Streamlit application for general survey analysis
  - Demographics visualization
  - Birth experience analysis  
  - Cross-variable analysis
  - Text response word clouds
  - Raw data exploration

- **`survey_analyzer_enhanced.py`** - Advanced Streamlit application with specialized maternity survey analysis
  - Statistical significance testing (Chi-square tests)
  - Education vs birth satisfaction analysis
  - Mental health vs family planning correlations
  - Support systems analysis
  - Comprehensive demographics with correlations

### Data Analysis Scripts
- **`analyze_questions.py`** - Categorizes survey questions by type (categorical, rating, yes/no, text)
- **`examine_data.py`** - Basic data exploration and structure analysis
- **`find_key_questions.py`** - Identifies key variables for relationship analysis

### Requirements
- **`requirements_enhanced.txt`** - Dependencies for the enhanced analyzer
- **`requirements_streamlit.txt`** - Basic dependencies for Streamlit applications

## Features

### Basic Analysis
- Automatic question type detection
- Interactive charts and visualizations
- Demographics breakdowns
- Text analysis with word clouds
- Data export capabilities

### Advanced Analysis
- Statistical significance testing
- Cross-variable relationship analysis
- Mental health indicators analysis
- Education level correlations
- Support system effectiveness analysis
- P-value calculations and interpretations

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements_enhanced.txt
   ```

## Usage

### Run Basic Analyzer
```bash
streamlit run survey_analyzer.py
```

### Run Enhanced Analyzer
```bash
streamlit run survey_analyzer_enhanced.py
```

### Run Data Analysis Scripts
```bash
python examine_data.py
python analyze_questions.py
python find_key_questions.py
```

## Data Requirements

- Excel files (.xlsx, .xls) or CSV files
- First row should contain question headers
- Each row represents one survey response
- Designed for maternity/pregnancy survey data with Serbian language support

## Key Analysis Features

- **Education vs Satisfaction**: Statistical analysis of how educational background relates to birth experience
- **Mental Health Impact**: Relationships between postpartum depression and family planning decisions  
- **Support System Analysis**: Correlation between partner support and mental health outcomes
- **Statistical Significance**: Chi-square tests and p-values for all relationships
- **Interactive Visualizations**: Plotly charts, heatmaps, and cross-tabulations

## Technical Stack

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive visualizations
- **SciPy** - Statistical testing
- **WordCloud** - Text analysis visualization
- **Matplotlib/Seaborn** - Additional plotting capabilities

## License

This project is designed for research and analysis purposes.