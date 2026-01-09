#!/usr/bin/env python3
"""
Quick Demo Script for ML for API Service
Runs a simplified version of the pipeline for demonstration purposes.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_quick_demo():
    """Run a quick demonstration of the ML pipeline"""
    print("🚀 ML for API Service - Quick Demo")
    print("=" * 50)
    
    # Step 1: Generate small sample dataset
    print("📊 Generating sample data...")
    
    from src.core.data_generator import APILogGenerator
    
    # Generate 2 hours of data for demo
    generator = APILogGenerator(duration_hours=2, requests_per_second=2)
    df = generator.generate_dataset()
    
    print(f"✅ Generated {len(df)} records")
    print(f"   Anomaly rate: {df['is_anomaly'].mean():.2%}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Step 2: Train simple model
    print("\n🤖 Training anomaly detection model...")
    
    from src.core.sagemaker_model import SageMakerRCFModel
    
    rcf_model = SageMakerRCFModel()
    X_scaled, features, feature_names = rcf_model.preprocess_data(df)
    
    # Use 70% for training, 30% for testing
    split_idx = int(0.7 * len(X_scaled))
    X_train = X_scaled[:split_idx]
    X_test = X_scaled[split_idx:]
    
    # Train local model
    model, anomaly_scores, predictions = rcf_model.local_rcf_training(X_train, X_test)
    
    # Prepare results
    test_features = features.iloc[split_idx:].copy()
    test_features['anomaly_score'] = anomaly_scores
    test_features['predicted_anomaly'] = (predictions == -1)
    
    print(f"✅ Model trained successfully")
    print(f"   Test samples: {len(test_features)}")
    print(f"   Predicted anomalies: {test_features['predicted_anomaly'].sum()}")
    print(f"   Prediction rate: {test_features['predicted_anomaly'].mean():.2%}")
    
    # Step 3: Generate simple visualization
    print("\n📈 Creating visualization...")
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # CPU usage over time
    axes[0].plot(test_features['timestamp'], test_features['cpu_usage_percent'], 
                color='blue', alpha=0.7, linewidth=1, label='CPU Usage')
    
    # Mark anomalies
    anomalies = test_features[test_features['predicted_anomaly']]
    if len(anomalies) > 0:
        axes[0].scatter(anomalies['timestamp'], anomalies['cpu_usage_percent'], 
                       color='red', s=50, alpha=0.8, zorder=5, label='Detected Anomalies')
    
    axes[0].set_title('CPU Usage with Anomaly Detection')
    axes[0].set_ylabel('CPU Usage (%)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Anomaly scores
    axes[1].plot(test_features['timestamp'], test_features['anomaly_score'], 
                color='orange', alpha=0.7, linewidth=1)
    axes[1].set_title('Anomaly Scores Over Time')
    axes[1].set_ylabel('Anomaly Score')
    axes[1].set_xlabel('Time')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs('reports/demo', exist_ok=True)
    plot_path = 'reports/demo/demo_visualization.png'
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Visualization saved to: {plot_path}")
    
    # Step 4: Generate simple report
    print("\n📄 Generating summary report...")
    
    # Calculate basic metrics
    total_requests = len(test_features)
    anomaly_count = test_features['predicted_anomaly'].sum()
    anomaly_rate = anomaly_count / total_requests
    avg_cpu = test_features['cpu_usage_percent'].mean()
    avg_memory = test_features['memory_usage_mb'].mean()
    avg_response_time = test_features['response_time_ms'].mean()
    
    # Calculate health score
    health_score = max(0, 100 - (anomaly_rate * 1000) - max(0, (avg_cpu - 70) * 0.5))
    
    # Create simple HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Health Demo Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e8f4f8; border-radius: 5px; }}
            .health-score {{ font-size: 24px; font-weight: bold; color: {'green' if health_score > 80 else 'orange' if health_score > 60 else 'red'}; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>API Health Demo Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <h2>Summary</h2>
        <div class="health-score">Health Score: {health_score:.1f}/100</div>
        
        <div class="metric"><strong>Total Requests:</strong> {total_requests}</div>
        <div class="metric"><strong>Anomalies:</strong> {int(anomaly_count)}</div>
        <div class="metric"><strong>Anomaly Rate:</strong> {anomaly_rate:.2%}</div>
        <div class="metric"><strong>Avg CPU:</strong> {avg_cpu:.1f}%</div>
        <div class="metric"><strong>Avg Memory:</strong> {avg_memory:.1f} MB</div>
        <div class="metric"><strong>Avg Response:</strong> {avg_response_time:.1f} ms</div>
        
        <h2>Visualization</h2>
        <img src="demo_visualization.png" alt="Demo Visualization" style="max-width: 100%;">
        
        <h2>Key Findings</h2>
        <ul>
    """
    
    if anomaly_count > 0:
        html_content += f"<li>Detected {int(anomaly_count)} anomalies in the test period</li>"
    else:
        html_content += "<li>No significant anomalies detected</li>"
    
    if avg_cpu > 70:
        html_content += f"<li>CPU usage is elevated at {avg_cpu:.1f}%</li>"
    
    if avg_response_time > 200:
        html_content += f"<li>Response times are slower than optimal at {avg_response_time:.1f}ms</li>"
    
    html_content += """
        </ul>
        
        <p><em>This is a demonstration report generated by the ML for API Service system.</em></p>
    </body>
    </html>
    """
    
    report_path = 'reports/demo/demo_report.html'
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Demo report saved to: {report_path}")
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"📊 Analyzed {total_requests} API requests")
    print(f"🔍 Detected {int(anomaly_count)} anomalies ({anomaly_rate:.2%} rate)")
    print(f"💚 System health score: {health_score:.1f}/100")
    print(f"📈 Visualization: {plot_path}")
    print(f"📄 Report: {report_path}")
    print("\nNext steps:")
    print("1. Run 'python run_complete_pipeline.py' for full pipeline")
    print("2. Check the AWS architecture guide in aws_architecture.md")
    print("3. Customize configuration in config/model_config.yaml")
    print("=" * 50)

def main():
    """Main demo execution"""
    try:
        # Check if required modules are available
        required_files = [
            'src/core/data_generator.py',
            'src/core/sagemaker_model.py'
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Required file not found: {file}")
                print("Please ensure all project files are in the current directory")
                return
        
        # Run the demo
        run_quick_demo()
        
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Please check the error details and try again")

if __name__ == "__main__":
    main()