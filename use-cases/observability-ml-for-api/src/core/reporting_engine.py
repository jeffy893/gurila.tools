#!/usr/bin/env python3
"""
Automated Reporting Engine for API Anomaly Detection
Generates comprehensive health reports with visualizations and root cause analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

class HealthReportGenerator:
    def __init__(self, results_path="data/anomaly_results.csv"):
        """Initialize the reporting engine"""
        self.results_path = results_path
        self.report_timestamp = datetime.now()
        
        # Create output directories
        os.makedirs('reports', exist_ok=True)
        os.makedirs('reports/images', exist_ok=True)
        
        # Load data
        self.df = pd.read_csv(results_path)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def calculate_health_metrics(self):
        """Calculate overall system health metrics"""
        total_requests = len(self.df)
        anomaly_count = self.df['predicted_anomaly'].sum()
        anomaly_rate = anomaly_count / total_requests
        
        # Calculate health score (0-100, where 100 is perfect health)
        base_score = 100
        
        # Deduct points for anomalies
        anomaly_penalty = min(50, anomaly_rate * 1000)  # Max 50 points for anomalies
        
        # Deduct points for high resource usage
        avg_cpu = self.df['cpu_usage_percent'].mean()
        avg_memory = self.df['memory_usage_mb'].mean()
        cpu_penalty = max(0, (avg_cpu - 70) * 0.5)  # Penalty if CPU > 70%
        memory_penalty = max(0, (avg_memory - 1000) * 0.02)  # Penalty if memory > 1GB
        
        # Deduct points for slow responses
        avg_response_time = self.df['response_time_ms'].mean()
        response_penalty = max(0, (avg_response_time - 200) * 0.1)  # Penalty if > 200ms
        
        health_score = max(0, base_score - anomaly_penalty - cpu_penalty - memory_penalty - response_penalty)
        
        return {
            'total_requests': total_requests,
            'anomaly_count': int(anomaly_count),
            'anomaly_rate': anomaly_rate,
            'health_score': round(health_score, 1),
            'avg_cpu': round(avg_cpu, 1),
            'avg_memory': round(avg_memory, 1),
            'avg_response_time': round(avg_response_time, 1),
            'pod_restarts': int(self.df['pod_restart_count'].sum()),
            'unapproved_sources': int((~self.df['is_approved_source']).sum())
        }
    
    def create_time_series_plot(self):
        """Create time-series plot with anomaly markers"""
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # CPU Usage plot
        axes[0].plot(self.df['timestamp'], self.df['cpu_usage_percent'], 
                    color='blue', alpha=0.7, linewidth=1)
        
        # Mark anomalies
        anomalies = self.df[self.df['predicted_anomaly']]
        if len(anomalies) > 0:
            axes[0].scatter(anomalies['timestamp'], anomalies['cpu_usage_percent'], 
                          color='red', s=50, alpha=0.8, zorder=5, label='Anomalies')
        
        axes[0].set_title('CPU Usage Over Time', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('CPU Usage (%)')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        
        # Memory Usage plot
        axes[1].plot(self.df['timestamp'], self.df['memory_usage_mb'], 
                    color='green', alpha=0.7, linewidth=1)
        
        if len(anomalies) > 0:
            axes[1].scatter(anomalies['timestamp'], anomalies['memory_usage_mb'], 
                          color='red', s=50, alpha=0.8, zorder=5, label='Anomalies')
        
        axes[1].set_title('Memory Usage Over Time', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Memory Usage (MB)')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        
        # Response Time plot
        axes[2].plot(self.df['timestamp'], self.df['response_time_ms'], 
                    color='orange', alpha=0.7, linewidth=1)
        
        if len(anomalies) > 0:
            axes[2].scatter(anomalies['timestamp'], anomalies['response_time_ms'], 
                          color='red', s=50, alpha=0.8, zorder=5, label='Anomalies')
        
        axes[2].set_title('API Response Time Over Time', fontsize=14, fontweight='bold')
        axes[2].set_ylabel('Response Time (ms)')
        axes[2].set_xlabel('Time')
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()
        
        plt.tight_layout()
        plt.savefig('reports/images/time_series_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return 'reports/images/time_series_plot.png'
    
    def create_anomaly_distribution_plot(self):
        """Create anomaly score distribution plot"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Anomaly score distribution
        axes[0, 0].hist(self.df['anomaly_score'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].axvline(self.df['anomaly_score'].mean(), color='red', linestyle='--', 
                          label=f'Mean: {self.df["anomaly_score"].mean():.3f}')
        axes[0, 0].set_title('Anomaly Score Distribution')
        axes[0, 0].set_xlabel('Anomaly Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Top anomalous endpoints
        endpoint_anomalies = self.df[self.df['predicted_anomaly']]['endpoint'].value_counts().head(5)
        if len(endpoint_anomalies) > 0:
            axes[0, 1].bar(range(len(endpoint_anomalies)), endpoint_anomalies.values, color='coral')
            axes[0, 1].set_title('Top Anomalous Endpoints')
            axes[0, 1].set_ylabel('Anomaly Count')
            axes[0, 1].set_xticks(range(len(endpoint_anomalies)))
            axes[0, 1].set_xticklabels(endpoint_anomalies.index, rotation=45, ha='right')
        
        # HTTP method distribution for anomalies
        if self.df['predicted_anomaly'].sum() > 0:
            method_dist = self.df[self.df['predicted_anomaly']]['http_method'].value_counts()
            axes[1, 0].pie(method_dist.values, labels=method_dist.index, autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title('HTTP Methods in Anomalies')
        
        # Resource usage correlation
        anomaly_data = self.df[self.df['predicted_anomaly']]
        if len(anomaly_data) > 0:
            axes[1, 1].scatter(anomaly_data['cpu_usage_percent'], anomaly_data['memory_usage_mb'], 
                             alpha=0.6, color='red', s=60)
            axes[1, 1].set_title('CPU vs Memory in Anomalies')
            axes[1, 1].set_xlabel('CPU Usage (%)')
            axes[1, 1].set_ylabel('Memory Usage (MB)')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('reports/images/anomaly_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return 'reports/images/anomaly_analysis.png'
    
    def analyze_root_causes(self):
        """Analyze root causes of detected anomalies"""
        anomalies = self.df[self.df['predicted_anomaly']].copy()
        
        if len(anomalies) == 0:
            return []
        
        root_causes = []
        
        # Group anomalies by time windows (5-minute windows)
        anomalies['time_window'] = anomalies['timestamp'].dt.floor('5min')
        
        for window, group in anomalies.groupby('time_window'):
            if len(group) == 0:
                continue
                
            causes = []
            
            # Check for high SQL execution times
            if group['sql_execution_time_ms'].mean() > 1000:  # > 1 second
                causes.append(f"High SQL execution time ({group['sql_execution_time_ms'].mean():.0f}ms avg)")
            
            # Check for unapproved sources
            unapproved = (~group['is_approved_source']).sum()
            if unapproved > 0:
                unique_ips = group[~group['is_approved_source']]['source_ip'].nunique()
                causes.append(f"Traffic from {unapproved} unapproved source(s) ({unique_ips} unique IPs)")
            
            # Check for high resource usage
            if group['cpu_usage_percent'].mean() > 80:
                causes.append(f"High CPU usage ({group['cpu_usage_percent'].mean():.1f}% avg)")
            
            if group['memory_usage_mb'].mean() > 1500:
                causes.append(f"High memory usage ({group['memory_usage_mb'].mean():.0f}MB avg)")
            
            # Check for pod restarts
            if group['pod_restart_count'].sum() > 0:
                causes.append(f"Pod restart(s) detected ({int(group['pod_restart_count'].sum())} total)")
            
            # Check for slow response times
            if group['response_time_ms'].mean() > 500:
                causes.append(f"Slow API responses ({group['response_time_ms'].mean():.0f}ms avg)")
            
            # Check for database connection issues
            if group['db_connection_pool_active'].mean() > 20:
                causes.append(f"High database connection usage ({group['db_connection_pool_active'].mean():.0f} avg)")
            
            if causes:
                root_causes.append({
                    'timestamp': window,
                    'anomaly_count': len(group),
                    'causes': causes,
                    'severity': 'High' if len(causes) >= 3 else 'Medium' if len(causes) >= 2 else 'Low'
                })
        
        # Sort by timestamp
        root_causes.sort(key=lambda x: x['timestamp'])
        
        return root_causes
    
    def generate_html_report(self):
        """Generate HTML report"""
        metrics = self.calculate_health_metrics()
        root_causes = self.analyze_root_causes()
        
        # Create plots
        time_series_plot = self.create_time_series_plot()
        anomaly_plot = self.create_anomaly_distribution_plot()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Health Report - {self.report_timestamp.strftime('%Y-%m-%d %H:%M')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e8f4f8; border-radius: 5px; }}
                .health-score {{ font-size: 24px; font-weight: bold; color: {'green' if metrics['health_score'] > 80 else 'orange' if metrics['health_score'] > 60 else 'red'}; }}
                .anomaly-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .anomaly-table th, .anomaly-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .anomaly-table th {{ background-color: #f2f2f2; }}
                .severity-high {{ background-color: #ffebee; }}
                .severity-medium {{ background-color: #fff3e0; }}
                .severity-low {{ background-color: #f3e5f5; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>API System Health Report</h1>
                <p>Generated: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Analysis Period: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}</p>
            </div>
            
            <h2>Executive Summary</h2>
            <div class="health-score">Overall Health Score: {metrics['health_score']}/100</div>
            
            <div class="metric">
                <strong>Total Requests:</strong> {metrics['total_requests']:,}
            </div>
            <div class="metric">
                <strong>Anomalies Detected:</strong> {metrics['anomaly_count']}
            </div>
            <div class="metric">
                <strong>Anomaly Rate:</strong> {metrics['anomaly_rate']:.2%}
            </div>
            <div class="metric">
                <strong>Pod Restarts:</strong> {metrics['pod_restarts']}
            </div>
            <div class="metric">
                <strong>Avg CPU Usage:</strong> {metrics['avg_cpu']}%
            </div>
            <div class="metric">
                <strong>Avg Memory Usage:</strong> {metrics['avg_memory']} MB
            </div>
            <div class="metric">
                <strong>Avg Response Time:</strong> {metrics['avg_response_time']} ms
            </div>
            
            <h2>System Performance Over Time</h2>
            <img src="images/time_series_plot.png" alt="Time Series Plot">
            
            <h2>Anomaly Analysis</h2>
            <img src="images/anomaly_analysis.png" alt="Anomaly Analysis">
            
            <h2>Root Cause Analysis</h2>
        """
        
        if root_causes:
            html_content += """
            <table class="anomaly-table">
                <tr>
                    <th>Timestamp</th>
                    <th>Severity</th>
                    <th>Anomaly Count</th>
                    <th>Root Causes</th>
                </tr>
            """
            
            for cause in root_causes:
                severity_class = f"severity-{cause['severity'].lower()}"
                causes_text = "; ".join(cause['causes'])
                html_content += f"""
                <tr class="{severity_class}">
                    <td>{cause['timestamp'].strftime('%Y-%m-%d %H:%M')}</td>
                    <td>{cause['severity']}</td>
                    <td>{cause['anomaly_count']}</td>
                    <td>{causes_text}</td>
                </tr>
                """
            
            html_content += "</table>"
        else:
            html_content += "<p>No significant anomalies detected during the analysis period.</p>"
        
        html_content += """
            <h2>Recommendations</h2>
            <ul>
        """
        
        # Add recommendations based on findings
        if metrics['anomaly_rate'] > 0.05:
            html_content += "<li>High anomaly rate detected. Consider investigating system performance and security.</li>"
        
        if metrics['avg_cpu'] > 70:
            html_content += "<li>CPU usage is high. Consider scaling up resources or optimizing application performance.</li>"
        
        if metrics['avg_memory'] > 1000:
            html_content += "<li>Memory usage is elevated. Monitor for potential memory leaks.</li>"
        
        if metrics['unapproved_sources'] > 0:
            html_content += "<li>Traffic from unapproved sources detected. Review security policies and access controls.</li>"
        
        if metrics['pod_restarts'] > 0:
            html_content += "<li>Pod restarts detected. Investigate application stability and resource limits.</li>"
        
        html_content += """
            </ul>
            
            <hr>
            <p><em>This report was generated automatically by the ML-powered API monitoring system.</em></p>
        </body>
        </html>
        """
        
        # Save HTML report
        html_path = f"reports/health_report_{self.report_timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        return html_path
    
    def generate_pdf_report(self):
        """Generate PDF report using ReportLab"""
        metrics = self.calculate_health_metrics()
        root_causes = self.analyze_root_causes()
        
        # Create plots first
        time_series_plot = self.create_time_series_plot()
        anomaly_plot = self.create_anomaly_distribution_plot()
        
        # Create PDF
        pdf_path = f"reports/health_report_{self.report_timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("API System Health Report", title_style))
        story.append(Spacer(1, 12))
        
        # Report info
        story.append(Paragraph(f"Generated: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Analysis Period: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        
        health_color = 'green' if metrics['health_score'] > 80 else 'orange' if metrics['health_score'] > 60 else 'red'
        story.append(Paragraph(f"<b>Overall Health Score: {metrics['health_score']}/100</b>", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Requests', f"{metrics['total_requests']:,}"],
            ['Anomalies Detected', str(metrics['anomaly_count'])],
            ['Anomaly Rate', f"{metrics['anomaly_rate']:.2%}"],
            ['Pod Restarts', str(metrics['pod_restarts'])],
            ['Avg CPU Usage', f"{metrics['avg_cpu']}%"],
            ['Avg Memory Usage', f"{metrics['avg_memory']} MB"],
            ['Avg Response Time', f"{metrics['avg_response_time']} ms"]
        ]
        
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(PageBreak())
        
        # Time series plot
        story.append(Paragraph("System Performance Over Time", styles['Heading2']))
        story.append(Image(time_series_plot, width=7*inch, height=5.6*inch))
        story.append(PageBreak())
        
        # Anomaly analysis plot
        story.append(Paragraph("Anomaly Analysis", styles['Heading2']))
        story.append(Image(anomaly_plot, width=7*inch, height=4.67*inch))
        story.append(Spacer(1, 20))
        
        # Root cause analysis
        story.append(Paragraph("Root Cause Analysis", styles['Heading2']))
        
        if root_causes:
            for cause in root_causes[:10]:  # Limit to top 10
                story.append(Paragraph(f"<b>{cause['timestamp'].strftime('%Y-%m-%d %H:%M')} - {cause['severity']} Severity</b>", styles['Normal']))
                story.append(Paragraph(f"Anomalies: {cause['anomaly_count']}", styles['Normal']))
                for root_cause in cause['causes']:
                    story.append(Paragraph(f"• {root_cause}", styles['Normal']))
                story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("No significant anomalies detected during the analysis period.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return pdf_path

def main():
    """Main execution function"""
    print("=== Health Report Generator ===")
    
    # Check if results file exists
    results_path = "data/anomaly_results.csv"
    if not os.path.exists(results_path):
        print(f"Error: Results file not found at {results_path}")
        print("Please run sagemaker_model.py first to generate anomaly detection results")
        return
    
    # Initialize report generator
    generator = HealthReportGenerator(results_path)
    
    print("Generating comprehensive health report...")
    
    # Generate HTML report
    html_path = generator.generate_html_report()
    print(f"HTML report generated: {html_path}")
    
    # Generate PDF report
    try:
        pdf_path = generator.generate_pdf_report()
        print(f"PDF report generated: {pdf_path}")
    except Exception as e:
        print(f"Warning: PDF generation failed: {e}")
        print("HTML report is still available")
    
    # Print summary
    metrics = generator.calculate_health_metrics()
    print(f"\n=== Report Summary ===")
    print(f"Health Score: {metrics['health_score']}/100")
    print(f"Total Requests Analyzed: {metrics['total_requests']:,}")
    print(f"Anomalies Detected: {metrics['anomaly_count']}")
    print(f"Anomaly Rate: {metrics['anomaly_rate']:.2%}")
    
    if metrics['health_score'] > 80:
        print("✅ System health is GOOD")
    elif metrics['health_score'] > 60:
        print("⚠️  System health is FAIR - monitoring recommended")
    else:
        print("🚨 System health is POOR - immediate attention required")

if __name__ == "__main__":
    main()