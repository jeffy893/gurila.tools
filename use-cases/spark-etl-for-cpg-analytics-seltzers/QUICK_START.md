# 🚀 Quick Start Guide - Beer-to-Seltzer Analysis Pipeline

## 📋 Prerequisites
```bash
# Environment Setup
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
export PYSPARK_PYTHON="python3.10"
export PYSPARK_DRIVER_PYTHON="python3.10"

# Install Dependencies
pip3.10 install pyspark pandas matplotlib seaborn plotly pyyaml reportlab
```

## ⚡ Quick Execution
```bash
# Run complete analysis (recommended)
python3.10 archive/core_pipeline/run_orchestrated_pipeline.py

# Alternative: simplified pipeline
python3.10 archive/core_pipeline/run_complete_analysis.py
```

## 📊 Expected Outputs
- **PDF Report**: `output/reports/beer_seltzer_analysis_report_*.pdf`
- **Charts**: `charts/*.png`
- **Data**: `visualization_data/*.csv`

## 🎯 Key Results
- **Recommendation**: PROCEED WITH HARD SELTZER MARKET ENTRY
- **Investment**: $2,964,237 (Moderate scenario)
- **ROI**: 50% annually
- **Market Opportunity**: $11.39M (97.7% untapped)

## 📚 Documentation
- **Complete Guide**: `archive/documentation/README_FINAL.md`
- **Technical Details**: `archive/documentation/TECHNICAL_DOCUMENTATION.md`
- **Business Summary**: `archive/documentation/BUSINESS_EXECUTIVE_SUMMARY.md`

## 🔍 Quality Validation
```bash
# Run data quality tests
python3.10 archive/quality_assurance/simple_data_quality_tests.py
```

---
*For detailed information, see the complete documentation in the archive/documentation/ directory.*
