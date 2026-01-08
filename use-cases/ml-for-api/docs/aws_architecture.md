# AWS Architecture for ML-Powered API Monitoring

## Overview

This document describes the production AWS architecture for operationalizing the ML-powered API monitoring system. The architecture provides real-time anomaly detection, automated reporting, and scalable data processing for high-traffic APIs.

## Architecture Components

### 1. Data Ingestion Layer

#### Amazon Kinesis Data Streams
- **Purpose**: Real-time ingestion of API logs and metrics
- **Configuration**:
  - Stream name: `api-monitoring-stream`
  - Shard count: 2-4 (based on 4 req/sec × scaling factor)
  - Retention period: 24 hours
  - Encryption: Server-side encryption with KMS

#### FluentBit/Fluent Agent
- **Deployment**: DaemonSet on Kubernetes cluster
- **Configuration**:
  ```yaml
  apiVersion: v1
  kind: ConfigMap
  metadata:
    name: fluent-bit-config
  data:
    fluent-bit.conf: |
      [SERVICE]
          Flush         1
          Log_Level     info
          Daemon        off
          Parsers_File  parsers.conf
      
      [INPUT]
          Name              tail
          Path              /var/log/containers/*api*.log
          Parser            docker
          Tag               api.logs
          Refresh_Interval  5
      
      [OUTPUT]
          Name              kinesis_streams
          Match             api.logs
          region            us-east-1
          stream            api-monitoring-stream
          partition_key     source_ip
  ```

### 2. Data Processing Layer

#### AWS Lambda Functions

##### Stream Processor Lambda
- **Function**: `api-log-processor`
- **Runtime**: Python 3.9
- **Memory**: 512 MB
- **Timeout**: 5 minutes
- **Trigger**: Kinesis Data Streams
- **Purpose**: Parse, enrich, and prepare data for ML inference

```python
# Lambda function structure
import json
import boto3
import pandas as pd
from datetime import datetime

def lambda_handler(event, context):
    """Process Kinesis stream records"""
    
    sagemaker_runtime = boto3.client('sagemaker-runtime')
    s3_client = boto3.client('s3')
    
    processed_records = []
    
    for record in event['Records']:
        # Decode Kinesis data
        payload = json.loads(base64.b64decode(record['kinesis']['data']))
        
        # Extract and enrich metrics
        enriched_data = enrich_log_data(payload)
        
        # Prepare for ML inference
        feature_vector = prepare_features(enriched_data)
        
        # Get anomaly score from SageMaker endpoint
        anomaly_score = get_anomaly_score(sagemaker_runtime, feature_vector)
        
        # Store results
        result = {
            'timestamp': enriched_data['timestamp'],
            'anomaly_score': anomaly_score,
            'raw_data': enriched_data
        }
        
        processed_records.append(result)
    
    # Batch write to S3 for reporting
    store_results(s3_client, processed_records)
    
    return {'statusCode': 200, 'processed': len(processed_records)}
```

##### Report Generator Lambda
- **Function**: `health-report-generator`
- **Runtime**: Python 3.9
- **Memory**: 1024 MB
- **Timeout**: 15 minutes
- **Trigger**: CloudWatch Events (scheduled)
- **Purpose**: Generate and distribute health reports

#### AWS Glue (Alternative Processing)
- **Job Type**: Python Shell
- **Purpose**: Batch processing for historical analysis
- **Schedule**: Daily ETL jobs for trend analysis
- **Data Catalog**: Automatic schema discovery for S3 data

### 3. Machine Learning Layer

#### Amazon SageMaker

##### Model Training
- **Algorithm**: Random Cut Forest (built-in)
- **Instance Type**: ml.m5.xlarge
- **Training Data**: S3 bucket with historical logs
- **Model Artifacts**: Stored in S3 model registry

##### Model Endpoint
- **Endpoint Name**: `api-anomaly-detector`
- **Instance Type**: ml.t2.medium (auto-scaling enabled)
- **Configuration**:
  ```json
  {
    "EndpointName": "api-anomaly-detector",
    "EndpointConfigName": "api-anomaly-config",
    "ProductionVariants": [
      {
        "VariantName": "primary",
        "ModelName": "api-rcf-model",
        "InitialInstanceCount": 1,
        "InstanceType": "ml.t2.medium",
        "InitialVariantWeight": 1.0
      }
    ]
  }
  ```

##### Auto Scaling Configuration
```json
{
  "ServiceNamespace": "sagemaker",
  "ResourceId": "endpoint/api-anomaly-detector/variant/primary",
  "ScalableDimension": "sagemaker:variant:DesiredInstanceCount",
  "MinCapacity": 1,
  "MaxCapacity": 5,
  "TargetTrackingScalingPolicies": [
    {
      "TargetValue": 70.0,
      "PredefinedMetricSpecification": {
        "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
      }
    }
  ]
}
```

### 4. Storage Layer

#### Amazon S3 Buckets

##### Raw Data Bucket
- **Name**: `api-monitoring-raw-data`
- **Purpose**: Store raw log data from Kinesis
- **Lifecycle Policy**: 
  - Transition to IA after 30 days
  - Transition to Glacier after 90 days
  - Delete after 2 years

##### Processed Data Bucket
- **Name**: `api-monitoring-processed`
- **Purpose**: Store processed data and ML results
- **Partitioning**: `year/month/day/hour`

##### Reports Bucket
- **Name**: `api-monitoring-reports`
- **Purpose**: Store generated health reports
- **Public Access**: Configured for report distribution

#### Amazon DynamoDB
- **Table**: `api-anomaly-alerts`
- **Purpose**: Store real-time alerts and metadata
- **Schema**:
  ```json
  {
    "TableName": "api-anomaly-alerts",
    "KeySchema": [
      {"AttributeName": "alert_id", "KeyType": "HASH"},
      {"AttributeName": "timestamp", "KeyType": "RANGE"}
    ],
    "AttributeDefinitions": [
      {"AttributeName": "alert_id", "AttributeType": "S"},
      {"AttributeName": "timestamp", "AttributeType": "S"}
    ],
    "BillingMode": "PAY_PER_REQUEST"
  }
  ```

### 5. Notification and Reporting Layer

#### Amazon SNS
- **Topic**: `api-health-alerts`
- **Subscribers**: 
  - Email notifications for critical alerts
  - Slack webhook for team notifications
  - Lambda function for automated responses

#### Amazon SES
- **Purpose**: Send formatted health reports via email
- **Configuration**:
  - Verified domain for sending
  - Templates for different report types
  - Scheduled delivery for daily/weekly reports

#### CloudWatch Dashboards
- **Dashboard**: `API-Health-Monitoring`
- **Widgets**:
  - Real-time anomaly count
  - System health score trends
  - Resource utilization metrics
  - Alert frequency charts

### 6. Security and Monitoring

#### IAM Roles and Policies

##### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kinesis:DescribeStream",
        "kinesis:GetShardIterator",
        "kinesis:GetRecords",
        "kinesis:ListStreams"
      ],
      "Resource": "arn:aws:kinesis:*:*:stream/api-monitoring-stream"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:*:*:endpoint/api-anomaly-detector"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::api-monitoring-processed/*",
        "arn:aws:s3:::api-monitoring-reports/*"
      ]
    }
  ]
}
```

#### VPC Configuration
- **VPC**: Dedicated VPC for ML workloads
- **Subnets**: Private subnets for SageMaker endpoints
- **Security Groups**: Restrictive rules for ML components
- **NAT Gateway**: For outbound internet access

#### Encryption
- **At Rest**: S3 buckets encrypted with KMS
- **In Transit**: TLS 1.2 for all API communications
- **Key Management**: Customer-managed KMS keys

### 7. Cost Optimization

#### Resource Optimization
- **SageMaker**: Use Spot instances for training
- **Lambda**: Optimize memory allocation based on usage
- **S3**: Implement intelligent tiering
- **Kinesis**: Right-size shard count based on throughput

#### Monitoring and Alerts
- **CloudWatch**: Cost anomaly detection
- **Budgets**: Monthly spending alerts
- **Trusted Advisor**: Regular cost optimization reviews

## Deployment Guide

### 1. Infrastructure as Code (CloudFormation)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'ML-powered API monitoring infrastructure'

Parameters:
  Environment:
    Type: String
    Default: 'prod'
    AllowedValues: ['dev', 'staging', 'prod']

Resources:
  # Kinesis Stream
  APIMonitoringStream:
    Type: AWS::Kinesis::Stream
    Properties:
      Name: !Sub 'api-monitoring-stream-${Environment}'
      ShardCount: 2
      RetentionPeriodHours: 24
      StreamEncryption:
        EncryptionType: KMS
        KeyId: alias/aws/kinesis

  # S3 Buckets
  RawDataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'api-monitoring-raw-data-${Environment}'
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

  # Lambda Functions
  StreamProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub 'api-log-processor-${Environment}'
      Runtime: python3.9
      Handler: lambda_function.lambda_handler
      Code:
        ZipFile: |
          # Lambda function code here
      MemorySize: 512
      Timeout: 300
      Role: !GetAtt LambdaExecutionRole.Arn

  # Event Source Mapping
  KinesisEventSourceMapping:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      EventSourceArn: !GetAtt APIMonitoringStream.Arn
      FunctionName: !Ref StreamProcessorFunction
      StartingPosition: LATEST
      BatchSize: 100
```

### 2. Deployment Steps

1. **Deploy Infrastructure**:
   ```bash
   aws cloudformation deploy \
     --template-file infrastructure.yaml \
     --stack-name api-monitoring-stack \
     --parameter-overrides Environment=prod \
     --capabilities CAPABILITY_IAM
   ```

2. **Deploy Lambda Functions**:
   ```bash
   # Package and deploy Lambda functions
   sam build
   sam deploy --guided
   ```

3. **Train and Deploy ML Model**:
   ```bash
   python sagemaker_model.py --deploy-endpoint
   ```

4. **Configure Kubernetes FluentBit**:
   ```bash
   kubectl apply -f fluent-bit-config.yaml
   kubectl apply -f fluent-bit-daemonset.yaml
   ```

### 3. Monitoring and Maintenance

#### CloudWatch Alarms
- Lambda function errors and duration
- Kinesis stream metrics
- SageMaker endpoint invocation errors
- S3 bucket size and request metrics

#### Automated Testing
- Synthetic data injection for testing
- Model performance validation
- End-to-end pipeline testing

## Cost Estimation

### Monthly Cost Breakdown (Production)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| Kinesis Data Streams | 2 shards, 24h retention | $22 |
| Lambda | 1M invocations, 512MB | $8 |
| SageMaker Endpoint | ml.t2.medium, 24/7 | $35 |
| S3 Storage | 100GB processed data | $3 |
| DynamoDB | 1M read/write units | $25 |
| SNS/SES | 1000 notifications | $2 |
| **Total** | | **~$95/month** |

### Scaling Considerations
- **10x traffic**: ~$300/month
- **100x traffic**: ~$1,200/month
- Cost scales primarily with Kinesis shards and SageMaker endpoints

## Security Best Practices

1. **Least Privilege Access**: IAM roles with minimal required permissions
2. **Network Isolation**: VPC with private subnets for ML components
3. **Data Encryption**: End-to-end encryption for all data
4. **Audit Logging**: CloudTrail for all API calls
5. **Secret Management**: AWS Secrets Manager for credentials
6. **Regular Updates**: Automated patching for Lambda runtimes

## Disaster Recovery

1. **Multi-AZ Deployment**: SageMaker endpoints across multiple AZs
2. **Cross-Region Replication**: S3 bucket replication for critical data
3. **Backup Strategy**: Automated snapshots of DynamoDB tables
4. **Recovery Testing**: Monthly DR drills and documentation

This architecture provides a robust, scalable, and cost-effective solution for ML-powered API monitoring in production environments.