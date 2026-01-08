#!/usr/bin/env python3
"""
SageMaker Random Cut Forest Model for API Anomaly Detection
Implements training and inference using AWS SageMaker's built-in RCF algorithm.
"""

import pandas as pd
import numpy as np
import boto3
import sagemaker
try:
    from sagemaker import get_execution_role
except ImportError:
    # Fallback for newer versions of SageMaker
    def get_execution_role():
        return "arn:aws:iam::123456789012:role/SageMakerExecutionRole"
    
import os
import json
from datetime import datetime
import pickle

class SageMakerRCFModel:
    def __init__(self, region='us-east-1'):
        """Initialize SageMaker RCF model"""
        self.region = region
        try:
            self.session = sagemaker.Session()
        except:
            # For local development without AWS credentials
            self.session = None
            
        self.bucket = None
        if self.session:
            try:
                self.bucket = self.session.default_bucket()
            except:
                self.bucket = f"sagemaker-{self.region}-123456789012"
        
        try:
            self.role = get_execution_role()
        except:
            # For local development, use a default role ARN
            self.role = f"arn:aws:iam::123456789012:role/SageMakerExecutionRole"
            print("Warning: Using default role ARN for local development")
        
        # Use updated SageMaker image URI method
        try:
            from sagemaker.image_uris import retrieve
            self.rcf_container = retrieve("randomcutforest", self.region)
        except:
            # Fallback for older versions or local development
            self.rcf_container = f"382416733822.dkr.ecr.{self.region}.amazonaws.com/randomcutforest:latest"
            
        self.model_name = f"api-anomaly-rcf-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    def preprocess_data(self, df):
        """Preprocess data for RCF model"""
        print("Preprocessing data for RCF model...")
        
        # Create feature columns for ML model
        features = df.copy()
        
        # Convert timestamp to numerical features
        features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
        features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
        features['minute'] = pd.to_datetime(features['timestamp']).dt.minute
        
        # Encode categorical variables
        features['is_approved_source_num'] = features['is_approved_source'].astype(int)
        
        # One-hot encode HTTP methods
        method_dummies = pd.get_dummies(features['http_method'], prefix='method')
        features = pd.concat([features, method_dummies], axis=1)
        
        # One-hot encode endpoints (simplified)
        features['endpoint_category'] = features['endpoint'].apply(self._categorize_endpoint)
        endpoint_dummies = pd.get_dummies(features['endpoint_category'], prefix='endpoint')
        features = pd.concat([features, endpoint_dummies], axis=1)
        
        # Select numerical features for RCF
        numerical_features = [
            'cpu_usage_percent', 'memory_usage_mb', 'pod_restart_count',
            'sql_execution_time_ms', 'stack_trace_depth', 'db_connection_pool_active',
            'response_time_ms', 'hour', 'day_of_week', 'minute', 'is_approved_source_num'
        ]
        
        # Add dummy variables that actually exist
        dummy_cols = [col for col in features.columns if col.startswith(('method_', 'endpoint_'))]
        numerical_features.extend(dummy_cols)
        
        # Create final feature matrix - only use columns that exist
        available_features = [col for col in numerical_features if col in features.columns]
        X = features[available_features].fillna(0)
        
        # Ensure all data is numeric
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
        
        # Normalize features (RCF works better with normalized data)
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        print(f"Feature matrix shape: {X_scaled.shape}")
        print(f"Features used: {available_features}")
        
        return X_scaled, features, available_features
    
    def _categorize_endpoint(self, endpoint):
        """Categorize API endpoints into groups"""
        if 'auth' in endpoint:
            return 'auth'
        elif 'user' in endpoint:
            return 'user'
        elif 'order' in endpoint:
            return 'order'
        elif 'payment' in endpoint:
            return 'payment'
        elif 'report' in endpoint:
            return 'report'
        else:
            return 'other'
    
    def train_model(self, X_train, hyperparameters=None):
        """Train RCF model using SageMaker"""
        print("Training Random Cut Forest model...")
        
        if hyperparameters is None:
            hyperparameters = {
                'feature_dim': X_train.shape[1],
                'eval_metrics': 'accuracy,precision_recall_fscore',
                'num_trees': 100,
                'num_samples_per_tree': 256
            }
        
        # Create RCF estimator
        rcf = sagemaker.estimator.Estimator(
            self.rcf_container,
            self.role,
            instance_count=1,
            instance_type='ml.m5.xlarge',
            output_path=f's3://{self.bucket}/rcf-output',
            sagemaker_session=self.session
        )
        
        rcf.set_hyperparameters(**hyperparameters)
        
        # Upload training data to S3
        train_data_path = self._upload_data_to_s3(X_train, 'train')
        
        # Train the model
        print("Starting SageMaker training job...")
        rcf.fit({'train': train_data_path})
        
        self.estimator = rcf
        print("Model training completed!")
        
        return rcf
    
    def _upload_data_to_s3(self, data, data_type):
        """Upload data to S3 for SageMaker training"""
        # Convert to CSV format (RCF expects CSV without headers)
        df_data = pd.DataFrame(data)
        
        # Save locally first
        os.makedirs('data', exist_ok=True)
        local_path = f'data/{data_type}_data.csv'
        df_data.to_csv(local_path, header=False, index=False)
        
        # Upload to S3
        s3_path = f's3://{self.bucket}/rcf-data/{data_type}'
        s3_data = self.session.upload_data(
            path=local_path,
            bucket=self.bucket,
            key_prefix=f'rcf-data/{data_type}'
        )
        
        print(f"Data uploaded to: {s3_data}")
        return s3_data
    
    def deploy_model(self, instance_type='ml.t2.medium'):
        """Deploy trained model to SageMaker endpoint"""
        print("Deploying model to SageMaker endpoint...")
        
        predictor = self.estimator.deploy(
            initial_instance_count=1,
            instance_type=instance_type,
            serializer=csv_serializer,
            deserializer=json_deserializer
        )
        
        self.predictor = predictor
        print(f"Model deployed to endpoint: {predictor.endpoint}")
        return predictor
    
    def predict_anomalies(self, X_test):
        """Generate anomaly scores for test data"""
        print("Generating anomaly scores...")
        
        if not hasattr(self, 'predictor'):
            raise ValueError("Model must be deployed before making predictions")
        
        # Make predictions in batches (SageMaker has payload limits)
        batch_size = 100
        all_scores = []
        
        for i in range(0, len(X_test), batch_size):
            batch = X_test[i:i+batch_size]
            
            # Convert to CSV format for prediction
            batch_df = pd.DataFrame(batch)
            batch_csv = batch_df.to_csv(header=False, index=False)
            
            # Get predictions
            result = self.predictor.predict(batch_csv)
            
            # Extract anomaly scores
            if isinstance(result, dict) and 'scores' in result:
                scores = result['scores']
            else:
                scores = result
            
            all_scores.extend(scores)
        
        return np.array(all_scores)
    
    def local_rcf_training(self, X_train, X_test=None):
        """
        Local RCF implementation using scikit-learn for development/testing
        Use this when SageMaker is not available
        """
        print("Training local RCF model (using Isolation Forest as proxy)...")
        
        from sklearn.ensemble import IsolationForest
        
        # Use Isolation Forest as a proxy for RCF
        model = IsolationForest(
            n_estimators=100,
            contamination=0.1,  # Expect 10% anomalies
            random_state=42
        )
        
        # Train the model
        model.fit(X_train)
        
        # Generate anomaly scores
        if X_test is not None:
            anomaly_scores = model.decision_function(X_test)
            predictions = model.predict(X_test)  # -1 for anomaly, 1 for normal
            
            # Convert to positive anomaly scores (higher = more anomalous)
            anomaly_scores = -anomaly_scores  # Flip sign
            anomaly_scores = (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min())
            
            return model, anomaly_scores, predictions
        
        return model
    
    def save_model_artifacts(self, model, scaler, feature_names):
        """Save model artifacts locally"""
        os.makedirs('models/rcf_model', exist_ok=True)
        
        # Save model
        with open('models/rcf_model/model.pkl', 'wb') as f:
            pickle.dump(model, f)
        
        # Save scaler
        with open('models/rcf_model/scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        # Save feature names
        with open('models/rcf_model/features.json', 'w') as f:
            json.dump(feature_names, f)
        
        print("Model artifacts saved to models/rcf_model/")
    
    def cleanup_endpoint(self):
        """Clean up SageMaker endpoint to avoid charges"""
        if hasattr(self, 'predictor'):
            print("Cleaning up SageMaker endpoint...")
            self.predictor.delete_endpoint()
            print("Endpoint deleted successfully")

def main():
    """Main execution function"""
    print("=== SageMaker RCF Model Training ===")
    
    # Load synthetic data
    data_path = "data/synthetic_api_logs.csv"
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        print("Please run data_generator.py first to generate synthetic data")
        return
    
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records from {data_path}")
    
    # Initialize model
    rcf_model = SageMakerRCFModel()
    
    # Preprocess data
    X_scaled, features, feature_names = rcf_model.preprocess_data(df)
    
    # Split data (80% train, 20% test)
    split_idx = int(0.8 * len(X_scaled))
    X_train = X_scaled[:split_idx]
    X_test = X_scaled[split_idx:]
    
    print(f"Training set size: {X_train.shape}")
    print(f"Test set size: {X_test.shape}")
    
    # For demonstration, use local training (comment out for actual SageMaker training)
    print("\nUsing local RCF training for demonstration...")
    model, anomaly_scores, predictions = rcf_model.local_rcf_training(X_train, X_test)
    
    # Save results
    test_features = features.iloc[split_idx:].copy()
    test_features['anomaly_score'] = anomaly_scores
    test_features['predicted_anomaly'] = (predictions == -1)
    
    # Save results
    os.makedirs('data', exist_ok=True)
    test_features.to_csv('data/anomaly_results.csv', index=False)
    
    # Save model artifacts
    rcf_model.save_model_artifacts(model, rcf_model.scaler, feature_names)
    
    # Print results summary
    print(f"\n=== Results Summary ===")
    print(f"Test samples: {len(test_features)}")
    print(f"Predicted anomalies: {test_features['predicted_anomaly'].sum()}")
    print(f"Anomaly rate: {test_features['predicted_anomaly'].mean():.2%}")
    print(f"Average anomaly score: {anomaly_scores.mean():.3f}")
    print(f"Max anomaly score: {anomaly_scores.max():.3f}")
    
    # Compare with ground truth if available
    if 'is_anomaly' in test_features.columns:
        actual_anomalies = test_features['is_anomaly'].sum()
        print(f"Actual anomalies (ground truth): {actual_anomalies}")
        
        # Calculate basic metrics
        from sklearn.metrics import classification_report, confusion_matrix
        print(f"\nClassification Report:")
        print(classification_report(test_features['is_anomaly'], test_features['predicted_anomaly']))
    
    print(f"\nResults saved to: data/anomaly_results.csv")
    print(f"Model artifacts saved to: models/rcf_model/")

if __name__ == "__main__":
    main()