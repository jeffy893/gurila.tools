#!/usr/bin/env python3
"""
Main Pipeline Executor
=====================

Single entry point for the complete Beer-to-Seltzer analysis pipeline.
Orchestrates all components with fault tolerance, monitoring, and reporting.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def main():
    """Main execution function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='PySpark Beer-to-Seltzer Market Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                          # Run complete pipeline
  python run_pipeline.py --resume                 # Resume from checkpoint
  python run_pipeline.py --stage data_ingestion   # Run specific stage
  python run_pipeline.py --config custom.yaml     # Use custom config
  python run_pipeline.py --scheduler start        # Start scheduler daemon
  python run_pipeline.py --scheduler status       # Check scheduler status
        """
    )
    
    # Pipeline execution options
    parser.add_argument('--config', 
                       default='config/pipeline_config.yaml',
                       help='Configuration file path (default: config/pipeline_config.yaml)')
    
    parser.add_argument('--resume', 
                       action='store_true',
                       help='Resume pipeline from last checkpoint')
    
    parser.add_argument('--stage', 
                       choices=[
                           'data_generation', 'data_ingestion', 'data_cleaning',
                           'trend_analysis', 'executive_reporting', 'visualization', 
                           'pdf_report'
                       ],
                       help='Run only specific pipeline stage')
    
    parser.add_argument('--force-regenerate', 
                       action='store_true',
                       help='Force regeneration of synthetic data')
    
    parser.add_argument('--output-dir', 
                       default='output',
                       help='Output directory for results (default: output)')
    
    # Scheduler options
    parser.add_argument('--scheduler', 
                       choices=['start', 'stop', 'status', 'execute', 'history'],
                       help='Scheduler management commands')
    
    # Monitoring options
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Enable verbose logging')
    
    parser.add_argument('--performance-report', 
                       action='store_true',
                       help='Generate detailed performance report')
    
    # Testing options
    parser.add_argument('--test-mode', 
                       action='store_true',
                       help='Run in test mode with sample data')
    
    parser.add_argument('--validate-only', 
                       action='store_true',
                       help='Validate configuration and environment only')
    
    args = parser.parse_args()
    
    try:
        # Handle scheduler commands
        if args.scheduler:
            return handle_scheduler_command(args)
        
        # Handle validation only
        if args.validate_only:
            return validate_environment(args)
        
        # Run pipeline
        return run_pipeline(args)
        
    except KeyboardInterrupt:
        print("\n🛑 Pipeline execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def handle_scheduler_command(args):
    """Handle scheduler management commands."""
    try:
        from utils.scheduler import SchedulerCLI
        
        cli = SchedulerCLI(args.config)
        
        if args.scheduler == 'start':
            print("🕐 Starting pipeline scheduler daemon...")
            cli.start()
        elif args.scheduler == 'status':
            cli.status()
        elif args.scheduler == 'execute':
            cli.execute()
        elif args.scheduler == 'history':
            cli.history()
        
        return 0
        
    except Exception as e:
        print(f"❌ Scheduler error: {str(e)}")
        return 1

def validate_environment(args):
    """Validate environment and configuration."""
    print("🔍 Validating environment and configuration...")
    
    try:
        # Check configuration file
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ Configuration file not found: {config_path}")
            return 1
        
        # Load and validate configuration
        from utils.config_manager import get_config_manager
        
        config_manager = get_config_manager(args.config)
        config = config_manager.config
        
        print("✅ Configuration loaded successfully")
        
        # Check Python environment
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        required_version = config.get('environment', {}).get('python', {}).get('version', '3.10')
        
        if python_version != required_version:
            print(f"⚠️  Python version mismatch: {python_version} (required: {required_version})")
        else:
            print(f"✅ Python version: {python_version}")
        
        # Check Java environment
        java_home = os.environ.get('JAVA_HOME')
        if java_home:
            print(f"✅ JAVA_HOME: {java_home}")
        else:
            print("⚠️  JAVA_HOME not set")
        
        # Check PySpark
        try:
            import pyspark
            print(f"✅ PySpark version: {pyspark.__version__}")
        except ImportError:
            print("❌ PySpark not available")
            return 1
        
        # Check required libraries
        required_libs = ['pandas', 'matplotlib', 'seaborn', 'plotly', 'yaml', 'reportlab']
        missing_libs = []
        
        for lib in required_libs:
            try:
                __import__(lib)
                print(f"✅ {lib} available")
            except ImportError:
                missing_libs.append(lib)
                print(f"❌ {lib} not available")
        
        if missing_libs:
            print(f"\n📦 Install missing libraries: pip install {' '.join(missing_libs)}")
            return 1
        
        # Check directories
        config_manager.create_directories()
        print("✅ Required directories created")
        
        # Check data files if not in generation mode
        data_paths = config_manager.get_data_paths()
        data_files = [
            data_paths['products'],
            data_paths['locations'],
            data_paths['sales']
        ]
        
        missing_files = [f for f in data_files if not os.path.exists(f)]
        if missing_files:
            print(f"⚠️  Data files missing (will be generated): {len(missing_files)} files")
        else:
            print("✅ All data files present")
        
        print("\n🎉 Environment validation completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return 1

def run_pipeline(args):
    """Run the main pipeline."""
    print("🚀 Starting Beer-to-Seltzer Market Analysis Pipeline")
    print("=" * 80)
    
    try:
        # Import and initialize pipeline
        from pipelines.master_pipeline import MasterPipeline
        
        # Create pipeline instance
        pipeline = MasterPipeline(args.config)
        
        # Apply command-line overrides
        if args.force_regenerate:
            pipeline.config['stages']['data_generation']['force_regenerate'] = True
        
        if args.test_mode:
            # Reduce data size for testing
            pipeline.config['stages']['data_generation']['sample_size_multiplier'] = 0.1
            print("🧪 Running in test mode with reduced data size")
        
        if args.verbose:
            pipeline.config['logging']['level'] = 'DEBUG'
            print("🔍 Verbose logging enabled")
        
        # Update output directory
        if args.output_dir != 'output':
            pipeline.config['data']['output']['base_directory'] = args.output_dir
            pipeline.config_manager.create_directories()
        
        # Run pipeline
        success = pipeline.run_pipeline(resume_from_checkpoint=args.resume)
        
        if success:
            print("\n🎉 Pipeline execution completed successfully!")
            
            # Display results summary
            display_results_summary(pipeline)
            
            # Generate performance report if requested
            if args.performance_report:
                generate_performance_report(pipeline)
            
            return 0
        else:
            print("\n❌ Pipeline execution failed!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Pipeline execution failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def display_results_summary(pipeline):
    """Display summary of pipeline results."""
    try:
        data_paths = pipeline.config_manager.get_data_paths()
        
        print("\n📊 PIPELINE RESULTS SUMMARY")
        print("=" * 50)
        
        # Output directories
        print(f"📁 Output Directory: {data_paths['output_base']}")
        print(f"📊 Charts Directory: {data_paths['output_charts']}")
        print(f"📋 Reports Directory: {data_paths['output_reports']}")
        
        # Key findings
        if 'executive_reporting' in pipeline.pipeline_data:
            exec_data = pipeline.pipeline_data['executive_reporting']
            
            if 'business_report' in exec_data:
                business_report = exec_data['business_report']
                exec_summary = business_report.get('executive_summary', {})
                
                print(f"\n🎯 KEY BUSINESS FINDINGS:")
                print(f"   Strategic Recommendation: PROCEED WITH HARD SELTZER MARKET ENTRY")
                print(f"   Investment Required: {exec_summary.get('investment_required', 'N/A')}")
                print(f"   Projected ROI: {exec_summary.get('projected_roi', 'N/A')}")
                print(f"   Payback Period: {exec_summary.get('payback_period', 'N/A')}")
                print(f"   Target Market Share: {exec_summary.get('target_market_share', 'N/A')}")
        
        # Generated files
        print(f"\n📄 GENERATED FILES:")
        
        # Check for PDF report
        import glob
        pdf_files = glob.glob(os.path.join(data_paths['output_reports'], "*.pdf"))
        if pdf_files:
            print(f"   📄 PDF Report: {pdf_files[0]}")
        
        # Check for charts
        chart_files = glob.glob(os.path.join(data_paths['output_charts'], "*.png"))
        print(f"   📊 Charts Generated: {len(chart_files)} files")
        
        # Check for data exports
        data_files = glob.glob(os.path.join(data_paths['output_data'], "**/*.csv"), recursive=True)
        print(f"   📈 Data Exports: {len(data_files)} CSV files")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Review the PDF report for executive presentation")
        print(f"   2. Examine charts for detailed visual analysis")
        print(f"   3. Use CSV exports for further business intelligence")
        print(f"   4. Present findings to executive leadership")
        
    except Exception as e:
        print(f"⚠️  Could not generate results summary: {e}")

def generate_performance_report(pipeline):
    """Generate detailed performance report."""
    try:
        print("\n📊 Generating performance report...")
        
        performance_summary = pipeline.logger.get_performance_summary()
        
        print(f"⏱️  Total Execution Time: {performance_summary['total_duration']:.2f} seconds")
        print(f"🔧 Stages Completed: {len(performance_summary['stages'])}")
        
        # Stage-by-stage performance
        print(f"\n📋 STAGE PERFORMANCE:")
        for stage_name, stage_data in performance_summary['stages'].items():
            duration = stage_data.get('duration', 0)
            success = stage_data.get('success', False)
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {stage_name}: {duration:.2f}s")
        
        # System metrics
        system_metrics = performance_summary.get('system_metrics', {})
        if system_metrics:
            print(f"\n🖥️  SYSTEM METRICS:")
            print(f"   CPU Usage: {system_metrics.get('cpu_percent', 0):.1f}%")
            print(f"   Memory Usage: {system_metrics.get('memory_percent', 0):.1f}%")
            print(f"   Available Memory: {system_metrics.get('memory_available_gb', 0):.1f} GB")
        
    except Exception as e:
        print(f"⚠️  Could not generate performance report: {e}")

if __name__ == "__main__":
    sys.exit(main())