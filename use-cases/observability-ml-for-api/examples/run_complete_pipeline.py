#!/usr/bin/env python3
"""
Complete ML Pipeline Orchestrator
Runs the entire ML for API Service pipeline from data generation to reporting.
"""

import os
import sys
import yaml
import argparse
import logging
from datetime import datetime
import subprocess

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MLPipelineOrchestrator:
    def __init__(self, config_path="config/model_config.yaml"):
        """Initialize the pipeline orchestrator"""
        self.config_path = config_path
        self.config = self.load_config()
        self.start_time = datetime.now()
        
        # Create necessary directories
        self.create_directories()
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def create_directories(self):
        """Create necessary directories for the pipeline"""
        directories = [
            'data',
            'models',
            'models/rcf_model',
            'reports',
            'reports/images',
            'logs'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def run_data_generation(self):
        """Step 1: Generate synthetic data"""
        logger.info("=" * 50)
        logger.info("STEP 1: Generating Synthetic Data")
        logger.info("=" * 50)
        
        try:
            # Import and run data generator
            from src.core.data_generator import APILogGenerator
            
            config = self.config['data_generation']
            generator = APILogGenerator(
                duration_hours=config['duration_hours'],
                requests_per_second=config['requests_per_second']
            )
            
            # Generate dataset
            df = generator.generate_dataset()
            
            # Save dataset
            filepath = generator.save_dataset(df, config['output_file'].split('/')[-1])
            
            logger.info(f"✅ Data generation completed successfully")
            logger.info(f"Generated {len(df)} records")
            logger.info(f"Anomaly rate: {df['is_anomaly'].mean():.2%}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Data generation failed: {e}")
            return False
    
    def run_model_training(self):
        """Step 2: Train ML model"""
        logger.info("=" * 50)
        logger.info("STEP 2: Training ML Model")
        logger.info("=" * 50)
        
        try:
            # Import and run model training
            from src.core.sagemaker_model import SageMakerRCFModel
            
            # Check if data exists
            data_path = self.config['data_generation']['output_file']
            if not os.path.exists(data_path):
                logger.error(f"Data file not found: {data_path}")
                return False
            
            # Initialize model
            rcf_model = SageMakerRCFModel()
            
            # Load and preprocess data
            import pandas as pd
            df = pd.read_csv(data_path)
            X_scaled, features, feature_names = rcf_model.preprocess_data(df)
            
            # Split data
            split_ratio = self.config['model_training']['train_test_split']
            split_idx = int(split_ratio * len(X_scaled))
            X_train = X_scaled[:split_idx]
            X_test = X_scaled[split_idx:]
            
            logger.info(f"Training set size: {X_train.shape}")
            logger.info(f"Test set size: {X_test.shape}")
            
            # Train model (using local mode for demo)
            if self.config.get('development', {}).get('local_mode', True):
                logger.info("Using local training mode")
                model, anomaly_scores, predictions = rcf_model.local_rcf_training(X_train, X_test)
                
                # Save results
                test_features = features.iloc[split_idx:].copy()
                test_features['anomaly_score'] = anomaly_scores
                test_features['predicted_anomaly'] = (predictions == -1)
                
                # Save results and model artifacts
                test_features.to_csv('data/anomaly_results.csv', index=False)
                rcf_model.save_model_artifacts(model, rcf_model.scaler, feature_names)
                
                logger.info(f"✅ Model training completed successfully")
                logger.info(f"Predicted anomalies: {test_features['predicted_anomaly'].sum()}")
                logger.info(f"Anomaly rate: {test_features['predicted_anomaly'].mean():.2%}")
                
            else:
                # Use actual SageMaker training
                logger.info("Using SageMaker training mode")
                hyperparameters = self.config['model_training']['hyperparameters']
                hyperparameters['feature_dim'] = X_train.shape[1]
                
                estimator = rcf_model.train_model(X_train, hyperparameters)
                
                # Deploy endpoint if configured
                if not self.config.get('development', {}).get('skip_sagemaker_deployment', False):
                    predictor = rcf_model.deploy_model()
                    anomaly_scores = rcf_model.predict_anomalies(X_test)
                    
                    # Clean up endpoint to avoid charges
                    rcf_model.cleanup_endpoint()
                
                logger.info(f"✅ SageMaker model training completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return False
    
    def run_report_generation(self):
        """Step 3: Generate health reports"""
        logger.info("=" * 50)
        logger.info("STEP 3: Generating Health Reports")
        logger.info("=" * 50)
        
        try:
            # Import and run report generator
            from src.core.reporting_engine import HealthReportGenerator
            
            # Check if results exist
            results_path = "data/anomaly_results.csv"
            if not os.path.exists(results_path):
                logger.error(f"Results file not found: {results_path}")
                return False
            
            # Initialize report generator
            generator = HealthReportGenerator(results_path)
            
            # Generate reports
            output_formats = self.config['reporting']['output_formats']
            
            reports_generated = []
            
            if 'html' in output_formats:
                html_path = generator.generate_html_report()
                reports_generated.append(html_path)
                logger.info(f"HTML report generated: {html_path}")
            
            if 'pdf' in output_formats:
                try:
                    pdf_path = generator.generate_pdf_report()
                    reports_generated.append(pdf_path)
                    logger.info(f"PDF report generated: {pdf_path}")
                except Exception as e:
                    logger.warning(f"PDF generation failed: {e}")
            
            # Print summary
            metrics = generator.calculate_health_metrics()
            logger.info(f"✅ Report generation completed successfully")
            logger.info(f"Health Score: {metrics['health_score']}/100")
            logger.info(f"Reports generated: {len(reports_generated)}")
            
            return True, reports_generated
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            return False, []
    
    def run_complete_pipeline(self, skip_data_generation=False, skip_training=False):
        """Run the complete ML pipeline"""
        logger.info("🚀 Starting ML for API Service Pipeline")
        logger.info(f"Start time: {self.start_time}")
        logger.info(f"Configuration: {self.config_path}")
        
        success_steps = 0
        total_steps = 3
        
        # Step 1: Data Generation
        if not skip_data_generation:
            if self.run_data_generation():
                success_steps += 1
            else:
                logger.error("Pipeline failed at data generation step")
                return False
        else:
            logger.info("Skipping data generation step")
            success_steps += 1
        
        # Step 2: Model Training
        if not skip_training:
            if self.run_model_training():
                success_steps += 1
            else:
                logger.error("Pipeline failed at model training step")
                return False
        else:
            logger.info("Skipping model training step")
            success_steps += 1
        
        # Step 3: Report Generation
        success, reports = self.run_report_generation()
        if success:
            success_steps += 1
        else:
            logger.error("Pipeline failed at report generation step")
            return False
        
        # Pipeline completion summary
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("=" * 60)
        logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Total duration: {duration}")
        logger.info(f"Steps completed: {success_steps}/{total_steps}")
        logger.info(f"Reports generated: {len(reports)}")
        
        for report in reports:
            logger.info(f"  📄 {report}")
        
        logger.info("=" * 60)
        
        return True
    
    def validate_environment(self):
        """Validate that all required dependencies are available"""
        logger.info("Validating environment...")
        
        required_packages = [
            'pandas', 'numpy', 'sklearn', 'matplotlib', 
            'seaborn', 'boto3', 'sagemaker', 'faker', 'reportlab'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing required packages: {missing_packages}")
            logger.error("Please install missing packages using: pip install -r requirements.txt")
            return False
        
        logger.info("✅ Environment validation passed")
        return True

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='ML for API Service Pipeline')
    parser.add_argument('--config', default='config/model_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--skip-data', action='store_true',
                       help='Skip data generation step')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training step')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate environment')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = MLPipelineOrchestrator(args.config)
    
    # Validate environment
    if not orchestrator.validate_environment():
        sys.exit(1)
    
    if args.validate_only:
        logger.info("Environment validation completed successfully")
        return
    
    # Run pipeline
    success = orchestrator.run_complete_pipeline(
        skip_data_generation=args.skip_data,
        skip_training=args.skip_training
    )
    
    if success:
        logger.info("🎉 Pipeline execution completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Pipeline execution failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()