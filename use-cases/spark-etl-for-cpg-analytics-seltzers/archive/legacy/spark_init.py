#!/usr/bin/env python3
"""
PySpark Initialization Script for Beer Company Analysis
======================================================

This script initializes a SparkSession with optimal configuration for
processing the synthetic POS data efficiently on local development.
"""

import os
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SparkEnvironment:
    """
    Manages PySpark environment setup and configuration for beer company analysis.
    """
    
    def __init__(self, app_name: str = "BeerCompanyAnalysis", 
                 memory_gb: int = 4, cores: str = "*"):
        """
        Initialize Spark environment with optimized configuration.
        
        Args:
            app_name (str): Spark application name
            memory_gb (int): Driver memory in GB
            cores (str): Number of cores ("*" for all available)
        """
        self.app_name = app_name
        self.memory_gb = memory_gb
        self.cores = cores
        self.spark = None
        
        logger.info(f"Initializing Spark environment: {app_name}")
        logger.info(f"Configuration: {memory_gb}GB memory, {cores} cores")
    
    def create_spark_session(self) -> SparkSession:
        """
        Create optimized SparkSession for POS data analysis.
        
        Returns:
            SparkSession: Configured Spark session
        """
        try:
            # Build SparkSession with optimized configuration
            builder = SparkSession.builder \
                .appName(self.app_name) \
                .master(f"local[{self.cores}]")
            
            # Memory configuration
            builder = builder.config("spark.driver.memory", f"{self.memory_gb}g")
            builder = builder.config("spark.driver.maxResultSize", "2g")
            builder = builder.config("spark.sql.adaptive.enabled", "true")
            builder = builder.config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            
            # Performance optimizations
            builder = builder.config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")
            builder = builder.config("spark.sql.broadcastTimeout", "36000")
            builder = builder.config("spark.sql.shuffle.partitions", "200")
            
            # Enable Arrow-based columnar data transfers (if available)
            builder = builder.config("spark.sql.execution.arrow.pyspark.enabled", "true")
            
            # Optimize for local development
            builder = builder.config("spark.sql.warehouse.dir", "./spark-warehouse")
            builder = builder.config("spark.sql.streaming.checkpointLocation", "./checkpoints")
            
            # Create session
            self.spark = builder.getOrCreate()
            
            # Set log level to reduce noise
            self.spark.sparkContext.setLogLevel("WARN")
            
            logger.info("✅ SparkSession created successfully")
            logger.info(f"   Spark Version: {self.spark.version}")
            logger.info(f"   Master: {self.spark.sparkContext.master}")
            logger.info(f"   App ID: {self.spark.sparkContext.applicationId}")
            
            return self.spark
            
        except Exception as e:
            logger.error(f"❌ Failed to create SparkSession: {e}")
            raise
    
    def get_system_info(self) -> dict:
        """
        Get system information for optimization.
        
        Returns:
            dict: System information
        """
        if not self.spark:
            raise ValueError("SparkSession not initialized")
        
        sc = self.spark.sparkContext
        
        info = {
            "spark_version": self.spark.version,
            "python_version": sys.version,
            "master": sc.master,
            "app_name": sc.appName,
            "app_id": sc.applicationId,
            "default_parallelism": sc.defaultParallelism,
            "total_cores": sc.defaultParallelism,
            "driver_memory": sc.getConf().get("spark.driver.memory", "Not set"),
            "sql_shuffle_partitions": self.spark.conf.get("spark.sql.shuffle.partitions")
        }
        
        return info
    
    def print_configuration(self):
        """Print current Spark configuration."""
        if not self.spark:
            logger.error("SparkSession not initialized")
            return
        
        print("\n🔧 SPARK CONFIGURATION")
        print("=" * 50)
        
        info = self.get_system_info()
        for key, value in info.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n📊 CONFIGURATION DETAILS")
        print("-" * 30)
        
        # Key configurations
        configs = [
            "spark.sql.adaptive.enabled",
            "spark.sql.adaptive.coalescePartitions.enabled", 
            "spark.sql.execution.arrow.pyspark.enabled",
            "spark.driver.memory",
            "spark.driver.maxResultSize",
            "spark.sql.shuffle.partitions"
        ]
        
        for config in configs:
            try:
                value = self.spark.conf.get(config)
                print(f"{config}: {value}")
            except:
                print(f"{config}: Not set")
    
    def test_performance(self):
        """
        Run performance tests to validate configuration.
        """
        if not self.spark:
            logger.error("SparkSession not initialized")
            return
        
        print("\n⚡ PERFORMANCE TESTS")
        print("=" * 30)
        
        try:
            # Test 1: RDD operations
            start_time = datetime.now()
            test_rdd = self.spark.sparkContext.parallelize(range(1000000))
            result = test_rdd.map(lambda x: x * 2).filter(lambda x: x % 100 == 0).count()
            rdd_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ RDD Test: {result:,} results in {rdd_time:.2f}s")
            
            # Test 2: DataFrame operations
            start_time = datetime.now()
            df = self.spark.range(1000000).toDF("number")
            df = df.withColumn("doubled", col("number") * 2)
            df = df.filter(col("doubled") % 100 == 0)
            result = df.count()
            df_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ DataFrame Test: {result:,} results in {df_time:.2f}s")
            
            # Test 3: SQL operations
            start_time = datetime.now()
            df.createOrReplaceTempView("numbers")
            sql_result = self.spark.sql("""
                SELECT COUNT(*) as count 
                FROM numbers 
                WHERE doubled > 50000
            """).collect()[0]['count']
            sql_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ SQL Test: {sql_result:,} results in {sql_time:.2f}s")
            
            print(f"\n🏆 Performance Summary:")
            print(f"   Average operation time: {(rdd_time + df_time + sql_time)/3:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
    
    def create_sample_dataframes(self):
        """
        Create sample DataFrames to test data processing capabilities.
        """
        if not self.spark:
            logger.error("SparkSession not initialized")
            return
        
        print("\n📊 SAMPLE DATAFRAMES")
        print("=" * 30)
        
        try:
            # Sample product data
            products_data = [
                ("BEER-1001", "Budweiser", "Beer", 5.0, 1.25),
                ("BEER-1002", "Coors", "Beer", 4.5, 1.20),
                ("SELT-2001", "White Claw", "Hard Seltzer", 5.0, 1.50),
                ("SELT-2002", "Truly", "Hard Seltzer", 5.0, 1.45)
            ]
            
            products_schema = StructType([
                StructField("SKU", StringType(), True),
                StructField("Brand", StringType(), True),
                StructField("Category", StringType(), True),
                StructField("ABV", DoubleType(), True),
                StructField("Price", DoubleType(), True)
            ])
            
            products_df = self.spark.createDataFrame(products_data, products_schema)
            
            print("Sample Products DataFrame:")
            products_df.show()
            
            # Sample sales data
            sales_data = [
                ("TXN-001", "2023-01-01", "BEER-1001", 5, 6.25),
                ("TXN-002", "2023-01-01", "SELT-2001", 3, 4.50),
                ("TXN-003", "2023-01-02", "BEER-1002", 4, 4.80),
                ("TXN-004", "2023-01-02", "SELT-2002", 2, 2.90)
            ]
            
            sales_schema = StructType([
                StructField("Transaction_ID", StringType(), True),
                StructField("Date", StringType(), True),
                StructField("SKU", StringType(), True),
                StructField("Units", IntegerType(), True),
                StructField("Revenue", DoubleType(), True)
            ])
            
            sales_df = self.spark.createDataFrame(sales_data, sales_schema)
            
            print("Sample Sales DataFrame:")
            sales_df.show()
            
            # Join test
            joined_df = sales_df.join(products_df, "SKU", "inner")
            
            print("Joined DataFrame (Sales + Products):")
            joined_df.select("Transaction_ID", "Date", "Brand", "Category", "Units", "Revenue").show()
            
            # Aggregation test
            category_summary = joined_df.groupBy("Category") \
                .agg(
                    sum("Units").alias("Total_Units"),
                    sum("Revenue").alias("Total_Revenue"),
                    avg("Revenue").alias("Avg_Revenue")
                )
            
            print("Category Summary:")
            category_summary.show()
            
            print("✅ Sample DataFrames created and tested successfully")
            
        except Exception as e:
            logger.error(f"❌ Sample DataFrame test failed: {e}")
    
    def stop(self):
        """Stop the SparkSession."""
        if self.spark:
            self.spark.stop()
            logger.info("SparkSession stopped")

def main():
    """
    Main function to initialize and test Spark environment.
    """
    print("🚀 PySpark Environment Initialization")
    print("=" * 50)
    
    # Initialize Spark environment
    spark_env = SparkEnvironment(
        app_name="BeerCompanyPOSAnalysis",
        memory_gb=4,  # Adjust based on your system
        cores="*"     # Use all available cores
    )
    
    try:
        # Create SparkSession
        spark = spark_env.create_spark_session()
        
        # Print configuration
        spark_env.print_configuration()
        
        # Run performance tests
        spark_env.test_performance()
        
        # Create sample DataFrames
        spark_env.create_sample_dataframes()
        
        print("\n🎉 SUCCESS! PySpark environment is ready for beer company analysis!")
        print("\nNext steps:")
        print("1. Run: python3 spark_etl_pipeline.py")
        print("2. Process your synthetic POS data")
        print("3. Generate business insights")
        
        # Keep session alive for interactive use
        print(f"\n💡 SparkSession available as 'spark' variable")
        print("   Access with: spark_env.spark")
        
        return spark_env
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        spark_env.stop()
        return None

if __name__ == "__main__":
    spark_env = main()
    
    # Interactive mode - keep session alive
    if spark_env:
        print("\n🔧 Interactive mode - SparkSession is running")
        print("Press Ctrl+C to stop...")
        
        try:
            # Keep alive until interrupted
            input("Press Enter to stop SparkSession...")
        except KeyboardInterrupt:
            print("\n\n👋 Stopping SparkSession...")
        finally:
            spark_env.stop()