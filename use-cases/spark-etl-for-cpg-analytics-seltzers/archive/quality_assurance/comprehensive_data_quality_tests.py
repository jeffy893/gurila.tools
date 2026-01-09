#!/usr/bin/env python3
"""
Comprehensive Data Quality Testing Suite
=======================================

Advanced PySpark-based data quality validation system with:
- Schema validation and type checking
- Referential integrity verification
- Business rule validation
- Statistical anomaly detection
- Data lineage validation
- Quality scoring and reporting
"""

import os
import sys
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# PySpark imports
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql.window import Window

# Statistical imports
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, kstest, normaltest

class ComprehensiveDataQualityTester:
    """
    Advanced data quality testing framework for the Beer-Seltzer analysis pipeline.
    """
    
    def __init__(self, spark_session: SparkSession = None):
        """Initialize the data quality tester."""
        self.spark = spark_session or self._create_spark_session()
        self.quality_results = {}
        self.test_results = []
        self.logger = self._setup_logger()
        
        # Quality thresholds
        self.thresholds = {
            'completeness': 0.95,      # 95% non-null values
            'validity': 0.98,          # 98% valid values
            'consistency': 0.99,       # 99% consistent values
            'accuracy': 0.95,          # 95% accurate values
            'integrity': 1.0,          # 100% referential integrity
            'uniqueness': 1.0,         # 100% unique primary keys
            'timeliness': 0.98,        # 98% within expected date ranges
            'anomaly_threshold': 3.0   # 3-sigma anomaly detection
        }
        
        self.logger.info("🔍 Comprehensive Data Quality Tester initialized")
    
    def _create_spark_session(self) -> SparkSession:
        """Create optimized Spark session for data quality testing."""
        return SparkSession.builder \
            .appName("DataQualityTesting") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.driver.memory", "4g") \
            .config("spark.driver.maxResultSize", "2g") \
            .getOrCreate()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for quality testing."""
        logger = logging.getLogger('DataQualityTester')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_comprehensive_quality_tests(self, data_path: str = "synthetic_data") -> Dict[str, Any]:
        """
        Execute comprehensive data quality testing suite.
        
        Args:
            data_path: Path to the data directory
            
        Returns:
            Comprehensive quality assessment results
        """
        self.logger.info("🚀 Starting comprehensive data quality testing")
        
        # Load datasets
        datasets = self._load_datasets(data_path)
        
        # Execute test categories
        test_categories = [
            ("Schema Validation", self._test_schema_validation),
            ("Data Completeness", self._test_data_completeness),
            ("Data Validity", self._test_data_validity),
            ("Referential Integrity", self._test_referential_integrity),
            ("Business Rules", self._test_business_rules),
            ("Statistical Anomalies", self._test_statistical_anomalies),
            ("Data Consistency", self._test_data_consistency),
            ("Temporal Validation", self._test_temporal_validation),
            ("Cross-Dataset Validation", self._test_cross_dataset_validation),
            ("Pipeline Results Validation", self._test_pipeline_results)
        ]
        
        for category_name, test_function in test_categories:
            self.logger.info(f"🔍 Executing {category_name} tests...")
            try:
                category_results = test_function(datasets)
                self.quality_results[category_name] = category_results
                self.logger.info(f"✅ {category_name} tests completed")
            except Exception as e:
                self.logger.error(f"❌ {category_name} tests failed: {str(e)}")
                self.quality_results[category_name] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'tests': []
                }
        
        # Generate comprehensive quality report
        quality_report = self._generate_quality_report()
        
        # Save results
        self._save_quality_results(quality_report)
        
        self.logger.info("🎉 Comprehensive data quality testing completed")
        return quality_report
    
    def _load_datasets(self, data_path: str) -> Dict[str, DataFrame]:
        """Load all datasets for quality testing."""
        datasets = {}
        
        try:
            # Load raw datasets
            datasets['products'] = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(f"{data_path}/products.csv")
            
            datasets['locations'] = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(f"{data_path}/locations.csv")
            
            datasets['sales'] = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(f"{data_path}/sales_transactions.csv")
            
            # Cache datasets for performance
            for name, df in datasets.items():
                df.cache()
                count = df.count()
                self.logger.info(f"📊 Loaded {name}: {count:,} records")
            
        except Exception as e:
            self.logger.error(f"Failed to load datasets: {str(e)}")
            raise
        
        return datasets
    
    def _test_schema_validation(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test schema validation and type consistency."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        # Expected schemas
        expected_schemas = {
            'products': {
                'SKU': StringType(),
                'Product_Name': StringType(),
                'Brand': StringType(),
                'Category': StringType(),
                'ABV': DoubleType(),
                'Price_Per_Unit': DoubleType()
            },
            'locations': {
                'Retailer_ID': StringType(),
                'Store_Name': StringType(),
                'Store_Type': StringType(),
                'Region': StringType(),
                'State': StringType(),
                'Alcohol_License': BooleanType()
            },
            'sales': {
                'Transaction_ID': StringType(),
                'Date': StringType(),  # Will be converted to DateType
                'Retailer_ID': StringType(),
                'SKU': StringType(),
                'Units_Sold': IntegerType(),
                'Unit_Price': DoubleType(),
                'Total_Revenue': DoubleType()
            }
        }
        
        total_tests = 0
        passed_tests = 0
        
        for dataset_name, df in datasets.items():
            if dataset_name in expected_schemas:
                expected = expected_schemas[dataset_name]
                actual_schema = {field.name: field.dataType for field in df.schema.fields}
                
                for field_name, expected_type in expected.items():
                    total_tests += 1
                    test_name = f"{dataset_name}.{field_name}_type_validation"
                    
                    if field_name in actual_schema:
                        # Type compatibility check
                        actual_type = actual_schema[field_name]
                        is_compatible = self._is_type_compatible(actual_type, expected_type)
                        
                        if is_compatible:
                            passed_tests += 1
                            results['tests'].append({
                                'test': test_name,
                                'status': 'PASSED',
                                'expected': str(expected_type),
                                'actual': str(actual_type)
                            })
                        else:
                            results['tests'].append({
                                'test': test_name,
                                'status': 'FAILED',
                                'expected': str(expected_type),
                                'actual': str(actual_type),
                                'issue': 'Type mismatch'
                            })
                    else:
                        results['tests'].append({
                            'test': test_name,
                            'status': 'FAILED',
                            'expected': str(expected_type),
                            'actual': 'MISSING',
                            'issue': 'Field not found'
                        })
        
        results['score'] = passed_tests / total_tests if total_tests > 0 else 0.0
        results['status'] = 'PASSED' if results['score'] >= self.thresholds['validity'] else 'FAILED'
        
        return results
    
    def _test_data_completeness(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test data completeness (null value analysis)."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        # Critical fields that cannot be null
        critical_fields = {
            'products': ['SKU', 'Product_Name', 'Brand', 'Category', 'ABV', 'Price_Per_Unit'],
            'locations': ['Retailer_ID', 'Store_Name', 'Store_Type', 'Region', 'State'],
            'sales': ['Transaction_ID', 'Date', 'Retailer_ID', 'SKU', 'Units_Sold', 'Total_Revenue']
        }
        
        total_completeness = 0.0
        test_count = 0
        
        for dataset_name, df in datasets.items():
            if dataset_name in critical_fields:
                total_records = df.count()
                
                for field in critical_fields[dataset_name]:
                    if field in df.columns:
                        null_count = df.filter(col(field).isNull()).count()
                        completeness = (total_records - null_count) / total_records
                        
                        test_count += 1
                        total_completeness += completeness
                        
                        status = 'PASSED' if completeness >= self.thresholds['completeness'] else 'FAILED'
                        
                        results['tests'].append({
                            'test': f"{dataset_name}.{field}_completeness",
                            'status': status,
                            'completeness_rate': completeness,
                            'null_count': null_count,
                            'total_records': total_records,
                            'threshold': self.thresholds['completeness']
                        })
        
        results['score'] = total_completeness / test_count if test_count > 0 else 0.0
        results['status'] = 'PASSED' if results['score'] >= self.thresholds['completeness'] else 'FAILED'
        
        return results
    
    def _test_data_validity(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test data validity against business constraints."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        # Validation rules
        validation_rules = {
            'products': [
                ('Category', lambda df: df.filter(col('Category').isin(['BEER', 'HARD SELTZER'])), 'Valid categories'),
                ('ABV', lambda df: df.filter((col('ABV') >= 0.1) & (col('ABV') <= 20.0)), 'ABV range 0.1-20%'),
                ('Price_Per_Unit', lambda df: df.filter((col('Price_Per_Unit') > 0) & (col('Price_Per_Unit') <= 10)), 'Price range $0.01-$10')
            ],
            'locations': [
                ('Region', lambda df: df.filter(col('Region').isin(['NORTHEAST', 'SOUTHEAST', 'MIDWEST', 'SOUTHWEST', 'WEST'])), 'Valid regions'),
                ('Alcohol_License', lambda df: df.filter(col('Alcohol_License') == True), 'Must have alcohol license')
            ],
            'sales': [
                ('Units_Sold', lambda df: df.filter((col('Units_Sold') >= 1) & (col('Units_Sold') <= 50)), 'Units range 1-50'),
                ('Unit_Price', lambda df: df.filter(col('Unit_Price') > 0), 'Positive unit price'),
                ('Total_Revenue', lambda df: df.filter(col('Total_Revenue') > 0), 'Positive total revenue')
            ]
        }
        
        total_validity = 0.0
        test_count = 0
        
        for dataset_name, df in datasets.items():
            if dataset_name in validation_rules:
                total_records = df.count()
                
                for field, validation_func, description in validation_rules[dataset_name]:
                    if field in df.columns:
                        valid_df = validation_func(df)
                        valid_count = valid_df.count()
                        validity_rate = valid_count / total_records
                        
                        test_count += 1
                        total_validity += validity_rate
                        
                        status = 'PASSED' if validity_rate >= self.thresholds['validity'] else 'FAILED'
                        
                        results['tests'].append({
                            'test': f"{dataset_name}.{field}_validity",
                            'status': status,
                            'description': description,
                            'validity_rate': validity_rate,
                            'valid_count': valid_count,
                            'total_records': total_records,
                            'threshold': self.thresholds['validity']
                        })
        
        results['score'] = total_validity / test_count if test_count > 0 else 0.0
        results['status'] = 'PASSED' if results['score'] >= self.thresholds['validity'] else 'FAILED'
        
        return results
    
    def _test_referential_integrity(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test referential integrity between datasets."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        # Foreign key relationships
        relationships = [
            ('sales', 'SKU', 'products', 'SKU', 'Sales must reference valid products'),
            ('sales', 'Retailer_ID', 'locations', 'Retailer_ID', 'Sales must reference valid locations')
        ]
        
        total_integrity = 0.0
        test_count = 0
        
        for child_table, child_key, parent_table, parent_key, description in relationships:
            if child_table in datasets and parent_table in datasets:
                child_df = datasets[child_table]
                parent_df = datasets[parent_table]
                
                # Get unique foreign key values from child table
                child_keys = child_df.select(child_key).distinct()
                parent_keys = parent_df.select(parent_key).distinct()
                
                # Find orphaned records (foreign keys not in parent)
                orphaned = child_keys.join(parent_keys, child_keys[child_key] == parent_keys[parent_key], 'left_anti')
                orphaned_count = orphaned.count()
                
                total_child_keys = child_keys.count()
                integrity_rate = (total_child_keys - orphaned_count) / total_child_keys if total_child_keys > 0 else 1.0
                
                test_count += 1
                total_integrity += integrity_rate
                
                status = 'PASSED' if integrity_rate >= self.thresholds['integrity'] else 'FAILED'
                
                results['tests'].append({
                    'test': f"{child_table}.{child_key}_to_{parent_table}.{parent_key}",
                    'status': status,
                    'description': description,
                    'integrity_rate': integrity_rate,
                    'orphaned_count': orphaned_count,
                    'total_keys': total_child_keys,
                    'threshold': self.thresholds['integrity']
                })
        
        results['score'] = total_integrity / test_count if test_count > 0 else 0.0
        results['status'] = 'PASSED' if results['score'] >= self.thresholds['integrity'] else 'FAILED'
        
        return results
    
    def _test_business_rules(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test complex business rules and logical consistency."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        business_rules = []
        
        # Sales business rules
        if 'sales' in datasets:
            sales_df = datasets['sales']
            
            # Rule 1: Total Revenue should approximately equal Units_Sold * Unit_Price
            revenue_check = sales_df.withColumn(
                'calculated_revenue', col('Units_Sold') * col('Unit_Price')
            ).withColumn(
                'revenue_diff', abs(col('Total_Revenue') - col('calculated_revenue'))
            ).withColumn(
                'revenue_valid', col('revenue_diff') <= (col('Total_Revenue') * 0.01)  # 1% tolerance
            )
            
            valid_revenue = revenue_check.filter(col('revenue_valid') == True).count()
            total_revenue = revenue_check.count()
            revenue_accuracy = valid_revenue / total_revenue if total_revenue > 0 else 0.0
            
            business_rules.append({
                'test': 'sales_revenue_calculation_accuracy',
                'status': 'PASSED' if revenue_accuracy >= self.thresholds['accuracy'] else 'FAILED',
                'description': 'Total Revenue = Units_Sold × Unit_Price (±1% tolerance)',
                'accuracy_rate': revenue_accuracy,
                'valid_records': valid_revenue,
                'total_records': total_revenue,
                'threshold': self.thresholds['accuracy']
            })
            
            # Rule 2: Date range validation
            if 'Date' in sales_df.columns:
                # Convert string dates to date type for validation
                date_df = sales_df.withColumn('Date_Parsed', to_date(col('Date'), 'yyyy-MM-dd'))
                
                valid_dates = date_df.filter(
                    (col('Date_Parsed') >= lit('2023-01-01')) & 
                    (col('Date_Parsed') <= lit('2023-12-31'))
                ).count()
                
                total_dates = date_df.filter(col('Date_Parsed').isNotNull()).count()
                date_validity = valid_dates / total_dates if total_dates > 0 else 0.0
                
                business_rules.append({
                    'test': 'sales_date_range_validation',
                    'status': 'PASSED' if date_validity >= self.thresholds['timeliness'] else 'FAILED',
                    'description': 'Sales dates within 2023 analysis period',
                    'validity_rate': date_validity,
                    'valid_records': valid_dates,
                    'total_records': total_dates,
                    'threshold': self.thresholds['timeliness']
                })
        
        # Product business rules
        if 'products' in datasets:
            products_df = datasets['products']
            
            # Rule 3: SKU uniqueness
            total_products = products_df.count()
            unique_skus = products_df.select('SKU').distinct().count()
            sku_uniqueness = unique_skus / total_products if total_products > 0 else 0.0
            
            business_rules.append({
                'test': 'products_sku_uniqueness',
                'status': 'PASSED' if sku_uniqueness >= self.thresholds['uniqueness'] else 'FAILED',
                'description': 'Product SKUs must be unique',
                'uniqueness_rate': sku_uniqueness,
                'unique_count': unique_skus,
                'total_records': total_products,
                'threshold': self.thresholds['uniqueness']
            })
        
        # Location business rules
        if 'locations' in datasets:
            locations_df = datasets['locations']
            
            # Rule 4: Retailer_ID uniqueness
            total_locations = locations_df.count()
            unique_retailers = locations_df.select('Retailer_ID').distinct().count()
            retailer_uniqueness = unique_retailers / total_locations if total_locations > 0 else 0.0
            
            business_rules.append({
                'test': 'locations_retailer_id_uniqueness',
                'status': 'PASSED' if retailer_uniqueness >= self.thresholds['uniqueness'] else 'FAILED',
                'description': 'Retailer IDs must be unique',
                'uniqueness_rate': retailer_uniqueness,
                'unique_count': unique_retailers,
                'total_records': total_locations,
                'threshold': self.thresholds['uniqueness']
            })
        
        results['tests'] = business_rules
        
        # Calculate overall score
        if business_rules:
            passed_rules = sum(1 for rule in business_rules if rule['status'] == 'PASSED')
            results['score'] = passed_rules / len(business_rules)
            results['status'] = 'PASSED' if results['score'] >= 0.8 else 'FAILED'  # 80% pass rate
        else:
            results['score'] = 0.0
            results['status'] = 'FAILED'
        
        return results
    
    def _test_statistical_anomalies(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test for statistical anomalies and outliers."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        # Numerical fields to test for anomalies
        numerical_tests = {
            'products': ['ABV', 'Price_Per_Unit'],
            'sales': ['Units_Sold', 'Unit_Price', 'Total_Revenue']
        }
        
        anomaly_tests = []
        
        for dataset_name, fields in numerical_tests.items():
            if dataset_name in datasets:
                df = datasets[dataset_name]
                
                for field in fields:
                    if field in df.columns:
                        # Calculate statistical measures
                        stats_df = df.select(
                            mean(col(field)).alias('mean'),
                            stddev(col(field)).alias('stddev'),
                            min(col(field)).alias('min'),
                            max(col(field)).alias('max'),
                            count(col(field)).alias('count')
                        ).collect()[0]
                        
                        if stats_df['stddev'] is not None and stats_df['stddev'] > 0:
                            # Identify outliers using 3-sigma rule
                            mean_val = stats_df['mean']
                            std_val = stats_df['stddev']
                            
                            outliers = df.filter(
                                (col(field) < (mean_val - self.thresholds['anomaly_threshold'] * std_val)) |
                                (col(field) > (mean_val + self.thresholds['anomaly_threshold'] * std_val))
                            ).count()
                            
                            total_records = stats_df['count']
                            anomaly_rate = outliers / total_records if total_records > 0 else 0.0
                            
                            # Acceptable anomaly rate is < 1% (99% normal)
                            status = 'PASSED' if anomaly_rate < 0.01 else 'WARNING'
                            
                            anomaly_tests.append({
                                'test': f"{dataset_name}.{field}_anomaly_detection",
                                'status': status,
                                'description': f'Statistical outlier detection (3-sigma rule)',
                                'anomaly_rate': anomaly_rate,
                                'outlier_count': outliers,
                                'total_records': total_records,
                                'mean': mean_val,
                                'stddev': std_val,
                                'min': stats_df['min'],
                                'max': stats_df['max']
                            })
        
        results['tests'] = anomaly_tests
        
        # Calculate score based on anomaly rates
        if anomaly_tests:
            low_anomaly_tests = sum(1 for test in anomaly_tests if test['anomaly_rate'] < 0.01)
            results['score'] = low_anomaly_tests / len(anomaly_tests)
            results['status'] = 'PASSED' if results['score'] >= 0.8 else 'WARNING'
        else:
            results['score'] = 1.0
            results['status'] = 'PASSED'
        
        return results
    
    def _test_data_consistency(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test data consistency across datasets."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        consistency_tests = []
        
        # Cross-dataset consistency checks
        if 'sales' in datasets and 'products' in datasets:
            sales_df = datasets['sales']
            products_df = datasets['products']
            
            # Check category consistency in sales vs products
            sales_categories = sales_df.join(products_df, 'SKU', 'inner') \
                .select(products_df.Category.alias('Product_Category')).distinct().collect()
            
            expected_categories = {'BEER', 'HARD SELTZER'}
            actual_categories = {row['Product_Category'] for row in sales_categories}
            
            category_consistency = len(actual_categories.intersection(expected_categories)) / len(expected_categories)
            
            consistency_tests.append({
                'test': 'cross_dataset_category_consistency',
                'status': 'PASSED' if category_consistency >= self.thresholds['consistency'] else 'FAILED',
                'description': 'Category values consistent across sales and products',
                'consistency_rate': category_consistency,
                'expected_categories': list(expected_categories),
                'actual_categories': list(actual_categories),
                'threshold': self.thresholds['consistency']
            })
        
        results['tests'] = consistency_tests
        
        if consistency_tests:
            passed_tests = sum(1 for test in consistency_tests if test['status'] == 'PASSED')
            results['score'] = passed_tests / len(consistency_tests)
            results['status'] = 'PASSED' if results['score'] >= self.thresholds['consistency'] else 'FAILED'
        else:
            results['score'] = 1.0
            results['status'] = 'PASSED'
        
        return results
    
    def _test_temporal_validation(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test temporal data patterns and trends."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        temporal_tests = []
        
        if 'sales' in datasets:
            sales_df = datasets['sales']
            
            # Convert date column and analyze temporal patterns
            if 'Date' in sales_df.columns:
                date_df = sales_df.withColumn('Date_Parsed', to_date(col('Date'), 'yyyy-MM-dd'))
                
                # Test 1: Date distribution (should be relatively even across months)
                monthly_counts = date_df.withColumn('Month', month(col('Date_Parsed'))) \
                    .groupBy('Month').count().collect()
                
                if len(monthly_counts) >= 12:  # Full year of data
                    counts = [row['count'] for row in monthly_counts]
                    mean_count = np.mean(counts)
                    std_count = np.std(counts)
                    cv = std_count / mean_count if mean_count > 0 else float('inf')
                    
                    # Coefficient of variation should be < 0.3 for reasonable distribution
                    temporal_consistency = 1.0 if cv < 0.3 else max(0.0, 1.0 - (cv - 0.3) / 0.7)
                    
                    temporal_tests.append({
                        'test': 'sales_temporal_distribution',
                        'status': 'PASSED' if temporal_consistency >= 0.7 else 'WARNING',
                        'description': 'Sales distribution across months',
                        'consistency_score': temporal_consistency,
                        'coefficient_of_variation': cv,
                        'monthly_counts': dict(zip([row['Month'] for row in monthly_counts], counts))
                    })
                
                # Test 2: No future dates
                future_dates = date_df.filter(col('Date_Parsed') > lit(date.today())).count()
                total_dates = date_df.filter(col('Date_Parsed').isNotNull()).count()
                
                future_date_rate = future_dates / total_dates if total_dates > 0 else 0.0
                
                temporal_tests.append({
                    'test': 'sales_no_future_dates',
                    'status': 'PASSED' if future_date_rate == 0.0 else 'FAILED',
                    'description': 'No sales dates in the future',
                    'future_date_rate': future_date_rate,
                    'future_dates_count': future_dates,
                    'total_dates': total_dates
                })
        
        results['tests'] = temporal_tests
        
        if temporal_tests:
            passed_tests = sum(1 for test in temporal_tests if test['status'] == 'PASSED')
            results['score'] = passed_tests / len(temporal_tests)
            results['status'] = 'PASSED' if results['score'] >= 0.8 else 'WARNING'
        else:
            results['score'] = 1.0
            results['status'] = 'PASSED'
        
        return results
    
    def _test_cross_dataset_validation(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test cross-dataset relationships and aggregations."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        cross_tests = []
        
        if all(dataset in datasets for dataset in ['sales', 'products', 'locations']):
            sales_df = datasets['sales']
            products_df = datasets['products']
            locations_df = datasets['locations']
            
            # Test 1: All sales reference valid products and locations
            valid_sales = sales_df.join(products_df, 'SKU', 'inner') \
                .join(locations_df, 'Retailer_ID', 'inner').count()
            
            total_sales = sales_df.count()
            reference_validity = valid_sales / total_sales if total_sales > 0 else 0.0
            
            cross_tests.append({
                'test': 'sales_reference_validity',
                'status': 'PASSED' if reference_validity >= self.thresholds['integrity'] else 'FAILED',
                'description': 'All sales transactions reference valid products and locations',
                'validity_rate': reference_validity,
                'valid_sales': valid_sales,
                'total_sales': total_sales,
                'threshold': self.thresholds['integrity']
            })
            
            # Test 2: Revenue aggregation consistency
            total_revenue_direct = sales_df.agg({"Total_Revenue": "sum"}).collect()[0][0]
            
            total_revenue_calculated = sales_df.agg(
                {"Units_Sold": "sum", "Unit_Price": "avg"}
            ).collect()[0]
            
            if total_revenue_direct and total_revenue_calculated:
                revenue_diff = abs(total_revenue_direct - total_revenue_calculated)
                revenue_consistency = 1.0 - (revenue_diff / total_revenue_direct)
                
                cross_tests.append({
                    'test': 'revenue_aggregation_consistency',
                    'status': 'PASSED' if revenue_consistency >= 0.99 else 'FAILED',
                    'description': 'Total revenue consistency between direct and calculated values',
                    'consistency_rate': revenue_consistency,
                    'direct_revenue': total_revenue_direct,
                    'calculated_revenue': total_revenue_calculated,
                    'difference': revenue_diff
                })
        
        results['tests'] = cross_tests
        
        if cross_tests:
            passed_tests = sum(1 for test in cross_tests if test['status'] == 'PASSED')
            results['score'] = passed_tests / len(cross_tests)
            results['status'] = 'PASSED' if results['score'] >= 0.9 else 'FAILED'
        else:
            results['score'] = 1.0
            results['status'] = 'PASSED'
        
        return results
    
    def _test_pipeline_results(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test the statistical soundness of pipeline analysis results."""
        results = {'status': 'PASSED', 'tests': [], 'score': 0.0}
        
        pipeline_tests = []
        
        if 'sales' in datasets and 'products' in datasets:
            # Create fact table for analysis
            fact_table = datasets['sales'].join(datasets['products'], 'SKU', 'inner')
            
            # Test 1: Category distribution statistical significance
            category_counts = fact_table.groupBy(datasets['products'].Category.alias('Product_Category')).count().collect()
            
            if len(category_counts) == 2:  # Beer and Hard Seltzer
                beer_count = next((row['count'] for row in category_counts if 'BEER' in row['Product_Category']), 0)
                seltzer_count = next((row['count'] for row in category_counts if 'SELTZER' in row['Product_Category']), 0)
                
                total_count = beer_count + seltzer_count
                
                if total_count > 0:
                    # Chi-square test for category distribution
                    expected_equal = total_count / 2
                    chi_stat = ((beer_count - expected_equal) ** 2 / expected_equal + 
                               (seltzer_count - expected_equal) ** 2 / expected_equal)
                    
                    # Critical value for alpha = 0.05, df = 1
                    critical_value = 3.841
                    
                    pipeline_tests.append({
                        'test': 'category_distribution_significance',
                        'status': 'PASSED' if chi_stat > critical_value else 'WARNING',
                        'description': 'Category distribution shows significant difference from equal split',
                        'chi_square_statistic': chi_stat,
                        'critical_value': critical_value,
                        'beer_count': beer_count,
                        'seltzer_count': seltzer_count,
                        'p_value_significant': chi_stat > critical_value
                    })
            
            # Test 2: Revenue distribution normality (for statistical tests)
            revenue_sample = fact_table.select('Total_Revenue').sample(0.1).toPandas()['Total_Revenue']
            
            if len(revenue_sample) > 50:  # Minimum sample size for normality test
                # Shapiro-Wilk test for normality (use sample due to size limitations)
                sample_size = min(5000, len(revenue_sample))
                test_sample = revenue_sample.sample(n=sample_size) if len(revenue_sample) > sample_size else revenue_sample
                
                try:
                    stat, p_value = normaltest(test_sample)
                    is_normal = p_value > 0.05
                    
                    pipeline_tests.append({
                        'test': 'revenue_distribution_normality',
                        'status': 'INFO',  # Informational test
                        'description': 'Revenue distribution normality test',
                        'is_normal': is_normal,
                        'p_value': p_value,
                        'sample_size': len(test_sample),
                        'recommendation': 'Use non-parametric tests' if not is_normal else 'Parametric tests appropriate'
                    })
                except Exception as e:
                    pipeline_tests.append({
                        'test': 'revenue_distribution_normality',
                        'status': 'ERROR',
                        'description': 'Failed to perform normality test',
                        'error': str(e)
                    })
            
            # Test 3: Sample size adequacy for statistical inference
            total_transactions = fact_table.count()
            
            # Rule of thumb: n >= 30 for CLT, n >= 100 for robust inference
            sample_adequacy = 'EXCELLENT' if total_transactions >= 1000 else \
                             'GOOD' if total_transactions >= 100 else \
                             'ADEQUATE' if total_transactions >= 30 else 'INSUFFICIENT'
            
            pipeline_tests.append({
                'test': 'sample_size_adequacy',
                'status': 'PASSED' if total_transactions >= 30 else 'FAILED',
                'description': 'Sample size adequacy for statistical inference',
                'sample_size': total_transactions,
                'adequacy_level': sample_adequacy,
                'minimum_required': 30,
                'recommended': 100
            })
        
        results['tests'] = pipeline_tests
        
        if pipeline_tests:
            passed_tests = sum(1 for test in pipeline_tests if test['status'] in ['PASSED', 'INFO'])
            results['score'] = passed_tests / len(pipeline_tests)
            results['status'] = 'PASSED' if results['score'] >= 0.8 else 'WARNING'
        else:
            results['score'] = 1.0
            results['status'] = 'PASSED'
        
        return results
    
    def _is_type_compatible(self, actual_type, expected_type) -> bool:
        """Check if actual data type is compatible with expected type."""
        # Handle string/numeric compatibility
        if isinstance(expected_type, StringType) and isinstance(actual_type, StringType):
            return True
        elif isinstance(expected_type, (IntegerType, LongType)) and isinstance(actual_type, (IntegerType, LongType)):
            return True
        elif isinstance(expected_type, (DoubleType, FloatType)) and isinstance(actual_type, (DoubleType, FloatType, IntegerType, LongType)):
            return True
        elif isinstance(expected_type, BooleanType) and isinstance(actual_type, BooleanType):
            return True
        elif isinstance(expected_type, DateType) and isinstance(actual_type, (DateType, StringType)):
            return True
        else:
            return type(actual_type) == type(expected_type)
    
    def _generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality assessment report."""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_test_categories': len(self.quality_results),
                'overall_status': 'PASSED',
                'overall_score': 0.0
            },
            'category_results': self.quality_results,
            'recommendations': [],
            'quality_metrics': {}
        }
        
        # Calculate overall metrics
        category_scores = []
        failed_categories = []
        
        for category, results in self.quality_results.items():
            if 'score' in results:
                category_scores.append(results['score'])
                if results['status'] in ['FAILED', 'ERROR']:
                    failed_categories.append(category)
        
        if category_scores:
            report['summary']['overall_score'] = sum(category_scores) / len(category_scores)
        
        # Determine overall status
        if failed_categories:
            report['summary']['overall_status'] = 'FAILED'
        elif any(results.get('status') == 'WARNING' for results in self.quality_results.values()):
            report['summary']['overall_status'] = 'WARNING'
        
        report['summary']['failed_categories'] = failed_categories
        
        # Generate recommendations
        recommendations = []
        
        if report['summary']['overall_score'] < 0.9:
            recommendations.append("Overall data quality score below 90%. Review failed test categories.")
        
        for category, results in self.quality_results.items():
            if results.get('status') == 'FAILED':
                recommendations.append(f"Address {category} issues before proceeding with analysis.")
            elif results.get('status') == 'WARNING':
                recommendations.append(f"Monitor {category} for potential issues.")
        
        if not recommendations:
            recommendations.append("Data quality is excellent. Proceed with confidence in analysis results.")
        
        report['recommendations'] = recommendations
        
        # Quality metrics summary
        report['quality_metrics'] = {
            'completeness': self._extract_metric('completeness'),
            'validity': self._extract_metric('validity'),
            'integrity': self._extract_metric('integrity'),
            'consistency': self._extract_metric('consistency'),
            'accuracy': self._extract_metric('accuracy')
        }
        
        return report
    
    def _extract_metric(self, metric_type: str) -> Dict[str, Any]:
        """Extract specific quality metric from results."""
        metric_data = {'scores': [], 'average': 0.0, 'status': 'UNKNOWN'}
        
        for category, results in self.quality_results.items():
            if 'tests' in results:
                for test in results['tests']:
                    if metric_type in test.get('test', '').lower():
                        if f'{metric_type}_rate' in test:
                            metric_data['scores'].append(test[f'{metric_type}_rate'])
        
        if metric_data['scores']:
            metric_data['average'] = sum(metric_data['scores']) / len(metric_data['scores'])
            threshold = self.thresholds.get(metric_type, 0.95)
            metric_data['status'] = 'PASSED' if metric_data['average'] >= threshold else 'FAILED'
        
        return metric_data
    
    def _save_quality_results(self, quality_report: Dict[str, Any]):
        """Save quality assessment results to files."""
        # Create quality reports directory
        os.makedirs('quality_reports', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON report
        json_path = f'quality_reports/data_quality_report_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(quality_report, f, indent=2, default=str)
        
        # Save summary report
        summary_path = f'quality_reports/quality_summary_{timestamp}.txt'
        with open(summary_path, 'w') as f:
            f.write("DATA QUALITY ASSESSMENT SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Timestamp: {quality_report['summary']['timestamp']}\n")
            f.write(f"Overall Status: {quality_report['summary']['overall_status']}\n")
            f.write(f"Overall Score: {quality_report['summary']['overall_score']:.3f}\n\n")
            
            f.write("CATEGORY RESULTS:\n")
            f.write("-" * 20 + "\n")
            for category, results in quality_report['category_results'].items():
                status = results.get('status', 'UNKNOWN')
                score = results.get('score', 0.0)
                f.write(f"{category}: {status} (Score: {score:.3f})\n")
            
            f.write("\nRECOMMENDATIONS:\n")
            f.write("-" * 15 + "\n")
            for i, rec in enumerate(quality_report['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        
        self.logger.info(f"📊 Quality reports saved:")
        self.logger.info(f"   Detailed: {json_path}")
        self.logger.info(f"   Summary: {summary_path}")

def main():
    """Main execution function for data quality testing."""
    print("🔍 Comprehensive Data Quality Testing Suite")
    print("=" * 60)
    
    try:
        # Initialize tester
        tester = ComprehensiveDataQualityTester()
        
        # Run comprehensive tests
        quality_report = tester.run_comprehensive_quality_tests()
        
        # Print summary
        print(f"\n📊 QUALITY ASSESSMENT SUMMARY")
        print("-" * 40)
        print(f"Overall Status: {quality_report['summary']['overall_status']}")
        print(f"Overall Score: {quality_report['summary']['overall_score']:.3f}")
        print(f"Test Categories: {quality_report['summary']['total_test_categories']}")
        
        if quality_report['summary']['failed_categories']:
            print(f"Failed Categories: {', '.join(quality_report['summary']['failed_categories'])}")
        
        print(f"\n💡 KEY RECOMMENDATIONS:")
        for i, rec in enumerate(quality_report['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n📁 Detailed reports saved in 'quality_reports/' directory")
        
        # Return appropriate exit code
        if quality_report['summary']['overall_status'] == 'FAILED':
            return 1
        else:
            return 0
            
    except Exception as e:
        print(f"\n❌ Quality testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())