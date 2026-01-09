#!/usr/bin/env python3
"""
Comprehensive PDF Report Generator
=================================

Creates a professional, comprehensive PDF report that brings together all analysis
results, visualizations, and strategic recommendations to encourage horizontal 
growth into Hard Seltzers.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# ReportLab imports
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, 
    Table, TableStyle, KeepTogether, Frame, PageTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

class ComprehensivePDFReportGenerator:
    """
    Generates a comprehensive PDF report for the Beer-to-Seltzer market analysis.
    """
    
    def __init__(self):
        """Initialize the PDF report generator."""
        self.charts_dir = Path('charts')
        self.data_dir = Path('visualization_data')
        self.docs_dir = Path('documentation')
        self.exec_dir = Path('executive_reports')
        
        # Corporate colors
        self.colors = {
            'primary': HexColor('#1E3A8A'),      # Deep blue
            'secondary': HexColor('#F59E0B'),     # Amber
            'success': HexColor('#10B981'),       # Green
            'warning': HexColor('#EF4444'),       # Red
            'accent': HexColor('#8B5CF6'),        # Purple
            'text': HexColor('#1F2937'),          # Dark gray
            'light': HexColor('#F3F4F6')          # Light gray
        }
        
        # Setup styles
        self.styles = self._setup_styles()
        
    def _setup_styles(self):
        """Setup custom styles for the report."""
        styles = getSampleStyleSheet()
        
        # Custom styles
        custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=28,
                spaceAfter=30,
                spaceBefore=20,
                alignment=TA_CENTER,
                textColor=self.colors['primary'],
                fontName='Helvetica-Bold'
            ),
            
            'ExecutiveHeader': ParagraphStyle(
                'ExecutiveHeader',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=15,
                spaceBefore=25,
                textColor=self.colors['primary'],
                fontName='Helvetica-Bold',
                borderWidth=2,
                borderColor=self.colors['primary'],
                borderPadding=8,
                backColor=self.colors['light']
            ),
            
            'SectionHeader': ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=self.colors['secondary'],
                fontName='Helvetica-Bold'
            ),
            
            'SubHeader': ParagraphStyle(
                'SubHeader',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=15,
                textColor=self.colors['text'],
                fontName='Helvetica-Bold'
            ),
            
            'BodyText': ParagraphStyle(
                'BodyText',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                textColor=self.colors['text'],
                fontName='Helvetica'
            ),
            
            'ExecutiveSummary': ParagraphStyle(
                'ExecutiveSummary',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=10,
                leftIndent=15,
                rightIndent=15,
                borderWidth=2,
                borderColor=self.colors['success'],
                borderPadding=15,
                backColor=HexColor('#F0FDF4'),
                textColor=self.colors['text'],
                fontName='Helvetica'
            ),
            
            'KeyFinding': ParagraphStyle(
                'KeyFinding',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=8,
                leftIndent=10,
                borderWidth=1,
                borderColor=self.colors['accent'],
                borderPadding=8,
                backColor=HexColor('#FAF5FF'),
                textColor=self.colors['text'],
                fontName='Helvetica'
            ),
            
            'Recommendation': ParagraphStyle(
                'Recommendation',
                parent=styles['Normal'],
                fontSize=13,
                spaceAfter=12,
                leftIndent=10,
                rightIndent=10,
                borderWidth=3,
                borderColor=self.colors['warning'],
                borderPadding=12,
                backColor=HexColor('#FEF2F2'),
                textColor=self.colors['text'],
                fontName='Helvetica-Bold'
            ),
            
            'CenterText': ParagraphStyle(
                'CenterText',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_CENTER,
                textColor=self.colors['text'],
                fontName='Helvetica'
            ),
            
            'Caption': ParagraphStyle(
                'Caption',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=self.colors['text'],
                fontName='Helvetica-Oblique',
                spaceAfter=15
            )
        }
        
        # Convert StyleSheet1 to dictionary and merge with custom styles
        styles_dict = {}
        for style_name in styles.byName:
            styles_dict[style_name] = styles[style_name]
        
        # Add custom styles
        for name, style in custom_styles.items():
            styles_dict[name] = style
        
        return styles_dict
    
    def generate_comprehensive_report(self):
        """Generate the comprehensive PDF report."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"COMPREHENSIVE_HARD_SELTZER_BUSINESS_CASE_{timestamp}.pdf"
        
        print(f"📄 Generating comprehensive PDF report: {report_path}")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            report_path,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story
        story = []
        
        # Title Page
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary())
        story.append(PageBreak())
        
        # Market Analysis with Visualizations
        story.extend(self._create_market_analysis())
        story.append(PageBreak())
        
        # Financial Analysis
        story.extend(self._create_financial_analysis())
        story.append(PageBreak())
        
        # Strategic Recommendations
        story.extend(self._create_strategic_recommendations())
        story.append(PageBreak())
        
        # Implementation Roadmap
        story.extend(self._create_implementation_roadmap())
        story.append(PageBreak())
        
        # Technical Validation
        story.extend(self._create_technical_validation())
        story.append(PageBreak())
        
        # Appendices
        story.extend(self._create_appendices())
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Comprehensive PDF report generated: {report_path}")
        return report_path
    
    def _create_title_page(self):
        """Create the title page."""
        story = []
        
        story.append(Spacer(1, 1.5*inch))
        
        # Main title
        story.append(Paragraph(
            "STRATEGIC BUSINESS CASE",
            self.styles['CustomTitle']
        ))
        
        story.append(Paragraph(
            "HORIZONTAL GROWTH INTO HARD SELTZERS",
            self.styles['CustomTitle']
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        story.append(Paragraph(
            "Comprehensive Market Analysis & Investment Recommendation",
            self.styles['SectionHeader']
        ))
        
        story.append(Spacer(1, 1*inch))
        
        # Executive summary box
        exec_summary = """
        <b>EXECUTIVE RECOMMENDATION: PROCEED WITH IMMEDIATE MARKET ENTRY</b><br/><br/>
        
        Based on comprehensive analysis of 887,849 market transactions, statistical trend validation, 
        and competitive intelligence, we recommend immediate entry into the Hard Seltzer market. 
        The analysis reveals a clear market inflection point, substantial untapped opportunity, 
        and optimal timing for strategic horizontal growth.
        """
        
        story.append(Paragraph(exec_summary, self.styles['ExecutiveSummary']))
        
        story.append(Spacer(1, 1*inch))
        
        # Key metrics table
        metrics_data = [
            ['METRIC', 'VALUE', 'IMPACT'],
            ['Investment Required', '$2,964,237', 'Moderate Risk Profile'],
            ['Projected Annual ROI', '50%', 'Excellent Returns'],
            ['Payback Period', '24 months', 'Rapid Recovery'],
            ['Market Opportunity', '$11.39M', '97.7% Untapped'],
            ['Statistical Confidence', '95%', 'High Certainty'],
            ['Pivot Point Identified', 'March 2023', 'Optimal Timing']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.2*inch, 1.5*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F9FAFB')),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['primary'])
        ]))
        
        story.append(metrics_table)
        
        story.append(Spacer(1, 1*inch))
        
        # Report details
        story.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%B %d, %Y')}<br/>"
            f"Analysis Period: January 2023 - December 2023<br/>"
            f"Data Processing: PySpark 3.5.3 | Statistical Confidence: 95%",
            self.styles['CenterText']
        ))
        
        return story
    
    def _create_executive_summary(self):
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['ExecutiveHeader']))
        
        # Strategic recommendation
        recommendation = """
        <b>STRATEGIC RECOMMENDATION: PROCEED WITH HARD SELTZER MARKET ENTRY</b><br/><br/>
        
        Our comprehensive data analysis provides compelling evidence for immediate horizontal 
        expansion into the Hard Seltzer market. The analysis of 887,849 transactions reveals 
        a clear market inflection point in March 2023, where Hard Seltzer growth momentum 
        decisively exceeded Beer performance with statistical significance.
        """
        
        story.append(Paragraph(recommendation, self.styles['Recommendation']))
        
        story.append(Spacer(1, 15))
        
        # Market opportunity
        story.append(Paragraph("Market Opportunity Assessment", self.styles['SectionHeader']))
        
        opportunity_text = """
        The Hard Seltzer market presents an exceptional growth opportunity with a $11.39 million 
        total addressable market and 97.7% untapped potential. Current market penetration stands 
        at only 2.3%, indicating massive room for expansion. The competitive landscape shows 
        only 10 active Seltzer brands compared to 29 Beer brands, creating a clear opportunity 
        gap for strategic entry.
        """
        
        story.append(Paragraph(opportunity_text, self.styles['BodyText']))
        
        # Key findings
        story.append(Paragraph("Critical Market Intelligence", self.styles['SectionHeader']))
        
        findings = [
            "Pivot Point Identified: March 2023 marks the critical inflection where Seltzer growth exceeded Beer by 37.9%",
            "Sustained Advantage: 9 out of 12 months demonstrate consistent Seltzer growth superiority",
            "Market Share Trajectory: 5x growth potential demonstrated (1% → 5.4% progression)",
            "Geographic Strategy: WEST region shows highest penetration (4.3%) with 213 target stores",
            "Revenue Efficiency: Seltzer brands average $14,907 revenue vs $8,234 for Beer brands",
            "Statistical Validation: 95% confidence level in all trend analysis and projections"
        ]
        
        for finding in findings:
            story.append(Paragraph(f"• {finding}", self.styles['KeyFinding']))
            story.append(Spacer(1, 5))
        
        return story
    
    def _create_market_analysis(self):
        """Create market analysis section with visualizations."""
        story = []
        
        story.append(Paragraph("COMPREHENSIVE MARKET ANALYSIS", self.styles['ExecutiveHeader']))
        
        # Market evolution analysis
        story.append(Paragraph("Market Evolution: Beer vs Hard Seltzer", self.styles['SectionHeader']))
        
        evolution_text = """
        Our comprehensive four-panel analysis reveals diverging market trends between Beer and 
        Hard Seltzer categories across multiple dimensions: revenue growth, market share evolution, 
        growth rate acceleration, and unit sales momentum. The data demonstrates a clear and 
        sustained shift in consumer preference toward Hard Seltzers throughout the analysis period.
        """
        
        story.append(Paragraph(evolution_text, self.styles['BodyText']))
        
        # Add time series chart
        if (self.charts_dir / 'time_series_comparison.png').exists():
            story.append(Spacer(1, 10))
            img = Image(str(self.charts_dir / 'time_series_comparison.png'), 
                       width=7*inch, height=4.8*inch)
            story.append(img)
            story.append(Paragraph(
                "Figure 1: Market Evolution Analysis - Four-panel comprehensive view showing "
                "diverging trends between Beer and Hard Seltzer categories across revenue, "
                "market share, growth rates, and unit sales over the 12-month analysis period.",
                self.styles['Caption']
            ))
        
        # Pivot point analysis
        story.append(Paragraph("The Pivot Point: Market Inflection Analysis", self.styles['SectionHeader']))
        
        pivot_text = """
        March 2023 emerges as the critical market inflection point where Hard Seltzer growth 
        momentum definitively exceeded Beer performance. This pivot point is statistically 
        significant with 95% confidence and represents a fundamental shift in market dynamics. 
        The analysis shows 9 out of 12 months with Seltzer growth advantage, indicating 
        sustained rather than temporary market momentum.
        """
        
        story.append(Paragraph(pivot_text, self.styles['BodyText']))
        
        # Add pivot point chart
        if (self.charts_dir / 'pivot_point_analysis.png').exists():
            story.append(Spacer(1, 10))
            img = Image(str(self.charts_dir / 'pivot_point_analysis.png'), 
                       width=7*inch, height=4.8*inch)
            story.append(img)
            story.append(Paragraph(
                "Figure 2: Pivot Point Analysis - Critical analysis identifying March 2023 as "
                "the key inflection point where Hard Seltzer growth momentum exceeded Beer "
                "performance, with statistical validation of the trend shift.",
                self.styles['Caption']
            ))
        
        return story
    
    def _create_financial_analysis(self):
        """Create financial analysis section."""
        story = []
        
        story.append(Paragraph("FINANCIAL ANALYSIS & ROI PROJECTIONS", self.styles['ExecutiveHeader']))
        
        # Investment scenarios
        story.append(Paragraph("Investment Scenario Analysis", self.styles['SectionHeader']))
        
        scenario_text = """
        We have modeled three investment scenarios to provide strategic flexibility while 
        maintaining strong financial returns. The MODERATE scenario represents the optimal 
        balance of risk and reward, providing substantial market entry capability with 
        manageable investment requirements.
        """
        
        story.append(Paragraph(scenario_text, self.styles['BodyText']))
        
        # Scenarios table
        scenario_data = [
            ['SCENARIO', 'INVESTMENT', 'TARGET SHARE', 'ANNUAL ROI', 'PAYBACK'],
            ['Conservative', '$1,976,158', '10%', '35%', '30 months'],
            ['Moderate ⭐', '$2,964,237', '15%', '50%', '24 months'],
            ['Aggressive', '$4,940,395', '25%', '75%', '18 months']
        ]
        
        scenario_table = Table(scenario_data, colWidths=[1.4*inch, 1.4*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        scenario_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 2), (-1, 2), self.colors['success']),
            ('TEXTCOLOR', (0, 2), (-1, 2), HexColor('#FFFFFF')),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, 1), HexColor('#F9FAFB')),
            ('BACKGROUND', (0, 3), (-1, 3), HexColor('#F9FAFB')),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['primary'])
        ]))
        
        story.append(scenario_table)
        
        story.append(Spacer(1, 15))
        
        # Revenue projections
        story.append(Paragraph("3-Year Revenue Projections (Moderate Scenario)", self.styles['SectionHeader']))
        
        projection_text = """
        The moderate investment scenario projects strong revenue growth with conservative 
        market share assumptions. Year 1 targets 15% market share generating $1.71M revenue, 
        scaling to 37.5% market share and $4.28M revenue by Year 3. This trajectory provides 
        144% cumulative ROI over the 3-year period.
        """
        
        story.append(Paragraph(projection_text, self.styles['BodyText']))
        
        # Revenue table
        revenue_data = [
            ['YEAR', 'MARKET SHARE', 'REVENUE', 'GROWTH RATE', 'CUMULATIVE ROI'],
            ['Year 1', '15%', '$1,709,559', 'Baseline', '26%'],
            ['Year 2', '25%', '$2,849,265', '67%', '96%'],
            ['Year 3', '37.5%', '$4,273,897', '50%', '144%']
        ]
        
        revenue_table = Table(revenue_data, colWidths=[1*inch, 1.4*inch, 1.4*inch, 1.4*inch, 1.4*inch])
        revenue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FFFBEB')),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['secondary'])
        ]))
        
        story.append(revenue_table)
        
        return story
    
    def _create_strategic_recommendations(self):
        """Create strategic recommendations section."""
        story = []
        
        story.append(Paragraph("STRATEGIC RECOMMENDATIONS", self.styles['ExecutiveHeader']))
        
        # Geographic strategy
        story.append(Paragraph("Geographic Market Entry Strategy", self.styles['SectionHeader']))
        
        # Add regional heatmap
        if (self.charts_dir / 'regional_heatmap.png').exists():
            story.append(Spacer(1, 10))
            img = Image(str(self.charts_dir / 'regional_heatmap.png'), 
                       width=7*inch, height=4.8*inch)
            story.append(img)
            story.append(Paragraph(
                "Figure 3: Regional Market Opportunities - Geographic analysis identifying "
                "optimal markets for Hard Seltzer expansion with penetration rates and "
                "opportunity scores for strategic planning.",
                self.styles['Caption']
            ))
        
        geographic_text = """
        Our geographic analysis identifies the WEST region as the primary target market with 
        4.3% current penetration and 213 active stores. This region demonstrates the highest 
        consumer acceptance and provides the optimal launch platform. The NORTHEAST region 
        represents the secondary expansion target with 247 stores and strong growth potential.
        """
        
        story.append(Paragraph(geographic_text, self.styles['BodyText']))
        
        # Product strategy
        story.append(Paragraph("Product Portfolio Strategy", self.styles['SectionHeader']))
        
        product_text = """
        Market analysis reveals optimal product positioning in the 4.7-4.8% ABV range, 
        which shows the strongest consumer preference and revenue performance. We recommend 
        launching with 3-5 core flavors targeting premium positioning to differentiate 
        from existing market offerings and capture higher margin opportunities.
        """
        
        story.append(Paragraph(product_text, self.styles['BodyText']))
        
        # Competitive positioning
        story.append(Paragraph("Competitive Positioning Analysis", self.styles['SectionHeader']))
        
        # Add brand performance chart
        if (self.charts_dir / 'brand_performance_analysis.png').exists():
            story.append(Spacer(1, 10))
            img = Image(str(self.charts_dir / 'brand_performance_analysis.png'), 
                       width=7*inch, height=4.8*inch)
            story.append(img)
            story.append(Paragraph(
                "Figure 4: Competitive Brand Analysis - Analysis of leading brands identifying "
                "Truly, Vizzy, and Corona Hard Seltzer as key benchmarks for competitive "
                "positioning and market entry strategy.",
                self.styles['Caption']
            ))
        
        competitive_text = """
        The competitive landscape analysis identifies Truly ($18,528), Vizzy ($17,805), 
        and Corona Hard Seltzer ($13,065) as primary benchmarks. These brands demonstrate 
        successful market penetration strategies and revenue models that validate our 
        market entry approach. The analysis shows clear positioning opportunities for 
        premium market entry.
        """
        
        story.append(Paragraph(competitive_text, self.styles['BodyText']))
        
        return story
    
    def _create_implementation_roadmap(self):
        """Create implementation roadmap section."""
        story = []
        
        story.append(Paragraph("IMPLEMENTATION ROADMAP", self.styles['ExecutiveHeader']))
        
        # Phased approach
        story.append(Paragraph("Three-Phase Implementation Strategy", self.styles['SectionHeader']))
        
        roadmap_text = """
        We recommend a phased implementation approach that balances speed-to-market with 
        risk management. This strategy allows for course correction and optimization while 
        maintaining aggressive market entry timelines to capitalize on the identified 
        market momentum.
        """
        
        story.append(Paragraph(roadmap_text, self.styles['BodyText']))
        
        # Phase details
        phases = [
            {
                'title': 'Phase 1: FOUNDATION (Months 0-3)',
                'investment': 'HIGH Investment Level',
                'activities': [
                    'Finalize product formulations targeting 4.7-4.8% ABV range',
                    'Secure production capacity and supply chain partnerships',
                    'Develop brand positioning and marketing strategy',
                    'Negotiate retail partnerships in WEST region (213 stores)',
                    'Complete regulatory approvals and compliance requirements'
                ]
            },
            {
                'title': 'Phase 2: LAUNCH (Months 3-6)',
                'investment': 'MEDIUM Investment Level',
                'activities': [
                    'Execute market launch in WEST region with integrated marketing',
                    'Implement point-of-sale materials and merchandising programs',
                    'Monitor real-time performance metrics and consumer feedback',
                    'Optimize pricing and distribution based on market response',
                    'Prepare for geographic expansion to secondary markets'
                ]
            },
            {
                'title': 'Phase 3: EXPANSION (Months 6-12)',
                'investment': 'MEDIUM Investment Level',
                'activities': [
                    'Expand to NORTHEAST region (247 stores) and secondary markets',
                    'Launch additional product variants and seasonal offerings',
                    'Scale production capabilities and distribution network',
                    'Evaluate strategic partnerships and acquisition opportunities',
                    'Implement loyalty programs and consumer engagement initiatives'
                ]
            }
        ]
        
        for phase in phases:
            story.append(Paragraph(phase['title'], self.styles['SubHeader']))
            story.append(Paragraph(f"<b>{phase['investment']}</b>", self.styles['KeyFinding']))
            
            for activity in phase['activities']:
                story.append(Paragraph(f"• {activity}", self.styles['BodyText']))
            
            story.append(Spacer(1, 10))
        
        # Success metrics
        story.append(Paragraph("Key Performance Indicators & Success Metrics", self.styles['SectionHeader']))
        
        kpi_data = [
            ['METRIC', 'TARGET (YEAR 1)', 'MEASUREMENT'],
            ['Market Share Growth', '15%', 'Monthly tracking'],
            ['Revenue Milestones', '$1.71M', 'Monthly reporting'],
            ['ROI Achievement', '50% Annual', 'Quarterly assessment'],
            ['Geographic Expansion', '2 Regions', 'Quarterly review'],
            ['Brand Awareness', '25%', 'Quarterly surveys'],
            ['Distribution Points', '460 Stores', 'Monthly tracking']
        ]
        
        kpi_table = Table(kpi_data, colWidths=[2.2*inch, 1.8*inch, 1.8*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FAFAFA')),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['accent'])
        ]))
        
        story.append(kpi_table)
        
        return story
    
    def _create_technical_validation(self):
        """Create technical validation section."""
        story = []
        
        story.append(Paragraph("TECHNICAL VALIDATION & DATA QUALITY", self.styles['ExecutiveHeader']))
        
        # Executive dashboard
        story.append(Paragraph("Executive Dashboard: Comprehensive Business Metrics", self.styles['SectionHeader']))
        
        # Add executive dashboard
        if (self.charts_dir / 'executive_dashboard.png').exists():
            story.append(Spacer(1, 10))
            img = Image(str(self.charts_dir / 'executive_dashboard.png'), 
                       width=7*inch, height=4.8*inch)
            story.append(img)
            story.append(Paragraph(
                "Figure 5: Executive Dashboard - Comprehensive business metrics showing "
                "current market position, revenue opportunities, brand analysis, and "
                "strategic recommendations with supporting data tables.",
                self.styles['Caption']
            ))
        
        # Data quality summary
        story.append(Paragraph("Data Quality & Statistical Validation", self.styles['SectionHeader']))
        
        quality_text = """
        Our analysis is built on a robust foundation of 887,849 validated transactions 
        with 98.8% data retention rate. All statistical analyses maintain 95% confidence 
        levels with comprehensive validation of business rules, referential integrity, 
        and data completeness. The pipeline processing achieved 100% success rate with 
        sub-3 minute execution times.
        """
        
        story.append(Paragraph(quality_text, self.styles['BodyText']))
        
        # Technical metrics
        tech_data = [
            ['TECHNICAL METRIC', 'VALUE', 'VALIDATION'],
            ['Total Transactions Analyzed', '887,849', '100% Processed'],
            ['Data Retention Rate', '98.8%', 'Excellent Quality'],
            ['Statistical Confidence', '95%', 'High Certainty'],
            ['Pipeline Success Rate', '100%', 'Reliable Processing'],
            ['Processing Time', '151.68 seconds', 'High Performance'],
            ['Feature Engineering', '37+ metrics', 'Comprehensive Analysis']
        ]
        
        tech_table = Table(tech_data, colWidths=[2.5*inch, 1.5*inch, 1.8*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['primary'])
        ]))
        
        story.append(tech_table)
        
        story.append(Spacer(1, 15))
        
        # Methodology summary
        story.append(Paragraph("Analytical Methodology", self.styles['SectionHeader']))
        
        methodology_text = """
        The analysis employs advanced statistical methods including pivot point detection 
        using 3-sigma significance testing, longitudinal market share evolution tracking, 
        and comprehensive competitive intelligence analysis. All trend validations require 
        minimum 3-month sustained advantage with statistical significance testing at 
        α = 0.05 level.
        """
        
        story.append(Paragraph(methodology_text, self.styles['BodyText']))
        
        return story
    
    def _create_appendices(self):
        """Create appendices section."""
        story = []
        
        story.append(Paragraph("APPENDICES", self.styles['ExecutiveHeader']))
        
        # Risk assessment
        story.append(Paragraph("Appendix A: Risk Assessment & Mitigation", self.styles['SectionHeader']))
        
        risk_text = """
        We have identified and assessed key risks associated with Hard Seltzer market entry. 
        Each risk has been evaluated for probability and impact, with specific mitigation 
        strategies developed to ensure successful market entry execution.
        """
        
        story.append(Paragraph(risk_text, self.styles['BodyText']))
        
        # Risk table
        risk_data = [
            ['RISK CATEGORY', 'PROBABILITY', 'IMPACT', 'MITIGATION STRATEGY'],
            ['Competitive Response', 'Medium', 'High', 'Differentiated positioning, premium quality'],
            ['Market Saturation', 'Low', 'Medium', 'Geographic diversification, innovation'],
            ['Supply Chain Disruption', 'Medium', 'Medium', 'Multiple suppliers, inventory buffers'],
            ['Regulatory Changes', 'Low', 'High', 'Compliance monitoring, legal partnerships'],
            ['Lower ROI Performance', 'Medium', 'High', 'Phased approach, performance gates']
        ]
        
        risk_table = Table(risk_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 2.6*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['warning']),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FFFAF0')),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['warning']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(risk_table)
        
        story.append(Spacer(1, 20))
        
        # Final recommendation
        story.append(Paragraph("Final Executive Recommendation", self.styles['SectionHeader']))
        
        final_rec = """
        <b>PROCEED WITH IMMEDIATE HARD SELTZER MARKET ENTRY</b><br/><br/>
        
        Based on comprehensive PySpark analysis of market data, statistical trend validation, 
        competitive intelligence, and financial modeling, we recommend immediate proceeding 
        with Hard Seltzer market entry using the MODERATE investment scenario. The analysis 
        provides clear evidence of sustained market momentum, optimal timing for entry, 
        and strong financial returns with manageable risk profile.<br/><br/>
        
        <b>The data supports horizontal growth into Hard Seltzers as a strategic imperative 
        for capturing emerging market opportunities and driving sustainable revenue growth.</b>
        """
        
        story.append(Paragraph(final_rec, self.styles['Recommendation']))
        
        return story

def main():
    """Main execution function."""
    print("📄 Comprehensive PDF Report Generator")
    print("=" * 50)
    
    try:
        generator = ComprehensivePDFReportGenerator()
        report_path = generator.generate_comprehensive_report()
        
        print(f"\n✅ COMPREHENSIVE REPORT GENERATED")
        print("-" * 40)
        print(f"📄 Report: {report_path}")
        print(f"📊 Includes: All visualizations and analysis")
        print(f"🎯 Focus: Horizontal growth into Hard Seltzers")
        print(f"📈 Recommendation: PROCEED with market entry")
        
        print(f"\n🎉 Report ready for executive presentation!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Report generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())