#!/usr/bin/env python3
"""
Test Script for ML for API Service Pipeline
Validates that all components work correctly with minimal data.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_generation():
    """Test synthetic data generation"""
    print("Testing data generation...")
    
    try:
        from src.core.data_generator import APILogGenerator
        
        # Generate small dataset for testing
        generator = APILogGenerator(duration_hours=0.1, requests_per_second=2)  # 6 minutes, 2 req/sec
        df = generator.generate_dataset()
        
        # Basic validation
        assert len(df) > 0, "No data generated"
        assert 'timestamp' in df.columns, "Missing timestamp column"
        assert 'cpu_usage_percent' in df.columns, "Missing CPU usage column"
        assert 'is_anomaly' in df.columns, "Missing anomaly flag column"
        
        print(f"✅ Data generation test passed ({len(df)} records)")
        return True
        
    except Exception as e:
        print(f"❌ Data generation test failed: {e}")
        return False

def test_model_training():
    """Test model training and inference"""
    print("Testing model training...")
    
    try:
        from src.core.sagemaker_model import SageMakerRCFModel
        import pandas as pd
        import numpy as np
        
        # Create minimal test data
        test_data = {
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1min'),
            'cpu_usage_percent': np.random.normal(50, 10, 100),
            'memory_usage_mb': np.random.normal(800, 100, 100),
            'pod_restart_count': np.random.choice([0, 1], 100, p=[0.9, 0.1]),
            'source_ip': ['10.0.1.100'] * 100,
            'is_approved_source': [True] * 100,
            'http_method': ['GET'] * 100,
            'endpoint': ['/api/v1/test'] * 100,
            'user_agent': ['test-agent'] * 100,
            'sql_execution_time_ms': np.random.lognormal(2, 1, 100),
            'stack_trace_depth': np.random.poisson(8, 100) + 1,
            'db_connection_pool_active': np.random.randint(5, 20, 100),
            'response_time_ms': np.random.lognormal(4, 0.5, 100),
            'status_code': [200] * 100
        }
        
        df = pd.DataFrame(test_data)
        
        # Initialize model
        rcf_model = SageMakerRCFModel()
        
        # Preprocess data
        X_scaled, features, feature_names = rcf_model.preprocess_data(df)
        
        # Split data
        split_idx = int(0.7 * len(X_scaled))
        X_train = X_scaled[:split_idx]
        X_test = X_scaled[split_idx:]
        
        # Train model (local mode)
        model, anomaly_scores, predictions = rcf_model.local_rcf_training(X_train, X_test)
        
        # Basic validation
        assert model is not None, "Model training failed"
        assert len(anomaly_scores) == len(X_test), "Anomaly scores length mismatch"
        assert len(predictions) == len(X_test), "Predictions length mismatch"
        
        print(f"✅ Model training test passed ({len(X_test)} predictions)")
        return True
        
    except Exception as e:
        print(f"❌ Model training test failed: {e}")
        return False

def test_report_generation():
    """Test report generation"""
    print("Testing report generation...")
    
    try:
        import pandas as pd
        import numpy as np
        from src.core.reporting_engine import HealthReportGenerator
        
        # Create minimal test results
        test_results = {
            'timestamp': pd.date_range('2024-01-01', periods=50, freq='1min'),
            'cpu_usage_percent': np.random.normal(60, 15, 50),
            'memory_usage_mb': np.random.normal(900, 150, 50),
            'pod_restart_count': np.random.choice([0, 1], 50, p=[0.95, 0.05]),
            'source_ip': ['10.0.1.100'] * 50,
            'is_approved_source': [True] * 50,
            'http_method': ['GET'] * 50,
            'endpoint': ['/api/v1/test'] * 50,
            'user_agent': ['test-agent'] * 50,
            'sql_execution_time_ms': np.random.lognormal(2.5, 1, 50),
            'stack_trace_depth': np.random.poisson(8, 50) + 1,
            'db_connection_pool_active': np.random.randint(5, 20, 50),
            'response_time_ms': np.random.lognormal(4, 0.5, 50),
            'status_code': [200] * 50,
            'anomaly_score': np.random.uniform(0, 1, 50),
            'predicted_anomaly': np.random.choice([True, False], 50, p=[0.1, 0.9])
        }
        
        df = pd.DataFrame(test_results)
        
        # Save test results to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            # Initialize report generator
            generator = HealthReportGenerator(temp_file)
            
            # Test metrics calculation
            metrics = generator.calculate_health_metrics()
            assert 'health_score' in metrics, "Missing health score"
            assert 'total_requests' in metrics, "Missing total requests"
            
            # Test visualization creation (without saving)
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            # Create temporary directory for test outputs
            test_dir = tempfile.mkdtemp()
            original_dir = os.getcwd()
            
            try:
                os.chdir(test_dir)
                os.makedirs('reports/images', exist_ok=True)
                
                # Test plot creation
                plot_path = generator.create_time_series_plot()
                assert os.path.exists(plot_path), "Time series plot not created"
                
                print(f"✅ Report generation test passed")
                return True
                
            finally:
                os.chdir(original_dir)
                shutil.rmtree(test_dir, ignore_errors=True)
                
        finally:
            os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("Testing configuration...")
    
    try:
        import yaml
        
        config_path = "config/model_config.yaml"
        if not os.path.exists(config_path):
            print(f"❌ Configuration file not found: {config_path}")
            return False
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required sections
        required_sections = ['data_generation', 'model_training', 'reporting', 'aws']
        for section in required_sections:
            assert section in config, f"Missing configuration section: {section}"
        
        print("✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running ML for API Service Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Data Generation", test_data_generation),
        ("Model Training", test_model_training),
        ("Report Generation", test_report_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
        else:
            print(f"Test failed: {test_name}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The pipeline is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python demo.py' for a quick demonstration")
        print("2. Run 'python run_complete_pipeline.py' for the full pipeline")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main test execution"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()