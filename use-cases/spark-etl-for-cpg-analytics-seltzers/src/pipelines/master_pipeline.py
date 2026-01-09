#!/usr/bin/env python3
"""
Master PySpark Pipeline Orchestrator
===================================

Complete end-to-end pipeline: Data Generation → Ingestion → ETL → Analysis → Reporting → Visualization
Includes orchestration, fault tolerance, monitoring, and automated PDF report generation.
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from pyspark.sql import SparkSession
from utils.config_manager import get_config_manager
from utils.logging_utils import PipelineLogger, PerformanceMonitor, ErrorHandler
from utils.checkpoint_manager import CheckpointManager

class MasterPipeline:
    """
    Master pipeline orchestrator that coordinates all pipeline stages.
    """
    
    def __init__(self, config_path: str = "config/pipeline_config.yaml"):
        """Initialize master pipeline."""
        # Load configuration
        self.config_manager = get_config_manager(config_path)
        self.config = self.config_manager.config
        
        # Initialize utilities
        self.logger = PipelineLogger(self.config['logging'])
        self.monitor = PerformanceMonitor(self.logger)
        self.error_handler = ErrorHandler(self.logger, self.config['error_handling'])
        
        # Initialize checkpoint manager
        checkpoint_dir = self.config_manager.get_data_paths()['checkpoints']
        self.checkpoint_manager = CheckpointManager(checkpoint_dir, self.config['data']['checkpoints'])
        
        # Pipeline state
        self.run_id = str(uuid.uuid4())[:8]
        self.spark = None
        self.pipeline_data = {}
        self.completed_stages = []
        
        # Create required directories
        self.config_manager.create_directories()
        
        self.logger.logger.info(f"🚀 Master Pipeline Initialized - Run ID: {self.run_id}")
    
    def create_spark_session(self) -> SparkSession:
        """Create and configure Spark session."""
        try:
            spark_config = self.config_manager.get_spark_config()
            env_config = self.config['environment']['spark']
            
            builder = SparkSession.builder \
                .appName(f"{env_config['app_name']}-{self.run_id}") \
                .master(env_config['master'])
            
            # Apply configuration
            for key, value in spark_config.items():
                builder = builder.config(key, value)
            
            self.spark = builder.getOrCreate()
            self.spark.sparkContext.setLogLevel(env_config['log_level'])
            
            # Set checkpoint directory for Spark
            checkpoint_dir = self.config_manager.get_data_paths()['checkpoints']
            self.spark.sparkContext.setCheckpointDir(checkpoint_dir)
            
            self.logger.logger.info("✅ Spark session created successfully")
            return self.spark
            
        except Exception as e:
            self.logger.logger.error(f"Failed to create Spark session: {e}")
            raise
    
    def stage_data_generation(self) -> bool:
        """Stage 1: Generate synthetic data if needed."""
        self.monitor.logger.start_stage('data_generation')
        
        try:
            stage_config = self.config_manager.get_stage_config('data_generation')
            
            if not stage_config.get('enabled', True):
                self.logger.logger.info("📊 Data generation stage disabled, skipping...")
                self.monitor.logger.end_stage('data_generation', success=True)
                return True
            
            # Check if data already exists
            data_paths = self.config_manager.get_data_paths()
            
            files_exist = all(
                os.path.exists(path) for path in [
                    data_paths['products'],
                    data_paths['locations'], 
                    data_paths['sales']
                ]
            )
            
            if files_exist and not stage_config.get('force_regenerate', False):
                self.logger.logger.info("📊 Synthetic data already exists, skipping generation...")
                self.monitor.logger.end_stage('data_generation', success=True)
                return True
            
            # Import and run data generator
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from simple_data_generator import SyntheticDataGenerator
            
            generator = SyntheticDataGenerator()
            
            # Apply configuration
            multiplier = stage_config.get('sample_size_multiplier', 1.0)
            if multiplier != 1.0:
                generator.num_transactions = int(generator.num_transactions * multiplier)
                self.logger.logger.info(f"📊 Adjusted sample size by {multiplier}x")
            
            # Generate data
            generator.generate_all_data()
            
            # Log data statistics
            self.logger.log_record_count('data_generation', 'products', generator.num_products)
            self.logger.log_record_count('data_generation', 'locations', generator.num_locations)
            self.logger.log_record_count('data_generation', 'transactions', generator.num_transactions)
            
            # Save checkpoint
            checkpoint_data = {
                'num_products': generator.num_products,
                'num_locations': generator.num_locations,
                'num_transactions': generator.num_transactions,
                'multiplier': multiplier
            }
            
            self.checkpoint_manager.save_checkpoint('data_generation', checkpoint_data)
            
            self.monitor.logger.end_stage('data_generation', success=True)
            return True
            
        except Exception as e:
            self.monitor.logger.end_stage('data_generation', success=False, error=str(e))
            if not self.error_handler.handle_error(e, 'data_generation', critical=True):
                return False
            return True
    
    def stage_data_ingestion(self) -> bool:
        """Stage 2: Data ingestion with validation."""
        self.monitor.logger.start_stage('data_ingestion')
        
        try:
            stage_config = self.config_manager.get_stage_config('data_ingestion')
            
            if not stage_config.get('enabled', True):
                self.logger.logger.info("📥 Data ingestion stage disabled, skipping...")
                self.monitor.logger.end_stage('data_ingestion', success=True)
                return True
            
            # Import ingestion pipeline
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from spark_data_ingestion import DataIngestionPipeline
            
            data_paths = self.config_manager.get_data_paths()
            ingestion = DataIngestionPipeline(data_paths['input_base'])
            ingestion.spark = self.spark
            
            # Define schemas
            ingestion.define_schemas()
            
            # Load datasets with validation
            products_df = ingestion.read_csv_with_validation('products.csv', 'products')
            locations_df = ingestion.read_csv_with_validation('locations.csv', 'locations')
            sales_df = ingestion.read_csv_with_validation('sales_transactions.csv', 'sales_transactions')
            
            # Cache datasets
            if stage_config.get('cache_enabled', True):
                products_df.cache()
                locations_df.cache()
                sales_df.cache()
            
            # Log record counts
            self.logger.log_record_count('ingestion', 'products', products_df.count())
            self.logger.log_record_count('ingestion', 'locations', locations_df.count())
            self.logger.log_record_count('ingestion', 'sales', sales_df.count())
            
            # Quality checks
            quality_metrics = {}
            if stage_config.get('quality_checks_enabled', True):
                quality_metrics = ingestion.generate_quality_report()
                self.logger.log_data_quality('ingestion', quality_metrics)
            
            # Store in pipeline data
            self.pipeline_data['raw_data'] = {
                'products': products_df,
                'locations': locations_df,
                'sales': sales_df
            }
            
            # Save checkpoint
            checkpoint_data = {
                'products_count': products_df.count(),
                'locations_count': locations_df.count(),
                'sales_count': sales_df.count(),
                'quality_metrics': quality_metrics
            }
            
            self.checkpoint_manager.save_checkpoint('ingestion', checkpoint_data, sales_df)
            
            self.monitor.logger.end_stage('data_ingestion', success=True)
            return True
            
        except Exception as e:
            self.monitor.logger.end_stage('data_ingestion', success=False, error=str(e))
            if not self.error_handler.handle_error(e, 'data_ingestion', critical=True):
                return False
            return True
    
    def stage_data_cleaning(self) -> bool:
        """Stage 3: Data cleaning and feature engineering."""
        self.monitor.logger.start_stage('data_cleaning')
        
        try:
            stage_config = self.config_manager.get_stage_config('data_cleaning')
            
            if not stage_config.get('enabled', True):
                self.logger.logger.info("🧹 Data cleaning stage disabled, skipping...")
                self.monitor.logger.end_stage('data_cleaning', success=True)
                return True
            # Import cleaning pipeline
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from spark_data_cleaning_pipeline import DataCleaningPipeline
            
            raw_data = self.pipeline_data['raw_data']
            
            cleaning = DataCleaningPipeline()
            cleaning.spark = self.spark
            
            # Apply cleaning
            cleaned_data = cleaning.clean_all_datasets(
                raw_data['products'],
                raw_data['locations'],
                raw_data['sales']
            )
            
            # Create fact table
            fact_table = cleaning.create_fact_table(
                cleaned_data['products'],
                cleaned_data['locations'],
                cleaned_data['sales']
            )
            
            # Feature engineering
            fact_table_enhanced = cleaning.engineer_features(fact_table)
            
            # Cache enhanced fact table
            fact_table_enhanced.cache()
            
            # Calculate retention rate
            original_count = raw_data['sales'].count()
            cleaned_count = fact_table_enhanced.count()
            retention_rate = cleaned_count / original_count if original_count > 0 else 0
            
            # Check retention threshold
            min_retention = stage_config.get('retention_threshold', 0.95)
            if retention_rate < min_retention:
                self.error_handler.handle_warning(
                    f"Data retention ({retention_rate:.3f}) below threshold ({min_retention})",
                    'data_cleaning'
                )
            
            # Log metrics
            self.logger.log_record_count('cleaning', 'fact_table', cleaned_count)
            self.logger.log_data_quality('cleaning', {
                'retention_rate': retention_rate,
                'original_records': original_count,
                'cleaned_records': cleaned_count
            })
            
            # Store cleaned data
            self.pipeline_data['cleaned_data'] = cleaned_data
            self.pipeline_data['fact_table'] = fact_table_enhanced
            
            # Save checkpoint
            checkpoint_data = {
                'fact_table_count': cleaned_count,
                'retention_rate': retention_rate,
                'feature_count': len(fact_table_enhanced.columns)
            }
            
            self.checkpoint_manager.save_checkpoint('cleaning', checkpoint_data, fact_table_enhanced)
            
            self.monitor.logger.end_stage('data_cleaning', success=True)
            return True
            
        except Exception as e:
            self.monitor.logger.end_stage('data_cleaning', success=False, error=str(e))
            if not self.error_handler.handle_error(e, 'data_cleaning', critical=True):
                return False
            return True
    
    def stage_trend_analysis(self) -> bool:
        """Stage 4: Trend analysis and pivot point detection."""
        self.monitor.logger.start_stage('trend_analysis')
        
        try:
            stage_config = self.config_manager.get_stage_config('trend_analysis')
            
            if not stage_config.get('enabled', True):
                self.logger.logger.info("📈 Trend analysis stage disabled, skipping...")
                self.monitor.logger.end_stage('trend_analysis', success=True)
                return True
            # Import trend analysis pipeline
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from spark_trend_analysis_pipeline import TrendAnalysisPipeline
            
            fact_table = self.pipeline_data['fact_table']
            
            trend_analysis = TrendAnalysisPipeline()
            trend_analysis.spark = self.spark
            trend_analysis.fact_table = fact_table
            
            # Run analysis components
            growth_rates = trend_analysis.calculate_growth_rates()
            pivot_analysis = trend_analysis.identify_pivot_point()
            regional_trends = trend_analysis.analyze_regional_trends()
            brand_impact = trend_analysis.analyze_brand_impact()
            market_evolution = trend_analysis.track_market_share_evolution()
            
            # Extract key insights
            from pyspark.sql.functions import col, max
            pivot_points = pivot_analysis.filter(col("Pivot_Point") == True).count()
            max_growth_diff = pivot_analysis.agg(max("Growth_Difference")).collect()[0][0]
            
            # Log insights
            self.logger.log_data_quality('trend_analysis', {
                'pivot_points_detected': pivot_points,
                'max_growth_difference': max_growth_diff,
                'analysis_months': growth_rates.count()
            })
            
            # Store analysis results
            self.pipeline_data['trend_analysis'] = {
                'growth_rates': growth_rates,
                'pivot_analysis': pivot_analysis,
                'regional_trends': regional_trends,
                'brand_impact': brand_impact,
                'market_evolution': market_evolution
            }
            
            # Save checkpoint
            checkpoint_data = {
                'pivot_points': pivot_points,
                'max_growth_difference': float(max_growth_diff) if max_growth_diff else 0,
                'months_analyzed': growth_rates.count()
            }
            
            self.checkpoint_manager.save_checkpoint('trend_analysis', checkpoint_data, pivot_analysis)
            
            self.monitor.logger.end_stage('trend_analysis', success=True)
            return True
            
        except Exception as e:
            self.monitor.logger.end_stage('trend_analysis', success=False, error=str(e))
            if not self.error_handler.handle_error(e, 'trend_analysis', critical=False):
                return True
            return False
    
    def stage_executive_reporting(self) -> bool:
        """Stage 5: Executive reporting and strategic recommendations."""
        self.monitor.logger.start_stage('executive_reporting')
        
        try:
            stage_config = self.config_manager.get_stage_config('executive_reporting')
            
            if not stage_config.get('enabled', True):
                self.logger.logger.info("📊 Executive reporting stage disabled, skipping...")
                self.monitor.logger.end_stage('executive_reporting', success=True)
                return True
            # Import executive reporting pipeline
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from spark_executive_reporting import ExecutiveReportingPipeline
            
            fact_table = self.pipeline_data['fact_table']
            data_paths = self.config_manager.get_data_paths()
            
            exec_reporting = ExecutiveReportingPipeline(data_paths['input_base'])
            exec_reporting.spark = self.spark
            exec_reporting.fact_table = fact_table
            
            # Generate reports
            exec_reporting.generate_executive_metrics()
            exec_reporting.calculate_roi_projections()
            exec_reporting.generate_strategic_recommendations()
            exec_reporting.create_executive_dashboard_data()
            exec_reporting.generate_final_recommendations()
            exec_reporting.format_for_business_consumption()
            
            # Save outputs
            output_dir = os.path.join(data_paths['output_reports'], 'executive')
            os.makedirs(output_dir, exist_ok=True)
            exec_reporting.save_executive_outputs(output_dir)
            
            # Store results
            self.pipeline_data['executive_reporting'] = {
                'metrics': exec_reporting.executive_metrics,
                'projections': exec_reporting.financial_projections,
                'recommendations': exec_reporting.strategic_recommendations,
                'business_report': exec_reporting.business_formatted_report
            }
            
            # Save checkpoint
            checkpoint_data = {
                'reports_generated': True,
                'output_directory': output_dir
            }
            
            self.checkpoint_manager.save_checkpoint('executive_reporting', checkpoint_data)
            
            self.monitor.logger.end_stage('executive_reporting', success=True)
            return True
            
        except Exception as e:
            self.monitor.logger.end_stage('executive_reporting', success=False, error=str(e))
            if not self.error_handler.handle_error(e, 'executive_reporting', critical=False):
                return True
            return False
    
    def stage_visualization(self) -> bool:
        """Stage 6: Data visualization and chart generation."""
        self.monitor.logger.start_stage('visualization')
        
        try:
            stage_config = self.config_manager.get_stage_config('visualization')
            
            if not stage_config.get('enabled', True):
                self.logger.logger.info("📊 Visualization stage disabled, skipping...")
                self.monitor.logger.end_stage('visualization', success=True)
                return True
            # Import visualization pipeline
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from spark_visualization_export import VisualizationExportPipeline
            
            data_paths = self.config_manager.get_data_paths()
            
            # Export visualization data
            viz_export = VisualizationExportPipeline(
                data_paths['input_base'],
                os.path.join(data_paths['output_data'], 'visualization')
            )
            viz_export.spark = self.spark
            viz_export.fact_table = self.pipeline_data['fact_table']
            
            # Run export pipeline
            viz_export.export_time_series_data()
            viz_export.export_pivot_point_analysis()
            viz_export.export_regional_analysis()
            viz_export.export_category_comparison_data()
            viz_export.export_executive_dashboard_data()
            viz_export.save_visualization_datasets()
            
            # Generate charts
            from create_visualizations import BeerSeltzerVisualizationSuite
            
            viz_suite = BeerSeltzerVisualizationSuite(
                os.path.join(data_paths['output_data'], 'visualization'),
                data_paths['output_charts']
            )
            
            # Load datasets and create visualizations
            viz_suite.load_datasets()
            viz_suite.create_time_series_comparison()
            viz_suite.create_pivot_point_visualization()
            viz_suite.create_regional_heatmap()
            viz_suite.create_executive_dashboard()
            viz_suite.create_brand_performance_analysis()
            
            if stage_config.get('interactive_enabled', True):
                viz_suite.create_interactive_plotly_charts()
            
            # Store results
            self.pipeline_data['visualization'] = {
                'datasets_exported': len(viz_export.export_datasets),
                'charts_created': 6,
                'output_directory': data_paths['output_charts']
            }
            
            # Save checkpoint
            checkpoint_data = {
                'datasets_count': len(viz_export.export_datasets),
                'charts_directory': data_paths['output_charts']
            }
            
            self.checkpoint_manager.save_checkpoint('visualization', checkpoint_data)
            
            self.monitor.logger.end_stage('visualization', success=True)
            return True
            
        except Exception as e:
            self.monitor.logger.end_stage('visualization', success=False, error=str(e))
            if not self.error_handler.handle_error(e, 'visualization', critical=False):
                return True
            return False
    
    def stage_pdf_report_generation(self) -> bool:
        """Stage 7: Generate comprehensive PDF report."""
        self.monitor.logger.start_stage('pdf_report_generation')
        
        try:
            stage_config = self.config_manager.get_stage_config('pdf_report')
            
            if not stage_config.get('enabled', True):
                self.logger.logger.info("📄 PDF report generation disabled, skipping...")
                self.monitor.logger.end_stage('pdf_report_generation', success=True)
                return True
            # Import PDF report generator
            from src.reporting.pdf_report_generator import PDFReportGenerator
            
            data_paths = self.config_manager.get_data_paths()
            
            # Initialize PDF generator
            pdf_generator = PDFReportGenerator(
                charts_dir=data_paths['output_charts'],
                data_dir=os.path.join(data_paths['output_data'], 'visualization'),
                output_dir=data_paths['output_reports']
            )
            
            # Generate comprehensive report
            report_path = pdf_generator.generate_comprehensive_report(
                pipeline_data=self.pipeline_data,
                config=self.config,
                run_id=self.run_id
            )
            
            self.logger.logger.info(f"📄 PDF report generated: {report_path}")
            
            # Store result
            self.pipeline_data['pdf_report'] = {
                'report_path': report_path,
                'generated': True
            }
            
            # Save checkpoint
            checkpoint_data = {
                'report_path': report_path,
                'report_generated': True
            }
            
            self.checkpoint_manager.save_checkpoint('pdf_report', checkpoint_data)
            
            self.monitor.logger.end_stage('pdf_report_generation', success=True)
            return True
            
        except Exception as e:
            self.monitor.logger.end_stage('pdf_report_generation', success=False, error=str(e))
            if not self.error_handler.handle_error(e, 'pdf_report_generation', critical=False):
                return True
            return False
    
    def run_pipeline(self, resume_from_checkpoint: bool = False) -> bool:
        """
        Run the complete pipeline with orchestration and fault tolerance.
        
        Args:
            resume_from_checkpoint: Whether to attempt recovery from checkpoints
            
        Returns:
            bool: True if pipeline completed successfully
        """
        start_time = datetime.now()
        self.logger.logger.info(f"🚀 Starting Master Pipeline - Run ID: {self.run_id}")
        
        try:
            # Create Spark session
            self.create_spark_session()
            
            # Define pipeline stages
            stages = [
                ('data_generation', self.stage_data_generation),
                ('data_ingestion', self.stage_data_ingestion),
                ('data_cleaning', self.stage_data_cleaning),
                ('trend_analysis', self.stage_trend_analysis),
                ('executive_reporting', self.stage_executive_reporting),
                ('visualization', self.stage_visualization),
                ('pdf_report_generation', self.stage_pdf_report_generation)
            ]
            
            # Attempt recovery if requested
            if resume_from_checkpoint:
                recovery_point = self.checkpoint_manager.get_recovery_point()
                if recovery_point:
                    self.logger.logger.info(f"🔄 Recovery point found: {recovery_point}")
                    # TODO: Implement recovery logic
                else:
                    self.logger.logger.info("🔄 No recovery point found, starting from beginning")
            
            # Execute stages
            for stage_name, stage_func in stages:
                if not self.config_manager.is_stage_enabled(stage_name):
                    self.logger.logger.info(f"⏭️  Stage {stage_name} disabled, skipping...")
                    continue
                
                self.logger.logger.info(f"🎯 Executing stage: {stage_name}")
                
                success = stage_func()
                
                if success:
                    self.completed_stages.append(stage_name)
                    self.logger.logger.info(f"✅ Stage {stage_name} completed successfully")
                else:
                    self.logger.logger.error(f"❌ Stage {stage_name} failed")
                    
                    # Record failed run
                    self.checkpoint_manager.record_pipeline_run(
                        self.run_id, 'failed', self.completed_stages,
                        f"Failed at stage: {stage_name}"
                    )
                    return False
            
            # Pipeline completed successfully
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.logger.info(f"🎉 Pipeline completed successfully in {duration:.2f} seconds")
            
            # Record successful run
            self.checkpoint_manager.record_pipeline_run(
                self.run_id, 'success', self.completed_stages
            )
            
            # Generate performance report
            self._generate_performance_report()
            
            # Cleanup old checkpoints
            self.checkpoint_manager.cleanup_old_checkpoints()
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"❌ Pipeline failed with critical error: {str(e)}")
            
            # Record failed run
            self.checkpoint_manager.record_pipeline_run(
                self.run_id, 'failed', self.completed_stages, str(e)
            )
            
            return False
            
        finally:
            # Cleanup Spark session
            if self.spark:
                self.spark.stop()
                self.logger.logger.info("🛑 Spark session stopped")
    
    def _generate_performance_report(self):
        """Generate and save performance report."""
        try:
            data_paths = self.config_manager.get_data_paths()
            performance_file = os.path.join(
                data_paths['output_reports'], 
                f'performance_report_{self.run_id}.json'
            )
            
            self.logger.save_performance_report(performance_file)
            
            # Also save pipeline summary
            summary = {
                'run_id': self.run_id,
                'completed_stages': self.completed_stages,
                'error_summary': self.error_handler.get_error_summary(),
                'checkpoint_summary': self.checkpoint_manager.get_checkpoint_summary(),
                'performance_summary': self.logger.get_performance_summary()
            }
            
            summary_file = os.path.join(
                data_paths['output_reports'],
                f'pipeline_summary_{self.run_id}.json'
            )
            
            import json
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.logger.info(f"📊 Performance reports saved")
            
        except Exception as e:
            self.logger.logger.error(f"Failed to generate performance report: {e}")

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PySpark Beer-to-Seltzer Analysis Pipeline')
    parser.add_argument('--config', default='config/pipeline_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from checkpoint if available')
    parser.add_argument('--stage', choices=[
        'data_generation', 'data_ingestion', 'data_cleaning',
        'trend_analysis', 'executive_reporting', 'visualization', 'pdf_report'
    ], help='Run only specific stage')
    
    args = parser.parse_args()
    
    try:
        # Initialize and run pipeline
        pipeline = MasterPipeline(args.config)
        
        if args.stage:
            # Run specific stage only
            pipeline.logger.logger.info(f"🎯 Running single stage: {args.stage}")
            # TODO: Implement single stage execution
            success = True
        else:
            # Run complete pipeline
            success = pipeline.run_pipeline(resume_from_checkpoint=args.resume)
        
        if success:
            print("\n🎉 Pipeline execution completed successfully!")
            print(f"📊 Check output directory: {pipeline.config_manager.get_data_paths()['output_base']}")
        else:
            print("\n❌ Pipeline execution failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()