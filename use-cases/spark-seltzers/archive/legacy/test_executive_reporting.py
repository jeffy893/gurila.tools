#!/usr/bin/env python3
"""
Test script for executive reporting pipeline - simplified version to verify core functionality
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

def test_executive_reporting():
    """Test the core executive reporting functionality."""
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("TestExecutiveReporting") \
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
        
        # Basic cleaning and fact table creation
        products_clean = products_df.filter(col("SKU").isNotNull()) \
            .withColumn("Category", upper(trim(col("Category"))))
        
        locations_clean = locations_df.filter(col("Retailer_ID").isNotNull()) \
            .withColumn("Region", upper(trim(col("Region"))))
        
        sales_clean = sales_sample.filter(col("Transaction_ID").isNotNull()) \
            .filter(col("Units_Sold") > 0) \
            .filter(col("Total_Revenue") > 0) \
            .withColumn("Category", upper(trim(col("Category"))))
        
        # Create comprehensive fact table
        fact_table = sales_clean.join(
            broadcast(products_clean.select("SKU", "Category", "Brand", "ABV", "Price_Per_Unit")),
            "SKU", "inner"
        ).join(
            broadcast(locations_clean.select("Retailer_ID", "Region", "Store_Type")),
            "Retailer_ID", "inner"
        ).select(
            sales_clean["*"],
            products_clean.Category.alias("Product_Category"),
            products_clean.Brand.alias("Product_Brand"),
            products_clean.ABV.alias("Product_ABV"),
            products_clean.Price_Per_Unit.alias("Product_Price"),
            locations_clean.Region.alias("Store_Region"),
            locations_clean.Store_Type.alias("Store_Channel")
        )
        
        # Add time dimensions
        fact_table = fact_table \
            .withColumn("Year", year(col("Date"))) \
            .withColumn("Month", month(col("Date"))) \
            .withColumn("Quarter", quarter(col("Date"))) \
            .withColumn("Year_Month", date_format(col("Date"), "yyyy-MM")) \
            .withColumn("Week_of_Year", weekofyear(col("Date"))) \
            .withColumn("Day_of_Week", dayofweek(col("Date")))
        
        fact_table.cache()
        record_count = fact_table.count()
        logger.info(f"✅ Fact table created: {record_count:,} records")
        
        # Test 1: Executive Metrics - Revenue Impact Analysis
        logger.info("Testing revenue impact analysis...")
        
        revenue_impact = fact_table.groupBy("Product_Category").agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            count("Transaction_ID").alias("Total_Transactions"),
            countDistinct("Product_Brand").alias("Active_Brands"),
            countDistinct("Store_Region").alias("Geographic_Reach"),
            countDistinct("Retailer_ID").alias("Active_Stores"),
            avg("Total_Revenue").alias("Avg_Transaction_Value"),
            avg("TDP").alias("Avg_TDP")
        ).withColumn("Revenue_Share", 
            col("Total_Revenue") / sum("Total_Revenue").over(Window.partitionBy())
        ).withColumn("Units_Share", 
            col("Total_Units") / sum("Total_Units").over(Window.partitionBy())
        )
        
        revenue_count = revenue_impact.count()
        logger.info(f"✅ Revenue impact analysis: {revenue_count} categories")
        
        # Test 2: Market Share Evolution
        logger.info("Testing market share evolution...")
        
        monthly_share = fact_table.groupBy("Year_Month", "Product_Category").agg(
            sum("Total_Revenue").alias("Monthly_Revenue"),
            sum("Units_Sold").alias("Monthly_Units")
        )
        
        monthly_total_window = Window.partitionBy("Year_Month")
        
        market_evolution = monthly_share \
            .withColumn("Monthly_Total_Revenue", 
                sum("Monthly_Revenue").over(monthly_total_window)
            ) \
            .withColumn("Market_Share_Revenue", 
                col("Monthly_Revenue") / col("Monthly_Total_Revenue") * 100
            )
        
        evolution_count = market_evolution.count()
        logger.info(f"✅ Market share evolution: {evolution_count} monthly records")
        
        # Test 3: ROI Projections
        logger.info("Testing ROI projections...")
        
        # Current performance baseline
        current_performance = fact_table.filter(col("Product_Category") == "HARD SELTZER") \
            .agg(
                sum("Total_Revenue").alias("Current_Seltzer_Revenue"),
                sum("Units_Sold").alias("Current_Seltzer_Units"),
                avg("Total_Revenue").alias("Avg_Seltzer_Transaction")
            ).collect()[0]
        
        beer_performance = fact_table.filter(col("Product_Category") == "BEER") \
            .agg(
                sum("Total_Revenue").alias("Current_Beer_Revenue"),
                sum("Units_Sold").alias("Current_Beer_Units"),
                avg("Total_Revenue").alias("Avg_Beer_Transaction")
            ).collect()[0]
        
        # Simple ROI calculation
        total_market_revenue = current_performance['Current_Seltzer_Revenue'] + beer_performance['Current_Beer_Revenue']
        current_seltzer_share = (current_performance['Current_Seltzer_Revenue'] / total_market_revenue) * 100
        
        logger.info(f"✅ ROI baseline calculated - Seltzer share: {current_seltzer_share:.2f}%")
        
        # Test 4: Geographic Analysis
        logger.info("Testing geographic analysis...")
        
        regional_opportunity = fact_table.groupBy("Store_Region", "Product_Category").agg(
            sum("Total_Revenue").alias("Regional_Revenue"),
            sum("Units_Sold").alias("Regional_Units"),
            countDistinct("Retailer_ID").alias("Store_Count")
        )
        
        regional_total_window = Window.partitionBy("Store_Region")
        
        regional_analysis = regional_opportunity \
            .withColumn("Regional_Total_Revenue", 
                sum("Regional_Revenue").over(regional_total_window)
            ) \
            .withColumn("Category_Penetration", 
                col("Regional_Revenue") / col("Regional_Total_Revenue") * 100
            )
        
        seltzer_regional = regional_analysis.filter(col("Product_Category") == "HARD SELTZER") \
            .withColumn("Opportunity_Score", 
                col("Category_Penetration") * col("Store_Count") / 100
            ) \
            .withColumn("Priority_Rank", 
                row_number().over(Window.orderBy(desc("Opportunity_Score")))
            )
        
        regional_count = seltzer_regional.count()
        logger.info(f"✅ Geographic analysis: {regional_count} regions")
        
        # Display sample results
        print("\n📊 EXECUTIVE REPORTING TEST RESULTS:")
        
        print("\n1. Revenue Impact by Category:")
        revenue_impact.select(
            "Product_Category", "Total_Revenue", "Revenue_Share", "Active_Brands", "Geographic_Reach"
        ).show()
        
        print("\n2. Market Share Evolution (Sample):")
        market_evolution.orderBy("Year_Month").select(
            "Year_Month", "Product_Category", "Market_Share_Revenue"
        ).show(10)
        
        print("\n3. Geographic Opportunities (Top 5):")
        seltzer_regional.orderBy("Priority_Rank").select(
            "Store_Region", "Category_Penetration", "Opportunity_Score", "Priority_Rank", "Store_Count"
        ).show(5)
        
        # Key business insights
        total_revenue = revenue_impact.agg(sum("Total_Revenue")).collect()[0][0]
        seltzer_revenue = revenue_impact.filter(col("Product_Category") == "HARD SELTZER") \
            .select("Total_Revenue").collect()[0]["Total_Revenue"]
        beer_revenue = revenue_impact.filter(col("Product_Category") == "BEER") \
            .select("Total_Revenue").collect()[0]["Total_Revenue"]
        
        seltzer_share = (seltzer_revenue / total_revenue) * 100
        beer_share = (beer_revenue / total_revenue) * 100
        
        print(f"\n🎯 KEY BUSINESS INSIGHTS:")
        print(f"   Total Market Revenue: ${total_revenue:,.0f}")
        print(f"   Beer Market Share: {beer_share:.1f}%")
        print(f"   Seltzer Market Share: {seltzer_share:.1f}%")
        print(f"   Untapped Market: {100 - seltzer_share:.1f}%")
        
        # ROI scenario example
        target_share = 15.0  # Target 15% market share
        target_revenue = total_revenue * (target_share / 100)
        incremental_revenue = target_revenue - seltzer_revenue
        investment_multiple = 2.0
        required_investment = incremental_revenue * investment_multiple
        annual_roi = (incremental_revenue / required_investment) * 100 if required_investment > 0 else 0
        
        print(f"\n💰 SAMPLE ROI PROJECTION (15% Market Share Target):")
        print(f"   Target Revenue: ${target_revenue:,.0f}")
        print(f"   Incremental Revenue: ${incremental_revenue:,.0f}")
        print(f"   Required Investment: ${required_investment:,.0f}")
        print(f"   Projected Annual ROI: {annual_roi:.1f}%")
        
        logger.info("🎉 Executive reporting test completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        spark.stop()

if __name__ == "__main__":
    success = test_executive_reporting()
    if success:
        print("\n✅ Executive reporting test passed! The full pipeline should work.")
    else:
        print("\n❌ Test failed. Check the logs above.")