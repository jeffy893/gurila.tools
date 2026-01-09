#!/usr/bin/env python3
"""
PySpark Hello World - Installation Verification Script
=====================================================

This script verifies that PySpark is properly installed and configured.
Run this after completing the installation steps.
"""

import sys
import os
from datetime import datetime

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check:")
    print(f"   Version: {sys.version}")
    
    if sys.version_info < (3, 7):
        print("   ❌ ERROR: Python 3.7+ required for PySpark")
        return False
    else:
        print("   ✅ Python version compatible")
        return True

def check_java_installation():
    """Check Java installation"""
    print("\n☕ Java Installation Check:")
    
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        print(f"   JAVA_HOME: {java_home}")
        print("   ✅ JAVA_HOME environment variable set")
    else:
        print("   ⚠️  WARNING: JAVA_HOME not set")
    
    # Try to run java command
    try:
        import subprocess
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            java_version = result.stderr.split('\n')[0]
            print(f"   Java Version: {java_version}")
            print("   ✅ Java executable found")
            return True
        else:
            print("   ❌ ERROR: Java command failed")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: Cannot run java command: {e}")
        return False

def test_pyspark_import():
    """Test PySpark import"""
    print("\n⚡ PySpark Import Test:")
    
    try:
        import pyspark
        print(f"   PySpark Version: {pyspark.__version__}")
        print("   ✅ PySpark imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ ERROR: Cannot import PySpark: {e}")
        print("   💡 Try: pip3 install pyspark")
        return False

def test_spark_context():
    """Test SparkContext creation"""
    print("\n🔥 SparkContext Test:")
    
    try:
        from pyspark import SparkContext, SparkConf
        
        # Create Spark configuration
        conf = SparkConf().setAppName("HelloWorldTest").setMaster("local[*]")
        sc = SparkContext(conf=conf)
        
        print(f"   Spark Version: {sc.version}")
        print(f"   Master: {sc.master}")
        print(f"   App Name: {sc.appName}")
        
        # Simple RDD test
        test_data = [1, 2, 3, 4, 5]
        rdd = sc.parallelize(test_data)
        result = rdd.map(lambda x: x * 2).collect()
        
        print(f"   Test RDD: {test_data} -> {result}")
        print("   ✅ SparkContext working correctly")
        
        sc.stop()
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: SparkContext failed: {e}")
        return False

def test_spark_session():
    """Test SparkSession creation"""
    print("\n✨ SparkSession Test:")
    
    try:
        from pyspark.sql import SparkSession
        
        spark = SparkSession.builder \
            .appName("HelloWorldSparkSession") \
            .master("local[*]") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        print(f"   Spark Version: {spark.version}")
        print(f"   Catalog: {type(spark.catalog)}")
        
        # Create test DataFrame
        test_data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
        columns = ["Name", "Age"]
        
        df = spark.createDataFrame(test_data, columns)
        print(f"   Test DataFrame created with {df.count()} rows")
        
        # Show DataFrame
        print("   DataFrame content:")
        df.show()
        
        # Simple SQL test
        df.createOrReplaceTempView("people")
        result = spark.sql("SELECT Name, Age FROM people WHERE Age > 25")
        print("   SQL Query result:")
        result.show()
        
        print("   ✅ SparkSession working correctly")
        
        spark.stop()
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: SparkSession failed: {e}")
        return False

def test_dataframe_operations():
    """Test DataFrame operations"""
    print("\n📊 DataFrame Operations Test:")
    
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, sum as spark_sum, avg, count
        
        spark = SparkSession.builder \
            .appName("DataFrameTest") \
            .master("local[*]") \
            .getOrCreate()
        
        # Create sample sales data
        sales_data = [
            ("Beer", "Budweiser", 100, 150.0),
            ("Beer", "Coors", 80, 120.0),
            ("Hard Seltzer", "White Claw", 60, 180.0),
            ("Hard Seltzer", "Truly", 40, 120.0),
            ("Beer", "Miller", 90, 135.0)
        ]
        
        columns = ["Category", "Brand", "Units", "Revenue"]
        df = spark.createDataFrame(sales_data, columns)
        
        print("   Sample data:")
        df.show()
        
        # Aggregation test
        category_summary = df.groupBy("Category") \
            .agg(
                spark_sum("Units").alias("Total_Units"),
                spark_sum("Revenue").alias("Total_Revenue"),
                avg("Revenue").alias("Avg_Revenue"),
                count("Brand").alias("Brand_Count")
            )
        
        print("   Category aggregation:")
        category_summary.show()
        
        print("   ✅ DataFrame operations working correctly")
        
        spark.stop()
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: DataFrame operations failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 PySpark Installation Verification")
    print("=" * 50)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Python Version", check_python_version),
        ("Java Installation", check_java_installation),
        ("PySpark Import", test_pyspark_import),
        ("SparkContext", test_spark_context),
        ("SparkSession", test_spark_session),
        ("DataFrame Operations", test_dataframe_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 SUCCESS! PySpark is properly installed and configured!")
        print("You're ready to process the beer company data!")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the installation.")
        print("Refer to PYSPARK_SETUP.md for troubleshooting steps.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)