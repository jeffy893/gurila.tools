# Beer Company POS Analysis with PySpark

A comprehensive data engineering portfolio project demonstrating end-to-end ETL, data analysis, and anomaly detection using PySpark. This project simulates a traditional beer company discovering the rapid rise of hard seltzers through Point of Sale (POS) data analysis.

## 🎯 Project Overview

**Business Scenario**: You are a data analyst for a traditional beer company. Through analysis of POS data, you need to discover a market anomaly: the rapid rise of hard seltzers. The final output is a pipeline that ingests raw data and produces a report recommending the company pivot into hard seltzers.

**Key Findings**: The analysis reveals a clear pivot point in February 2023 where hard seltzer growth (10.9%) overtakes beer growth (-0.1%), demonstrating a fundamental market shift requiring strategic action.

## 📊 Generated Data Overview

- **Products**: 120 items (74 beers, 46 hard seltzers)
- **Locations**: 1,441 retail locations across 5 US regions
- **Transactions**: 887,849 POS transactions over 12 months
- **Total Revenue**: $11.2M with clear category trend patterns

## 🛠️ Prerequisites

- **macOS** (tested on macOS Sequoia)
- **Python 3.10+**
- **Homebrew** package manager
- **4GB+ RAM** recommended for Spark processing

## 📋 Installation Guide

### Step 1: Install Java 17 (Required for PySpark)

```bash
# Install Java 17 using Homebrew
brew install openjdk@17

# Add Java to your PATH (add to ~/.zshrc)
echo 'export JAVA_HOME="/opt/homebrew/opt/openjdk@17"' >> ~/.zshrc
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc

# Reload shell configuration
source ~/.zshrc

# Verify Java installation
java -version
```

### Step 2: Install Python Dependencies

```bash
# Install PySpark and data science libraries
pip3 install pyspark==3.5.3 pandas numpy matplotlib plotly pyarrow

# Verify PySpark installation
python3 -c "import pyspark; print('PySpark version:', pyspark.__version__)"
```

### Step 3: Set Environment Variables

Add these to your `~/.zshrc` file:

```bash
# Java Configuration
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# PySpark Configuration
export PYSPARK_PYTHON=python3.10
export PYSPARK_DRIVER_PYTHON=python3.10
```

Then reload: `source ~/.zshrc`

## 🚀 Quick Start

### 1. Verify Installation

```bash
# Test PySpark installation and configuration
python3.10 spark_hello_world.py
```

Expected output: All 6 tests should pass ✅

### 2. Generate Synthetic Data

```bash
# Generate sample dataset (fast - for testing)
python3.10 simple_data_generator.py

# OR generate full dataset (comprehensive - for production)
python3.10 data_generator.py
```

### 3. Run PySpark Analysis

```bash
# Initialize and test Spark environment
python3.10 spark_init.py

# Run complete ETL pipeline
python3.10 spark_etl_pipeline.py
```

## 📁 Project Structure

```
spark-seltzers/
├── README.md                          # This file
├── PYSPARK_SETUP.md                   # Detailed setup guide
├── pyspark_beer_seltzer_prompts.csv   # LLM prompt sequence
├── install_pyspark.sh                 # Automated installation script
│
├── Data Generation:
│   ├── simple_data_generator.py       # Quick sample data (recommended)
│   └── data_generator.py              # Full comprehensive dataset
│
├── PySpark Environment:
│   ├── spark_hello_world.py           # Installation verification
│   ├── spark_init.py                  # Environment initialization
│   └── spark_etl_pipeline.py          # Complete analysis pipeline
│
└── synthetic_data/                    # Generated CSV files
    ├── products.csv                   # Product catalog
    ├── locations.csv                  # Retailer locations
    └── sales_transactions.csv         # POS transaction data
```

## 🔧 Usage Commands

### Environment Setup Commands

```bash
# Complete environment setup (one-time)
chmod +x install_pyspark.sh
./install_pyspark.sh

# Manual verification
JAVA_HOME="/opt/homebrew/opt/openjdk@17" \
PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH" \
PYSPARK_PYTHON=python3.10 \
PYSPARK_DRIVER_PYTHON=python3.10 \
python3.10 spark_hello_world.py
```

### Data Generation Commands

```bash
# Quick sample data (recommended for testing)
python3.10 simple_data_generator.py

# Full dataset with comprehensive features
python3.10 data_generator.py
```

### PySpark Analysis Commands

```bash
# Set environment variables for all Spark commands
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
export PYSPARK_PYTHON=python3.10
export PYSPARK_DRIVER_PYTHON=python3.10

# Initialize Spark environment
python3.10 spark_init.py

# Run complete ETL pipeline
python3.10 spark_etl_pipeline.py
```

## 📊 Expected Results

### Key Business Insights

1. **Market Pivot Point**: February 2023
   - Hard Seltzer Growth: **10.9%**
   - Beer Growth: **-0.1%**
   - Advantage: **11.0 percentage points**

2. **Final Market Position** (December 2023):
   - Beer Revenue: **$873,897**
   - Seltzer Revenue: **$49,121**
   - Seltzer Market Share: **5.3%**

3. **Strategic Recommendations**:
   - Immediate launch of hard seltzer product line
   - Focus on gas station and convenience channels
   - 6-month timeline for market entry
   - Pivot marketing to wellness trends

### Sample Output

```
🚨 MARKET PIVOT DETECTED: 2023-02
   Seltzer Growth: 10.9%
   Beer Growth: -0.1%
   Advantage: 11.0 percentage points

📊 FINAL MARKET POSITION (December 2023):
   Beer Revenue: $873,897.12
   Seltzer Revenue: $49,121.05
   Seltzer Market Share: 5.3%

💡 STRATEGIC RECOMMENDATIONS:
   1. IMMEDIATE: Launch hard seltzer product line
   2. PRIORITY: Focus on Gas Station region first
   3. TIMELINE: Market entry within 6 months to capture growth
```

## 🐛 Troubleshooting

### Common Issues

1. **Java Version Mismatch**
   ```bash
   # Error: UnsupportedClassVersionError
   # Solution: Ensure Java 17 is installed and JAVA_HOME is set
   java -version  # Should show OpenJDK 17
   echo $JAVA_HOME  # Should point to Java 17
   ```

2. **Python Version Mismatch**
   ```bash
   # Error: PYTHON_VERSION_MISMATCH
   # Solution: Set PySpark Python variables
   export PYSPARK_PYTHON=python3.10
   export PYSPARK_DRIVER_PYTHON=python3.10
   ```

3. **PySpark Import Error**
   ```bash
   # Error: No module named 'pyspark'
   # Solution: Install PySpark
   pip3 install pyspark==3.5.3
   ```

4. **Memory Issues**
   ```bash
   # Error: OutOfMemoryError
   # Solution: Reduce dataset size or increase memory
   # Edit spark_etl_pipeline.py: .config("spark.driver.memory", "2g")
   ```

### Verification Steps

```bash
# Check all prerequisites
java -version                    # Should show OpenJDK 17
python3.10 --version            # Should show Python 3.10+
echo $JAVA_HOME                  # Should point to Java 17
echo $PYSPARK_PYTHON            # Should be python3.10
pip3 show pyspark               # Should show version 3.5.3

# Test complete pipeline
python3.10 spark_hello_world.py  # All tests should pass
python3.10 simple_data_generator.py  # Should generate data
python3.10 spark_etl_pipeline.py     # Should show analysis results
```

## 🎓 Learning Objectives

This project demonstrates:

- **PySpark Setup**: Local development environment configuration
- **Data Generation**: Realistic synthetic dataset creation
- **ETL Pipeline**: Data ingestion, transformation, and analysis
- **Business Intelligence**: Trend analysis and anomaly detection
- **Strategic Insights**: Data-driven business recommendations

## 📈 Extensions

### Advanced Analytics
- Add predictive modeling for future trend forecasting
- Implement customer segmentation analysis
- Create real-time streaming analytics

### Visualization
- Connect to Tableau/Power BI for executive dashboards
- Build interactive Plotly visualizations
- Create automated reporting systems

### Production Deployment
- Containerize with Docker
- Deploy to cloud platforms (AWS EMR, Databricks)
- Implement CI/CD pipelines

## 🤝 Contributing

This is a portfolio project demonstrating data engineering skills. Feel free to:
- Fork and extend the analysis
- Add new data sources or metrics
- Improve the synthetic data generation
- Enhance the visualization components

## 📄 License

This project is for educational and portfolio purposes. The synthetic data and analysis methods can be freely used and modified.

---

**🍺➡️🥤 Ready to discover your market disruption? Start with the Quick Start guide above!**