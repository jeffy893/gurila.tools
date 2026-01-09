# Quick Reference - PySpark Beer Analysis

## 🚀 Essential Commands

### One-Time Setup
```bash
# Install dependencies
brew install openjdk@17
pip3 install pyspark==3.5.3 pandas numpy matplotlib plotly pyarrow

# Set environment variables (add to ~/.zshrc)
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
export PYSPARK_PYTHON=python3.10
export PYSPARK_DRIVER_PYTHON=python3.10

# Reload shell
source ~/.zshrc
```

### Daily Usage
```bash
# 1. Verify setup
python3.10 spark_hello_world.py

# 2. Generate data
python3.10 simple_data_generator.py

# 3. Run analysis
python3.10 spark_etl_pipeline.py
```

## 📊 Expected Output

**Key Finding**: Market pivot detected in February 2023
- Seltzer Growth: **10.9%** 
- Beer Growth: **-0.1%**
- Final Seltzer Market Share: **5.3%**

## 🐛 Quick Fixes

**Java Error**: `brew install openjdk@17` + set JAVA_HOME
**Python Error**: Set `PYSPARK_PYTHON=python3.10`
**Import Error**: `pip3 install pyspark==3.5.3`
**Memory Error**: Reduce dataset size in simple_data_generator.py

## 📁 Key Files

- `spark_hello_world.py` - Verify installation
- `simple_data_generator.py` - Generate sample data  
- `spark_etl_pipeline.py` - Run complete analysis
- `synthetic_data/` - Generated CSV files
- `README.md` - Full documentation