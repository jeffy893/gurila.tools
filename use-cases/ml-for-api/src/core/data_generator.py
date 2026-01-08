#!/usr/bin/env python3
"""
Synthetic Data Generator for API Observability
Generates realistic API logs with infrastructure metrics, network metadata, and trace data.
Includes deliberate anomaly injection for testing ML models.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker
import os

class APILogGenerator:
    def __init__(self, duration_hours=24, requests_per_second=4):
        self.fake = Faker()
        self.duration_hours = duration_hours
        self.requests_per_second = requests_per_second
        self.total_requests = int(duration_hours * 3600 * requests_per_second)  # Convert to int
        
        # Define approved source IPs (simulating known clients)
        self.approved_ips = [
            "10.0.1.100", "10.0.1.101", "10.0.1.102", "192.168.1.50",
            "172.16.0.10", "172.16.0.11", "203.0.113.5", "198.51.100.10"
        ]
        
        # Define API endpoints
        self.endpoints = [
            "/api/v1/users", "/api/v1/orders", "/api/v1/products",
            "/api/v1/payments", "/api/v1/inventory", "/api/v1/reports",
            "/api/v1/auth", "/api/v1/notifications"
        ]
        
        # User agents for different client types
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "PostmanRuntime/7.29.2", "curl/7.68.0", "Java/11.0.16",
            "Apache-HttpClient/4.5.13", "okhttp/4.9.3"
        ]
    
    def generate_base_metrics(self, timestamp):
        """Generate base infrastructure and network metrics"""
        # Normal CPU usage with some variation
        cpu_base = np.random.normal(45, 15)
        cpu_usage = max(5, min(95, cpu_base))
        
        # Memory usage with gradual increase pattern
        hours_elapsed = (timestamp - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600
        memory_base = 512 + (hours_elapsed * 2)  # Gradual increase
        memory_usage = max(256, memory_base + np.random.normal(0, 50))
        
        # Pod restart count (usually 0, occasionally 1-2)
        pod_restarts = np.random.choice([0, 0, 0, 0, 0, 1, 2], p=[0.85, 0.05, 0.05, 0.02, 0.02, 0.005, 0.005])
        
        # Network metadata
        source_ip = random.choice(self.approved_ips + [self.fake.ipv4() for _ in range(3)])
        is_approved = source_ip in self.approved_ips
        
        http_method = np.random.choice(["GET", "POST", "PUT", "DELETE"], p=[0.6, 0.25, 0.1, 0.05])
        endpoint = random.choice(self.endpoints)
        user_agent = random.choice(self.user_agents)
        
        # Trace data (observability metrics)
        sql_execution_time = max(1, np.random.lognormal(2.5, 1.2))  # Log-normal distribution
        stack_trace_depth = np.random.poisson(8) + 1
        db_connection_pool = np.random.randint(5, 25)
        
        return {
            'timestamp': timestamp,
            'cpu_usage_percent': round(cpu_usage, 2),
            'memory_usage_mb': round(memory_usage, 2),
            'pod_restart_count': pod_restarts,
            'source_ip': source_ip,
            'is_approved_source': is_approved,
            'http_method': http_method,
            'endpoint': endpoint,
            'user_agent': user_agent,
            'sql_execution_time_ms': round(sql_execution_time, 2),
            'stack_trace_depth': stack_trace_depth,
            'db_connection_pool_active': db_connection_pool,
            'response_time_ms': round(np.random.lognormal(4, 0.8), 2),
            'status_code': np.random.choice([200, 201, 400, 404, 500], p=[0.85, 0.05, 0.05, 0.03, 0.02])
        }
    
    def inject_security_anomaly(self, data_point):
        """Inject security event: traffic from unapproved source"""
        data_point['source_ip'] = self.fake.ipv4()
        data_point['is_approved_source'] = False
        data_point['http_method'] = 'POST'  # Suspicious POST from unknown source
        data_point['endpoint'] = '/api/v1/auth'  # Targeting auth endpoint
        data_point['response_time_ms'] *= 1.5  # Slightly slower response
        return data_point
    
    def inject_resource_leak(self, data_point, leak_severity=1.0):
        """Inject resource leak: gradual memory increase"""
        data_point['memory_usage_mb'] *= (1.0 + leak_severity * 0.3)  # 30% increase per severity level
        data_point['cpu_usage_percent'] = min(95, data_point['cpu_usage_percent'] * 1.2)
        if data_point['memory_usage_mb'] > 1800:  # Trigger pod restart
            data_point['pod_restart_count'] = 1
            data_point['memory_usage_mb'] = 512  # Reset after restart
        return data_point
    
    def inject_database_bottleneck(self, data_point):
        """Inject database bottleneck: high SQL execution times"""
        data_point['sql_execution_time_ms'] *= random.uniform(5, 15)  # 5-15x normal time
        data_point['db_connection_pool_active'] = min(24, data_point['db_connection_pool_active'] + 10)
        data_point['response_time_ms'] *= random.uniform(3, 8)  # Much slower API response
        data_point['endpoint'] = random.choice(['/api/v1/reports', '/api/v1/orders'])  # Data-heavy endpoints
        return data_point
    
    def generate_dataset(self):
        """Generate complete synthetic dataset with anomalies"""
        print(f"Generating {self.total_requests} API log entries over {self.duration_hours} hours...")
        
        data = []
        start_time = datetime.now() - timedelta(hours=self.duration_hours)
        
        # Track anomaly injection
        security_anomalies = 0
        resource_leaks = 0
        db_bottlenecks = 0
        leak_severity = 0
        
        for i in range(self.total_requests):
            # Calculate timestamp
            seconds_offset = i / self.requests_per_second
            timestamp = start_time + timedelta(seconds=seconds_offset)
            
            # Generate base data point
            data_point = self.generate_base_metrics(timestamp)
            
            # Inject anomalies based on probability and patterns
            anomaly_injected = False
            
            # Security anomaly: 0.5% chance
            if random.random() < 0.005:
                data_point = self.inject_security_anomaly(data_point)
                security_anomalies += 1
                anomaly_injected = True
            
            # Resource leak: gradual buildup over time
            if i > self.total_requests * 0.3:  # Start after 30% of time
                if random.random() < 0.02:  # 2% chance to increase leak
                    leak_severity = min(5, leak_severity + 0.1)
                if leak_severity > 0:
                    data_point = self.inject_resource_leak(data_point, leak_severity)
                    resource_leaks += 1
                    anomaly_injected = True
            
            # Database bottleneck: 1% chance, more likely during peak hours
            hour = timestamp.hour
            peak_multiplier = 2 if 9 <= hour <= 17 else 1  # Business hours
            if random.random() < (0.01 * peak_multiplier):
                data_point = self.inject_database_bottleneck(data_point)
                db_bottlenecks += 1
                anomaly_injected = True
            
            # Add anomaly flag for ground truth
            data_point['is_anomaly'] = anomaly_injected
            data.append(data_point)
            
            if (i + 1) % 10000 == 0:
                print(f"Generated {i + 1}/{self.total_requests} records...")
        
        df = pd.DataFrame(data)
        
        print(f"\nDataset generation complete!")
        print(f"Total records: {len(df)}")
        print(f"Security anomalies injected: {security_anomalies}")
        print(f"Resource leak events: {resource_leaks}")
        print(f"Database bottleneck events: {db_bottlenecks}")
        print(f"Total anomalies: {df['is_anomaly'].sum()}")
        print(f"Anomaly rate: {df['is_anomaly'].mean():.2%}")
        
        return df
    
    def save_dataset(self, df, filename="synthetic_api_logs.csv"):
        """Save dataset to CSV file"""
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        df.to_csv(filepath, index=False)
        print(f"\nDataset saved to: {filepath}")
        return filepath

def main():
    """Main execution function"""
    print("=== API Log Synthetic Data Generator ===")
    
    # Generate 24 hours of data at 4 requests/second
    generator = APILogGenerator(duration_hours=24, requests_per_second=4)
    
    # Generate the dataset
    df = generator.generate_dataset()
    
    # Save to file
    filepath = generator.save_dataset(df)
    
    # Display sample statistics
    print(f"\nDataset Statistics:")
    print(f"Shape: {df.shape}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Unique source IPs: {df['source_ip'].nunique()}")
    print(f"Approved sources: {df['is_approved_source'].sum()}")
    print(f"Average CPU usage: {df['cpu_usage_percent'].mean():.1f}%")
    print(f"Average memory usage: {df['memory_usage_mb'].mean():.1f} MB")
    print(f"Average SQL execution time: {df['sql_execution_time_ms'].mean():.1f} ms")
    
    print(f"\nFirst 5 records:")
    print(df.head())

if __name__ == "__main__":
    main()