#!/usr/bin/env python3
"""
Test script for the data cleaning pipeline - simplified version
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pipeline():
    """Test the core functionality of the cleaning pipeline."""
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("TestDataCleaning") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        # Load raw data using existing ingestion
        from spark_data_ingestion import DataIngestionPipeline
        
        ingestion = DataIngestionPipeline()
        ingestion.spark = spark
        ingestion.define_schemas()
        
        # Load just products and a sample of sales for testing
        logger.info("Loading test data...")
        products_df = ingestion.read_csv_with_validation('products.csv', 'products')
        locations_df = ingestion.read_csv_with_validation('locations.csv', 'locations')
        
        # Load only first 1000 sales records for testing
        sales_df = ingestion.read_csv_with_validation('sales_transactions.csv', 'sales_transactions')
        sales_df = sales_df.limit(1000)
        
        logger.info(f"Loaded test data: {products_df.count()} products, {locations_df.count()} locations, {sales_df.count()} sales")
        
        # Test basic cleaning
        logger.info("Testing data cleaning...")
        
        # Clean products
        products_clean = products_df \
            .filter(col("SKU").isNotNull()) \
            .withColumn("Brand", upper(trim(col("Brand")))) \
            .withColumn("Category", upper(trim(col("Category")))) \
            .withColumn("Is_Beer", col("Category") == "BEER") \
            .withColumn("Is_Seltzer", col("Category") == "HARD SELTZER")
        
        # Clean locations  
        locations_clean = locations_df \
            .filter(col("Retailer_ID").isNotNull()) \
            .withColumn("Region", upper(trim(col("Region")))) \
            .withColumn("Store_Type", initcap(trim(col("Store_Type"))))
        
        # Clean sales
        sales_clean = sales_df \
            .filter(col("Transaction_ID").isNotNull()) \
            .filter(col("Units_Sold") > 0) \
            .filter(col("Total_Revenue") > 0) \
            .withColumn("Category", upper(trim(col("Category")))) \
            .withColumn("Brand", upper(trim(col("Brand"))))
        
        logger.info("✅ Basic cleaning completed")
        
        # Test joins
        logger.info("Testing joins...")
        
        # Join sales with products
        fact_table = sales_clean.join(
            broadcast(products_clean),
            sales_clean.SKU == products_clean.SKU,
            "inner"
        ).select(
            sales_clean["*"],
            products_clean.Brand.alias("Product_Brand_Master"),
            products_clean.Category.alias("Product_Category_Master"),
            products_clean.ABV.alias("Product_ABV"),
            products_clean.Is_Beer.alias("Product_Is_Beer"),
            products_clean.Is_Seltzer.alias("Product_Is_Seltzer")
        )
        
        # Join with locations
        fact_table = fact_table.join(
            broadcast(locations_clean),
            fact_table.Retailer_ID == locations_clean.Retailer_ID,
            "inner"
        ).select(
            fact_table["*"],
            locations_clean.Region.alias("Store_Region_Master"),
            locations_clean.Store_Type.alias("Store_Type_Master")
        )
        
        record_count = fact_table.count()
        logger.info(f"✅ Joins completed: {record_count} records in fact table")
        
        # Test basic feature engineering
        logger.info("Testing feature engineering...")
        
        fact_table = fact_table \
            .withColumn("Revenue_Per_Unit_Calc", col("Total_Revenue") / col("Units_Sold")) \
            .withColumn("Month", month(col("Date"))) \
            .withColumn("Quarter", quarter(col("Date"))) \
            .withColumn("Is_Weekend", dayofweek(col("Date")).isin([1, 7])) \
            .withColumn("Market_Share", col("Total_Revenue") / sum("Total_Revenue").over(Window.partitionBy("Date")))
        
        logger.info("✅ Feature engineering completed")
        
        # Test aggregation
        logger.info("Testing aggregation...")
        
        monthly_agg = fact_table.groupBy("Month", "Product_Category_Master").agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            count("Transaction_ID").alias("Transaction_Count")
        )
        
        agg_count = monthly_agg.count()
        logger.info(f"✅ Aggregation completed: {agg_count} monthly records")
        
        # Show sample results
        print("\n📊 SAMPLE RESULTS:")
        print("\nFact Table Schema:")
        fact_table.printSchema()
        
        print(f"\nFact Table Sample (5 rows):")
        fact_table.select("Transaction_ID", "Date", "Product_Category_Master", "Store_Region_Master", "Total_Revenue", "Market_Share").show(5)
        
        print(f"\nMonthly Aggregation:")
        monthly_agg.orderBy("Month", "Product_Category_Master").show()
        
        logger.info("🎉 Test pipeline completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False
    finally:
        spark.stop()

if __name__ == "__main__":
    success = test_pipeline()
    if success:
        print("\n✅ All tests passed! The full pipeline should work.")
    else:
        print("\n❌ Tests failed. Check the logs above.")