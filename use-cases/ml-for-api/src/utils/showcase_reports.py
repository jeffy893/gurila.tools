#!/usr/bin/env python3.10
"""
Showcase Script for ML for API Service Reports
Demonstrates the PNG integration in both HTML and PDF reports.
"""

import os
import webbrowser
from pathlib import Path

def showcase_reports():
    """Display information about generated reports and their PNG integration"""
    
    print("🎨 ML for API Service - Report Showcase")
    print("=" * 60)
    
    # Check for generated files
    reports_dir = Path("reports")
    images_dir = reports_dir / "images"
    demo_dir = reports_dir / "demo"
    
    # Find the latest HTML and PDF reports
    html_reports = list(reports_dir.glob("health_report_*.html"))
    pdf_reports = list(reports_dir.glob("health_report_*.pdf"))
    
    if html_reports:
        latest_html = max(html_reports, key=os.path.getctime)
        print(f"📄 Latest HTML Report: {latest_html}")
        
    if pdf_reports:
        latest_pdf = max(pdf_reports, key=os.path.getctime)
        print(f"📄 Latest PDF Report: {latest_pdf}")
    
    # Show PNG files
    print(f"\n🖼️  Generated PNG Visualizations:")
    
    png_files = [
        ("Time Series Plot", "time_series_plot.png"),
        ("Anomaly Analysis", "anomaly_analysis.png"), 
        ("Demo Visualization", "demo_visualization.png")
    ]
    
    for name, filename in png_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename) / 1024  # KB
            print(f"   ✅ {name}: {filename} ({size:.1f} KB)")
        else:
            print(f"   ❌ {name}: {filename} (not found)")
    
    # Show integration details
    print(f"\n🔗 PNG Integration Details:")
    print(f"   • HTML Reports: PNGs embedded via <img> tags with relative paths")
    print(f"   • PDF Reports: PNGs embedded directly using ReportLab Image objects")
    print(f"   • All images: High-resolution (300 DPI) for crisp display")
    print(f"   • Responsive: Images scale automatically in HTML reports")
    
    # Show file structure
    print(f"\n📁 File Structure:")
    print(f"   reports/")
    print(f"   ├── images/")
    print(f"   │   ├── time_series_plot.png")
    print(f"   │   └── anomaly_analysis.png")
    print(f"   ├── demo/")
    print(f"   │   ├── demo_visualization.png")
    print(f"   │   └── demo_report.html")
    print(f"   ├── health_report_YYYYMMDD_HHMMSS.html")
    print(f"   └── health_report_YYYYMMDD_HHMMSS.pdf")
    
    # Show sample metrics from latest report
    if html_reports:
        print(f"\n📊 Sample Report Metrics:")
        try:
            with open(latest_html, 'r') as f:
                content = f.read()
                
            # Extract some key metrics
            if "Health Score:" in content:
                start = content.find("Health Score:") + len("Health Score:")
                end = content.find("/100", start) + 4
                health_score = content[start:end].strip()
                print(f"   • Overall {health_score}")
                
            if "Total Requests:" in content:
                start = content.find("Total Requests:</strong>") + len("Total Requests:</strong>")
                end = content.find("</div>", start)
                total_requests = content[start:end].strip()
                print(f"   • Total Requests: {total_requests}")
                
            if "Anomalies Detected:" in content:
                start = content.find("Anomalies Detected:</strong>") + len("Anomalies Detected:</strong>")
                end = content.find("</div>", start)
                anomalies = content[start:end].strip()
                print(f"   • Anomalies Detected: {anomalies}")
                
        except Exception as e:
            print(f"   Could not parse report metrics: {e}")
    
    # Offer to open reports
    print(f"\n🌐 View Reports:")
    if html_reports:
        print(f"   To view HTML report: open {latest_html}")
        
        # Try to open in browser (optional)
        try:
            response = input("   Open HTML report in browser? (y/n): ").lower().strip()
            if response == 'y':
                webbrowser.open(f"file://{os.path.abspath(latest_html)}")
                print("   ✅ Opened in default browser")
        except KeyboardInterrupt:
            print("\n   Skipped browser opening")
    
    if pdf_reports:
        print(f"   To view PDF report: open {latest_pdf}")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"   ✅ Synthetic data generation with realistic anomaly patterns")
    print(f"   ✅ ML-powered anomaly detection using Isolation Forest")
    print(f"   ✅ High-quality PNG visualization generation")
    print(f"   ✅ Seamless PNG integration in HTML reports")
    print(f"   ✅ Professional PDF reports with embedded images")
    print(f"   ✅ Root cause analysis and health scoring")
    print(f"   ✅ Production-ready AWS architecture documentation")
    
    print(f"\n" + "=" * 60)
    print(f"🎉 Report showcase complete!")

if __name__ == "__main__":
    showcase_reports()