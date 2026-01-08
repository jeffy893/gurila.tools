# PySpark Local Setup Guide for macOS

## Prerequisites Check

First, let's check what you already have installed:

```bash
# Check Python version (need 3.7+)
python3 --version

# Check if Java is installed
java -version

# Check if Homebrew is installed
brew --version
```

## Step 1: Install Java (Required for Spark)

PySpark requires Java 8, 11, or 17. Let's install Java 11:

```bash
# Install Java 11 using Homebrew
brew install openjdk@11

# Add Java to your PATH (add to ~/.zshrc)
echo 'export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
echo 'export JAVA_HOME="/opt/homebrew/opt/openjdk@11"' >> ~/.zshrc

# Reload your shell configuration
source ~/.zshrc

# Verify Java installation
java -version
javac -version
```

## Step 2: Install PySpark

```bash
# Install PySpark using pip
pip3 install pyspark

# Or if you prefer conda
# conda install pyspark

# Verify PySpark installation
pip3 show pyspark
```

## Step 3: Set Environment Variables

Add these to your `~/.zshrc` file:

```bash
# Open your shell configuration
nano ~/.zshrc

# Add these lines:
export JAVA_HOME="/opt/homebrew/opt/openjdk@11"
export SPARK_HOME="/opt/homebrew/lib/python3.10/site-packages/pyspark"
export PATH="$SPARK_HOME/bin:$PATH"
export PYTHONPATH="$SPARK_HOME/python:$PYTHONPATH"

# Reload configuration
source ~/.zshrc
```

## Step 4: Verify Installation

```bash
# Test Spark shell (should open interactive shell)
pyspark

# In the PySpark shell, try:
# spark.version
# sc.parallelize([1,2,3,4,5]).collect()
# exit()

# Test spark-submit command
spark-submit --version
```

## Step 5: Install Additional Dependencies

```bash
# Install additional Python packages for data analysis
pip3 install pandas numpy matplotlib plotly jupyter

# For better performance with large datasets
pip3 install pyarrow
```

## Troubleshooting

### Common Issues:

1. **Java not found**: Make sure JAVA_HOME is set correctly
2. **Permission errors**: Use `sudo` if needed for system-wide installation
3. **Path issues**: Ensure all paths in ~/.zshrc are correct

### Verification Commands:

```bash
# Check all environment variables
echo $JAVA_HOME
echo $SPARK_HOME
echo $PATH | grep spark

# Test Python can import PySpark
python3 -c "import pyspark; print(pyspark.__version__)"
```

## Alternative: Docker Setup (Optional)

If you prefer Docker:

```bash
# Pull official Spark image
docker pull apache/spark-py:latest

# Run Spark in Docker
docker run -it --rm apache/spark-py:latest /opt/spark/bin/pyspark
```

## Next Steps

Once installation is complete:
1. Run the verification script: `python3 spark_hello_world.py`
2. Initialize your PySpark environment: `python3 spark_init.py`
3. Process the synthetic data: `python3 spark_etl_pipeline.py`