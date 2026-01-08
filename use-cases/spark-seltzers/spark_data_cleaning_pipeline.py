#!/usr/bin/env python3
"""
PySpark Data Cleaning and Feature Engineering Pipeline
====================================================

This script implements comprehensive data cleaning, joining, and feature engineering
for the beer company POS analysis. It transforms raw data into analysis-ready datasets
with proper quality controls and business-relevant features.

Key Features:
- Comprehensive data cleaning with business rationale
- Referential integrity validation
- Multi-table joins with skew handling
- Advanced feature engineering for trend analysis
- Monthly/quarterly aggregations
- Performance optimizations
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

class DataCleaningPipeline:
    """
    Comprehensive data cleaning and feature engineering pipeline.
    """
    
    def __init__(self, data_dir: str = "synthetic_data"):
        """Initialize the pipeline."""
        self.data_dir = data_dir
        self.spark = None
        self.raw_dataframes = {}
        self.cleaned_dataframes = {}
        self.fact_table = None
        self.aggregated_tables = {}
        self.cleaning_report = {}
        
    def create_spark_session(self) -> SparkSession:
        """Create optimized SparkSession for data processing."""
        logger.info("Creating SparkSession for data cleaning pipeline...")
        
        self.spark = SparkSession.builder \
            .appName("BeerCompanyDataCleaning") \
            .master("local[*]") \
            .config("spark.driver.memory", "6g") \
            .config("spark.driver.maxResultSize", "3g") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"✅ SparkSession created successfully")
        logger.info(f"   Spark Version: {self.spark.version}")
        logger.info(f"   Default Parallelism: {self.spark.sparkContext.defaultParallelism}")
        
        return self.spark
    
    def load_raw_data(self):
        """Load raw data using the existing ingestion pipeline."""
        logger.info("Loading raw data from CSV files...")
        
        # Import and use the existing ingestion pipeline
        from spark_data_ingestion import DataIngestionPipeline
        
        ingestion_pipeline = DataIngestionPipeline(self.data_dir)
        ingestion_pipeline.spark = self.spark  # Reuse our spark session
        ingestion_pipeline.define_schemas()
        
        # Load each dataset
        datasets = [
            ('products.csv', 'products'),
            ('locations.csv', 'locations'),
            ('sales_transactions.csv', 'sales_transactions')
        ]
        
        for filename, schema_name in datasets:
            df = ingestion_pipeline.read_csv_with_validation(filename, schema_name)
            self.raw_dataframes[schema_name] = df
            logger.info(f"✅ Loaded {schema_name}: {df.count():,} rows")
        
        return self.raw_dataframes
    
    def clean_products_data(self):
        """
        Clean products data with comprehensive validation.
        
        Business Rationale:
        - Products are master data - must be complete and consistent
        - ABV validation ensures regulatory compliance
        - Price validation prevents analysis errors
        - Brand/category standardization enables proper grouping
        """
        logger.info("Cleaning products data...")
        
        df = self.raw_dataframes['products']
        initial_count = df.count()
        
        cleaning_steps = []
        
        # Step 1: Handle null values
        logger.info("  Step 1: Handling null values...")
        null_counts_before = {column_name: df.filter(col(column_name).isNull()).count() for column_name in df.columns}
        
        # Business Rule: Core fields cannot be null
        core_fields = ['SKU', 'Brand', 'Product_Name', 'Category', 'ABV', 'Price_Per_Unit']
        
        # Create filter condition for non-null core fields
        filter_condition = col(core_fields[0]).isNotNull()
        for field in core_fields[1:]:
            filter_condition = filter_condition & col(field).isNotNull()
        
        df_clean = df.filter(filter_condition)
        
        null_removed = initial_count - df_clean.count()
        cleaning_steps.append(f"Removed {null_removed} records with null core fields")
        
        # Step 2: Standardize text fields
        logger.info("  Step 2: Standardizing text fields...")
        df_clean = df_clean \
            .withColumn("Brand", trim(upper(col("Brand")))) \
            .withColumn("Category", trim(upper(col("Category")))) \
            .withColumn("Product_Name", trim(col("Product_Name"))) \
            .withColumn("Package_Size", trim(col("Package_Size")))
        
        cleaning_steps.append("Standardized Brand and Category to uppercase, trimmed whitespace")
        
        # Step 3: Validate ABV ranges
        logger.info("  Step 3: Validating ABV ranges...")
        invalid_abv_before = df_clean.filter((col("ABV") < 0) | (col("ABV") > 20)).count()
        df_clean = df_clean.filter((col("ABV") >= 0) & (col("ABV") <= 20))
        
        cleaning_steps.append(f"Removed {invalid_abv_before} products with invalid ABV (must be 0-20%)")
        
        # Step 4: Validate price ranges
        logger.info("  Step 4: Validating price ranges...")
        invalid_price_before = df_clean.filter((col("Price_Per_Unit") <= 0) | (col("Price_Per_Unit") > 10)).count()
        df_clean = df_clean.filter((col("Price_Per_Unit") > 0) & (col("Price_Per_Unit") <= 10))
        
        cleaning_steps.append(f"Removed {invalid_price_before} products with invalid prices (must be $0.01-$10.00)")
        
        # Step 5: Remove duplicates
        logger.info("  Step 5: Removing duplicates...")
        duplicates_before = df_clean.count() - df_clean.dropDuplicates(['SKU']).count()
        df_clean = df_clean.dropDuplicates(['SKU'])
        
        cleaning_steps.append(f"Removed {duplicates_before} duplicate SKUs")
        
        # Step 6: Add derived fields
        logger.info("  Step 6: Adding derived fields...")
        df_clean = df_clean \
            .withColumn("Is_Beer", when(col("Category") == "BEER", True).otherwise(False)) \
            .withColumn("Is_Seltzer", when(col("Category") == "HARD SELTZER", True).otherwise(False)) \
            .withColumn("Price_Tier", 
                when(col("Price_Per_Unit") < 1.0, "Budget")
                .when(col("Price_Per_Unit") < 1.5, "Mid-Range")
                .otherwise("Premium")
            )
        
        cleaning_steps.append("Added derived fields: Is_Beer, Is_Seltzer, Price_Tier")
        
        final_count = df_clean.count()
        
        # Store cleaning report
        self.cleaning_report['products'] = {
            'initial_count': initial_count,
            'final_count': final_count,
            'records_removed': initial_count - final_count,
            'cleaning_steps': cleaning_steps,
            'null_counts_before': null_counts_before
        }
        
        self.cleaned_dataframes['products'] = df_clean
        
        logger.info(f"✅ Products cleaning completed: {initial_count:,} → {final_count:,} records")
        return df_clean
    
    def clean_locations_data(self):
        """
        Clean locations data with geographic validation.
        
        Business Rationale:
        - Location data drives regional analysis
        - Store type standardization enables channel analysis
        - Alcohol license validation ensures compliance
        """
        logger.info("Cleaning locations data...")
        
        df = self.raw_dataframes['locations']
        initial_count = df.count()
        
        cleaning_steps = []
        
        # Step 1: Handle null values
        logger.info("  Step 1: Handling null values...")
        core_fields = ['Retailer_ID', 'Chain_Name', 'Store_Type', 'Region', 'State', 'City']
        
        # Create filter condition for non-null core fields
        filter_condition = col(core_fields[0]).isNotNull()
        for field in core_fields[1:]:
            filter_condition = filter_condition & col(field).isNotNull()
        
        df_clean = df.filter(filter_condition)
        
        null_removed = initial_count - df_clean.count()
        cleaning_steps.append(f"Removed {null_removed} records with null core fields")
        
        # Step 2: Standardize geographic fields
        logger.info("  Step 2: Standardizing geographic fields...")
        df_clean = df_clean \
            .withColumn("Region", trim(upper(col("Region")))) \
            .withColumn("State", trim(upper(col("State")))) \
            .withColumn("City", trim(initcap(col("City")))) \
            .withColumn("Store_Type", trim(initcap(col("Store_Type")))) \
            .withColumn("Chain_Name", trim(col("Chain_Name")))
        
        cleaning_steps.append("Standardized geographic and store type fields")
        
        # Step 3: Validate regions
        logger.info("  Step 3: Validating regions...")
        valid_regions = ["NORTHEAST", "SOUTHEAST", "MIDWEST", "WEST", "SOUTHWEST"]
        invalid_regions_before = df_clean.filter(~col("Region").isin(valid_regions)).count()
        df_clean = df_clean.filter(col("Region").isin(valid_regions))
        
        cleaning_steps.append(f"Removed {invalid_regions_before} locations with invalid regions")
        
        # Step 4: Remove duplicates
        logger.info("  Step 4: Removing duplicates...")
        duplicates_before = df_clean.count() - df_clean.dropDuplicates(['Retailer_ID']).count()
        df_clean = df_clean.dropDuplicates(['Retailer_ID'])
        
        cleaning_steps.append(f"Removed {duplicates_before} duplicate Retailer_IDs")
        
        # Step 5: Add derived fields
        logger.info("  Step 5: Adding derived fields...")
        df_clean = df_clean \
            .withColumn("Has_Alcohol_License", coalesce(col("Alcohol_License"), lit(False))) \
            .withColumn("Store_Size_Numeric", 
                when(col("Store_Size") == "Small", 1)
                .when(col("Store_Size") == "Medium", 2)
                .when(col("Store_Size") == "Large", 3)
                .otherwise(2)
            )
        
        cleaning_steps.append("Added derived fields: Has_Alcohol_License, Store_Size_Numeric")
        
        final_count = df_clean.count()
        
        # Store cleaning report
        self.cleaning_report['locations'] = {
            'initial_count': initial_count,
            'final_count': final_count,
            'records_removed': initial_count - final_count,
            'cleaning_steps': cleaning_steps
        }
        
        self.cleaned_dataframes['locations'] = df_clean
        
        logger.info(f"✅ Locations cleaning completed: {initial_count:,} → {final_count:,} records")
        return df_clean
    
    def clean_sales_transactions_data(self):
        """
        Clean sales transactions data with business validation.
        
        Business Rationale:
        - Transaction data is the core of analysis
        - Revenue validation prevents calculation errors
        - Date validation ensures proper time series analysis
        - Outlier removal improves trend detection
        """
        logger.info("Cleaning sales transactions data...")
        
        df = self.raw_dataframes['sales_transactions']
        initial_count = df.count()
        
        cleaning_steps = []
        
        # Step 1: Handle null values
        logger.info("  Step 1: Handling null values...")
        core_fields = ['Transaction_ID', 'Date', 'Retailer_ID', 'SKU', 'Category', 'Units_Sold', 'Total_Revenue']
        
        # Create filter condition for non-null core fields
        filter_condition = col(core_fields[0]).isNotNull()
        for field in core_fields[1:]:
            filter_condition = filter_condition & col(field).isNotNull()
        
        df_clean = df.filter(filter_condition)
        
        null_removed = initial_count - df_clean.count()
        cleaning_steps.append(f"Removed {null_removed} records with null core fields")
        
        # Step 2: Validate business rules
        logger.info("  Step 2: Validating business rules...")
        
        # Units sold must be positive
        invalid_units_before = df_clean.filter(col("Units_Sold") <= 0).count()
        df_clean = df_clean.filter(col("Units_Sold") > 0)
        
        # Revenue must be positive
        invalid_revenue_before = df_clean.filter(col("Total_Revenue") <= 0).count()
        df_clean = df_clean.filter(col("Total_Revenue") > 0)
        
        # Unit price must be reasonable
        df_clean = df_clean.filter((col("Unit_Price") > 0) & (col("Unit_Price") <= 10))
        
        cleaning_steps.append(f"Removed {invalid_units_before} records with invalid units sold")
        cleaning_steps.append(f"Removed {invalid_revenue_before} records with invalid revenue")
        
        # Step 3: Remove extreme outliers
        logger.info("  Step 3: Removing extreme outliers...")
        
        # Calculate percentiles for outlier detection
        percentiles = df_clean.select(
            expr("percentile_approx(Units_Sold, 0.99)").alias("units_99th"),
            expr("percentile_approx(Total_Revenue, 0.99)").alias("revenue_99th")
        ).collect()[0]
        
        units_threshold = percentiles['units_99th']
        revenue_threshold = percentiles['revenue_99th']
        
        outliers_before = df_clean.filter(
            (col("Units_Sold") > units_threshold) | 
            (col("Total_Revenue") > revenue_threshold)
        ).count()
        
        df_clean = df_clean.filter(
            (col("Units_Sold") <= units_threshold) & 
            (col("Total_Revenue") <= revenue_threshold)
        )
        
        cleaning_steps.append(f"Removed {outliers_before} extreme outliers (>99th percentile)")
        
        # Step 4: Standardize categorical fields
        logger.info("  Step 4: Standardizing categorical fields...")
        df_clean = df_clean \
            .withColumn("Category", trim(upper(col("Category")))) \
            .withColumn("Brand", trim(upper(col("Brand")))) \
            .withColumn("Region", trim(upper(col("Region")))) \
            .withColumn("Store_Type", trim(initcap(col("Store_Type"))))
        
        cleaning_steps.append("Standardized categorical fields")
        
        # Step 5: Remove duplicates
        logger.info("  Step 5: Removing duplicates...")
        duplicates_before = df_clean.count() - df_clean.dropDuplicates(['Transaction_ID']).count()
        df_clean = df_clean.dropDuplicates(['Transaction_ID'])
        
        cleaning_steps.append(f"Removed {duplicates_before} duplicate Transaction_IDs")
        
        # Step 6: Add derived fields
        logger.info("  Step 6: Adding derived fields...")
        df_clean = df_clean \
            .withColumn("Revenue_Per_Unit_Calculated", col("Total_Revenue") / col("Units_Sold")) \
            .withColumn("Is_Weekend", dayofweek(col("Date")).isin([1, 7])) \
            .withColumn("Month", month(col("Date"))) \
            .withColumn("Quarter", quarter(col("Date"))) \
            .withColumn("Year", year(col("Date"))) \
            .withColumn("Day_of_Year", dayofyear(col("Date")))
        
        cleaning_steps.append("Added derived fields: Revenue_Per_Unit_Calculated, Is_Weekend, temporal fields")
        
        final_count = df_clean.count()
        
        # Store cleaning report
        self.cleaning_report['sales_transactions'] = {
            'initial_count': initial_count,
            'final_count': final_count,
            'records_removed': initial_count - final_count,
            'cleaning_steps': cleaning_steps,
            'outlier_thresholds': {
                'units_99th': units_threshold,
                'revenue_99th': revenue_threshold
            }
        }
        
        self.cleaned_dataframes['sales_transactions'] = df_clean
        
        logger.info(f"✅ Sales transactions cleaning completed: {initial_count:,} → {final_count:,} records")
        return df_clean
    
    def validate_referential_integrity(self):
        """
        Validate referential integrity between tables.
        
        Business Rationale:
        - Ensures all transactions reference valid products and locations
        - Identifies data quality issues early
        - Prevents analysis errors from orphaned records
        """
        logger.info("Validating referential integrity...")
        
        products_df = self.cleaned_dataframes['products']
        locations_df = self.cleaned_dataframes['locations']
        sales_df = self.cleaned_dataframes['sales_transactions']
        
        integrity_report = {}
        
        # Check SKU references
        logger.info("  Checking SKU references...")
        valid_skus = products_df.select("SKU").distinct()
        sales_with_invalid_skus = sales_df.join(valid_skus, "SKU", "left_anti")
        invalid_sku_count = sales_with_invalid_skus.count()
        
        if invalid_sku_count > 0:
            logger.warning(f"  Found {invalid_sku_count} sales records with invalid SKUs")
            # Remove invalid SKU references
            sales_df = sales_df.join(valid_skus, "SKU", "inner")
            self.cleaned_dataframes['sales_transactions'] = sales_df
        
        integrity_report['invalid_skus'] = invalid_sku_count
        
        # Check Retailer_ID references
        logger.info("  Checking Retailer_ID references...")
        valid_retailers = locations_df.select("Retailer_ID").distinct()
        sales_with_invalid_retailers = sales_df.join(valid_retailers, "Retailer_ID", "left_anti")
        invalid_retailer_count = sales_with_invalid_retailers.count()
        
        if invalid_retailer_count > 0:
            logger.warning(f"  Found {invalid_retailer_count} sales records with invalid Retailer_IDs")
            # Remove invalid retailer references
            sales_df = sales_df.join(valid_retailers, "Retailer_ID", "inner")
            self.cleaned_dataframes['sales_transactions'] = sales_df
        
        integrity_report['invalid_retailers'] = invalid_retailer_count
        
        # Final counts after integrity validation
        final_sales_count = sales_df.count()
        integrity_report['final_sales_count'] = final_sales_count
        
        self.cleaning_report['referential_integrity'] = integrity_report
        
        logger.info(f"✅ Referential integrity validation completed")
        logger.info(f"   Invalid SKUs removed: {invalid_sku_count}")
        logger.info(f"   Invalid Retailers removed: {invalid_retailer_count}")
        logger.info(f"   Final sales records: {final_sales_count:,}")
        
        return integrity_report
    
    def create_comprehensive_fact_table(self):
        """
        Join all three DataFrames into a comprehensive fact table.
        
        Business Rationale:
        - Creates single source of truth for analysis
        - Preserves all dimensional attributes
        - Handles potential data skew with broadcast joins
        - Optimizes for analytical queries
        """
        logger.info("Creating comprehensive fact table...")
        
        products_df = self.cleaned_dataframes['products']
        locations_df = self.cleaned_dataframes['locations']
        sales_df = self.cleaned_dataframes['sales_transactions']
        
        # Broadcast smaller tables to handle skew
        logger.info("  Broadcasting products and locations tables...")
        products_broadcast = broadcast(products_df)
        locations_broadcast = broadcast(locations_df)
        
        # Primary join: Sales with Products
        logger.info("  Joining sales with products...")
        fact_table = sales_df.join(
            products_broadcast,
            sales_df.SKU == products_broadcast.SKU,
            "inner"
        ).select(
            # Sales columns
            sales_df["*"],
            # Product columns (with prefixes to avoid conflicts)
            products_broadcast.Brand.alias("Product_Brand_Master"),
            products_broadcast.Product_Name.alias("Product_Name_Master"),
            products_broadcast.Category.alias("Product_Category_Master"),
            products_broadcast.ABV.alias("Product_ABV"),
            products_broadcast.Package_Size.alias("Product_Package_Size"),
            products_broadcast.Pack_Size.alias("Product_Pack_Size"),
            products_broadcast.Price_Per_Unit.alias("Product_Price_Master"),
            products_broadcast.Launch_Date.alias("Product_Launch_Date"),
            products_broadcast.Is_Beer.alias("Product_Is_Beer"),
            products_broadcast.Is_Seltzer.alias("Product_Is_Seltzer"),
            products_broadcast.Price_Tier.alias("Product_Price_Tier")
        )
        
        # Secondary join: Result with Locations
        logger.info("  Joining with locations...")
        fact_table = fact_table.join(
            locations_broadcast,
            fact_table.Retailer_ID == locations_broadcast.Retailer_ID,
            "inner"
        ).select(
            # All previous columns
            fact_table["*"],
            # Location columns (with prefixes to avoid conflicts)
            locations_broadcast.Chain_Name.alias("Store_Chain_Name"),
            locations_broadcast.Store_Type.alias("Store_Type_Master"),
            locations_broadcast.Region.alias("Store_Region_Master"),
            locations_broadcast.State.alias("Store_State_Master"),
            locations_broadcast.City.alias("Store_City"),
            locations_broadcast.Warehouse_ID.alias("Store_Warehouse_ID"),
            locations_broadcast.Store_Size.alias("Store_Size_Category"),
            locations_broadcast.Urban_Rural.alias("Store_Urban_Rural"),
            locations_broadcast.Location_Type.alias("Store_Location_Type"),
            locations_broadcast.Market_Tier.alias("Store_Market_Tier"),
            locations_broadcast.Alcohol_License.alias("Store_Has_License"),
            locations_broadcast.Has_Alcohol_License.alias("Store_License_Verified"),
            locations_broadcast.Store_Size_Numeric.alias("Store_Size_Score")
        )
        
        # Add table source indicators
        fact_table = fact_table \
            .withColumn("Record_Source", lit("FACT_TABLE")) \
            .withColumn("Created_Timestamp", current_timestamp())
        
        # Cache the fact table for performance
        fact_table.cache()
        
        record_count = fact_table.count()
        logger.info(f"✅ Fact table created with {record_count:,} records")
        
        self.fact_table = fact_table
        return fact_table
    
    def engineer_features(self):
        """
        Implement comprehensive feature engineering.
        
        Business Rationale:
        - Sales velocity metrics identify high-performing products
        - Time-based features enable seasonality analysis
        - Rolling averages smooth out noise for trend detection
        - Growth rates highlight market shifts
        - Market share metrics show competitive positioning
        """
        logger.info("Engineering features for trend analysis...")
        
        df = self.fact_table
        
        # Define window specifications for different calculations
        logger.info("  Defining window specifications...")
        
        # Window by product over time (for product-level trends)
        product_time_window = Window.partitionBy("SKU").orderBy("Date")
        
        # Window by category over time (for category-level trends)
        category_time_window = Window.partitionBy("Product_Category_Master").orderBy("Date")
        
        # Window for rolling calculations (30-day window)
        rolling_30_window = Window.partitionBy("SKU").orderBy("Date").rowsBetween(-29, 0)
        
        # Window for market share calculations (by date)
        market_share_window = Window.partitionBy("Date")
        
        logger.info("  Step 1: Sales velocity and TDP metrics...")
        
        # Sales per TDP (velocity metric)
        df = df.withColumn("Sales_Velocity_Calculated", 
            when(col("TDP") > 0, col("Total_Revenue") / col("TDP")).otherwise(0)
        )
        
        # Units per TDP
        df = df.withColumn("Units_Per_TDP", 
            when(col("TDP") > 0, col("Units_Sold") / col("TDP")).otherwise(0)
        )
        
        logger.info("  Step 2: Time-based features...")
        
        # Enhanced time features
        df = df \
            .withColumn("Week_of_Year", weekofyear(col("Date"))) \
            .withColumn("Month_Name", date_format(col("Date"), "MMMM")) \
            .withColumn("Quarter_Name", concat(lit("Q"), col("Quarter"))) \
            .withColumn("Is_Holiday_Season", 
                when(col("Month").isin([11, 12]), True).otherwise(False)
            ) \
            .withColumn("Is_Summer_Season", 
                when(col("Month").isin([6, 7, 8]), True).otherwise(False)
            ) \
            .withColumn("Days_Since_Launch", 
                datediff(col("Date"), to_date(col("Product_Launch_Date"), "yyyy-MM-dd"))
            )
        
        logger.info("  Step 3: Rolling averages and trends...")
        
        # 30-day rolling averages
        df = df \
            .withColumn("Rolling_30_Revenue", 
                avg("Total_Revenue").over(rolling_30_window)
            ) \
            .withColumn("Rolling_30_Units", 
                avg("Units_Sold").over(rolling_30_window)
            ) \
            .withColumn("Rolling_30_Velocity", 
                avg("Sales_Velocity_Calculated").over(rolling_30_window)
            )
        
        # Growth rates (compared to previous period)
        df = df \
            .withColumn("Previous_Revenue", 
                lag("Total_Revenue", 1).over(product_time_window)
            ) \
            .withColumn("Revenue_Growth_Rate", 
                when(col("Previous_Revenue") > 0, 
                    (col("Total_Revenue") - col("Previous_Revenue")) / col("Previous_Revenue")
                ).otherwise(0)
            )
        
        logger.info("  Step 4: Market share metrics...")
        
        # Daily market share by category
        df = df \
            .withColumn("Daily_Total_Revenue", 
                sum("Total_Revenue").over(market_share_window)
            ) \
            .withColumn("Daily_Category_Revenue", 
                sum("Total_Revenue").over(Window.partitionBy("Date", "Product_Category_Master"))
            ) \
            .withColumn("Market_Share_by_Revenue", 
                col("Total_Revenue") / col("Daily_Total_Revenue")
            ) \
            .withColumn("Category_Share_by_Revenue", 
                col("Daily_Category_Revenue") / col("Daily_Total_Revenue")
            )
        
        # Brand performance metrics
        df = df \
            .withColumn("Daily_Brand_Revenue", 
                sum("Total_Revenue").over(Window.partitionBy("Date", "Product_Brand_Master"))
            ) \
            .withColumn("Brand_Share_by_Revenue", 
                col("Daily_Brand_Revenue") / col("Daily_Total_Revenue")
            )
        
        logger.info("  Step 5: Trend strength indicators...")
        
        # Category momentum (7-day vs 30-day average)
        category_7_window = Window.partitionBy("Product_Category_Master").orderBy("Date").rowsBetween(-6, 0)
        category_30_window = Window.partitionBy("Product_Category_Master").orderBy("Date").rowsBetween(-29, 0)
        
        df = df \
            .withColumn("Category_7_Day_Avg", 
                avg("Total_Revenue").over(category_7_window)
            ) \
            .withColumn("Category_30_Day_Avg", 
                avg("Total_Revenue").over(category_30_window)
            ) \
            .withColumn("Category_Momentum", 
                when(col("Category_30_Day_Avg") > 0,
                    col("Category_7_Day_Avg") / col("Category_30_Day_Avg")
                ).otherwise(1)
            )
        
        # Beer vs Seltzer competitive metrics
        df = df \
            .withColumn("Is_Beer_Category", col("Product_Category_Master") == "BEER") \
            .withColumn("Is_Seltzer_Category", col("Product_Category_Master") == "HARD SELTZER") \
            .withColumn("Competitive_Pressure", 
                when(col("Is_Beer_Category"), col("Seltzer_Trend_Strength"))
                .when(col("Is_Seltzer_Category"), col("Beer_Trend_Strength"))
                .otherwise(0)
            )
        
        logger.info("  Step 6: Performance tiers and flags...")
        
        # Performance tier based on sales velocity
        velocity_percentiles = df.select(
            expr("percentile_approx(Sales_Velocity_Calculated, 0.33)").alias("p33"),
            expr("percentile_approx(Sales_Velocity_Calculated, 0.67)").alias("p67")
        ).collect()[0]
        
        df = df.withColumn("Performance_Tier",
            when(col("Sales_Velocity_Calculated") >= velocity_percentiles['p67'], "High")
            .when(col("Sales_Velocity_Calculated") >= velocity_percentiles['p33'], "Medium")
            .otherwise("Low")
        )
        
        # Anomaly flags
        df = df \
            .withColumn("Is_High_Volume_Transaction", 
                col("Units_Sold") > col("Rolling_30_Units") * 3
            ) \
            .withColumn("Is_High_Value_Transaction", 
                col("Total_Revenue") > col("Rolling_30_Revenue") * 3
            ) \
            .withColumn("Is_Promotion_Likely", 
                col("Unit_Price") < col("Product_Price_Master") * 0.8
            )
        
        # Cache the enhanced fact table
        df.cache()
        
        feature_count = len(df.columns)
        logger.info(f"✅ Feature engineering completed: {feature_count} total features")
        
        self.fact_table = df
        return df
    
    def create_monthly_aggregations(self):
        """
        Create monthly aggregations by Category, Region, and Brand.
        
        Business Rationale:
        - Monthly view smooths daily volatility
        - Multi-dimensional aggregation enables drill-down analysis
        - Foundation for trend detection and forecasting
        """
        logger.info("Creating monthly aggregations...")
        
        df = self.fact_table
        
        # Monthly aggregation by Category and Region
        logger.info("  Creating monthly category-region aggregations...")
        monthly_category_region = df.groupBy(
            "Year", "Month", "Product_Category_Master", "Store_Region_Master"
        ).agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            avg("Unit_Price").alias("Avg_Unit_Price"),
            avg("TDP").alias("Avg_TDP"),
            count("Transaction_ID").alias("Transaction_Count"),
            countDistinct("SKU").alias("Unique_Products"),
            countDistinct("Retailer_ID").alias("Unique_Stores"),
            avg("Sales_Velocity_Calculated").alias("Avg_Sales_Velocity"),
            avg("Category_Share_by_Revenue").alias("Avg_Category_Share"),
            sum(when(col("Is_Promotion_Likely"), 1).otherwise(0)).alias("Promotion_Count")
        ).withColumn("Revenue_Per_Transaction", 
            col("Total_Revenue") / col("Transaction_Count")
        ).withColumn("Units_Per_Transaction", 
            col("Total_Units") / col("Transaction_Count")
        ).withColumn("TDP_Coverage", 
            col("Avg_TDP") * col("Unique_Products")
        )
        
        # Monthly aggregation by Brand
        logger.info("  Creating monthly brand aggregations...")
        monthly_brand = df.groupBy(
            "Year", "Month", "Product_Brand_Master", "Product_Category_Master"
        ).agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            avg("Unit_Price").alias("Avg_Unit_Price"),
            avg("TDP").alias("Avg_TDP"),
            count("Transaction_ID").alias("Transaction_Count"),
            countDistinct("SKU").alias("Unique_Products"),
            countDistinct("Store_Region_Master").alias("Regional_Presence"),
            avg("Sales_Velocity_Calculated").alias("Avg_Sales_Velocity"),
            avg("Brand_Share_by_Revenue").alias("Avg_Brand_Share")
        ).withColumn("Revenue_Per_Product", 
            col("Total_Revenue") / col("Unique_Products")
        ).withColumn("Geographic_Reach", 
            col("Regional_Presence") / 5.0  # Normalize by total regions
        )
        
        # Overall monthly summary
        logger.info("  Creating overall monthly summary...")
        monthly_summary = df.groupBy("Year", "Month").agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            count("Transaction_ID").alias("Transaction_Count"),
            countDistinct("SKU").alias("Unique_Products"),
            countDistinct("Retailer_ID").alias("Active_Stores"),
            avg("Sales_Velocity_Calculated").alias("Avg_Sales_Velocity")
        ).withColumn("Revenue_Per_Store", 
            col("Total_Revenue") / col("Active_Stores")
        ).withColumn("Units_Per_Store", 
            col("Total_Units") / col("Active_Stores")
        )
        
        # Store aggregations
        self.aggregated_tables['monthly_category_region'] = monthly_category_region
        self.aggregated_tables['monthly_brand'] = monthly_brand
        self.aggregated_tables['monthly_summary'] = monthly_summary
        
        logger.info("✅ Monthly aggregations completed")
        return {
            'category_region': monthly_category_region,
            'brand': monthly_brand,
            'summary': monthly_summary
        }
    
    def create_quarterly_aggregations(self):
        """
        Create quarterly aggregations for longer-term trend analysis.
        
        Business Rationale:
        - Quarterly view removes seasonal noise
        - Better for strategic planning and trend identification
        - Aligns with business reporting cycles
        """
        logger.info("Creating quarterly aggregations...")
        
        df = self.fact_table
        
        # Quarterly aggregation by Category
        logger.info("  Creating quarterly category aggregations...")
        quarterly_category = df.groupBy(
            "Year", "Quarter", "Product_Category_Master"
        ).agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            avg("Unit_Price").alias("Avg_Unit_Price"),
            avg("TDP").alias("Avg_TDP"),
            count("Transaction_ID").alias("Transaction_Count"),
            countDistinct("SKU").alias("Unique_Products"),
            countDistinct("Retailer_ID").alias("Active_Stores"),
            countDistinct("Store_Region_Master").alias("Regional_Presence"),
            avg("Sales_Velocity_Calculated").alias("Avg_Sales_Velocity"),
            avg("Category_Share_by_Revenue").alias("Avg_Category_Share"),
            avg("Category_Momentum").alias("Avg_Category_Momentum")
        ).withColumn("Market_Penetration", 
            col("Active_Stores") / 1441.0  # Total stores in dataset
        ).withColumn("Product_Diversity", 
            col("Unique_Products") / when(col("Product_Category_Master") == "BEER", 74).otherwise(46)
        )
        
        # Add quarter-over-quarter growth
        category_window = Window.partitionBy("Product_Category_Master").orderBy("Year", "Quarter")
        quarterly_category = quarterly_category \
            .withColumn("Previous_Quarter_Revenue", 
                lag("Total_Revenue", 1).over(category_window)
            ) \
            .withColumn("QoQ_Revenue_Growth", 
                when(col("Previous_Quarter_Revenue") > 0,
                    (col("Total_Revenue") - col("Previous_Quarter_Revenue")) / col("Previous_Quarter_Revenue")
                ).otherwise(0)
            )
        
        # Quarterly regional performance
        logger.info("  Creating quarterly regional aggregations...")
        quarterly_regional = df.groupBy(
            "Year", "Quarter", "Store_Region_Master"
        ).agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            count("Transaction_ID").alias("Transaction_Count"),
            countDistinct("Product_Category_Master").alias("Category_Diversity"),
            avg("Sales_Velocity_Calculated").alias("Avg_Sales_Velocity"),
            sum(when(col("Product_Category_Master") == "BEER", col("Total_Revenue")).otherwise(0)).alias("Beer_Revenue"),
            sum(when(col("Product_Category_Master") == "HARD SELTZER", col("Total_Revenue")).otherwise(0)).alias("Seltzer_Revenue")
        ).withColumn("Seltzer_Share", 
            col("Seltzer_Revenue") / (col("Beer_Revenue") + col("Seltzer_Revenue"))
        ).withColumn("Beer_Share", 
            col("Beer_Revenue") / (col("Beer_Revenue") + col("Seltzer_Revenue"))
        )
        
        # Store aggregations
        self.aggregated_tables['quarterly_category'] = quarterly_category
        self.aggregated_tables['quarterly_regional'] = quarterly_regional
        
        logger.info("✅ Quarterly aggregations completed")
        return {
            'category': quarterly_category,
            'regional': quarterly_regional
        }
    
    def generate_cleaning_report(self):
        """Generate comprehensive data cleaning and processing report."""
        print(f"\n" + "=" * 80)
        print(f"📋 DATA CLEANING AND PROCESSING REPORT")
        print("=" * 80)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Cleaning summary
        print(f"\n🧹 DATA CLEANING SUMMARY:")
        for table_name, report in self.cleaning_report.items():
            if table_name != 'referential_integrity':
                print(f"\n📊 {table_name.upper()}:")
                print(f"   Initial Records: {report['initial_count']:,}")
                print(f"   Final Records: {report['final_count']:,}")
                print(f"   Records Removed: {report['records_removed']:,}")
                print(f"   Data Quality: {((report['final_count']/report['initial_count'])*100):.1f}% retained")
                
                print(f"   Cleaning Steps:")
                for step in report['cleaning_steps']:
                    print(f"     • {step}")
        
        # Referential integrity
        if 'referential_integrity' in self.cleaning_report:
            integrity = self.cleaning_report['referential_integrity']
            print(f"\n🔗 REFERENTIAL INTEGRITY:")
            print(f"   Invalid SKU references removed: {integrity['invalid_skus']:,}")
            print(f"   Invalid Retailer references removed: {integrity['invalid_retailers']:,}")
            print(f"   Final valid transactions: {integrity['final_sales_count']:,}")
        
        # Feature engineering summary
        if self.fact_table:
            feature_count = len(self.fact_table.columns)
            record_count = self.fact_table.count()
            print(f"\n🔧 FEATURE ENGINEERING:")
            print(f"   Total Features Created: {feature_count}")
            print(f"   Fact Table Records: {record_count:,}")
            print(f"   Key Features Added:")
            print(f"     • Sales velocity and TDP metrics")
            print(f"     • Time-based features (seasonality, trends)")
            print(f"     • Rolling averages and growth rates")
            print(f"     • Market share and competitive metrics")
            print(f"     • Performance tiers and anomaly flags")
        
        # Aggregation summary
        if self.aggregated_tables:
            print(f"\n📈 AGGREGATION TABLES:")
            for table_name, df in self.aggregated_tables.items():
                count = df.count()
                print(f"   {table_name}: {count:,} records")
        
        print(f"\n🎯 PIPELINE STATUS: ✅ COMPLETED SUCCESSFULLY")
        print(f"   Data is ready for trend analysis and anomaly detection")
        print(f"   All business rules validated and applied")
        print(f"   Comprehensive feature set available for modeling")
    
    def run_complete_pipeline(self):
        """Run the complete data cleaning and feature engineering pipeline."""
        print("🚀 Starting Complete Data Cleaning and Feature Engineering Pipeline")
        print("=" * 80)
        
        try:
            # Initialize Spark
            self.create_spark_session()
            
            # Load raw data
            self.load_raw_data()
            
            # Clean each dataset
            self.clean_products_data()
            self.clean_locations_data()
            self.clean_sales_transactions_data()
            
            # Validate referential integrity
            self.validate_referential_integrity()
            
            # Create fact table
            self.create_comprehensive_fact_table()
            
            # Engineer features
            self.engineer_features()
            
            # Create aggregations
            self.create_monthly_aggregations()
            self.create_quarterly_aggregations()
            
            # Generate report
            self.generate_cleaning_report()
            
            print(f"\n🎉 Pipeline completed successfully!")
            print(f"📊 Data is ready for business analysis")
            print(f"🔍 Trend detection can now begin")
            
            return {
                'fact_table': self.fact_table,
                'aggregated_tables': self.aggregated_tables,
                'cleaning_report': self.cleaning_report
            }
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            raise
        finally:
            if self.spark:
                self.spark.stop()

def main():
    """Main execution function."""
    pipeline = DataCleaningPipeline()
    results = pipeline.run_complete_pipeline()
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Run trend analysis on fact table")
    print(f"   2. Use monthly/quarterly aggregations for reporting")
    print(f"   3. Apply anomaly detection algorithms")
    print(f"   4. Generate business recommendations")

if __name__ == "__main__":
    main()