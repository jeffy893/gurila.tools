#!/usr/bin/env python3.10
"""
AWS Architecture Diagram Generator for ML API Monitoring System
Creates a comprehensive architecture diagram showing data flow and AWS services.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np

def create_aws_architecture_diagram():
    """Generate AWS architecture diagram for ML API monitoring system"""
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Define colors
    colors = {
        'aws_orange': '#FF9900',
        'aws_blue': '#232F3E',
        'compute': '#FF9900',
        'storage': '#3F48CC',
        'analytics': '#8C4FFF',
        'ml': '#01A88D',
        'networking': '#FF4B4B',
        'security': '#DD344C',
        'kubernetes': '#326CE5',
        'data_flow': '#2E8B57'
    }
    
    # Title
    ax.text(8, 11.5, 'ML for API Service - AWS Architecture', 
            fontsize=20, fontweight='bold', ha='center', color=colors['aws_blue'])
    ax.text(8, 11, 'Real-time Anomaly Detection & Automated Reporting', 
            fontsize=14, ha='center', color='gray')
    
    # Draw main sections
    sections = [
        {'name': 'Data Sources', 'x': 0.5, 'y': 8, 'width': 3, 'height': 3, 'color': colors['kubernetes']},
        {'name': 'Data Ingestion', 'x': 4.5, 'y': 8, 'width': 3, 'height': 3, 'color': colors['networking']},
        {'name': 'Processing & ML', 'x': 8.5, 'y': 8, 'width': 3, 'height': 3, 'color': colors['ml']},
        {'name': 'Storage & Analytics', 'x': 12.5, 'y': 8, 'width': 3, 'height': 3, 'color': colors['storage']},
        {'name': 'Monitoring & Alerts', 'x': 0.5, 'y': 4, 'width': 7, 'height': 3, 'color': colors['analytics']},
        {'name': 'Reporting & Distribution', 'x': 8.5, 'y': 4, 'width': 7, 'height': 3, 'color': colors['compute']}
    ]
    
    for section in sections:
        rect = FancyBboxPatch(
            (section['x'], section['y']), section['width'], section['height'],
            boxstyle="round,pad=0.1", facecolor=section['color'], alpha=0.1,
            edgecolor=section['color'], linewidth=2
        )
        ax.add_patch(rect)
        ax.text(section['x'] + section['width']/2, section['y'] + section['height'] - 0.3,
                section['name'], fontsize=12, fontweight='bold', ha='center', color=section['color'])
    
    # Data Sources (Kubernetes)
    k8s_services = [
        {'name': 'Java Spring Boot\nAPI Pods', 'x': 1, 'y': 9.5, 'icon': '🚀'},
        {'name': 'FluentBit\nDaemonSet', 'x': 1, 'y': 8.5, 'icon': '📊'}
    ]
    
    for service in k8s_services:
        draw_service_box(ax, service['x'], service['y'], service['name'], service['icon'], colors['kubernetes'])
    
    # Data Ingestion
    ingestion_services = [
        {'name': 'Amazon Kinesis\nData Streams', 'x': 5, 'y': 9.5, 'icon': '🌊'},
        {'name': 'API Gateway\n(Optional)', 'x': 5, 'y': 8.5, 'icon': '🚪'}
    ]
    
    for service in ingestion_services:
        draw_service_box(ax, service['x'], service['y'], service['name'], service['icon'], colors['networking'])
    
    # Processing & ML
    ml_services = [
        {'name': 'AWS Lambda\nStream Processor', 'x': 9, 'y': 10, 'icon': 'λ'},
        {'name': 'SageMaker\nRCF Endpoint', 'x': 9, 'y': 9, 'icon': '🧠'},
        {'name': 'AWS Glue\nETL Jobs', 'x': 9, 'y': 8.2, 'icon': '🔄'}
    ]
    
    for service in ml_services:
        draw_service_box(ax, service['x'], service['y'], service['name'], service['icon'], colors['ml'])
    
    # Storage & Analytics
    storage_services = [
        {'name': 'S3 Raw Data\nBucket', 'x': 13, 'y': 10, 'icon': '🪣'},
        {'name': 'S3 Processed\nBucket', 'x': 13, 'y': 9, 'icon': '📦'},
        {'name': 'DynamoDB\nAlerts Table', 'x': 13, 'y': 8.2, 'icon': '🗃️'}
    ]
    
    for service in storage_services:
        draw_service_box(ax, service['x'], service['y'], service['name'], service['icon'], colors['storage'])
    
    # Monitoring & Alerts
    monitoring_services = [
        {'name': 'CloudWatch\nDashboards', 'x': 1, 'y': 5.5, 'icon': '📈'},
        {'name': 'CloudWatch\nAlarms', 'x': 3, 'y': 5.5, 'icon': '🚨'},
        {'name': 'SNS Topics\n& SQS', 'x': 5, 'y': 5.5, 'icon': '📢'},
        {'name': 'EventBridge\nScheduler', 'x': 1, 'y': 4.5, 'icon': '⏰'},
        {'name': 'Lambda Report\nGenerator', 'x': 3, 'y': 4.5, 'icon': 'λ'},
        {'name': 'Step Functions\nOrchestration', 'x': 5, 'y': 4.5, 'icon': '🔀'}
    ]
    
    for service in monitoring_services:
        draw_service_box(ax, service['x'], service['y'], service['name'], service['icon'], colors['analytics'])
    
    # Reporting & Distribution
    reporting_services = [
        {'name': 'S3 Reports\nBucket', 'x': 9, 'y': 5.5, 'icon': '📄'},
        {'name': 'Amazon SES\nEmail Service', 'x': 11, 'y': 5.5, 'icon': '📧'},
        {'name': 'CloudFront\nCDN', 'x': 13, 'y': 5.5, 'icon': '🌐'},
        {'name': 'Slack/Teams\nWebhooks', 'x': 9, 'y': 4.5, 'icon': '💬'},
        {'name': 'QuickSight\nDashboards', 'x': 11, 'y': 4.5, 'icon': '📊'},
        {'name': 'Athena\nAd-hoc Queries', 'x': 13, 'y': 4.5, 'icon': '🔍'}
    ]
    
    for service in reporting_services:
        draw_service_box(ax, service['x'], service['y'], service['name'], service['icon'], colors['compute'])
    
    # Draw data flow arrows
    data_flows = [
        # From K8s to Kinesis
        {'start': (2.5, 9.5), 'end': (4.8, 9.5), 'label': 'API Logs\n4 req/sec'},
        # From Kinesis to Lambda
        {'start': (6.5, 9.5), 'end': (8.8, 10), 'label': 'Stream\nEvents'},
        # From Lambda to SageMaker
        {'start': (9.5, 9.8), 'end': (9.5, 9.2), 'label': 'Feature\nVectors'},
        # From SageMaker to S3
        {'start': (10.5, 9), 'end': (12.8, 9), 'label': 'Anomaly\nScores'},
        # From S3 to Monitoring
        {'start': (13, 8.8), 'end': (6, 6.5), 'label': 'Metrics'},
        # From Monitoring to Reporting
        {'start': (6, 5.5), 'end': (8.8, 5.5), 'label': 'Alerts &\nReports'}
    ]
    
    for flow in data_flows:
        draw_data_flow(ax, flow['start'], flow['end'], flow['label'], colors['data_flow'])
    
    # Add security and networking layer
    security_box = FancyBboxPatch(
        (0.2, 0.5), 15.6, 2.5,
        boxstyle="round,pad=0.1", facecolor=colors['security'], alpha=0.05,
        edgecolor=colors['security'], linewidth=2, linestyle='--'
    )
    ax.add_patch(security_box)
    ax.text(8, 2.7, 'Security & Networking Layer', fontsize=14, fontweight='bold', 
            ha='center', color=colors['security'])
    
    # Security services
    security_services = [
        {'name': 'VPC with\nPrivate Subnets', 'x': 1, 'y': 1.5, 'icon': '🔒'},
        {'name': 'IAM Roles\n& Policies', 'x': 3.5, 'y': 1.5, 'icon': '👤'},
        {'name': 'KMS\nEncryption', 'x': 6, 'y': 1.5, 'icon': '🔐'},
        {'name': 'Security Groups\n& NACLs', 'x': 8.5, 'y': 1.5, 'icon': '🛡️'},
        {'name': 'CloudTrail\nAudit Logs', 'x': 11, 'y': 1.5, 'icon': '📋'},
        {'name': 'WAF\nProtection', 'x': 13.5, 'y': 1.5, 'icon': '🔥'}
    ]
    
    for service in security_services:
        draw_service_box(ax, service['x'], service['y'], service['name'], service['icon'], colors['security'])
    
    # Add cost and performance annotations
    ax.text(0.5, 0.2, '💰 Estimated Cost: ~$95/month for typical workloads', 
            fontsize=10, color='green', fontweight='bold')
    ax.text(8.5, 0.2, '⚡ Performance: <100ms inference, 4 req/sec throughput', 
            fontsize=10, color='blue', fontweight='bold')
    
    # Add legend
    legend_elements = [
        {'color': colors['kubernetes'], 'label': 'Data Sources (Kubernetes)'},
        {'color': colors['networking'], 'label': 'Data Ingestion'},
        {'color': colors['ml'], 'label': 'ML Processing'},
        {'color': colors['storage'], 'label': 'Storage & Analytics'},
        {'color': colors['analytics'], 'label': 'Monitoring & Alerts'},
        {'color': colors['compute'], 'label': 'Reporting & Distribution'},
        {'color': colors['security'], 'label': 'Security & Networking'}
    ]
    
    for i, element in enumerate(legend_elements):
        y_pos = 7.5 - i * 0.3
        ax.add_patch(Circle((0.3, y_pos), 0.1, color=element['color'], alpha=0.7))
        ax.text(0.5, y_pos, element['label'], fontsize=9, va='center')
    
    plt.tight_layout()
    plt.savefig('aws_architecture_diagram.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("✅ AWS Architecture diagram generated: aws_architecture_diagram.png")

def draw_service_box(ax, x, y, name, icon, color):
    """Draw a service box with icon and name"""
    # Service box
    box = FancyBboxPatch(
        (x-0.4, y-0.3), 0.8, 0.6,
        boxstyle="round,pad=0.05", facecolor='white', 
        edgecolor=color, linewidth=1.5
    )
    ax.add_patch(box)
    
    # Icon
    ax.text(x, y+0.1, icon, fontsize=16, ha='center', va='center')
    
    # Service name
    ax.text(x, y-0.15, name, fontsize=8, ha='center', va='center', 
            color=color, fontweight='bold')

def draw_data_flow(ax, start, end, label, color):
    """Draw data flow arrow with label"""
    arrow = ConnectionPatch(start, end, "data", "data",
                          arrowstyle="->", shrinkA=5, shrinkB=5,
                          mutation_scale=20, fc=color, ec=color, linewidth=2)
    ax.add_patch(arrow)
    
    # Add label at midpoint
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2 + 0.2
    ax.text(mid_x, mid_y, label, fontsize=7, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8),
            color=color, fontweight='bold')

def create_detailed_data_flow_diagram():
    """Create a detailed data flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'ML API Monitoring - Data Flow Architecture', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Define the data flow stages
    stages = [
        {'name': 'API Requests\n(4/sec)', 'x': 1, 'y': 8, 'color': '#326CE5'},
        {'name': 'FluentBit\nCollection', 'x': 3, 'y': 8, 'color': '#FF6B6B'},
        {'name': 'Kinesis\nStreaming', 'x': 5, 'y': 8, 'color': '#4ECDC4'},
        {'name': 'Lambda\nProcessing', 'x': 7, 'y': 8, 'color': '#45B7D1'},
        {'name': 'SageMaker\nInference', 'x': 9, 'y': 8, 'color': '#96CEB4'},
        {'name': 'S3 Storage\n& Analysis', 'x': 11, 'y': 8, 'color': '#FFEAA7'},
        {'name': 'Report\nGeneration', 'x': 13, 'y': 8, 'color': '#DDA0DD'}
    ]
    
    # Draw stages
    for i, stage in enumerate(stages):
        # Stage box
        box = FancyBboxPatch(
            (stage['x']-0.5, stage['y']-0.4), 1, 0.8,
            boxstyle="round,pad=0.1", facecolor=stage['color'], alpha=0.3,
            edgecolor=stage['color'], linewidth=2
        )
        ax.add_patch(box)
        ax.text(stage['x'], stage['y'], stage['name'], fontsize=10, fontweight='bold',
                ha='center', va='center', color='black')
        
        # Draw arrow to next stage
        if i < len(stages) - 1:
            arrow = ConnectionPatch((stage['x']+0.5, stage['y']), 
                                  (stages[i+1]['x']-0.5, stages[i+1]['y']),
                                  "data", "data", arrowstyle="->", 
                                  shrinkA=5, shrinkB=5, mutation_scale=20,
                                  fc='gray', ec='gray', linewidth=2)
            ax.add_patch(arrow)
    
    # Add detailed process descriptions
    processes = [
        {'x': 1, 'y': 6.5, 'text': '• HTTP requests\n• Response times\n• Error codes\n• Resource usage'},
        {'x': 3, 'y': 6.5, 'text': '• Log parsing\n• Metric extraction\n• Real-time streaming\n• Format conversion'},
        {'x': 5, 'y': 6.5, 'text': '• Stream buffering\n• Partition by IP\n• 24hr retention\n• Auto-scaling'},
        {'x': 7, 'y': 6.5, 'text': '• Feature engineering\n• Data validation\n• Batch processing\n• Error handling'},
        {'x': 9, 'y': 6.5, 'text': '• RCF algorithm\n• Anomaly scoring\n• Real-time inference\n• Auto-scaling'},
        {'x': 11, 'y': 6.5, 'text': '• Raw data lake\n• Processed results\n• Historical analysis\n• Data lifecycle'},
        {'x': 13, 'y': 6.5, 'text': '• HTML/PDF reports\n• PNG visualizations\n• Email distribution\n• Dashboard updates'}
    ]
    
    for process in processes:
        ax.text(process['x'], process['y'], process['text'], fontsize=8,
                ha='center', va='top', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
    
    # Add performance metrics
    metrics = [
        {'x': 2, 'y': 4.5, 'text': 'Throughput:\n4 requests/sec\n345K requests/day'},
        {'x': 5, 'y': 4.5, 'text': 'Latency:\n<50ms processing\n<100ms inference'},
        {'x': 8, 'y': 4.5, 'text': 'Accuracy:\n14.46% anomaly rate\n43.5/100 health score'},
        {'x': 11, 'y': 4.5, 'text': 'Storage:\nTB-scale capacity\n99.99% durability'}
    ]
    
    for metric in metrics:
        ax.text(metric['x'], metric['y'], metric['text'], fontsize=9, fontweight='bold',
                ha='center', va='center', color='blue',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.5))
    
    # Add cost breakdown
    ax.text(7, 2.5, 'Monthly Cost Breakdown (~$95 total)', fontsize=12, fontweight='bold', ha='center')
    cost_items = [
        'Kinesis: $22', 'Lambda: $8', 'SageMaker: $35', 'S3: $3', 
        'DynamoDB: $25', 'SNS/SES: $2'
    ]
    
    for i, item in enumerate(cost_items):
        x_pos = 2 + (i % 3) * 4
        y_pos = 1.8 - (i // 3) * 0.4
        ax.text(x_pos, y_pos, item, fontsize=10, ha='center',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('data_flow_diagram.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("✅ Data Flow diagram generated: data_flow_diagram.png")

def main():
    """Generate both architecture diagrams"""
    print("🎨 Generating AWS Architecture Diagrams...")
    
    # Generate main architecture diagram
    create_aws_architecture_diagram()
    
    # Generate detailed data flow diagram
    create_detailed_data_flow_diagram()
    
    print("\n📊 Diagrams generated successfully!")
    print("   • aws_architecture_diagram.png - Complete AWS architecture")
    print("   • data_flow_diagram.png - Detailed data flow and metrics")
    print("\n🔗 Ready for integration into README.md")

if __name__ == "__main__":
    main()