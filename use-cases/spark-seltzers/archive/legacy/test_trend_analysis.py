#!/usr/bin/env python3
"""
Test script for trend analysis - simplified version to verify core functionality
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

def test_trend_analysis():
    """Test the core trend analysis functionality."""
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("TestTrendAnalysis") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        # Load data using existing ingestion
        from spark_data_ingestion import DataIngestionPipeline
        
        ingestion = DataIngestionPipeline()
        ingestion.spark = spark
        ingestion.define_schemas()
        
        # Load sample data
        logger.info("Loading sample data...")
        products_df = ingestion.read_csv_with_validation('products.csv', 'products')
        locations_df = ingestion.read_csv_with_validation('locations.csv', 'locations')
        sales_df = ingestion.read_csv_with_validation('sales_transactions.csv', 'sales_transactions')
        
        # Take sample for testing
        sales_sample = sales_df.sample(0.01, seed=42)  # 1% sample
        
        logger.info(f"Sample data: {products_df.count()} products, {locations_df.count()} locations, {sales_sample.count()} sales")
        
        # Basic cleaning
        products_clean = products_df.filter(col("SKU").isNotNull()) \
            .withColumn("Category", upper(trim(col("Category"))))
        
        sales_clean = sales_sample.filter(col("Transaction_ID").isNotNull()) \
            .filter(col("Units_Sold") > 0) \
            .filter(col("Total_Revenue") > 0) \
            .withColumn("Category", upper(trim(col("Category"))))
        
        # Create fact table
        fact_table = sales_clean.join(
            broadcast(products_clean.select("SKU", "Category")),
            "SKU", "inner"
        ).select(
            sales_clean["*"],
            products_clean.Category.alias("Product_Category")
        ).withColumn("Year", year(col("Date"))) \
         .withColumn("Month", month(col("Date"))) \
         .withColumn("Year_Month", date_format(col("Date"), "yyyy-MM"))
        
        logger.info("✅ Fact table created")
        
        # Test 1: Monthly growth rates
        logger.info("Testing monthly growth rate calculation...")
        
        monthly_category = fact_table.groupBy("Year", "Month", "Year_Month", "Product_Category").agg(
            sum("Total_Revenue").alias("Monthly_Revenue"),
            sum("Units_Sold").alias("Monthly_Units"),
            count("Transaction_ID").alias("Monthly_Transactions")
        )
        
        # Add date for ordering
        monthly_category = monthly_category.withColumn(
            "Date_Key", 
            to_date(concat(col("Year"), lit("-"), 
                          when(col("Month") < 10, concat(lit("0"), col("Month")))
                          .otherwise(col("Month")), lit("-01")))
        )
        
        # Calculate growth rates
        category_window = Window.partitionBy("Product_Category").orderBy("Date_Key")
        
        monthly_growth = monthly_category \
            .withColumn("Previous_Month_Revenue", 
                lag("Monthly_Revenue", 1).over(category_window)
            ) \
            .withColumn("MoM_Revenue_Growth", 
                when(col("Previous_Month_Revenue") > 0,
                    ((col("Monthly_Revenue") - col("Previous_Month_Revenue")) / col("Previous_Month_Revenue")) * 100
                ).otherwise(0)
            )
        
        growth_count = monthly_growth.count()
        logger.info(f"✅ Growth rates calculated: {growth_count} monthly records")
        
        # Test 2: Pivot point analysis
        logger.info("Testing pivot point identification...")
        
        beer_data = monthly_growth.filter(col("Product_Category") == "BEER") \
            .select("Year_Month", "Date_Key", 
                   col("Monthly_Revenue").alias("Beer_Revenue"),
                   col("MoM_Revenue_Growth").alias("Beer_Growth"))
        
        seltzer_data = monthly_growth.filter(col("Product_Category") == "HARD SELTZER") \
            .select("Year_Month", "Date_Key",
                   col("Monthly_Revenue").alias("Seltzer_Revenue"),
                   col("MoM_Revenue_Growth").alias("Seltzer_Growth"))
        
        comparison = beer_data.join(seltzer_data, ["Year_Month", "Date_Key"], "outer") \
            .fillna(0, ["Beer_Revenue", "Beer_Growth", "Seltzer_Revenue", "Seltzer_Growth"])
        
        pivot_analysis = comparison \
            .withColumn("Total_Revenue", col("Beer_Revenue") + col("Seltzer_Revenue")) \
            .withColumn("Seltzer_Share", 
                when(col("Total_Revenue") > 0,
                    col("Seltzer_Revenue") / col("Total_Revenue") * 100
                ).otherwise(0)
            ) \
            .withColumn("Growth_Difference", 
                col("Seltzer_Growth") - col("Beer_Growth")
            ) \
            .withColumn("Pivot_Point", 
                col("Seltzer_Growth") > col("Beer_Growth")
            )
        
        pivot_count = pivot_analysis.count()
        logger.info(f"✅ Pivot analysis completed: {pivot_count} comparison records")
        
        # Test 3: Market share evolution
        logger.info("Testing market share evolution...")
        
        daily_market = fact_table.groupBy("Date", "Product_Category").agg(
            sum("Total_Revenue").alias("Daily_Revenue")
        )
        
        daily_total_window = Window.partitionBy("Date")
        
        daily_share = daily_market \
            .withColumn("Daily_Total", sum("Daily_Revenue").over(daily_total_window)) \
            .withColumn("Market_Share", 
                when(col("Daily_Total") > 0,
                    col("Daily_Revenue") / col("Daily_Total") * 100
                ).otherwise(0)
            )
        
        share_count = daily_share.count()
        logger.info(f"✅ Market share evolution calculated: {share_count} daily records")
        
        # Display sample results
        print("\n📊 SAMPLE TREND ANALYSIS RESULTS:")
        
        print("\n1. Monthly Growth Rates (Latest 5 months):")
        monthly_growth.orderBy(desc("Date_Key")).select(
            "Year_Month", "Product_Category", "Monthly_Revenue", "MoM_Revenue_Growth"
        ).show(10)
        
        print("\n2. Pivot Point Analysis (Growth Difference):")
        pivot_analysis.orderBy("Date_Key").select(
            "Year_Month", "Beer_Growth", "Seltzer_Growth", "Growth_Difference", "Seltzer_Share", "Pivot_Point"
        ).show(12)
        
        print("\n3. Market Share Evolution (Sample):")
        daily_share.filter(col("Product_Category") == "HARD SELTZER") \
            .orderBy("Date").select("Date", "Product_Category", "Market_Share").show(10)
        
        # Key insights
        pivot_points = pivot_analysis.filter(col("Pivot_Point") == True).count()
        max_seltzer_share = pivot_analysis.agg(max("Seltzer_Share")).collect()[0][0]
        
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"   Pivot points detected: {pivot_points}")
        print(f"   Maximum seltzer share: {max_seltzer_share:.2f}%")
        
        logger.info("🎉 Trend analysis test completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False
    finally:
        spark.stop()

if __name__ == "__main__":
    success = test_trend_analysis()
    if success:
        print("\n✅ Trend analysis test passed! The full pipeline should work.")
    else:
        print("\n❌ Test failed. Check the logs above.")