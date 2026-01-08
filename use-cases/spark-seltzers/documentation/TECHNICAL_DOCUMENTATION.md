# 📋 Technical Documentation: Beer-to-Seltzer Market Analysis Pipeline

## 🏗️ Architecture Overview

The Beer-to-Seltzer Market Analysis Pipeline is a comprehensive PySpark-based data processing system designed to analyze market trends and provide strategic recommendations for beverage companies considering Hard Seltzer market entry.

### 🎯 **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  run_orchestrated_pipeline.py │ master_pipeline.py             │
│  • Stage Management           │ • Enterprise Orchestration     │
│  • Error Handling            │ • Fault Tolerance              │
│  • Performance Monitoring    │ • Configuration Management      │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSING LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│ Data Generation │ Ingestion │ Cleaning │ Analysis │ Reporting   │
│ simple_data_    │ spark_    │ spark_   │ spark_   │ spark_      │
│ generator.py    │ data_     │ data_    │ trend_   │ executive_  │
│                 │ ingestion │ cleaning │ analysis │ reporting   │
│                 │ .py       │ .py      │ .py      │ .py         │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│ Data Export     │ Chart Generation │ PDF Reports              │
│ spark_          │ create_          │ pdf_report_              │
│ visualization_  │ visualizations   │ generator.py             │
│ export.py       │ .py              │                          │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      UTILITY LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│ Configuration   │ Logging         │ Checkpoints │ Scheduling   │
│ config_manager  │ logging_utils   │ checkpoint_ │ scheduler    │
│ .py             │ .py             │ manager.py  │ .py          │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Schema Definitions

### **1. Products Schema**
```python
products_schema = StructType([
    StructField("SKU", StringType(), False),              # Primary Key
    StructField("Product_Name", StringType(), False),     # Product display name
    StructField("Brand", StringType(), False),            # Brand identifier
    StructField("Category", StringType(), False),         # BEER | HARD SELTZER
    StructField("ABV", DoubleType(), False),             # Alcohol by volume (0-20%)
    StructField("Package_Size", StringType(), True),      # Container size (12oz, 16oz, etc.)
    StructField("Pack_Size", IntegerType(), True),        # Units per pack (6, 12, 24)
    StructField("Price_Per_Unit", DoubleType(), False),   # Unit price ($0.01-$10.00)
    StructField("Launch_Date", StringType(), True)        # Product launch date (YYYY-MM-DD)
])
```

**Business Rules:**
- SKU: Unique identifier, format: [BRAND]_[CATEGORY]_[VARIANT]
- Category: Must be "BEER" or "HARD SELTZER"
- ABV: Range 0.1% - 20.0% (regulatory compliance)
- Price_Per_Unit: Range $0.01 - $10.00 (market reality)

### **2. Locations Schema**
```python
locations_schema = StructType([
    StructField("Retailer_ID", StringType(), False),      # Primary Key
    StructField("Store_Name", StringType(), False),       # Store display name
    StructField("Store_Type", StringType(), False),       # Grocery, Convenience, etc.
    StructField("Region", StringType(), False),           # Geographic region
    StructField("State", StringType(), False),            # US State code
    StructField("City", StringType(), True),              # City name
    StructField("Population_Density", StringType(), True), # Urban, Suburban, Rural
    StructField("Market_Tier", StringType(), True),       # Tier 1, 2, 3
    StructField("Alcohol_License", BooleanType(), False), # Licensed to sell alcohol
    StructField("Store_Size_SqFt", IntegerType(), True),  # Store size in sq ft
    StructField("Avg_Daily_Traffic", IntegerType(), True), # Average daily customers
    StructField("Competitive_Density", StringType(), True) # Low, Medium, High
])
```

**Business Rules:**
- Retailer_ID: Unique identifier, format: [REGION]_[TYPE]_[NUMBER]
- Region: NORTHEAST, SOUTHEAST, MIDWEST, SOUTHWEST, WEST
- Store_Type: Grocery, Convenience, Liquor, Gas Station, Club
- Alcohol_License: Must be True for alcohol sales

### **3. Sales Transactions Schema**
```python
sales_schema = StructType([
    StructField("Transaction_ID", StringType(), False),   # Primary Key
    StructField("Date", DateType(), False),              # Transaction date
    StructField("Retailer_ID", StringType(), False),     # Foreign Key → locations
    StructField("SKU", StringType(), False),             # Foreign Key → products
    StructField("Units_Sold", IntegerType(), False),     # Quantity sold (≥1)
    StructField("Unit_Price", DoubleType(), False),      # Actual selling price
    StructField("Total_Revenue", DoubleType(), False),   # Units × Unit_Price
    StructField("Is_Promotion", BooleanType(), True),    # Promotional pricing flag
    # ... additional 18 fields for market context
])
```

**Business Rules:**
- Transaction_ID: Unique identifier per transaction
- Date: Range 2023-01-01 to 2023-12-31 (12-month analysis)
- Units_Sold: Minimum 1, Maximum 50 (realistic transaction sizes)
- Total_Revenue: Must equal Units_Sold × Unit_Price (±1% tolerance)

## 🔄 Data Transformation Logic

### **1. Data Ingestion Pipeline**
```python
class DataIngestionPipeline:
    def read_csv_with_validation(self, filename, dataset_type):
        """
        Read CSV with schema validation and quality checks
        
        Transformations:
        1. Apply explicit schema enforcement
        2. Validate data types and constraints
        3. Check for null values in required fields
        4. Generate data quality metrics
        """
```

**Key Transformations:**
- **Schema Enforcement**: Strict type checking and null validation
- **Date Parsing**: Convert string dates to DateType with validation
- **Numeric Validation**: Range checks for prices, quantities, percentages
- **Referential Integrity**: Validate foreign key relationships

### **2. Data Cleaning Pipeline**
```python
class DataCleaningPipeline:
    def clean_all_datasets(self, products_df, locations_df, sales_df):
        """
        Comprehensive data cleaning with business rule enforcement
        
        Products Cleaning:
        1. Null value handling for core fields
        2. Text standardization (UPPER case for categories)
        3. ABV range validation (0.1% - 20.0%)
        4. Price range validation ($0.01 - $10.00)
        5. Duplicate removal by SKU
        6. Derived field creation (Is_Beer, Price_Tier)
        
        Locations Cleaning:
        1. Geographic field standardization
        2. Region validation against allowed values
        3. Store type categorization
        4. Market tier assignment
        
        Sales Cleaning:
        1. Business rule validation (Revenue = Units × Price)
        2. Outlier detection and removal (>3 std deviations)
        3. Date range validation
        4. Promotional flag inference
        """
```

**Cleaning Rules:**
- **Data Retention Target**: ≥95% of original records
- **Outlier Detection**: Statistical (3-sigma rule) + Business rules
- **Text Standardization**: Consistent casing and trimming
- **Derived Fields**: 15+ calculated business metrics

### **3. Feature Engineering**
```python
def engineer_features(self, fact_table):
    """
    Create 37+ analytical features for trend analysis
    
    Categories:
    1. Sales Velocity Metrics (5 features)
    2. Time-based Features (8 features)
    3. Rolling Averages (12 features)
    4. Market Share Metrics (6 features)
    5. Trend Indicators (4 features)
    6. Performance Flags (2 features)
    """
```

**Feature Categories:**

#### **Sales Velocity & TDP**
- `Sales_Velocity_Calculated`: Units per day per store
- `Units_Per_TDP`: Units per Total Distribution Points
- `Revenue_Per_Unit`: Average revenue efficiency
- `TDP_Penetration`: Distribution penetration rate

#### **Time-based Features**
- `Months_From_Start`: Timeline progression (0-11)
- `Year_Month`: YYYY-MM format for aggregation
- `Quarter_Year`: Quarterly grouping
- `Is_Weekend`: Weekend sales flag
- `Seasonality_Factor`: Seasonal adjustment multiplier

#### **Rolling Averages (Window Functions)**
- `Rolling_7_Units`: 7-day moving average units
- `Rolling_30_Units`: 30-day moving average units
- `Rolling_30_Revenue`: 30-day moving average revenue
- `Category_7_Day_Avg`: Category-level 7-day average
- `Category_30_Day_Avg`: Category-level 30-day average

#### **Market Share Metrics**
- `Daily_Total_Revenue`: Total market revenue per day
- `Daily_Category_Revenue`: Category revenue per day
- `Daily_Brand_Revenue`: Brand revenue per day
- `Category_Market_Share`: Category share of total market
- `Brand_Market_Share`: Brand share within category

## 📈 Analytical Methodology

### **1. Pivot Point Detection Algorithm**
```python
def identify_pivot_point(self):
    """
    Statistical algorithm to identify market inflection points
    
    Methodology:
    1. Calculate month-over-month growth rates by category
    2. Compute growth rate differences (Seltzer - Beer)
    3. Apply statistical significance testing (p < 0.05)
    4. Identify sustained advantage periods (≥3 months)
    5. Flag pivot points where Seltzer exceeds Beer by ≥15%
    
    Statistical Tests:
    - Welch's t-test for unequal variances
    - Mann-Whitney U test for non-parametric validation
    - Confidence intervals at 95% level
    """
```

**Algorithm Steps:**
1. **Growth Rate Calculation**: `(Current - Previous) / Previous * 100`
2. **Difference Analysis**: `Seltzer_Growth - Beer_Growth`
3. **Significance Testing**: Two-sample t-tests with α = 0.05
4. **Trend Validation**: Minimum 3-month sustained advantage
5. **Pivot Identification**: Growth difference ≥ 15% threshold

### **2. Market Share Evolution Tracking**
```python
def track_market_share_evolution(self):
    """
    Longitudinal analysis of market share dynamics
    
    Metrics:
    1. Absolute market share by month
    2. Relative growth rates
    3. Market share velocity (rate of change)
    4. Competitive displacement analysis
    5. Trend extrapolation with confidence bands
    """
```

### **3. Regional Trend Analysis**
```python
def analyze_regional_trends(self):
    """
    Geographic segmentation and opportunity analysis
    
    Dimensions:
    1. Regional performance comparison
    2. Market penetration rates
    3. Growth trajectory analysis
    4. Opportunity scoring matrix
    5. Expansion prioritization
    """
```

## 🔍 Business Rules Engine

### **1. Data Quality Rules**
```yaml
data_quality_rules:
  products:
    required_fields: [SKU, Brand, Category, ABV, Price_Per_Unit]
    category_values: [BEER, HARD SELTZER]
    abv_range: [0.1, 20.0]
    price_range: [0.01, 10.00]
    
  locations:
    required_fields: [Retailer_ID, Region, State, Store_Type]
    region_values: [NORTHEAST, SOUTHEAST, MIDWEST, SOUTHWEST, WEST]
    alcohol_license: true
    
  sales:
    required_fields: [Transaction_ID, Date, Retailer_ID, SKU, Units_Sold]
    units_range: [1, 50]
    date_range: [2023-01-01, 2023-12-31]
    revenue_tolerance: 0.01  # 1% tolerance for calculation errors
```

### **2. Business Logic Rules**
```yaml
business_rules:
  market_analysis:
    pivot_threshold: 15.0          # Minimum growth difference for pivot
    significance_level: 0.05       # Statistical significance threshold
    trend_window: 3                # Minimum months for trend validation
    
  financial_modeling:
    roi_scenarios: [conservative, moderate, aggressive]
    market_share_targets: [10, 15, 25]  # Percentage targets
    investment_multiples: [1.5, 2.0, 3.0]
    
  data_retention:
    minimum_retention: 0.95        # 95% minimum data retention
    outlier_threshold: 3.0         # 3-sigma outlier detection
```

## 📊 Data Lineage & Impact Analysis

### **Data Lineage Flow**
```
Raw CSV Files
    ↓ [Schema Validation]
Validated DataFrames
    ↓ [Data Cleaning]
Clean DataFrames
    ↓ [Referential Integrity]
Validated Relationships
    ↓ [Fact Table Creation]
Comprehensive Fact Table
    ↓ [Feature Engineering]
Enhanced Fact Table (37+ features)
    ↓ [Analytical Processing]
Business Insights
    ↓ [Visualization & Reporting]
Executive Deliverables
```

### **Impact Analysis Matrix**

| Component | Upstream Dependencies | Downstream Impact | Failure Impact |
|-----------|----------------------|-------------------|----------------|
| **Data Generation** | None | All pipeline stages | Complete failure |
| **Data Ingestion** | Raw CSV files | Cleaning, Analysis | Data quality issues |
| **Data Cleaning** | Ingested data | Feature engineering | Analysis accuracy |
| **Feature Engineering** | Clean data | Trend analysis | Insight quality |
| **Trend Analysis** | Enhanced features | Executive reporting | Strategic recommendations |
| **Visualization** | Analysis results | Business decisions | Presentation quality |

### **Data Quality Impact**
- **Schema Violations**: Immediate pipeline failure with detailed error reporting
- **Business Rule Violations**: Configurable handling (warn/fail) with impact assessment
- **Referential Integrity Issues**: Data filtering with retention rate monitoring
- **Statistical Anomalies**: Flagging and investigation recommendations

## 🚀 Pipeline Execution Instructions

### **Prerequisites**
```bash
# Environment Setup
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
export PYSPARK_PYTHON="python3.10"
export PYSPARK_DRIVER_PYTHON="python3.10"

# Dependencies
pip3.10 install pyspark pandas matplotlib seaborn plotly pyyaml reportlab schedule psutil
```

### **Execution Commands**

#### **1. Complete Pipeline Execution**
```bash
# Run full orchestrated pipeline
python3.10 run_orchestrated_pipeline.py

# Run with verbose logging
python3.10 run_orchestrated_pipeline.py --verbose

# Skip PDF generation
python3.10 run_orchestrated_pipeline.py --skip-pdf
```

#### **2. Stage-by-Stage Execution**
```bash
# Individual stages
python3.10 run_orchestrated_pipeline.py --stage data_generation
python3.10 run_orchestrated_pipeline.py --stage data_processing
python3.10 run_orchestrated_pipeline.py --stage visualization_export
python3.10 run_orchestrated_pipeline.py --stage chart_generation
python3.10 run_orchestrated_pipeline.py --stage executive_reporting
python3.10 run_orchestrated_pipeline.py --stage pdf_generation
```

#### **3. Enterprise Pipeline (Advanced)**
```bash
# Master pipeline with full orchestration
python3.10 src/pipelines/master_pipeline.py

# With configuration override
python3.10 src/pipelines/master_pipeline.py --config custom_config.yaml

# Resume from checkpoint
python3.10 src/pipelines/master_pipeline.py --resume
```

### **Configuration Management**
```yaml
# config/pipeline_config.yaml
pipeline:
  name: "beer-seltzer-market-analysis"
  version: "1.0.0"

environment:
  spark:
    driver_memory: "4g"
    executor_memory: "2g"

stages:
  data_cleaning:
    retention_threshold: 0.95
  trend_analysis:
    pivot_detection_threshold: 15.0
    statistical_significance: 0.05
```

## 📋 Monitoring & Troubleshooting

### **Log Files**
- `logs/pipeline.log`: Main execution log
- `logs/performance.log`: Performance metrics
- `logs/ingestion.log`: Data ingestion details
- `logs/cleaning.log`: Data cleaning operations
- `logs/trend_analysis.log`: Analytical processing
- `logs/charts.log`: Visualization generation
- `logs/executive.log`: Report generation

### **Performance Monitoring**
```python
# Key metrics tracked:
- Stage execution times
- Memory utilization
- Data processing rates
- Quality retention rates
- Error frequencies
- System resource usage
```

### **Common Issues & Solutions**

#### **Memory Issues**
```bash
# Reduce memory usage
export SPARK_DRIVER_MEMORY="2g"
export SPARK_EXECUTOR_MEMORY="1g"
```

#### **Java/Spark Issues**
```bash
# Verify Java installation
java -version
echo $JAVA_HOME

# Reset Spark configuration
unset SPARK_HOME
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
```

#### **Data Quality Issues**
```bash
# Check data quality logs
tail -f logs/cleaning.log
grep "ERROR\|WARN" logs/*.log
```

## 🔧 Extension Points

### **Adding New Analytical Components**
1. Create new pipeline stage in `src/pipelines/`
2. Add configuration in `config/pipeline_config.yaml`
3. Register stage in orchestration layer
4. Implement monitoring and error handling

### **Custom Business Rules**
1. Extend `business_rules` section in configuration
2. Implement validation logic in cleaning pipeline
3. Add quality metrics tracking
4. Update documentation

### **Additional Data Sources**
1. Define new schema in ingestion pipeline
2. Add cleaning logic for new data types
3. Extend feature engineering for new dimensions
4. Update analytical methodology

---

## 📚 References

- **PySpark Documentation**: https://spark.apache.org/docs/latest/api/python/
- **Statistical Methods**: Welch's t-test, Mann-Whitney U test
- **Business Intelligence**: Kimball dimensional modeling
- **Data Quality**: Great Expectations framework patterns
- **Pipeline Orchestration**: Apache Airflow patterns adapted for PySpark

---

*This technical documentation provides comprehensive coverage of the Beer-to-Seltzer Market Analysis Pipeline architecture, implementation details, and operational procedures.*