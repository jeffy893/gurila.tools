#!/usr/bin/env python3
"""
PySpark Visualization Data Export Pipeline
=========================================

This pipeline exports processed data in formats optimized for visualization tools
including Matplotlib, Plotly, and business intelligence platforms. Creates clean,
structured datasets for time series analysis, category comparisons, and regional breakdowns.

Key Outputs:
- Time series data for trend visualization
- Category comparison datasets
- Regional breakdown analysis
- Pivot point detection data
- Market share evolution tracking
- Executive dashboard datasets
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging
from datetime import datetime, timedelta
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VisualizationExportPipeline:
    """
    Export pipeline for creating visualization-ready datasets from PySpark analysis.
    """
    
    def __init__(self, data_dir: str = "synthetic_data", output_dir: str = "visualization_data"):
        """Initialize the visualization export pipeline."""
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.spark = None
        self.fact_table = None
        self.export_datasets = {}
        
    def create_spark_session(self) -> SparkSession:
        """Create optimized SparkSession for data export."""
        logger.info("Creating SparkSession for visualization export...")
        
        self.spark = SparkSession.builder \
            .appName("VisualizationExport") \
            .master("local[*]") \
            .config("spark.driver.memory", "4g") \
            .config("spark.driver.maxResultSize", "2g") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"✅ SparkSession created successfully")
        return self.spark
    
    def load_and_prepare_data(self):
        """Load and prepare comprehensive fact table for visualization export."""
        logger.info("Loading and preparing data for visualization export...")
        
        # Use existing ingestion pipeline
        from spark_data_ingestion import DataIngestionPipeline
        
        ingestion = DataIngestionPipeline(self.data_dir)
        ingestion.spark = self.spark
        ingestion.define_schemas()
        
        # Load datasets
        products_df = ingestion.read_csv_with_validation('products.csv', 'products')
        locations_df = ingestion.read_csv_with_validation('locations.csv', 'locations')
        sales_df = ingestion.read_csv_with_validation('sales_transactions.csv', 'sales_transactions')
        
        # Apply cleaning and create comprehensive fact table
        products_clean = products_df.filter(col("SKU").isNotNull()) \
            .withColumn("Category", upper(trim(col("Category"))))
        
        locations_clean = locations_df.filter(col("Retailer_ID").isNotNull()) \
            .withColumn("Region", upper(trim(col("Region"))))
        
        sales_clean = sales_df.filter(col("Transaction_ID").isNotNull()) \
            .filter(col("Units_Sold") > 0) \
            .filter(col("Total_Revenue") > 0) \
            .withColumn("Category", upper(trim(col("Category"))))
        
        # Create comprehensive fact table with all dimensions
        fact_table = sales_clean.join(
            broadcast(products_clean.select("SKU", "Category", "Brand", "ABV", "Price_Per_Unit")),
            "SKU", "inner"
        ).join(
            broadcast(locations_clean.select("Retailer_ID", "Region", "Store_Type", "City", "State")),
            "Retailer_ID", "inner"
        ).select(
            sales_clean["*"],
            products_clean.Category.alias("Product_Category"),
            products_clean.Brand.alias("Product_Brand"),
            products_clean.ABV.alias("Product_ABV"),
            products_clean.Price_Per_Unit.alias("Product_Price"),
            locations_clean.Region.alias("Store_Region"),
            locations_clean.Store_Type.alias("Store_Channel"),
            locations_clean.City.alias("Store_City"),
            locations_clean.State.alias("Store_State")
        )
        
        # Add comprehensive time dimensions for visualization
        fact_table = fact_table \
            .withColumn("Year", year(col("Date"))) \
            .withColumn("Month", month(col("Date"))) \
            .withColumn("Quarter", quarter(col("Date"))) \
            .withColumn("Year_Month", date_format(col("Date"), "yyyy-MM")) \
            .withColumn("Year_Quarter", concat(col("Year"), lit("-Q"), col("Quarter"))) \
            .withColumn("Week_of_Year", weekofyear(col("Date"))) \
            .withColumn("Day_of_Week", dayofweek(col("Date"))) \
            .withColumn("Day_Name", date_format(col("Date"), "EEEE")) \
            .withColumn("Month_Name", date_format(col("Date"), "MMMM")) \
            .withColumn("Date_String", date_format(col("Date"), "yyyy-MM-dd"))
        
        # Add calculated metrics for visualization
        fact_table = fact_table \
            .withColumn("Revenue_Per_Unit", col("Total_Revenue") / col("Units_Sold")) \
            .withColumn("TDP_Revenue_Ratio", col("Total_Revenue") / col("TDP")) \
            .withColumn("Units_Per_TDP", col("Units_Sold") / col("TDP"))
        
        # Cache for performance
        fact_table.cache()
        
        record_count = fact_table.count()
        logger.info(f"✅ Visualization data prepared: {record_count:,} records")
        
        self.fact_table = fact_table
        return fact_table
    
    def export_time_series_data(self):
        """
        Export time series datasets optimized for trend visualization.
        """
        logger.info("Exporting time series datasets...")
        
        df = self.fact_table
        
        # 1. Daily Time Series by Category
        daily_category = df.groupBy("Date", "Date_String", "Product_Category").agg(
            sum("Total_Revenue").alias("Daily_Revenue"),
            sum("Units_Sold").alias("Daily_Units"),
            count("Transaction_ID").alias("Daily_Transactions"),
            avg("Total_Revenue").alias("Avg_Transaction_Value"),
            countDistinct("Product_Brand").alias("Active_Brands"),
            countDistinct("Store_Region").alias("Active_Regions")
        ).orderBy("Date", "Product_Category")
        
        # Add market share calculations
        daily_total_window = Window.partitionBy("Date")
        
        daily_category_with_share = daily_category \
            .withColumn("Total_Daily_Revenue", sum("Daily_Revenue").over(daily_total_window)) \
            .withColumn("Market_Share_Revenue", 
                (col("Daily_Revenue") / col("Total_Daily_Revenue")) * 100
            ) \
            .withColumn("Market_Share_Units", 
                (col("Daily_Units") / sum("Daily_Units").over(daily_total_window)) * 100
            )
        
        self.export_datasets['daily_time_series'] = daily_category_with_share
        
        # 2. Weekly Time Series (Smoothed for visualization)
        weekly_category = df.groupBy("Year", "Week_of_Year", "Product_Category").agg(
            sum("Total_Revenue").alias("Weekly_Revenue"),
            sum("Units_Sold").alias("Weekly_Units"),
            count("Transaction_ID").alias("Weekly_Transactions"),
            avg("Total_Revenue").alias("Avg_Weekly_Transaction"),
            min("Date").alias("Week_Start_Date"),
            max("Date").alias("Week_End_Date")
        ).withColumn("Year_Week", concat(col("Year"), lit("-W"), 
                    when(col("Week_of_Year") < 10, concat(lit("0"), col("Week_of_Year")))
                    .otherwise(col("Week_of_Year"))
                ))
        
        # Add weekly market share
        weekly_total_window = Window.partitionBy("Year", "Week_of_Year")
        
        weekly_category_with_share = weekly_category \
            .withColumn("Total_Weekly_Revenue", sum("Weekly_Revenue").over(weekly_total_window)) \
            .withColumn("Market_Share_Revenue", 
                (col("Weekly_Revenue") / col("Total_Weekly_Revenue")) * 100
            ) \
            .orderBy("Year", "Week_of_Year", "Product_Category")
        
        self.export_datasets['weekly_time_series'] = weekly_category_with_share
        
        # 3. Monthly Time Series with Growth Rates
        monthly_category = df.groupBy("Year", "Month", "Year_Month", "Month_Name", "Product_Category").agg(
            sum("Total_Revenue").alias("Monthly_Revenue"),
            sum("Units_Sold").alias("Monthly_Units"),
            count("Transaction_ID").alias("Monthly_Transactions"),
            avg("Total_Revenue").alias("Avg_Monthly_Transaction"),
            countDistinct("Product_Brand").alias("Monthly_Active_Brands"),
            countDistinct("Store_Region").alias("Monthly_Active_Regions"),
            min("Date").alias("Month_Start_Date"),
            max("Date").alias("Month_End_Date")
        )
        
        # Add growth rate calculations
        category_window = Window.partitionBy("Product_Category").orderBy("Year", "Month")
        
        monthly_with_growth = monthly_category \
            .withColumn("Previous_Month_Revenue", 
                lag("Monthly_Revenue", 1).over(category_window)
            ) \
            .withColumn("MoM_Growth_Rate", 
                when(col("Previous_Month_Revenue") > 0,
                    ((col("Monthly_Revenue") - col("Previous_Month_Revenue")) / col("Previous_Month_Revenue")) * 100
                ).otherwise(0)
            ) \
            .withColumn("YoY_Base_Revenue", 
                lag("Monthly_Revenue", 12).over(category_window)
            ) \
            .withColumn("YoY_Growth_Rate", 
                when(col("YoY_Base_Revenue") > 0,
                    ((col("Monthly_Revenue") - col("YoY_Base_Revenue")) / col("YoY_Base_Revenue")) * 100
                ).otherwise(0)
            )
        
        # Add monthly market share
        monthly_total_window = Window.partitionBy("Year", "Month")
        
        monthly_final = monthly_with_growth \
            .withColumn("Total_Monthly_Revenue", sum("Monthly_Revenue").over(monthly_total_window)) \
            .withColumn("Market_Share_Revenue", 
                (col("Monthly_Revenue") / col("Total_Monthly_Revenue")) * 100
            ) \
            .orderBy("Year", "Month", "Product_Category")
        
        self.export_datasets['monthly_time_series'] = monthly_final
        
        logger.info("✅ Time series datasets exported")
        return monthly_final
    
    def export_pivot_point_analysis(self):
        """
        Export pivot point analysis data for visualization.
        """
        logger.info("Exporting pivot point analysis data...")
        
        # Get monthly data with growth rates
        monthly_data = self.export_datasets['monthly_time_series']
        
        # Create side-by-side comparison for pivot analysis
        beer_data = monthly_data.filter(col("Product_Category") == "BEER") \
            .select("Year", "Month", "Year_Month", "Month_Name",
                   col("Monthly_Revenue").alias("Beer_Revenue"),
                   col("MoM_Growth_Rate").alias("Beer_MoM_Growth"),
                   col("YoY_Growth_Rate").alias("Beer_YoY_Growth"),
                   col("Market_Share_Revenue").alias("Beer_Market_Share"))
        
        seltzer_data = monthly_data.filter(col("Product_Category") == "HARD SELTZER") \
            .select("Year", "Month", "Year_Month", "Month_Name",
                   col("Monthly_Revenue").alias("Seltzer_Revenue"),
                   col("MoM_Growth_Rate").alias("Seltzer_MoM_Growth"),
                   col("YoY_Growth_Rate").alias("Seltzer_YoY_Growth"),
                   col("Market_Share_Revenue").alias("Seltzer_Market_Share"))
        
        # Join for comparison analysis
        pivot_comparison = beer_data.join(seltzer_data, 
            ["Year", "Month", "Year_Month", "Month_Name"], "outer") \
            .fillna(0, ["Beer_Revenue", "Beer_MoM_Growth", "Beer_YoY_Growth", "Beer_Market_Share",
                       "Seltzer_Revenue", "Seltzer_MoM_Growth", "Seltzer_YoY_Growth", "Seltzer_Market_Share"])
        
        # Calculate pivot indicators
        pivot_analysis = pivot_comparison \
            .withColumn("Total_Revenue", col("Beer_Revenue") + col("Seltzer_Revenue")) \
            .withColumn("Growth_Difference_MoM", col("Seltzer_MoM_Growth") - col("Beer_MoM_Growth")) \
            .withColumn("Growth_Difference_YoY", col("Seltzer_YoY_Growth") - col("Beer_YoY_Growth")) \
            .withColumn("Market_Share_Difference", col("Seltzer_Market_Share") - col("Beer_Market_Share")) \
            .withColumn("Pivot_Point_MoM", col("Seltzer_MoM_Growth") > col("Beer_MoM_Growth")) \
            .withColumn("Pivot_Point_YoY", col("Seltzer_YoY_Growth") > col("Beer_YoY_Growth")) \
            .withColumn("Strong_Pivot", 
                (col("Growth_Difference_MoM") > 15) & (col("Seltzer_MoM_Growth") > 0)
            ) \
            .orderBy("Year", "Month")
        
        # Add rolling averages for trend smoothing
        time_window = Window.orderBy("Year", "Month").rowsBetween(-2, 2)  # 5-month rolling
        
        pivot_with_trends = pivot_analysis \
            .withColumn("Beer_Growth_Trend", avg("Beer_MoM_Growth").over(time_window)) \
            .withColumn("Seltzer_Growth_Trend", avg("Seltzer_MoM_Growth").over(time_window)) \
            .withColumn("Growth_Diff_Trend", avg("Growth_Difference_MoM").over(time_window)) \
            .withColumn("Seltzer_Share_Trend", avg("Seltzer_Market_Share").over(time_window))
        
        self.export_datasets['pivot_point_analysis'] = pivot_with_trends
        
        logger.info("✅ Pivot point analysis data exported")
        return pivot_with_trends
    
    def export_regional_analysis(self):
        """
        Export regional breakdown data for geographic visualization.
        """
        logger.info("Exporting regional analysis data...")
        
        df = self.fact_table
        
        # 1. Regional Performance by Category
        regional_category = df.groupBy("Store_Region", "Store_State", "Product_Category").agg(
            sum("Total_Revenue").alias("Regional_Revenue"),
            sum("Units_Sold").alias("Regional_Units"),
            count("Transaction_ID").alias("Regional_Transactions"),
            countDistinct("Product_Brand").alias("Regional_Brands"),
            countDistinct("Retailer_ID").alias("Regional_Stores"),
            countDistinct("Store_City").alias("Regional_Cities"),
            avg("Total_Revenue").alias("Avg_Regional_Transaction"),
            avg("TDP").alias("Avg_Regional_TDP")
        )
        
        # Add regional market share calculations
        regional_total_window = Window.partitionBy("Store_Region")
        
        regional_with_share = regional_category \
            .withColumn("Regional_Total_Revenue", sum("Regional_Revenue").over(regional_total_window)) \
            .withColumn("Category_Penetration", 
                (col("Regional_Revenue") / col("Regional_Total_Revenue")) * 100
            ) \
            .withColumn("Revenue_Per_Store", col("Regional_Revenue") / col("Regional_Stores")) \
            .withColumn("Units_Per_Store", col("Regional_Units") / col("Regional_Stores"))
        
        self.export_datasets['regional_category_analysis'] = regional_with_share
        
        # 2. Regional Time Series for Trend Analysis
        regional_monthly = df.groupBy("Store_Region", "Year", "Month", "Year_Month", "Product_Category").agg(
            sum("Total_Revenue").alias("Regional_Monthly_Revenue"),
            sum("Units_Sold").alias("Regional_Monthly_Units"),
            count("Transaction_ID").alias("Regional_Monthly_Transactions")
        )
        
        # Add regional growth rates
        regional_category_window = Window.partitionBy("Store_Region", "Product_Category").orderBy("Year", "Month")
        
        regional_monthly_growth = regional_monthly \
            .withColumn("Previous_Month_Revenue", 
                lag("Regional_Monthly_Revenue", 1).over(regional_category_window)
            ) \
            .withColumn("Regional_MoM_Growth", 
                when(col("Previous_Month_Revenue") > 0,
                    ((col("Regional_Monthly_Revenue") - col("Previous_Month_Revenue")) / col("Previous_Month_Revenue")) * 100
                ).otherwise(0)
            ) \
            .orderBy("Store_Region", "Year", "Month", "Product_Category")
        
        self.export_datasets['regional_time_series'] = regional_monthly_growth
        
        # 3. State-Level Analysis for Detailed Geographic Visualization
        state_category = df.groupBy("Store_State", "Store_Region", "Product_Category").agg(
            sum("Total_Revenue").alias("State_Revenue"),
            sum("Units_Sold").alias("State_Units"),
            countDistinct("Retailer_ID").alias("State_Stores"),
            countDistinct("Store_City").alias("State_Cities"),
            avg("Total_Revenue").alias("Avg_State_Transaction")
        )
        
        # Add state market share
        state_total_window = Window.partitionBy("Store_State")
        
        state_with_share = state_category \
            .withColumn("State_Total_Revenue", sum("State_Revenue").over(state_total_window)) \
            .withColumn("State_Category_Share", 
                (col("State_Revenue") / col("State_Total_Revenue")) * 100
            ) \
            .orderBy("Store_State", "Product_Category")
        
        self.export_datasets['state_analysis'] = state_with_share
        
        logger.info("✅ Regional analysis data exported")
        return regional_with_share
    
    def export_category_comparison_data(self):
        """
        Export category comparison datasets for competitive analysis visualization.
        """
        logger.info("Exporting category comparison data...")
        
        df = self.fact_table
        
        # 1. Overall Category Performance Metrics
        category_performance = df.groupBy("Product_Category").agg(
            sum("Total_Revenue").alias("Total_Category_Revenue"),
            sum("Units_Sold").alias("Total_Category_Units"),
            count("Transaction_ID").alias("Total_Category_Transactions"),
            countDistinct("Product_Brand").alias("Category_Brand_Count"),
            countDistinct("Store_Region").alias("Category_Geographic_Reach"),
            countDistinct("Retailer_ID").alias("Category_Store_Count"),
            avg("Total_Revenue").alias("Avg_Category_Transaction"),
            avg("Product_ABV").alias("Avg_Category_ABV"),
            avg("Product_Price").alias("Avg_Category_Price"),
            min("Date").alias("Category_First_Sale"),
            max("Date").alias("Category_Last_Sale")
        )
        
        # Add market share and performance ratios
        total_window = Window.partitionBy()
        
        category_with_metrics = category_performance \
            .withColumn("Market_Share_Revenue", 
                (col("Total_Category_Revenue") / sum("Total_Category_Revenue").over(total_window)) * 100
            ) \
            .withColumn("Market_Share_Units", 
                (col("Total_Category_Units") / sum("Total_Category_Units").over(total_window)) * 100
            ) \
            .withColumn("Market_Share_Transactions", 
                (col("Total_Category_Transactions") / sum("Total_Category_Transactions").over(total_window)) * 100
            ) \
            .withColumn("Revenue_Per_Brand", col("Total_Category_Revenue") / col("Category_Brand_Count")) \
            .withColumn("Revenue_Per_Store", col("Total_Category_Revenue") / col("Category_Store_Count")) \
            .withColumn("Units_Per_Transaction", col("Total_Category_Units") / col("Total_Category_Transactions"))
        
        self.export_datasets['category_performance'] = category_with_metrics
        
        # 2. Brand Performance within Categories
        brand_performance = df.groupBy("Product_Category", "Product_Brand").agg(
            sum("Total_Revenue").alias("Brand_Revenue"),
            sum("Units_Sold").alias("Brand_Units"),
            count("Transaction_ID").alias("Brand_Transactions"),
            countDistinct("Store_Region").alias("Brand_Geographic_Reach"),
            countDistinct("Retailer_ID").alias("Brand_Store_Count"),
            avg("Total_Revenue").alias("Avg_Brand_Transaction"),
            avg("Product_ABV").alias("Brand_ABV"),
            avg("Product_Price").alias("Brand_Price")
        )
        
        # Add brand rankings within category
        category_brand_window = Window.partitionBy("Product_Category").orderBy(desc("Brand_Revenue"))
        
        brand_with_rankings = brand_performance \
            .withColumn("Brand_Rank_in_Category", row_number().over(category_brand_window)) \
            .withColumn("Brand_Revenue_Share_in_Category", 
                (col("Brand_Revenue") / sum("Brand_Revenue").over(Window.partitionBy("Product_Category"))) * 100
            ) \
            .orderBy("Product_Category", "Brand_Rank_in_Category")
        
        self.export_datasets['brand_performance'] = brand_with_rankings
        
        # 3. ABV Analysis for Product Strategy
        abv_performance = df.groupBy("Product_Category", "Product_ABV").agg(
            sum("Total_Revenue").alias("ABV_Revenue"),
            sum("Units_Sold").alias("ABV_Units"),
            count("Transaction_ID").alias("ABV_Transactions"),
            countDistinct("Product_Brand").alias("ABV_Brand_Count"),
            avg("Total_Revenue").alias("Avg_ABV_Transaction")
        )
        
        # Add ABV rankings within category
        category_abv_window = Window.partitionBy("Product_Category").orderBy(desc("ABV_Revenue"))
        
        abv_with_rankings = abv_performance \
            .withColumn("ABV_Rank_in_Category", row_number().over(category_abv_window)) \
            .withColumn("ABV_Revenue_Share_in_Category", 
                (col("ABV_Revenue") / sum("ABV_Revenue").over(Window.partitionBy("Product_Category"))) * 100
            ) \
            .orderBy("Product_Category", "ABV_Rank_in_Category")
        
        self.export_datasets['abv_analysis'] = abv_with_rankings
        
        logger.info("✅ Category comparison data exported")
        return category_with_metrics
    
    def export_executive_dashboard_data(self):
        """
        Export executive dashboard datasets for high-level visualization.
        """
        logger.info("Exporting executive dashboard data...")
        
        # 1. Key Performance Indicators (KPIs)
        kpi_data = self.export_datasets['category_performance'].select(
            "Product_Category",
            "Total_Category_Revenue",
            "Market_Share_Revenue",
            "Total_Category_Units",
            "Market_Share_Units",
            "Category_Brand_Count",
            "Category_Geographic_Reach",
            "Avg_Category_Transaction",
            "Revenue_Per_Brand",
            "Revenue_Per_Store"
        )
        
        self.export_datasets['executive_kpis'] = kpi_data
        
        # 2. Monthly Executive Summary
        monthly_summary = self.export_datasets['monthly_time_series'].groupBy("Year_Month", "Month_Name").agg(
            sum("Monthly_Revenue").alias("Total_Monthly_Revenue"),
            sum("Monthly_Units").alias("Total_Monthly_Units"),
            sum("Monthly_Transactions").alias("Total_Monthly_Transactions"),
            avg("MoM_Growth_Rate").alias("Avg_MoM_Growth"),
            max("MoM_Growth_Rate").alias("Max_MoM_Growth"),
            min("MoM_Growth_Rate").alias("Min_MoM_Growth")
        ).orderBy("Year_Month")
        
        self.export_datasets['monthly_executive_summary'] = monthly_summary
        
        # 3. Regional Executive Summary
        regional_summary = self.export_datasets['regional_category_analysis'] \
            .groupBy("Store_Region").agg(
                sum("Regional_Revenue").alias("Total_Regional_Revenue"),
                sum("Regional_Units").alias("Total_Regional_Units"),
                sum("Regional_Stores").alias("Total_Regional_Stores"),
                avg("Category_Penetration").alias("Avg_Category_Penetration"),
                max("Category_Penetration").alias("Max_Category_Penetration")
            ).orderBy(desc("Total_Regional_Revenue"))
        
        self.export_datasets['regional_executive_summary'] = regional_summary
        
        logger.info("✅ Executive dashboard data exported")
        return kpi_data
    
    def save_visualization_datasets(self):
        """
        Save all datasets as CSV files optimized for visualization tools.
        """
        logger.info(f"Saving visualization datasets to {self.output_dir}/...")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        try:
            # Save each dataset as CSV with proper formatting
            for dataset_name, df in self.export_datasets.items():
                logger.info(f"  Saving {dataset_name}...")
                
                # Convert to single partition for clean CSV output
                df.coalesce(1).write.mode("overwrite") \
                    .option("header", "true") \
                    .option("timestampFormat", "yyyy-MM-dd HH:mm:ss") \
                    .option("dateFormat", "yyyy-MM-dd") \
                    .csv(f"{self.output_dir}/{dataset_name}")
                
                # Also save as Pandas DataFrame for immediate use
                pandas_df = df.toPandas()
                pandas_df.to_csv(f"{self.output_dir}/{dataset_name}.csv", index=False)
                
                logger.info(f"    ✅ {dataset_name}: {df.count():,} records")
            
            # Create dataset inventory
            inventory = {
                'export_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_datasets': len(self.export_datasets),
                'datasets': {}
            }
            
            for dataset_name, df in self.export_datasets.items():
                inventory['datasets'][dataset_name] = {
                    'record_count': df.count(),
                    'columns': df.columns,
                    'description': self._get_dataset_description(dataset_name)
                }
            
            # Save inventory as JSON
            import json
            with open(f"{self.output_dir}/dataset_inventory.json", 'w') as f:
                json.dump(inventory, f, indent=2)
            
            logger.info("✅ All visualization datasets saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving datasets: {str(e)}")
            raise
    
    def _get_dataset_description(self, dataset_name: str) -> str:
        """Get description for dataset inventory."""
        descriptions = {
            'daily_time_series': 'Daily revenue, units, and market share by category for detailed trend analysis',
            'weekly_time_series': 'Weekly aggregated data with smoothed trends for visualization',
            'monthly_time_series': 'Monthly data with growth rates and market share evolution',
            'pivot_point_analysis': 'Side-by-side category comparison with pivot point indicators',
            'regional_category_analysis': 'Regional performance breakdown by category',
            'regional_time_series': 'Regional monthly trends with growth rates',
            'state_analysis': 'State-level performance for detailed geographic analysis',
            'category_performance': 'Overall category metrics and market share analysis',
            'brand_performance': 'Brand-level performance within categories',
            'abv_analysis': 'ABV preference analysis by category',
            'executive_kpis': 'Key performance indicators for executive dashboards',
            'monthly_executive_summary': 'Monthly executive summary metrics',
            'regional_executive_summary': 'Regional executive summary metrics'
        }
        return descriptions.get(dataset_name, 'Dataset for visualization analysis')
    
    def run_visualization_export(self):
        """Run the complete visualization export pipeline."""
        print("🚀 Starting Visualization Data Export Pipeline")
        print("=" * 80)
        
        try:
            # Initialize and load data
            self.create_spark_session()
            self.load_and_prepare_data()
            
            # Export all visualization datasets
            self.export_time_series_data()
            self.export_pivot_point_analysis()
            self.export_regional_analysis()
            self.export_category_comparison_data()
            self.export_executive_dashboard_data()
            
            # Save all datasets
            self.save_visualization_datasets()
            
            # Display summary
            print(f"\n📊 VISUALIZATION EXPORT SUMMARY:")
            print(f"   Total Datasets Created: {len(self.export_datasets)}")
            print(f"   Output Directory: {self.output_dir}/")
            print(f"   Total Records Processed: {self.fact_table.count():,}")
            
            print(f"\n📁 DATASETS CREATED:")
            for dataset_name, df in self.export_datasets.items():
                print(f"   {dataset_name}: {df.count():,} records")
            
            print(f"\n💡 Next Steps:")
            print(f"   1. Use CSV files in {self.output_dir}/ for visualization tools")
            print(f"   2. Import datasets into Matplotlib, Plotly, or BI tools")
            print(f"   3. Create compelling visualizations using provided data")
            print(f"   4. Reference dataset_inventory.json for column descriptions")
            
            return {
                'datasets': self.export_datasets,
                'output_directory': self.output_dir,
                'total_records': self.fact_table.count()
            }
            
        except Exception as e:
            logger.error(f"❌ Visualization export failed: {str(e)}")
            raise
        finally:
            if self.spark:
                self.spark.stop()

def main():
    """Main execution function."""
    pipeline = VisualizationExportPipeline()
    results = pipeline.run_visualization_export()
    
    print(f"\n✅ Visualization data export completed!")
    print(f"📊 All datasets ready for visualization tools")

if __name__ == "__main__":
    main()