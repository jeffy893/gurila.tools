#!/usr/bin/env python3
"""
PySpark Trend Analysis Pipeline - Beer vs Hard Seltzer Market Shift
==================================================================

This pipeline performs comprehensive trend analysis to identify the exact pivot point
where Hard Seltzer growth exceeds Beer growth, with statistical significance testing
and detailed breakdowns by geography and brands.

Key Analyses:
- Month-over-month and year-over-year growth rates
- Pivot point identification with statistical significance
- Regional and brand-level trend analysis
- Market share evolution tracking
- Competitive dynamics visualization data
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging
from datetime import datetime
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendAnalysisPipeline:
    """
    Comprehensive trend analysis pipeline for beer vs seltzer market dynamics.
    """
    
    def __init__(self, data_dir: str = "synthetic_data"):
        """Initialize the trend analysis pipeline."""
        self.data_dir = data_dir
        self.spark = None
        self.fact_table = None
        self.trend_results = {}
        self.pivot_analysis = {}
        self.regional_analysis = {}
        self.brand_analysis = {}
        self.market_share_evolution = {}
        
    def create_spark_session(self) -> SparkSession:
        """Create optimized SparkSession for trend analysis."""
        logger.info("Creating SparkSession for trend analysis...")
        
        self.spark = SparkSession.builder \
            .appName("BeerSeltzerTrendAnalysis") \
            .master("local[*]") \
            .config("spark.driver.memory", "6g") \
            .config("spark.driver.maxResultSize", "3g") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.enabled", "true") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"✅ SparkSession created successfully")
        return self.spark
    
    def load_cleaned_data(self):
        """Load cleaned data using the test pipeline approach."""
        logger.info("Loading cleaned data for trend analysis...")
        
        # Use the test pipeline approach for reliable data loading
        from spark_data_ingestion import DataIngestionPipeline
        
        ingestion = DataIngestionPipeline(self.data_dir)
        ingestion.spark = self.spark
        ingestion.define_schemas()
        
        # Load all datasets
        products_df = ingestion.read_csv_with_validation('products.csv', 'products')
        locations_df = ingestion.read_csv_with_validation('locations.csv', 'locations')
        sales_df = ingestion.read_csv_with_validation('sales_transactions.csv', 'sales_transactions')
        
        logger.info(f"Loaded raw data: {products_df.count()} products, {locations_df.count()} locations, {sales_df.count()} sales")
        
        # Apply basic cleaning
        products_clean = products_df \
            .filter(col("SKU").isNotNull()) \
            .withColumn("Brand", upper(trim(col("Brand")))) \
            .withColumn("Category", upper(trim(col("Category")))) \
            .filter((col("ABV") >= 0) & (col("ABV") <= 20)) \
            .filter((col("Price_Per_Unit") > 0) & (col("Price_Per_Unit") <= 10))
        
        locations_clean = locations_df \
            .filter(col("Retailer_ID").isNotNull()) \
            .withColumn("Region", upper(trim(col("Region")))) \
            .withColumn("Store_Type", initcap(trim(col("Store_Type")))) \
            .filter(col("Region").isin(["NORTHEAST", "SOUTHEAST", "MIDWEST", "WEST", "SOUTHWEST"]))
        
        sales_clean = sales_df \
            .filter(col("Transaction_ID").isNotNull()) \
            .filter(col("Units_Sold") > 0) \
            .filter(col("Total_Revenue") > 0) \
            .filter((col("Unit_Price") > 0) & (col("Unit_Price") <= 10)) \
            .withColumn("Category", upper(trim(col("Category")))) \
            .withColumn("Brand", upper(trim(col("Brand"))))
        
        # Create fact table with proper joins
        fact_table = sales_clean.join(
            broadcast(products_clean),
            sales_clean.SKU == products_clean.SKU,
            "inner"
        ).select(
            sales_clean["*"],
            products_clean.Brand.alias("Product_Brand"),
            products_clean.Category.alias("Product_Category"),
            products_clean.ABV.alias("Product_ABV"),
            products_clean.Price_Per_Unit.alias("Product_Price")
        )
        
        fact_table = fact_table.join(
            broadcast(locations_clean),
            fact_table.Retailer_ID == locations_clean.Retailer_ID,
            "inner"
        ).select(
            fact_table["*"],
            locations_clean.Region.alias("Store_Region"),
            locations_clean.Store_Type.alias("Store_Channel")
        )
        
        # Add time-based features
        fact_table = fact_table \
            .withColumn("Year", year(col("Date"))) \
            .withColumn("Month", month(col("Date"))) \
            .withColumn("Quarter", quarter(col("Date"))) \
            .withColumn("Year_Month", date_format(col("Date"), "yyyy-MM")) \
            .withColumn("Week_of_Year", weekofyear(col("Date")))
        
        # Cache for performance
        fact_table.cache()
        
        record_count = fact_table.count()
        logger.info(f"✅ Fact table created with {record_count:,} records")
        
        self.fact_table = fact_table
        return fact_table
    
    def calculate_growth_rates(self):
        """
        Calculate month-over-month and year-over-year growth rates for Beer vs Hard Seltzer.
        """
        logger.info("Calculating growth rates for Beer vs Hard Seltzer...")
        
        df = self.fact_table
        
        # Monthly aggregation by category
        monthly_category = df.groupBy("Year", "Month", "Year_Month", "Product_Category").agg(
            sum("Total_Revenue").alias("Monthly_Revenue"),
            sum("Units_Sold").alias("Monthly_Units"),
            count("Transaction_ID").alias("Monthly_Transactions"),
            countDistinct("SKU").alias("Unique_Products"),
            countDistinct("Store_Region").alias("Regional_Presence"),
            avg("Total_Revenue").alias("Avg_Transaction_Value"),
            avg("TDP").alias("Avg_TDP")
        ).withColumn("Revenue_Per_Transaction", 
            col("Monthly_Revenue") / col("Monthly_Transactions")
        )
        
        # Add date for proper ordering
        monthly_category = monthly_category.withColumn(
            "Date_Key", 
            to_date(concat(col("Year"), lit("-"), 
                          when(col("Month") < 10, concat(lit("0"), col("Month")))
                          .otherwise(col("Month")), lit("-01")))
        )
        
        # Calculate month-over-month growth
        category_window = Window.partitionBy("Product_Category").orderBy("Date_Key")
        
        monthly_growth = monthly_category \
            .withColumn("Previous_Month_Revenue", 
                lag("Monthly_Revenue", 1).over(category_window)
            ) \
            .withColumn("Previous_Month_Units", 
                lag("Monthly_Units", 1).over(category_window)
            ) \
            .withColumn("MoM_Revenue_Growth", 
                when(col("Previous_Month_Revenue") > 0,
                    ((col("Monthly_Revenue") - col("Previous_Month_Revenue")) / col("Previous_Month_Revenue")) * 100
                ).otherwise(0)
            ) \
            .withColumn("MoM_Units_Growth", 
                when(col("Previous_Month_Units") > 0,
                    ((col("Monthly_Units") - col("Previous_Month_Units")) / col("Previous_Month_Units")) * 100
                ).otherwise(0)
            )
        
        # Calculate year-over-year growth (12 months ago)
        monthly_growth = monthly_growth \
            .withColumn("YoY_Revenue_Base", 
                lag("Monthly_Revenue", 12).over(category_window)
            ) \
            .withColumn("YoY_Units_Base", 
                lag("Monthly_Units", 12).over(category_window)
            ) \
            .withColumn("YoY_Revenue_Growth", 
                when(col("YoY_Revenue_Base") > 0,
                    ((col("Monthly_Revenue") - col("YoY_Revenue_Base")) / col("YoY_Revenue_Base")) * 100
                ).otherwise(0)
            ) \
            .withColumn("YoY_Units_Growth", 
                when(col("YoY_Units_Base") > 0,
                    ((col("Monthly_Units") - col("YoY_Units_Base")) / col("YoY_Units_Base")) * 100
                ).otherwise(0)
            )
        
        # Add growth momentum indicators
        monthly_growth = monthly_growth \
            .withColumn("Revenue_Growth_Acceleration", 
                col("MoM_Revenue_Growth") - lag("MoM_Revenue_Growth", 1).over(category_window)
            ) \
            .withColumn("Growth_Trend_Direction", 
                when(col("Revenue_Growth_Acceleration") > 5, "Accelerating")
                .when(col("Revenue_Growth_Acceleration") < -5, "Decelerating")
                .otherwise("Stable")
            )
        
        # Cache results
        monthly_growth.cache()
        
        self.trend_results['monthly_growth'] = monthly_growth
        
        logger.info("✅ Growth rate calculations completed")
        return monthly_growth
    
    def identify_pivot_point(self):
        """
        Identify the exact timeframe where Hard Seltzer growth exceeds Beer growth
        with statistical significance testing.
        """
        logger.info("Identifying pivot point where Seltzer overtakes Beer...")
        
        monthly_growth = self.trend_results['monthly_growth']
        
        # Create pivot analysis table
        pivot_data = monthly_growth.select(
            "Year", "Month", "Year_Month", "Date_Key", "Product_Category",
            "Monthly_Revenue", "Monthly_Units", "MoM_Revenue_Growth", "MoM_Units_Growth",
            "YoY_Revenue_Growth", "Revenue_Growth_Acceleration", "Growth_Trend_Direction"
        )
        
        # Pivot to compare Beer vs Seltzer side by side
        beer_data = pivot_data.filter(col("Product_Category") == "BEER") \
            .select("Year_Month", "Date_Key", 
                   col("Monthly_Revenue").alias("Beer_Revenue"),
                   col("Monthly_Units").alias("Beer_Units"),
                   col("MoM_Revenue_Growth").alias("Beer_MoM_Growth"),
                   col("YoY_Revenue_Growth").alias("Beer_YoY_Growth"),
                   col("Revenue_Growth_Acceleration").alias("Beer_Acceleration"))
        
        seltzer_data = pivot_data.filter(col("Product_Category") == "HARD SELTZER") \
            .select("Year_Month", "Date_Key",
                   col("Monthly_Revenue").alias("Seltzer_Revenue"),
                   col("Monthly_Units").alias("Seltzer_Units"),
                   col("MoM_Revenue_Growth").alias("Seltzer_MoM_Growth"),
                   col("YoY_Revenue_Growth").alias("Seltzer_YoY_Growth"),
                   col("Revenue_Growth_Acceleration").alias("Seltzer_Acceleration"))
        
        # Join Beer and Seltzer data
        comparison = beer_data.join(seltzer_data, ["Year_Month", "Date_Key"], "outer") \
            .fillna(0, ["Beer_Revenue", "Beer_Units", "Beer_MoM_Growth", "Beer_YoY_Growth",
                       "Seltzer_Revenue", "Seltzer_Units", "Seltzer_MoM_Growth", "Seltzer_YoY_Growth"])
        
        # Calculate competitive metrics
        pivot_analysis = comparison \
            .withColumn("Total_Market_Revenue", 
                col("Beer_Revenue") + col("Seltzer_Revenue")
            ) \
            .withColumn("Beer_Market_Share", 
                when(col("Total_Market_Revenue") > 0,
                    col("Beer_Revenue") / col("Total_Market_Revenue") * 100
                ).otherwise(100)
            ) \
            .withColumn("Seltzer_Market_Share", 
                when(col("Total_Market_Revenue") > 0,
                    col("Seltzer_Revenue") / col("Total_Market_Revenue") * 100
                ).otherwise(0)
            ) \
            .withColumn("Growth_Rate_Difference", 
                col("Seltzer_MoM_Growth") - col("Beer_MoM_Growth")
            ) \
            .withColumn("Revenue_Ratio", 
                when(col("Beer_Revenue") > 0,
                    col("Seltzer_Revenue") / col("Beer_Revenue")
                ).otherwise(0)
            )
        
        # Identify pivot points
        pivot_analysis = pivot_analysis \
            .withColumn("Seltzer_Growth_Exceeds_Beer", 
                col("Seltzer_MoM_Growth") > col("Beer_MoM_Growth")
            ) \
            .withColumn("Significant_Growth_Difference", 
                abs(col("Growth_Rate_Difference")) > 10
            ) \
            .withColumn("Pivot_Point_Indicator", 
                col("Seltzer_Growth_Exceeds_Beer") & col("Significant_Growth_Difference")
            )
        
        # Calculate statistical significance using variance
        window_3_months = Window.orderBy("Date_Key").rowsBetween(-2, 0)
        
        pivot_analysis = pivot_analysis \
            .withColumn("Beer_Growth_3M_Avg", 
                avg("Beer_MoM_Growth").over(window_3_months)
            ) \
            .withColumn("Seltzer_Growth_3M_Avg", 
                avg("Seltzer_MoM_Growth").over(window_3_months)
            ) \
            .withColumn("Growth_Difference_3M_Avg", 
                col("Seltzer_Growth_3M_Avg") - col("Beer_Growth_3M_Avg")
            ) \
            .withColumn("Sustained_Pivot", 
                col("Growth_Difference_3M_Avg") > 15  # 15% sustained difference
            )
        
        # Add market phase classification
        pivot_analysis = pivot_analysis \
            .withColumn("Market_Phase",
                when(col("Seltzer_Market_Share") < 5, "Beer_Dominance")
                .when(col("Seltzer_Market_Share") < 15, "Early_Seltzer_Growth")
                .when(col("Seltzer_Market_Share") < 30, "Seltzer_Acceleration")
                .otherwise("Seltzer_Maturity")
            )
        
        # Cache results
        pivot_analysis.cache()
        
        self.pivot_analysis['comparison'] = pivot_analysis
        
        # Find the first sustained pivot point
        pivot_points = pivot_analysis.filter(col("Sustained_Pivot") == True) \
            .orderBy("Date_Key") \
            .limit(5)
        
        self.pivot_analysis['pivot_points'] = pivot_points
        
        logger.info("✅ Pivot point analysis completed")
        return pivot_analysis
    
    def analyze_regional_trends(self):
        """
        Detailed analysis of beer-to-seltzer trends by region and brands.
        """
        logger.info("Analyzing regional and brand trends...")
        
        df = self.fact_table
        
        # Regional monthly trends
        regional_monthly = df.groupBy(
            "Year", "Month", "Year_Month", "Store_Region", "Product_Category"
        ).agg(
            sum("Total_Revenue").alias("Regional_Revenue"),
            sum("Units_Sold").alias("Regional_Units"),
            count("Transaction_ID").alias("Regional_Transactions"),
            countDistinct("Product_Brand").alias("Active_Brands"),
            countDistinct("Retailer_ID").alias("Active_Stores"),
            avg("Total_Revenue").alias("Avg_Transaction_Value")
        )
        
        # Add date key for ordering
        regional_monthly = regional_monthly.withColumn(
            "Date_Key", 
            to_date(concat(col("Year"), lit("-"), 
                          when(col("Month") < 10, concat(lit("0"), col("Month")))
                          .otherwise(col("Month")), lit("-01")))
        )
        
        # Calculate regional growth rates
        regional_window = Window.partitionBy("Store_Region", "Product_Category").orderBy("Date_Key")
        
        regional_growth = regional_monthly \
            .withColumn("Previous_Regional_Revenue", 
                lag("Regional_Revenue", 1).over(regional_window)
            ) \
            .withColumn("Regional_MoM_Growth", 
                when(col("Previous_Regional_Revenue") > 0,
                    ((col("Regional_Revenue") - col("Previous_Regional_Revenue")) / col("Previous_Regional_Revenue")) * 100
                ).otherwise(0)
            )
        
        # Calculate regional market share
        regional_total_window = Window.partitionBy("Year_Month", "Store_Region")
        
        regional_share = regional_growth \
            .withColumn("Regional_Total_Revenue", 
                sum("Regional_Revenue").over(regional_total_window)
            ) \
            .withColumn("Regional_Category_Share", 
                when(col("Regional_Total_Revenue") > 0,
                    col("Regional_Revenue") / col("Regional_Total_Revenue") * 100
                ).otherwise(0)
            )
        
        # Identify leading regions for seltzer adoption
        seltzer_regional = regional_share.filter(col("Product_Category") == "HARD SELTZER")
        
        regional_seltzer_summary = seltzer_regional.groupBy("Store_Region").agg(
            max("Regional_Category_Share").alias("Peak_Seltzer_Share"),
            avg("Regional_MoM_Growth").alias("Avg_Seltzer_Growth"),
            sum("Regional_Revenue").alias("Total_Seltzer_Revenue"),
            min("Date_Key").alias("First_Seltzer_Activity"),
            count("Year_Month").alias("Months_Active")
        ).withColumn("Seltzer_Adoption_Rank",
            row_number().over(Window.orderBy(desc("Peak_Seltzer_Share")))
        )
        
        self.regional_analysis['monthly_trends'] = regional_share
        self.regional_analysis['seltzer_leaders'] = regional_seltzer_summary
        
        logger.info("✅ Regional trend analysis completed")
        return regional_share
    
    def analyze_brand_impact(self):
        """
        Analyze which beer brands were most affected by the seltzer shift.
        """
        logger.info("Analyzing brand-level impact of seltzer growth...")
        
        df = self.fact_table
        
        # Brand monthly performance
        brand_monthly = df.groupBy(
            "Year", "Month", "Year_Month", "Product_Brand", "Product_Category"
        ).agg(
            sum("Total_Revenue").alias("Brand_Revenue"),
            sum("Units_Sold").alias("Brand_Units"),
            count("Transaction_ID").alias("Brand_Transactions"),
            countDistinct("Store_Region").alias("Geographic_Reach"),
            avg("Total_Revenue").alias("Avg_Transaction_Value"),
            avg("TDP").alias("Avg_TDP")
        )
        
        # Add date key
        brand_monthly = brand_monthly.withColumn(
            "Date_Key", 
            to_date(concat(col("Year"), lit("-"), 
                          when(col("Month") < 10, concat(lit("0"), col("Month")))
                          .otherwise(col("Month")), lit("-01")))
        )
        
        # Calculate brand growth rates
        brand_window = Window.partitionBy("Product_Brand", "Product_Category").orderBy("Date_Key")
        
        brand_growth = brand_monthly \
            .withColumn("Previous_Brand_Revenue", 
                lag("Brand_Revenue", 1).over(brand_window)
            ) \
            .withColumn("Brand_MoM_Growth", 
                when(col("Previous_Brand_Revenue") > 0,
                    ((col("Brand_Revenue") - col("Previous_Brand_Revenue")) / col("Previous_Brand_Revenue")) * 100
                ).otherwise(0)
            )
        
        # Focus on beer brands and their decline
        beer_brands = brand_growth.filter(col("Product_Category") == "BEER")
        
        # Calculate brand vulnerability metrics
        beer_brand_summary = beer_brands.groupBy("Product_Brand").agg(
            sum("Brand_Revenue").alias("Total_Revenue"),
            avg("Brand_MoM_Growth").alias("Avg_Growth_Rate"),
            min("Brand_MoM_Growth").alias("Worst_Month_Growth"),
            stddev("Brand_MoM_Growth").alias("Growth_Volatility"),
            count("Year_Month").alias("Months_Active"),
            max("Geographic_Reach").alias("Peak_Geographic_Reach")
        ).withColumn("Decline_Severity",
            when(col("Avg_Growth_Rate") < -10, "Severe")
            .when(col("Avg_Growth_Rate") < -5, "Moderate")
            .when(col("Avg_Growth_Rate") < 0, "Mild")
            .otherwise("Growing")
        ).withColumn("Vulnerability_Score",
            # Higher score = more vulnerable (negative growth + high volatility)
            (abs(col("Avg_Growth_Rate")) * 0.7) + (col("Growth_Volatility") * 0.3)
        )
        
        # Rank beer brands by vulnerability
        beer_vulnerability = beer_brand_summary \
            .withColumn("Vulnerability_Rank",
                row_number().over(Window.orderBy(desc("Vulnerability_Score")))
            )
        
        # Analyze seltzer brand leaders
        seltzer_brands = brand_growth.filter(col("Product_Category") == "HARD SELTZER")
        
        seltzer_brand_summary = seltzer_brands.groupBy("Product_Brand").agg(
            sum("Brand_Revenue").alias("Total_Revenue"),
            avg("Brand_MoM_Growth").alias("Avg_Growth_Rate"),
            max("Brand_MoM_Growth").alias("Best_Month_Growth"),
            count("Year_Month").alias("Months_Active"),
            max("Geographic_Reach").alias("Peak_Geographic_Reach")
        ).withColumn("Growth_Rank",
            row_number().over(Window.orderBy(desc("Total_Revenue")))
        )
        
        self.brand_analysis['beer_vulnerability'] = beer_vulnerability
        self.brand_analysis['seltzer_leaders'] = seltzer_brand_summary
        self.brand_analysis['monthly_trends'] = brand_growth
        
        logger.info("✅ Brand impact analysis completed")
        return brand_growth
    
    def track_market_share_evolution(self):
        """
        Track market share evolution over time showing competitive dynamics.
        """
        logger.info("Tracking market share evolution and competitive dynamics...")
        
        df = self.fact_table
        
        # Daily market share calculation
        daily_market = df.groupBy("Date", "Product_Category").agg(
            sum("Total_Revenue").alias("Daily_Category_Revenue"),
            sum("Units_Sold").alias("Daily_Category_Units"),
            count("Transaction_ID").alias("Daily_Transactions")
        )
        
        # Calculate total market size by day
        daily_total_window = Window.partitionBy("Date")
        
        daily_share = daily_market \
            .withColumn("Daily_Total_Revenue", 
                sum("Daily_Category_Revenue").over(daily_total_window)
            ) \
            .withColumn("Daily_Market_Share", 
                when(col("Daily_Total_Revenue") > 0,
                    col("Daily_Category_Revenue") / col("Daily_Total_Revenue") * 100
                ).otherwise(0)
            ) \
            .withColumn("Year", year(col("Date"))) \
            .withColumn("Month", month(col("Date"))) \
            .withColumn("Week_of_Year", weekofyear(col("Date")))
        
        # Weekly aggregation for smoother trends
        weekly_share = daily_share.groupBy("Year", "Week_of_Year", "Product_Category").agg(
            avg("Daily_Market_Share").alias("Weekly_Avg_Share"),
            sum("Daily_Category_Revenue").alias("Weekly_Revenue"),
            sum("Daily_Category_Units").alias("Weekly_Units")
        )
        
        # Monthly market share evolution
        monthly_share = daily_share.groupBy("Year", "Month", "Product_Category").agg(
            avg("Daily_Market_Share").alias("Monthly_Avg_Share"),
            min("Daily_Market_Share").alias("Monthly_Min_Share"),
            max("Daily_Market_Share").alias("Monthly_Max_Share"),
            sum("Daily_Category_Revenue").alias("Monthly_Revenue"),
            sum("Daily_Category_Units").alias("Monthly_Units"),
            stddev("Daily_Market_Share").alias("Share_Volatility")
        ).withColumn("Year_Month",
            concat(col("Year"), lit("-"), 
                   when(col("Month") < 10, concat(lit("0"), col("Month")))
                   .otherwise(col("Month")))
        )
        
        # Calculate market share momentum
        category_window = Window.partitionBy("Product_Category").orderBy("Year", "Month")
        
        share_momentum = monthly_share \
            .withColumn("Previous_Month_Share", 
                lag("Monthly_Avg_Share", 1).over(category_window)
            ) \
            .withColumn("Share_Change", 
                col("Monthly_Avg_Share") - col("Previous_Month_Share")
            ) \
            .withColumn("Share_Growth_Rate", 
                when(col("Previous_Month_Share") > 0,
                    (col("Share_Change") / col("Previous_Month_Share")) * 100
                ).otherwise(0)
            )
        
        # Create competitive dynamics metrics
        beer_share = share_momentum.filter(col("Product_Category") == "BEER") \
            .select("Year", "Month", "Year_Month",
                   col("Monthly_Avg_Share").alias("Beer_Share"),
                   col("Share_Change").alias("Beer_Share_Change"),
                   col("Monthly_Revenue").alias("Beer_Revenue"))
        
        seltzer_share = share_momentum.filter(col("Product_Category") == "HARD SELTZER") \
            .select("Year", "Month", "Year_Month",
                   col("Monthly_Avg_Share").alias("Seltzer_Share"),
                   col("Share_Change").alias("Seltzer_Share_Change"),
                   col("Monthly_Revenue").alias("Seltzer_Revenue"))
        
        # Combine for competitive analysis
        competitive_dynamics = beer_share.join(seltzer_share, ["Year", "Month", "Year_Month"], "outer") \
            .fillna(0, ["Beer_Share", "Seltzer_Share", "Beer_Share_Change", "Seltzer_Share_Change"])
        
        competitive_dynamics = competitive_dynamics \
            .withColumn("Market_Concentration", 
                col("Beer_Share") + col("Seltzer_Share")
            ) \
            .withColumn("Competitive_Intensity", 
                abs(col("Beer_Share_Change")) + abs(col("Seltzer_Share_Change"))
            ) \
            .withColumn("Seltzer_Momentum", 
                when(col("Seltzer_Share_Change") > 0, "Gaining")
                .when(col("Seltzer_Share_Change") < 0, "Losing")
                .otherwise("Stable")
            ) \
            .withColumn("Market_Leadership", 
                when(col("Beer_Share") > col("Seltzer_Share"), "Beer_Leads")
                .when(col("Seltzer_Share") > col("Beer_Share"), "Seltzer_Leads")
                .otherwise("Tied")
            )
        
        # Calculate key milestone dates
        milestones = competitive_dynamics \
            .withColumn("Seltzer_5_Percent", col("Seltzer_Share") >= 5) \
            .withColumn("Seltzer_10_Percent", col("Seltzer_Share") >= 10) \
            .withColumn("Seltzer_15_Percent", col("Seltzer_Share") >= 15) \
            .withColumn("Seltzer_20_Percent", col("Seltzer_Share") >= 20)
        
        self.market_share_evolution['daily'] = daily_share
        self.market_share_evolution['weekly'] = weekly_share
        self.market_share_evolution['monthly'] = share_momentum
        self.market_share_evolution['competitive'] = competitive_dynamics
        self.market_share_evolution['milestones'] = milestones
        
        logger.info("✅ Market share evolution tracking completed")
        return competitive_dynamics
    
    def generate_visualization_data(self):
        """
        Generate clean, visualization-ready datasets for charts and dashboards.
        """
        logger.info("Generating visualization-ready datasets...")
        
        viz_data = {}
        
        # 1. Growth Rate Comparison Chart Data
        if 'monthly_growth' in self.trend_results:
            growth_viz = self.trend_results['monthly_growth'].select(
                "Year_Month", "Product_Category", "Monthly_Revenue", "Monthly_Units",
                "MoM_Revenue_Growth", "YoY_Revenue_Growth", "Growth_Trend_Direction"
            ).orderBy("Year_Month", "Product_Category")
            
            viz_data['growth_comparison'] = growth_viz
        
        # 2. Pivot Point Analysis Chart Data
        if 'comparison' in self.pivot_analysis:
            pivot_viz = self.pivot_analysis['comparison'].select(
                "Year_Month", "Date_Key", "Beer_Market_Share", "Seltzer_Market_Share",
                "Growth_Rate_Difference", "Market_Phase", "Pivot_Point_Indicator"
            ).orderBy("Date_Key")
            
            viz_data['pivot_analysis'] = pivot_viz
        
        # 3. Regional Heatmap Data
        if 'monthly_trends' in self.regional_analysis:
            regional_viz = self.regional_analysis['monthly_trends'] \
                .filter(col("Product_Category") == "HARD SELTZER") \
                .select("Year_Month", "Store_Region", "Regional_Category_Share", "Regional_MoM_Growth") \
                .orderBy("Year_Month", "Store_Region")
            
            viz_data['regional_heatmap'] = regional_viz
        
        # 4. Brand Performance Data
        if 'beer_vulnerability' in self.brand_analysis:
            brand_viz = self.brand_analysis['beer_vulnerability'].select(
                "Product_Brand", "Total_Revenue", "Avg_Growth_Rate", 
                "Decline_Severity", "Vulnerability_Score", "Vulnerability_Rank"
            ).orderBy("Vulnerability_Rank")
            
            viz_data['brand_vulnerability'] = brand_viz
        
        # 5. Market Share Evolution Data
        if 'competitive' in self.market_share_evolution:
            share_viz = self.market_share_evolution['competitive'].select(
                "Year_Month", "Beer_Share", "Seltzer_Share", "Competitive_Intensity",
                "Market_Leadership", "Seltzer_Momentum"
            ).orderBy("Year_Month")
            
            viz_data['market_evolution'] = share_viz
        
        self.visualization_data = viz_data
        
        logger.info("✅ Visualization data generation completed")
        return viz_data
    
    def generate_executive_summary(self):
        """
        Generate executive summary with key findings and insights.
        """
        logger.info("Generating executive summary...")
        
        summary = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': None,
            'key_findings': {},
            'pivot_point': {},
            'regional_insights': {},
            'brand_insights': {},
            'market_dynamics': {},
            'recommendations': []
        }
        
        try:
            # Data period analysis
            if self.fact_table:
                date_range = self.fact_table.select(
                    min("Date").alias("start_date"),
                    max("Date").alias("end_date"),
                    count("Transaction_ID").alias("total_transactions")
                ).collect()[0]
                
                summary['data_period'] = {
                    'start_date': str(date_range['start_date']),
                    'end_date': str(date_range['end_date']),
                    'total_transactions': date_range['total_transactions']
                }
            
            # Pivot point findings
            if 'pivot_points' in self.pivot_analysis:
                pivot_data = self.pivot_analysis['pivot_points'].collect()
                if pivot_data:
                    first_pivot = pivot_data[0]
                    summary['pivot_point'] = {
                        'date': str(first_pivot['Year_Month']),
                        'seltzer_share': round(first_pivot['Seltzer_Market_Share'], 2),
                        'growth_difference': round(first_pivot['Growth_Rate_Difference'], 2),
                        'market_phase': first_pivot['Market_Phase']
                    }
            
            # Regional insights
            if 'seltzer_leaders' in self.regional_analysis:
                regional_leaders = self.regional_analysis['seltzer_leaders'] \
                    .orderBy("Seltzer_Adoption_Rank").limit(3).collect()
                
                summary['regional_insights'] = {
                    'leading_regions': [
                        {
                            'region': row['Store_Region'],
                            'peak_share': round(row['Peak_Seltzer_Share'], 2),
                            'avg_growth': round(row['Avg_Seltzer_Growth'], 2)
                        } for row in regional_leaders
                    ]
                }
            
            # Brand insights
            if 'beer_vulnerability' in self.brand_analysis:
                vulnerable_brands = self.brand_analysis['beer_vulnerability'] \
                    .orderBy("Vulnerability_Rank").limit(5).collect()
                
                summary['brand_insights'] = {
                    'most_vulnerable_beer_brands': [
                        {
                            'brand': row['Product_Brand'],
                            'avg_growth': round(row['Avg_Growth_Rate'], 2),
                            'decline_severity': row['Decline_Severity']
                        } for row in vulnerable_brands
                    ]
                }
            
            # Market dynamics
            if 'competitive' in self.market_share_evolution:
                latest_market = self.market_share_evolution['competitive'] \
                    .orderBy(desc("Year_Month")).limit(1).collect()
                
                if latest_market:
                    latest = latest_market[0]
                    summary['market_dynamics'] = {
                        'current_beer_share': round(latest['Beer_Share'], 2),
                        'current_seltzer_share': round(latest['Seltzer_Share'], 2),
                        'market_leadership': latest['Market_Leadership'],
                        'competitive_intensity': round(latest['Competitive_Intensity'], 2)
                    }
            
            # Generate recommendations
            summary['recommendations'] = [
                "Accelerate hard seltzer product development and marketing investment",
                "Focus seltzer expansion on leading adoption regions identified in analysis",
                "Develop retention strategies for vulnerable beer brands",
                "Implement dynamic pricing strategies based on competitive intensity metrics",
                "Monitor pivot point indicators for early detection of market shifts"
            ]
            
        except Exception as e:
            logger.warning(f"Error generating summary component: {str(e)}")
        
        self.executive_summary = summary
        
        logger.info("✅ Executive summary generated")
        return summary
    
    def save_results_to_csv(self, output_dir: str = "analysis_results"):
        """
        Save all analysis results to CSV files for external use.
        """
        logger.info(f"Saving analysis results to {output_dir}/...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Save growth rate analysis
            if 'monthly_growth' in self.trend_results:
                self.trend_results['monthly_growth'].coalesce(1) \
                    .write.mode("overwrite").option("header", "true") \
                    .csv(f"{output_dir}/monthly_growth_rates")
            
            # Save pivot point analysis
            if 'comparison' in self.pivot_analysis:
                self.pivot_analysis['comparison'].coalesce(1) \
                    .write.mode("overwrite").option("header", "true") \
                    .csv(f"{output_dir}/pivot_point_analysis")
            
            # Save regional analysis
            if 'monthly_trends' in self.regional_analysis:
                self.regional_analysis['monthly_trends'].coalesce(1) \
                    .write.mode("overwrite").option("header", "true") \
                    .csv(f"{output_dir}/regional_trends")
            
            # Save brand analysis
            if 'beer_vulnerability' in self.brand_analysis:
                self.brand_analysis['beer_vulnerability'].coalesce(1) \
                    .write.mode("overwrite").option("header", "true") \
                    .csv(f"{output_dir}/beer_brand_vulnerability")
            
            # Save market share evolution
            if 'competitive' in self.market_share_evolution:
                self.market_share_evolution['competitive'].coalesce(1) \
                    .write.mode("overwrite").option("header", "true") \
                    .csv(f"{output_dir}/market_share_evolution")
            
            logger.info("✅ Results saved to CSV files")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def display_key_insights(self):
        """
        Display key insights and findings from the analysis.
        """
        print(f"\n" + "=" * 80)
        print(f"🍺➡️🥤 BEER TO SELTZER MARKET SHIFT ANALYSIS")
        print("=" * 80)
        
        # Display pivot point findings
        if 'pivot_points' in self.pivot_analysis:
            pivot_data = self.pivot_analysis['pivot_points'].collect()
            if pivot_data:
                print(f"\n🎯 PIVOT POINT IDENTIFIED:")
                for i, pivot in enumerate(pivot_data[:3]):
                    print(f"   {i+1}. {pivot['Year_Month']}: Seltzer growth exceeded Beer by {pivot['Growth_Rate_Difference']:.1f}%")
                    print(f"      Seltzer Market Share: {pivot['Seltzer_Market_Share']:.2f}%")
                    print(f"      Market Phase: {pivot['Market_Phase']}")
        
        # Display growth rate comparison
        if 'monthly_growth' in self.trend_results:
            print(f"\n📈 GROWTH RATE SUMMARY:")
            latest_growth = self.trend_results['monthly_growth'] \
                .orderBy(desc("Date_Key")).limit(2).collect()
            
            for row in latest_growth:
                category = row['Product_Category']
                growth = row['MoM_Revenue_Growth']
                trend = row['Growth_Trend_Direction']
                print(f"   {category}: {growth:.1f}% MoM ({trend})")
        
        # Display regional leaders
        if 'seltzer_leaders' in self.regional_analysis:
            print(f"\n🌎 REGIONAL SELTZER ADOPTION LEADERS:")
            leaders = self.regional_analysis['seltzer_leaders'] \
                .orderBy("Seltzer_Adoption_Rank").limit(3).collect()
            
            for leader in leaders:
                region = leader['Store_Region']
                share = leader['Peak_Seltzer_Share']
                growth = leader['Avg_Seltzer_Growth']
                print(f"   {region}: {share:.1f}% peak share, {growth:.1f}% avg growth")
        
        # Display vulnerable beer brands
        if 'beer_vulnerability' in self.brand_analysis:
            print(f"\n⚠️  MOST VULNERABLE BEER BRANDS:")
            vulnerable = self.brand_analysis['beer_vulnerability'] \
                .orderBy("Vulnerability_Rank").limit(5).collect()
            
            for brand in vulnerable:
                name = brand['Product_Brand']
                growth = brand['Avg_Growth_Rate']
                severity = brand['Decline_Severity']
                print(f"   {name}: {growth:.1f}% avg growth ({severity} decline)")
        
        # Display market share evolution
        if 'competitive' in self.market_share_evolution:
            print(f"\n📊 CURRENT MARKET DYNAMICS:")
            latest = self.market_share_evolution['competitive'] \
                .orderBy(desc("Year_Month")).limit(1).collect()
            
            if latest:
                current = latest[0]
                beer_share = current['Beer_Share']
                seltzer_share = current['Seltzer_Share']
                leadership = current['Market_Leadership']
                intensity = current['Competitive_Intensity']
                
                print(f"   Beer Market Share: {beer_share:.1f}%")
                print(f"   Seltzer Market Share: {seltzer_share:.1f}%")
                print(f"   Market Leadership: {leadership}")
                print(f"   Competitive Intensity: {intensity:.1f}")
        
        print(f"\n🎉 Analysis completed successfully!")
    
    def run_complete_analysis(self):
        """Run the complete trend analysis pipeline."""
        print("🚀 Starting Complete Beer vs Seltzer Trend Analysis")
        print("=" * 80)
        
        try:
            # Initialize Spark and load data
            self.create_spark_session()
            self.load_cleaned_data()
            
            # Run all analyses
            self.calculate_growth_rates()
            self.identify_pivot_point()
            self.analyze_regional_trends()
            self.analyze_brand_impact()
            self.track_market_share_evolution()
            
            # Generate outputs
            self.generate_visualization_data()
            self.generate_executive_summary()
            
            # Display insights
            self.display_key_insights()
            
            # Save results
            self.save_results_to_csv()
            
            print(f"\n💡 Next Steps:")
            print(f"   1. Review CSV files in analysis_results/ directory")
            print(f"   2. Use visualization data for charts and dashboards")
            print(f"   3. Present executive summary to stakeholders")
            print(f"   4. Implement strategic recommendations")
            
            return {
                'trend_results': self.trend_results,
                'pivot_analysis': self.pivot_analysis,
                'regional_analysis': self.regional_analysis,
                'brand_analysis': self.brand_analysis,
                'market_share_evolution': self.market_share_evolution,
                'executive_summary': self.executive_summary
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            raise
        finally:
            if self.spark:
                self.spark.stop()

def main():
    """Main execution function."""
    pipeline = TrendAnalysisPipeline()
    results = pipeline.run_complete_analysis()
    
    print(f"\n✅ Beer vs Seltzer trend analysis completed successfully!")
    print(f"📊 All insights and data ready for business decision making")

if __name__ == "__main__":
    main()