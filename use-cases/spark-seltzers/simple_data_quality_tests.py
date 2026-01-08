#!/usr/bin/env python3
"""
Simplified Data Quality Testing Suite
====================================

Focused data quality validation for the Beer-Seltzer analysis pipeline.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# PySpark imports
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import *
from pyspark.sql.functions import *

class SimpleDataQualityTester:
    """
    Simplified data quality testing framework.
    """
    
    def __init__(self):
        """Initialize the data quality tester."""
        self.spark = self._create_spark_session()
        self.quality_results = {}
        self.logger = self._setup_logger()
        
        self.logger.info("🔍 Simple Data Quality Tester initialized")
    
    def _create_spark_session(self) -> SparkSession:
        """Create Spark session."""
        return SparkSession.builder \
            .appName("SimpleDataQualityTesting") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger('SimpleDataQualityTester')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_quality_tests(self, data_path: str = "synthetic_data") -> Dict[str, Any]:
        """Run comprehensive data quality tests."""
        self.logger.info("🚀 Starting data quality testing")
        
        # Load datasets
        datasets = self._load_datasets(data_path)
        
        # Run tests
        results = {
            'timestamp': datetime.now().isoformat(),
            'data_completeness': self._test_completeness(datasets),
            'data_validity': self._test_validity(datasets),
            'referential_integrity': self._test_integrity(datasets),
            'business_rules': self._test_business_rules(datasets),
            'statistical_summary': self._generate_statistics(datasets)
        }
        
        # Calculate overall score
        scores = []
        for test_name, test_result in results.items():
            if isinstance(test_result, dict) and 'score' in test_result:
                scores.append(test_result['score'])
        
        if scores:
            total_score = 0.0
            for score in scores:
                total_score += score
            overall_score = total_score / len(scores)
        else:
            overall_score = 0.0
        results['overall_score'] = overall_score
        results['overall_status'] = 'PASSED' if overall_score >= 0.9 else 'FAILED'
        
        # Save results
        self._save_results(results)
        
        self.logger.info("🎉 Data quality testing completed")
        return results
    
    def _load_datasets(self, data_path: str) -> Dict[str, DataFrame]:
        """Load datasets."""
        datasets = {}
        
        try:
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
            
            for name, df in datasets.items():
                df.cache()
                count = df.count()
                self.logger.info(f"📊 Loaded {name}: {count:,} records")
            
        except Exception as e:
            self.logger.error(f"Failed to load datasets: {str(e)}")
            raise
        
        return datasets
    
    def _test_completeness(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test data completeness."""
        results = {'test_name': 'Data Completeness', 'tests': [], 'score': 0.0}
        
        critical_fields = {
            'products': ['SKU', 'Product_Name', 'Brand', 'Category'],
            'locations': ['Retailer_ID', 'Store_Name', 'Region', 'State'],
            'sales': ['Transaction_ID', 'Date', 'Retailer_ID', 'SKU', 'Units_Sold']
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
                        
                        results['tests'].append({
                            'field': f"{dataset_name}.{field}",
                            'completeness_rate': completeness,
                            'null_count': null_count,
                            'total_records': total_records,
                            'status': 'PASSED' if completeness >= 0.95 else 'FAILED'
                        })
        
        results['score'] = total_completeness / test_count if test_count > 0 else 0.0
        return results
    
    def _test_validity(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test data validity."""
        results = {'test_name': 'Data Validity', 'tests': [], 'score': 0.0}
        
        validity_tests = []
        
        # Products validity
        if 'products' in datasets:
            products_df = datasets['products']
            total_products = products_df.count()
            
            # Category validity
            valid_categories = products_df.filter(
                col('Category').isin(['BEER', 'HARD SELTZER'])
            ).count()
            category_validity = valid_categories / total_products
            
            validity_tests.append({
                'field': 'products.Category',
                'validity_rate': category_validity,
                'valid_count': valid_categories,
                'total_records': total_products,
                'status': 'PASSED' if category_validity >= 0.98 else 'FAILED'
            })
            
            # ABV validity
            if 'ABV' in products_df.columns:
                valid_abv = products_df.filter(
                    (col('ABV') >= 0.1) & (col('ABV') <= 20.0)
                ).count()
                abv_validity = valid_abv / total_products
                
                validity_tests.append({
                    'field': 'products.ABV',
                    'validity_rate': abv_validity,
                    'valid_count': valid_abv,
                    'total_records': total_products,
                    'status': 'PASSED' if abv_validity >= 0.98 else 'FAILED'
                })
        
        # Sales validity
        if 'sales' in datasets:
            sales_df = datasets['sales']
            total_sales = sales_df.count()
            
            # Units sold validity
            valid_units = sales_df.filter(
                (col('Units_Sold') >= 1) & (col('Units_Sold') <= 50)
            ).count()
            units_validity = valid_units / total_sales
            
            validity_tests.append({
                'field': 'sales.Units_Sold',
                'validity_rate': units_validity,
                'valid_count': valid_units,
                'total_records': total_sales,
                'status': 'PASSED' if units_validity >= 0.98 else 'FAILED'
            })
        
        results['tests'] = validity_tests
        
        if validity_tests:
            total_validity = 0.0
            for test in validity_tests:
                total_validity += test['validity_rate']
            results['score'] = total_validity / len(validity_tests)
        
        return results
    
    def _test_integrity(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test referential integrity."""
        results = {'test_name': 'Referential Integrity', 'tests': [], 'score': 0.0}
        
        integrity_tests = []
        
        if 'sales' in datasets and 'products' in datasets:
            sales_df = datasets['sales']
            products_df = datasets['products']
            
            # Check SKU references
            sales_skus = sales_df.select('SKU').distinct()
            product_skus = products_df.select('SKU').distinct()
            
            orphaned_skus = sales_skus.join(product_skus, 'SKU', 'left_anti').count()
            total_sales_skus = sales_skus.count()
            
            sku_integrity = (total_sales_skus - orphaned_skus) / total_sales_skus if total_sales_skus > 0 else 1.0
            
            integrity_tests.append({
                'relationship': 'sales.SKU -> products.SKU',
                'integrity_rate': sku_integrity,
                'orphaned_count': orphaned_skus,
                'total_references': total_sales_skus,
                'status': 'PASSED' if sku_integrity >= 1.0 else 'FAILED'
            })
        
        if 'sales' in datasets and 'locations' in datasets:
            sales_df = datasets['sales']
            locations_df = datasets['locations']
            
            # Check Retailer_ID references
            sales_retailers = sales_df.select('Retailer_ID').distinct()
            location_retailers = locations_df.select('Retailer_ID').distinct()
            
            orphaned_retailers = sales_retailers.join(location_retailers, 'Retailer_ID', 'left_anti').count()
            total_sales_retailers = sales_retailers.count()
            
            retailer_integrity = (total_sales_retailers - orphaned_retailers) / total_sales_retailers if total_sales_retailers > 0 else 1.0
            
            integrity_tests.append({
                'relationship': 'sales.Retailer_ID -> locations.Retailer_ID',
                'integrity_rate': retailer_integrity,
                'orphaned_count': orphaned_retailers,
                'total_references': total_sales_retailers,
                'status': 'PASSED' if retailer_integrity >= 1.0 else 'FAILED'
            })
        
        results['tests'] = integrity_tests
        
        if integrity_tests:
            total_integrity = 0.0
            for test in integrity_tests:
                total_integrity += test['integrity_rate']
            results['score'] = total_integrity / len(integrity_tests)
        
        return results
    
    def _test_business_rules(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Test business rules."""
        results = {'test_name': 'Business Rules', 'tests': [], 'score': 0.0}
        
        business_tests = []
        
        if 'sales' in datasets:
            sales_df = datasets['sales']
            
            # Revenue calculation accuracy
            revenue_check = sales_df.withColumn(
                'calculated_revenue', col('Units_Sold') * col('Unit_Price')
            ).withColumn(
                'revenue_diff', abs(col('Total_Revenue') - col('calculated_revenue'))
            ).withColumn(
                'revenue_valid', col('revenue_diff') <= (col('Total_Revenue') * 0.01)
            )
            
            valid_revenue = revenue_check.filter(col('revenue_valid') == True).count()
            total_revenue = revenue_check.count()
            revenue_accuracy = valid_revenue / total_revenue if total_revenue > 0 else 0.0
            
            business_tests.append({
                'rule': 'Revenue Calculation Accuracy',
                'description': 'Total_Revenue = Units_Sold × Unit_Price (±1% tolerance)',
                'accuracy_rate': revenue_accuracy,
                'valid_records': valid_revenue,
                'total_records': total_revenue,
                'status': 'PASSED' if revenue_accuracy >= 0.95 else 'FAILED'
            })
        
        if 'products' in datasets:
            products_df = datasets['products']
            
            # SKU uniqueness
            total_products = products_df.count()
            unique_skus = products_df.select('SKU').distinct().count()
            sku_uniqueness = unique_skus / total_products if total_products > 0 else 0.0
            
            business_tests.append({
                'rule': 'SKU Uniqueness',
                'description': 'All product SKUs must be unique',
                'uniqueness_rate': sku_uniqueness,
                'unique_count': unique_skus,
                'total_records': total_products,
                'status': 'PASSED' if sku_uniqueness >= 1.0 else 'FAILED'
            })
        
        results['tests'] = business_tests
        
        if business_tests:
            passed_tests = 0
            for test in business_tests:
                if test['status'] == 'PASSED':
                    passed_tests += 1
            results['score'] = passed_tests / len(business_tests)
        
        return results
    
    def _generate_statistics(self, datasets: Dict[str, DataFrame]) -> Dict[str, Any]:
        """Generate statistical summary."""
        stats = {'test_name': 'Statistical Summary', 'datasets': {}}
        
        for name, df in datasets.items():
            dataset_stats = {
                'record_count': df.count(),
                'column_count': len(df.columns),
                'columns': df.columns
            }
            
            # Numerical column statistics
            numerical_cols = [field.name for field in df.schema.fields 
                            if isinstance(field.dataType, (IntegerType, LongType, DoubleType, FloatType))]
            
            if numerical_cols:
                for col_name in numerical_cols[:5]:  # Limit to first 5 numerical columns
                    try:
                        col_stats = df.select(col_name).describe().collect()
                        dataset_stats[f'{col_name}_stats'] = {
                            row['summary']: row[col_name] for row in col_stats
                        }
                    except:
                        pass
            
            stats['datasets'][name] = dataset_stats
        
        stats['score'] = 1.0  # Statistics always pass
        return stats
    
    def _save_results(self, results: Dict[str, Any]):
        """Save quality test results."""
        os.makedirs('quality_reports', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        json_path = f'quality_reports/simple_quality_report_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save summary
        summary_path = f'quality_reports/simple_quality_summary_{timestamp}.txt'
        with open(summary_path, 'w') as f:
            f.write("SIMPLE DATA QUALITY ASSESSMENT\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Timestamp: {results['timestamp']}\n")
            f.write(f"Overall Status: {results['overall_status']}\n")
            f.write(f"Overall Score: {results['overall_score']:.3f}\n\n")
            
            for test_name, test_result in results.items():
                if isinstance(test_result, dict) and 'test_name' in test_result:
                    f.write(f"{test_result['test_name']}: ")
                    if 'score' in test_result:
                        f.write(f"Score {test_result['score']:.3f}\n")
                    else:
                        f.write("Completed\n")
        
        self.logger.info(f"📊 Quality reports saved: {json_path}")

def main():
    """Main execution function."""
    print("🔍 Simple Data Quality Testing Suite")
    print("=" * 50)
    
    try:
        tester = SimpleDataQualityTester()
        results = tester.run_quality_tests()
        
        print(f"\n📊 QUALITY ASSESSMENT RESULTS")
        print("-" * 35)
        print(f"Overall Status: {results['overall_status']}")
        print(f"Overall Score: {results['overall_score']:.3f}")
        
        for test_name, test_result in results.items():
            if isinstance(test_result, dict) and 'test_name' in test_result:
                score = test_result.get('score', 'N/A')
                print(f"{test_result['test_name']}: {score}")
        
        print(f"\n📁 Detailed reports saved in 'quality_reports/' directory")
        
        return 0 if results['overall_status'] == 'PASSED' else 1
        
    except Exception as e:
        print(f"\n❌ Quality testing failed: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())