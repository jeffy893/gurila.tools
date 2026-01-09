#!/usr/bin/env python3
"""
PySpark Data Ingestion and Exploration Script
============================================

This script demonstrates comprehensive data ingestion practices including:
- Explicit schema definition for all CSV files
- Data validation and quality checks
- Error handling and data exploration
- Statistical analysis and pattern verification
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    """
    Comprehensive data ingestion pipeline with schema validation and quality checks.
    """
    
    def __init__(self, data_dir: str = "synthetic_data"):
        """
        Initialize the data ingestion pipeline.
        
        Args:
            data_dir (str): Directory containing CSV files
        """
        self.data_dir = data_dir
        self.spark = None
        self.schemas = {}
        self.dataframes = {}
        self.quality_report = {}
        
    def create_spark_session(self) -> SparkSession:
        """Create optimized SparkSession for data ingestion."""
        logger.info("Creating SparkSession for data ingestion...")
        
        self.spark = SparkSession.builder \
            .appName("BeerCompanyDataIngestion") \
            .master("local[*]") \
            .config("spark.driver.memory", "4g") \
            .config("spark.driver.maxResultSize", "2g") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB") \
            .getOrCreate()
        
        # Set log level to reduce noise
        self.spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"✅ SparkSession created successfully")
        logger.info(f"   Spark Version: {self.spark.version}")
        logger.info(f"   Default Parallelism: {self.spark.sparkContext.defaultParallelism}")
        
        return self.spark
    
    def define_schemas(self):
        """
        Define explicit schemas for all CSV files with appropriate data types.
        """
        logger.info("Defining explicit schemas for CSV files...")
        
        # Products Schema - Updated to match actual CSV structure
        self.schemas['products'] = StructType([
            StructField("SKU", StringType(), False),
            StructField("Brand", StringType(), False),
            StructField("Product_Name", StringType(), False),
            StructField("Category", StringType(), False),
            StructField("ABV", DoubleType(), False),
            StructField("Package_Size", StringType(), True),
            StructField("Pack_Size", IntegerType(), True),
            StructField("Price_Per_Unit", DoubleType(), False),
            StructField("Launch_Date", StringType(), True)
        ])
        
        # Locations Schema - Updated to match actual CSV structure
        self.schemas['locations'] = StructType([
            StructField("Retailer_ID", StringType(), False),
            StructField("Chain_Name", StringType(), False),
            StructField("Store_Type", StringType(), False),
            StructField("Region", StringType(), False),
            StructField("State", StringType(), False),
            StructField("City", StringType(), False),
            StructField("Warehouse_ID", StringType(), True),
            StructField("Store_Size", StringType(), False),
            StructField("Urban_Rural", StringType(), True),
            StructField("Location_Type", StringType(), True),
            StructField("Market_Tier", StringType(), True),
            StructField("Alcohol_License", BooleanType(), False)
        ])
        
        # Sales Transactions Schema - Updated to match actual CSV structure
        self.schemas['sales_transactions'] = StructType([
            StructField("Transaction_ID", StringType(), False),
            StructField("Date", DateType(), False),
            StructField("Retailer_ID", StringType(), False),
            StructField("SKU", StringType(), False),
            StructField("Product_Name", StringType(), True),
            StructField("Brand", StringType(), True),
            StructField("Category", StringType(), False),
            StructField("Units_Sold", IntegerType(), False),
            StructField("Unit_Price", DoubleType(), False),
            StructField("Total_Revenue", DoubleType(), False),
            StructField("Is_Promotion", BooleanType(), True),
            StructField("Store_Type", StringType(), True),
            StructField("Region", StringType(), True),
            StructField("State", StringType(), True),
            StructField("Market_Tier", StringType(), True),
            StructField("Months_From_Start", DoubleType(), True),
            StructField("Beer_Trend_Strength", DoubleType(), True),
            StructField("Seltzer_Trend_Strength", DoubleType(), True),
            StructField("Market_Phase", StringType(), True),
            StructField("Seasonality_Factor", DoubleType(), True),
            StructField("Consumer_Seltzer_Awareness", DoubleType(), True),
            StructField("Revenue_Per_Unit", DoubleType(), True),
            StructField("Year_Month", StringType(), True),
            StructField("Quarter_Year", StringType(), True),
            StructField("TDP", DoubleType(), True),
            StructField("Sales_Velocity", DoubleType(), True)
        ])
        
        logger.info("✅ Schemas defined for all datasets:")
        for name, schema in self.schemas.items():
            logger.info(f"   {name}: {len(schema.fields)} fields")
    
    def read_csv_with_validation(self, filename: str, schema_name: str) -> DataFrame:
        """
        Read CSV file with schema validation and error handling.
        
        Args:
            filename (str): CSV filename
            schema_name (str): Schema name from self.schemas
            
        Returns:
            DataFrame: Validated DataFrame
        """
        filepath = os.path.join(self.data_dir, filename)
        schema = self.schemas[schema_name]
        
        logger.info(f"Reading {filename} with schema validation...")
        
        # Check if file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            # Read CSV with explicit schema
            if schema_name == 'sales_transactions':
                # Special handling for sales transactions (date conversion)
                df = self.spark.read.csv(
                    filepath,
                    header=True,
                    inferSchema=False,  # Use explicit schema
                    timestampFormat="yyyy-MM-dd",
                    dateFormat="yyyy-MM-dd"
                )
                
                # Convert string date to DateType
                df = df.withColumn("Date", to_date(col("Date"), "yyyy-MM-dd"))
                
                # Apply schema with proper types
                for field in schema.fields:
                    if field.name != "Date":  # Date already converted
                        if field.dataType == IntegerType():
                            df = df.withColumn(field.name, col(field.name).cast(IntegerType()))
                        elif field.dataType == DoubleType():
                            df = df.withColumn(field.name, col(field.name).cast(DoubleType()))
                        elif field.dataType == BooleanType():
                            df = df.withColumn(field.name, col(field.name).cast(BooleanType()))
            else:
                # Standard CSV reading for products and locations
                df = self.spark.read.csv(
                    filepath,
                    header=True,
                    schema=schema,
                    inferSchema=False
                )
            
            logger.info(f"✅ Successfully read {filename}: {df.count()} rows")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to read {filename}: {str(e)}")
            raise
    
    def perform_data_quality_checks(self, df: DataFrame, dataset_name: str) -> dict:
        """
        Perform comprehensive data quality checks on a DataFrame.
        
        Args:
            df (DataFrame): DataFrame to check
            dataset_name (str): Name of the dataset for reporting
            
        Returns:
            dict: Quality check results
        """
        logger.info(f"Performing data quality checks for {dataset_name}...")
        
        quality_results = {
            'dataset_name': dataset_name,
            'total_rows': 0,
            'total_columns': 0,
            'null_counts': {},
            'duplicate_counts': {},
            'data_type_issues': [],
            'business_rule_violations': [],
            'summary_stats': {}
        }
        
        try:
            # Basic counts
            quality_results['total_rows'] = df.count()
            quality_results['total_columns'] = len(df.columns)
            
            # Null value analysis
            logger.info(f"  Checking null values...")
            for column in df.columns:
                null_count = df.filter(col(column).isNull()).count()
                quality_results['null_counts'][column] = null_count
                
                if null_count > 0:
                    null_percentage = (null_count / quality_results['total_rows']) * 100
                    logger.warning(f"    {column}: {null_count} nulls ({null_percentage:.2f}%)")
            
            # Duplicate analysis
            logger.info(f"  Checking duplicates...")
            if dataset_name == 'products':
                duplicate_skus = df.groupBy("SKU").count().filter(col("count") > 1).count()
                quality_results['duplicate_counts']['SKU'] = duplicate_skus
            elif dataset_name == 'locations':
                duplicate_retailers = df.groupBy("Retailer_ID").count().filter(col("count") > 1).count()
                quality_results['duplicate_counts']['Retailer_ID'] = duplicate_retailers
            elif dataset_name == 'sales_transactions':
                duplicate_transactions = df.groupBy("Transaction_ID").count().filter(col("count") > 1).count()
                quality_results['duplicate_counts']['Transaction_ID'] = duplicate_transactions
            
            # Business rule validation
            logger.info(f"  Validating business rules...")
            if dataset_name == 'products':
                # ABV should be between 0 and 20%
                invalid_abv = df.filter((col("ABV") < 0) | (col("ABV") > 20)).count()
                if invalid_abv > 0:
                    quality_results['business_rule_violations'].append(f"Invalid ABV values: {invalid_abv}")
                
                # Price should be positive
                invalid_price = df.filter(col("Price_Per_Unit") <= 0).count()
                if invalid_price > 0:
                    quality_results['business_rule_violations'].append(f"Invalid prices: {invalid_price}")
                    
            elif dataset_name == 'sales_transactions':
                # Units sold should be positive
                invalid_units = df.filter(col("Units_Sold") <= 0).count()
                if invalid_units > 0:
                    quality_results['business_rule_violations'].append(f"Invalid units sold: {invalid_units}")
                
                # Revenue should be positive
                invalid_revenue = df.filter(col("Total_Revenue") <= 0).count()
                if invalid_revenue > 0:
                    quality_results['business_rule_violations'].append(f"Invalid revenue: {invalid_revenue}")
                
                # Revenue consistency check (Units * Price ≈ Revenue, allowing for discounts)
                revenue_check = df.withColumn("Expected_Revenue", col("Units_Sold") * col("Unit_Price")) \
                    .withColumn("Revenue_Ratio", col("Total_Revenue") / col("Expected_Revenue")) \
                    .filter((col("Revenue_Ratio") < 0.7) | (col("Revenue_Ratio") > 1.05))  # Allow 30% discount, 5% markup
                
                revenue_inconsistencies = revenue_check.count()
                if revenue_inconsistencies > 0:
                    quality_results['business_rule_violations'].append(f"Revenue inconsistencies: {revenue_inconsistencies}")
            
            # Calculate summary statistics for numeric columns
            logger.info(f"  Calculating summary statistics...")
            numeric_columns = [field.name for field in df.schema.fields 
                             if field.dataType in [IntegerType(), DoubleType(), FloatType()]]
            
            if numeric_columns:
                stats_df = df.select(numeric_columns).describe()
                quality_results['summary_stats'] = {
                    row['summary']: {col_name: row[col_name] for col_name in numeric_columns}
                    for row in stats_df.collect()
                }
            
            logger.info(f"✅ Quality checks completed for {dataset_name}")
            
        except Exception as e:
            logger.error(f"❌ Quality check failed for {dataset_name}: {str(e)}")
            quality_results['error'] = str(e)
        
        return quality_results
    
    def explore_dataset(self, df: DataFrame, dataset_name: str):
        """
        Perform comprehensive data exploration and display results.
        
        Args:
            df (DataFrame): DataFrame to explore
            dataset_name (str): Name of the dataset
        """
        logger.info(f"Exploring {dataset_name} dataset...")
        
        print(f"\n" + "=" * 60)
        print(f"📊 DATASET EXPLORATION: {dataset_name.upper()}")
        print("=" * 60)
        
        # Schema information
        print(f"\n🔍 SCHEMA INFORMATION:")
        print(f"   Rows: {df.count():,}")
        print(f"   Columns: {len(df.columns)}")
        print(f"\n   Schema Details:")
        df.printSchema()
        
        # Sample data
        print(f"\n📋 SAMPLE DATA (First 10 rows):")
        df.show(10, truncate=False)
        
        # Column analysis
        print(f"\n📈 COLUMN ANALYSIS:")
        for column in df.columns:
            distinct_count = df.select(column).distinct().count()
            null_count = df.filter(col(column).isNull()).count()
            print(f"   {column}: {distinct_count:,} unique values, {null_count} nulls")
        
        # Category-specific analysis
        if dataset_name == 'products':
            print(f"\n🍺 PRODUCT ANALYSIS:")
            category_counts = df.groupBy("Category").count().orderBy(desc("count"))
            category_counts.show()
            
            brand_counts = df.groupBy("Brand").count().orderBy(desc("count"))
            print(f"\n   Top 10 Brands by Product Count:")
            brand_counts.show(10)
            
        elif dataset_name == 'locations':
            print(f"\n🏪 LOCATION ANALYSIS:")
            region_counts = df.groupBy("Region").count().orderBy(desc("count"))
            region_counts.show()
            
            store_type_counts = df.groupBy("Store_Type").count().orderBy(desc("count"))
            store_type_counts.show()
            
        elif dataset_name == 'sales_transactions':
            print(f"\n💰 SALES ANALYSIS:")
            
            # Monthly sales summary
            monthly_sales = df.withColumn("Year_Month", date_format(col("Date"), "yyyy-MM")) \
                .groupBy("Year_Month") \
                .agg(
                    sum("Units_Sold").alias("Total_Units"),
                    sum("Total_Revenue").alias("Total_Revenue"),
                    count("Transaction_ID").alias("Transaction_Count")
                ) \
                .orderBy("Year_Month")
            
            print(f"\n   Monthly Sales Summary:")
            monthly_sales.show(12)
            
            # Category performance
            category_performance = df.groupBy("Category") \
                .agg(
                    sum("Units_Sold").alias("Total_Units"),
                    sum("Total_Revenue").alias("Total_Revenue"),
                    avg("Total_Revenue").alias("Avg_Transaction_Value"),
                    count("Transaction_ID").alias("Transaction_Count")
                ) \
                .orderBy(desc("Total_Revenue"))
            
            print(f"\n   Category Performance:")
            category_performance.show()
    
    def generate_quality_report(self):
        """Generate comprehensive data quality report."""
        print(f"\n" + "=" * 80)
        print(f"📋 DATA QUALITY REPORT")
        print("=" * 80)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for dataset_name, results in self.quality_report.items():
            print(f"\n📊 {dataset_name.upper()} QUALITY SUMMARY:")
            print(f"   Total Rows: {results['total_rows']:,}")
            print(f"   Total Columns: {results['total_columns']}")
            
            # Null analysis
            null_issues = [col for col, count in results['null_counts'].items() if count > 0]
            if null_issues:
                print(f"   ⚠️  Columns with nulls: {len(null_issues)}")
                for col in null_issues[:5]:  # Show first 5
                    print(f"      {col}: {results['null_counts'][col]} nulls")
            else:
                print(f"   ✅ No null values found")
            
            # Duplicate analysis
            duplicate_issues = [key for key, count in results['duplicate_counts'].items() if count > 0]
            if duplicate_issues:
                print(f"   ⚠️  Duplicate issues: {duplicate_issues}")
            else:
                print(f"   ✅ No duplicate keys found")
            
            # Business rule violations
            if results['business_rule_violations']:
                print(f"   ⚠️  Business rule violations:")
                for violation in results['business_rule_violations']:
                    print(f"      {violation}")
            else:
                print(f"   ✅ All business rules validated")
        
        # Overall assessment
        total_issues = 0
        for results in self.quality_report.values():
            total_issues += len(results['business_rule_violations'])
            total_issues += len([c for c in results['duplicate_counts'].values() if c > 0])
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if total_issues == 0:
            print(f"   ✅ EXCELLENT: No data quality issues detected")
            print(f"   📈 Data is ready for analysis")
        elif total_issues <= 5:
            print(f"   ⚠️  GOOD: Minor issues detected ({total_issues} total)")
            print(f"   🔧 Consider data cleaning before analysis")
        else:
            print(f"   ❌ POOR: Significant issues detected ({total_issues} total)")
            print(f"   🚨 Data cleaning required before analysis")
    
    def run_complete_ingestion(self):
        """Run the complete data ingestion and exploration pipeline."""
        print("🚀 Starting Complete Data Ingestion Pipeline")
        print("=" * 60)
        
        try:
            # Initialize Spark
            self.create_spark_session()
            
            # Define schemas
            self.define_schemas()
            
            # Read and validate each dataset
            datasets = [
                ('products.csv', 'products'),
                ('locations.csv', 'locations'),
                ('sales_transactions.csv', 'sales_transactions')
            ]
            
            for filename, schema_name in datasets:
                # Read CSV with validation
                df = self.read_csv_with_validation(filename, schema_name)
                self.dataframes[schema_name] = df
                
                # Perform quality checks
                quality_results = self.perform_data_quality_checks(df, schema_name)
                self.quality_report[schema_name] = quality_results
                
                # Explore dataset
                self.explore_dataset(df, schema_name)
            
            # Generate quality report
            self.generate_quality_report()
            
            print(f"\n🎉 Data ingestion pipeline completed successfully!")
            print(f"📊 All datasets loaded and validated")
            print(f"🔍 Data exploration completed")
            print(f"📋 Quality report generated")
            
            return self.dataframes
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            raise
        finally:
            if self.spark:
                self.spark.stop()

def main():
    """Main execution function."""
    pipeline = DataIngestionPipeline()
    dataframes = pipeline.run_complete_ingestion()
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Review quality report above")
    print(f"   2. Address any data quality issues")
    print(f"   3. Proceed with ETL transformations")
    print(f"   4. Run business analysis pipeline")

if __name__ == "__main__":
    main()