#!/usr/bin/env python3
"""
PySpark ETL Pipeline for Beer Company Analysis
==============================================

This script processes the synthetic POS data to identify the beer-to-seltzer
market trend and generate business insights for strategic decision making.
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create optimized SparkSession for POS data analysis."""
    return SparkSession.builder \
        .appName("BeerCompanyPOSAnalysis") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .getOrCreate()

def load_data(spark):
    """Load synthetic POS data into Spark DataFrames."""
    logger.info("Loading synthetic POS data...")
    
    # Define schemas for better performance
    products_schema = StructType([
        StructField("SKU", StringType(), True),
        StructField("Brand", StringType(), True),
        StructField("Product_Name", StringType(), True),
        StructField("Category", StringType(), True),
        StructField("ABV", DoubleType(), True),
        StructField("Price_Per_Unit", DoubleType(), True)
    ])
    
    locations_schema = StructType([
        StructField("Retailer_ID", StringType(), True),
        StructField("Chain_Name", StringType(), True),
        StructField("Store_Type", StringType(), True),
        StructField("Region", StringType(), True),
        StructField("State", StringType(), True),
        StructField("City", StringType(), True),
        StructField("Store_Size", StringType(), True),
        StructField("Alcohol_License", BooleanType(), True)
    ])
    
    sales_schema = StructType([
        StructField("Transaction_ID", StringType(), True),
        StructField("Date", StringType(), True),
        StructField("Retailer_ID", StringType(), True),
        StructField("SKU", StringType(), True),
        StructField("Product_Name", StringType(), True),
        StructField("Brand", StringType(), True),
        StructField("Category", StringType(), True),
        StructField("Units_Sold", IntegerType(), True),
        StructField("Unit_Price", DoubleType(), True),
        StructField("Total_Revenue", DoubleType(), True),
        StructField("Store_Type", StringType(), True),
        StructField("Region", StringType(), True),
        StructField("State", StringType(), True)
    ])
    
    # Load CSV files
    products_df = spark.read.csv("synthetic_data/products.csv", header=True, schema=products_schema)
    locations_df = spark.read.csv("synthetic_data/locations.csv", header=True, schema=locations_schema)
    sales_df = spark.read.csv("synthetic_data/sales_transactions.csv", header=True, schema=sales_schema)
    
    # Convert date column
    sales_df = sales_df.withColumn("Date", to_date(col("Date"), "yyyy-MM-dd"))
    sales_df = sales_df.withColumn("Month", month(col("Date")))
    sales_df = sales_df.withColumn("Year_Month", date_format(col("Date"), "yyyy-MM"))
    
    logger.info(f"Loaded data: {products_df.count()} products, {locations_df.count()} locations, {sales_df.count()} transactions")
    
    return products_df, locations_df, sales_df

def analyze_category_trends(sales_df):
    """Analyze category trends over time to identify the pivot point."""
    logger.info("Analyzing category trends...")
    
    # Monthly category performance
    monthly_trends = sales_df.groupBy("Year_Month", "Category") \
        .agg(
            sum("Units_Sold").alias("Total_Units"),
            sum("Total_Revenue").alias("Total_Revenue"),
            count("Transaction_ID").alias("Transaction_Count"),
            avg("Total_Revenue").alias("Avg_Transaction_Value")
        ) \
        .orderBy("Year_Month", "Category")
    
    print("\n📈 MONTHLY CATEGORY TRENDS")
    print("=" * 50)
    monthly_trends.show(24, truncate=False)
    
    # Calculate growth rates
    window_spec = Window.partitionBy("Category").orderBy("Year_Month")
    
    growth_analysis = monthly_trends.withColumn(
        "Previous_Revenue", 
        lag("Total_Revenue").over(window_spec)
    ).withColumn(
        "Growth_Rate",
        when(col("Previous_Revenue").isNotNull(), 
             ((col("Total_Revenue") - col("Previous_Revenue")) / col("Previous_Revenue") * 100))
        .otherwise(0)
    )
    
    print("\n📊 GROWTH RATE ANALYSIS")
    print("=" * 50)
    growth_analysis.select("Year_Month", "Category", "Total_Revenue", "Growth_Rate") \
        .orderBy("Year_Month", "Category").show(24, truncate=False)
    
    return monthly_trends, growth_analysis

def identify_pivot_point(growth_analysis):
    """Identify the specific pivot point where seltzers overtake beer growth."""
    logger.info("Identifying market pivot point...")
    
    # Find months where seltzer growth exceeds beer growth
    beer_growth = growth_analysis.filter(col("Category") == "Beer") \
        .select("Year_Month", col("Growth_Rate").alias("Beer_Growth_Rate"))
    
    seltzer_growth = growth_analysis.filter(col("Category") == "Hard Seltzer") \
        .select("Year_Month", col("Growth_Rate").alias("Seltzer_Growth_Rate"))
    
    pivot_analysis = beer_growth.join(seltzer_growth, "Year_Month", "inner") \
        .withColumn("Seltzer_Advantage", col("Seltzer_Growth_Rate") - col("Beer_Growth_Rate")) \
        .withColumn("Pivot_Point", col("Seltzer_Growth_Rate") > col("Beer_Growth_Rate")) \
        .orderBy("Year_Month")
    
    print("\n🎯 PIVOT POINT ANALYSIS")
    print("=" * 50)
    pivot_analysis.show(12, truncate=False)
    
    # Find first pivot month
    first_pivot = pivot_analysis.filter(col("Pivot_Point") == True).first()
    if first_pivot:
        print(f"\n🚨 MARKET PIVOT DETECTED: {first_pivot['Year_Month']}")
        print(f"   Seltzer Growth: {first_pivot['Seltzer_Growth_Rate']:.1f}%")
        print(f"   Beer Growth: {first_pivot['Beer_Growth_Rate']:.1f}%")
        print(f"   Advantage: {first_pivot['Seltzer_Advantage']:.1f} percentage points")
    
    return pivot_analysis

def regional_analysis(sales_df):
    """Analyze regional adoption patterns."""
    logger.info("Analyzing regional patterns...")
    
    regional_performance = sales_df.groupBy("Region", "Category") \
        .agg(
            sum("Total_Revenue").alias("Total_Revenue"),
            sum("Units_Sold").alias("Total_Units"),
            count("Transaction_ID").alias("Transaction_Count")
        )
    
    # Calculate seltzer market share by region
    regional_totals = regional_performance.groupBy("Region") \
        .agg(sum("Total_Revenue").alias("Region_Total_Revenue"))
    
    regional_share = regional_performance.join(regional_totals, "Region") \
        .withColumn("Market_Share_Pct", 
                   round((col("Total_Revenue") / col("Region_Total_Revenue")) * 100, 2)) \
        .filter(col("Category") == "Hard Seltzer") \
        .select("Region", "Market_Share_Pct", "Total_Revenue") \
        .orderBy(desc("Market_Share_Pct"))
    
    print("\n🗺️ REGIONAL SELTZER ADOPTION")
    print("=" * 50)
    regional_share.show()
    
    return regional_share

def generate_business_insights(monthly_trends, pivot_analysis, regional_share):
    """Generate executive summary and business recommendations."""
    logger.info("Generating business insights...")
    
    # Calculate final market position
    final_month_data = monthly_trends.filter(col("Year_Month") == "2023-12")
    
    beer_final = final_month_data.filter(col("Category") == "Beer").first()
    seltzer_final = final_month_data.filter(col("Category") == "Hard Seltzer").first()
    
    print("\n" + "=" * 60)
    print("🍺 EXECUTIVE SUMMARY: BEER COMPANY MARKET ANALYSIS")
    print("=" * 60)
    
    if beer_final and seltzer_final:
        total_revenue = beer_final['Total_Revenue'] + seltzer_final['Total_Revenue']
        seltzer_share = (seltzer_final['Total_Revenue'] / total_revenue) * 100
        
        print(f"\n📊 FINAL MARKET POSITION (December 2023):")
        print(f"   Beer Revenue: ${beer_final['Total_Revenue']:,.2f}")
        print(f"   Seltzer Revenue: ${seltzer_final['Total_Revenue']:,.2f}")
        print(f"   Seltzer Market Share: {seltzer_share:.1f}%")
        
        if seltzer_share > 50:
            print(f"\n🚨 CRITICAL FINDING: Hard Seltzers now dominate the market!")
        elif seltzer_share > 30:
            print(f"\n⚠️  WARNING: Hard Seltzers represent significant market threat!")
        
    # Regional insights
    top_seltzer_region = regional_share.first()
    if top_seltzer_region:
        print(f"\n🗺️ REGIONAL LEADER: {top_seltzer_region['Region']}")
        print(f"   Seltzer Market Share: {top_seltzer_region['Market_Share_Pct']}%")
    
    print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
    print(f"   1. IMMEDIATE: Launch hard seltzer product line")
    print(f"   2. PRIORITY: Focus on {top_seltzer_region['Region']} region first")
    print(f"   3. TIMELINE: Market entry within 6 months to capture growth")
    print(f"   4. INVESTMENT: Allocate R&D budget to seltzer innovation")
    print(f"   5. MARKETING: Pivot brand messaging to include wellness trends")
    
    print("\n" + "=" * 60)

def main():
    """Main ETL pipeline execution."""
    print("🍺 Beer Company POS Data Analysis Pipeline")
    print("=" * 50)
    
    # Initialize Spark
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        # Load data
        products_df, locations_df, sales_df = load_data(spark)
        
        # Perform analysis
        monthly_trends, growth_analysis = analyze_category_trends(sales_df)
        pivot_analysis = identify_pivot_point(growth_analysis)
        regional_share = regional_analysis(sales_df)
        
        # Generate insights
        generate_business_insights(monthly_trends, pivot_analysis, regional_share)
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"📈 Clear evidence of market disruption detected")
        print(f"🎯 Strategic pivot to hard seltzers recommended")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()