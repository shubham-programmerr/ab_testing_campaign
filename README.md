# A/B Testing Campaign Analysis Project

This A/B Testing Campaign Analysis Project is a comprehensive end-to-end framework designed to conduct rigorous, statistically sound A/B tests that drive informed business decisions. Starting with power analysis to determine optimal sample sizes, the project guides users through data cleaning and validation using Sample Ratio Mismatch checks to ensure randomization integrity. It then applies appropriate statistical tests (t-tests, chi-square, proportion tests) tailored to different metric types, calculates effect sizes and confidence intervals, and performs segmented analysis to uncover heterogeneous treatment effects across user demographics and device types. All results are synthesized in an interactive Streamlit dashboard featuring KPI cards, funnel charts, distribution visualizations, and segment heatmaps, making it easy to explore findings and export results. The final output translates complex statistical analyses into actionable business recommendations with projected revenue impact, enabling stakeholders to confidently decide whether to deploy, monitor, or continue testing a variant.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   cd "c:\Personal_file\data analytic project"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your data**
   - Place your A/B test CSV file in `data/raw/` directory
   - Required columns: `user_id`, `variant` (control/treatment), `metric`, `timestamp`
   - Optional: demographic/device columns for segmentation

### Running the Project

#### Option 1: Interactive Streamlit Dashboard
```bash
cd dashboard
streamlit run app.py
```
Then open your browser to `http://localhost:8501`

#### Option 2: Jupyter Notebooks (Step-by-step Analysis)
```bash
# Run notebooks in sequence
jupyter notebook notebooks/
```

Order of execution:
1. `01_eda.ipynb` - Exploratory Data Analysis
2. `02_preprocessing.ipynb` - Data Cleaning & Validation
3. `03_statistical_tests.ipynb` - Statistical Testing & Power Analysis
4. `04_visualization.ipynb` - Create Visualizations
5. `05_report_summary.ipynb` - Generate Report & Recommendations

## 📊 Project Structure

```
.
├── config.yaml                 # Project configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── data/
│   ├── raw/                   # Place your CSV data here
│   └── processed/             # Cleaned data output
│
├── src/                        # Core Python modules
│   ├── data_loader.py         # Load and validate data
│   ├── preprocessing.py       # Data cleaning & SRM checks
│   ├── stats_tests.py         # Statistical testing functions
│   ├── sample_size.py         # Power analysis & sample size
│   ├── visualizations.py      # Plotting functions
│   └── utils.py               # Utility functions
│
├── notebooks/                 # Jupyter notebooks
│   ├── 01_eda.ipynb           # Exploratory Data Analysis
│   ├── 02_preprocessing.ipynb # Data preprocessing
│   ├── 03_statistical_tests.ipynb # Statistical analysis
│   ├── 04_visualization.ipynb # Visualizations
│   └── 05_report_summary.ipynb # Final report
│
├── dashboard/                 # Streamlit dashboard
│   ├── app.py                 # Main app
│   ├── layout.py              # UI components
│   └── callbacks.py           # Data processing logic
│
└── reports/                   # Output reports
    └── figures/               # Generated visualizations
```

## 🔧 Core Features

### 1. **Power Analysis**
- Calculate required sample sizes for continuous and binary metrics
- Support for custom alpha, power, and effect size parameters
- T-test and chi-square test design

### 2. **Data Validation**
- Check for Sample Ratio Mismatch (SRM) to ensure randomization
- Data quality checks (duplicates, missing values)
- Automatic outlier detection and handling

### 3. **Statistical Testing**
- **Continuous Metrics**: Independent samples t-test
- **Binary Metrics**: Two-proportion z-test, Chi-square test
- Effect size calculation (Cohen's d, Cramér's V)
- 95% confidence intervals

### 4. **Segmentation Analysis**
- Heterogeneous treatment effects by demographics
- Device type analysis
- Geographic/regional breakdown
- Custom segment definitions

### 5. **Interactive Dashboard**
- Real-time data exploration
- Distribution visualizations
- Segment heatmaps
- KPI cards and funnel charts
- One-click report generation

## 📈 Configuration

Edit `config.yaml` to customize:

```yaml
power_analysis:
  alpha: 0.05              # Significance level
  power: 0.80              # Statistical power
  effect_size: 0.2         # Minimum detectable effect (Cohen's d)

statistical_tests:
  default_alpha: 0.05      # P-value threshold
  confidence_level: 0.95   # Confidence intervals

segmentation:
  demographics:
    - age_group
    - gender
    - region
  device_types:
    - mobile
    - desktop
    - tablet
```

## 📊 Sample Data Format

Your CSV should include:

| user_id | variant | metric | timestamp | age_group | device_type |
|---------|---------|--------|-----------|-----------|-------------|
| user_001 | control | 45.2 | 2024-01-01 | 25-34 | mobile |
| user_002 | treatment | 52.8 | 2024-01-01 | 35-44 | desktop |
| user_003 | control | 41.5 | 2024-01-02 | 18-24 | tablet |

## 🎯 Interpretation Guide

### P-Value Interpretation
- **p < 0.05**: Statistically significant result
- **0.05 ≤ p < 0.10**: Borderline significance (continue monitoring)
- **p ≥ 0.10**: Not significant (no evidence of difference)

### Effect Size (Cohen's d)
- **0.0 - 0.2**: Negligible effect
- **0.2 - 0.5**: Small effect
- **0.5 - 0.8**: Medium effect
- **> 0.8**: Large effect

### Recommendations

| Result | Decision |
|--------|----------|
| Significant + Positive | ✅ Deploy |
| Significant + Negative | ❌ Stop & Revert |
| Borderline Significant | ⏳ Continue Monitoring |
| Not Significant | 📊 Inconclusive |

## 🛠️ Development

### Adding Custom Metrics
Edit `src/stats_tests.py` to add new test types:

```python
@staticmethod
def custom_test(control, treatment, alpha=0.05):
    # Your test implementation
    return results
```

### Extending Dashboard
Edit `dashboard/app.py` to add new analysis pages:

```python
elif page == "New Analysis":
    show_new_analysis_page(df)
```

## 📝 Example Workflow

1. **Prepare Data**
   ```bash
   # Place your file in data/raw/your_experiment.csv
   ```

2. **Run Dashboard**
   ```bash
   cd dashboard
   streamlit run app.py
   ```

3. **Upload Data**
   - Use the file uploader in the sidebar
   - Dashboard validates and processes automatically

4. **Review Results**
   - Check statistical significance and effect sizes
   - Analyze segment-level effects
   - Export final report

5. **Make Decision**
   - Follow recommendations for deployment
   - Document findings in `reports/`

## 🤝 Contributing

To add features or fix bugs:

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit for review

## 📞 Support & Documentation

- **API Reference**: See docstrings in `src/` modules
- **Statistical Methods**: See comments in `src/stats_tests.py`
- **Dashboard Guide**: Check dashboard page titles for guidance

## ⚠️ Important Notes

- **Minimum Sample Size**: At least 30 observations per group recommended
- **Data Requirements**: Ensure proper randomization and data quality
- **Multiple Testing**: Be careful with multiple comparisons across segments
- **Business Context**: Always consider business impact alongside statistics

## 📄 License

This project is provided as-is for A/B testing analysis.

## 🎓 Learn More

- A/B Testing Theory: https://en.wikipedia.org/wiki/A/B_testing
- Statistical Power: https://en.wikipedia.org/wiki/Statistical_power
- Effect Sizes: https://en.wikipedia.org/wiki/Effect_size
- Streamlit Documentation: https://docs.streamlit.io/

---

**Ready to begin your A/B testing analysis?** 
1. Prepare your data
2. Run `cd dashboard && streamlit run app.py`
3. Upload your data and explore!

Happy testing! 🚀📊