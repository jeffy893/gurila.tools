#!/usr/bin/env python3
"""
Beer vs Seltzer Market Analysis Visualization Suite
==================================================

Creates compelling visualizations to support the business case for Hard Seltzer market entry.
Generates publication-ready charts showing market trends, pivot points, and strategic insights.

Key Visualizations:
- Time series trends (Beer vs Seltzer)
- Market share evolution
- Pivot point identification
- Regional performance heatmaps
- Growth rate comparisons
- Executive dashboard charts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class BeerSeltzerVisualizationSuite:
    """
    Comprehensive visualization suite for Beer vs Seltzer market analysis.
    """
    
    def __init__(self, data_dir: str = "visualization_data", output_dir: str = "charts"):
        """Initialize the visualization suite."""
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.datasets = {}
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Color scheme for consistent branding
        self.colors = {
            'beer': '#D4A574',      # Golden beer color
            'seltzer': '#4A90E2',   # Fresh blue for seltzer
            'pivot': '#E74C3C',     # Red for pivot points
            'growth': '#27AE60',    # Green for growth
            'decline': '#E67E22',   # Orange for decline
            'neutral': '#95A5A6'    # Gray for neutral
        }
        
    def load_datasets(self):
        """Load all visualization datasets."""
        print("📊 Loading visualization datasets...")
        
        try:
            # Load key datasets
            dataset_files = [
                'monthly_time_series.csv',
                'pivot_point_analysis.csv',
                'regional_category_analysis.csv',
                'category_performance.csv',
                'brand_performance.csv',
                'daily_time_series.csv',
                'executive_kpis.csv'
            ]
            
            for file in dataset_files:
                file_path = os.path.join(self.data_dir, file)
                if os.path.exists(file_path):
                    dataset_name = file.replace('.csv', '')
                    self.datasets[dataset_name] = pd.read_csv(file_path)
                    print(f"  ✅ Loaded {dataset_name}: {len(self.datasets[dataset_name]):,} records")
                else:
                    print(f"  ⚠️  File not found: {file}")
            
            # Prepare data for visualization
            self._prepare_data()
            
            print(f"✅ All datasets loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading datasets: {str(e)}")
            raise
    
    def _prepare_data(self):
        """Prepare and clean data for visualization."""
        # Convert date columns
        if 'monthly_time_series' in self.datasets:
            df = self.datasets['monthly_time_series']
            df['Date'] = pd.to_datetime(df['Year_Month'] + '-01')
            self.datasets['monthly_time_series'] = df
        
        if 'pivot_point_analysis' in self.datasets:
            df = self.datasets['pivot_point_analysis']
            df['Date'] = pd.to_datetime(df['Year_Month'] + '-01')
            self.datasets['pivot_point_analysis'] = df
        
        if 'daily_time_series' in self.datasets:
            df = self.datasets['daily_time_series']
            df['Date'] = pd.to_datetime(df['Date_String'])
            self.datasets['daily_time_series'] = df
    
    def create_time_series_comparison(self):
        """
        Create compelling time series comparison of Beer vs Seltzer trends.
        """
        print("📈 Creating time series comparison chart...")
        
        if 'monthly_time_series' not in self.datasets:
            print("⚠️  Monthly time series data not available")
            return
        
        df = self.datasets['monthly_time_series']
        
        # Prepare data
        beer_data = df[df['Product_Category'] == 'BEER'].copy()
        seltzer_data = df[df['Product_Category'] == 'HARD SELTZER'].copy()
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Beer vs Hard Seltzer Market Analysis: The Great Pivot', 
                     fontsize=20, fontweight='bold', y=0.98)
        
        # 1. Revenue Trends
        ax1.plot(beer_data['Date'], beer_data['Monthly_Revenue'], 
                color=self.colors['beer'], linewidth=3, label='Beer Revenue', marker='o')
        ax1.plot(seltzer_data['Date'], seltzer_data['Monthly_Revenue'], 
                color=self.colors['seltzer'], linewidth=3, label='Hard Seltzer Revenue', marker='s')
        
        ax1.set_title('Monthly Revenue Trends', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Revenue ($)', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Format y-axis as currency
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # 2. Market Share Evolution
        ax2.fill_between(beer_data['Date'], beer_data['Market_Share_Revenue'], 
                        color=self.colors['beer'], alpha=0.7, label='Beer Market Share')
        ax2.fill_between(seltzer_data['Date'], seltzer_data['Market_Share_Revenue'], 
                        color=self.colors['seltzer'], alpha=0.7, label='Seltzer Market Share')
        
        ax2.set_title('Market Share Evolution', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Market Share (%)', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylim(0, 100)
        
        # 3. Growth Rate Comparison
        ax3.bar(beer_data['Date'], beer_data['MoM_Growth_Rate'], 
               color=self.colors['beer'], alpha=0.7, label='Beer MoM Growth', width=20)
        ax3.bar(seltzer_data['Date'], seltzer_data['MoM_Growth_Rate'], 
               color=self.colors['seltzer'], alpha=0.7, label='Seltzer MoM Growth', width=20)
        
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax3.set_title('Month-over-Month Growth Rates', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Growth Rate (%)', fontsize=12)
        ax3.legend(fontsize=11)
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Units Sold Comparison
        ax4.plot(beer_data['Date'], beer_data['Monthly_Units'], 
                color=self.colors['beer'], linewidth=3, label='Beer Units', marker='o')
        ax4.plot(seltzer_data['Date'], seltzer_data['Monthly_Units'], 
                color=self.colors['seltzer'], linewidth=3, label='Seltzer Units', marker='s')
        
        ax4.set_title('Monthly Units Sold', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Units Sold', fontsize=12)
        ax4.legend(fontsize=11)
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(axis='x', rotation=45)
        
        # Format units with commas
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/time_series_comparison.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{self.output_dir}/time_series_comparison.pdf', bbox_inches='tight')
        plt.show()
        
        print("✅ Time series comparison chart created")
    
    def create_pivot_point_visualization(self):
        """
        Create dramatic pivot point visualization highlighting the market shift.
        """
        print("🎯 Creating pivot point visualization...")
        
        if 'pivot_point_analysis' not in self.datasets:
            print("⚠️  Pivot point data not available")
            return
        
        df = self.datasets['pivot_point_analysis']
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('THE PIVOT POINT: When Hard Seltzer Overtook Beer Growth', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        # 1. Growth Rate Difference with Pivot Points
        ax1.plot(df['Date'], df['Growth_Difference_MoM'], 
                color=self.colors['pivot'], linewidth=3, label='Growth Rate Difference (Seltzer - Beer)')
        
        # Highlight pivot points
        pivot_points = df[df['Pivot_Point_MoM'] == True]
        if not pivot_points.empty:
            ax1.scatter(pivot_points['Date'], pivot_points['Growth_Difference_MoM'], 
                       color=self.colors['pivot'], s=100, zorder=5, 
                       label=f'Pivot Points ({len(pivot_points)} months)')
        
        # Add zero line
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.7, label='Break-even Line')
        
        # Shade positive area
        ax1.fill_between(df['Date'], df['Growth_Difference_MoM'], 0, 
                        where=(df['Growth_Difference_MoM'] > 0), 
                        color=self.colors['seltzer'], alpha=0.3, label='Seltzer Advantage')
        
        # Shade negative area
        ax1.fill_between(df['Date'], df['Growth_Difference_MoM'], 0, 
                        where=(df['Growth_Difference_MoM'] < 0), 
                        color=self.colors['beer'], alpha=0.3, label='Beer Advantage')
        
        ax1.set_title('Growth Rate Advantage: Seltzer vs Beer', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Growth Rate Difference (%)', fontsize=12)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 2. Market Share Trends with Annotations
        ax2.plot(df['Date'], df['Beer_Market_Share'], 
                color=self.colors['beer'], linewidth=3, label='Beer Market Share', marker='o')
        ax2.plot(df['Date'], df['Seltzer_Market_Share'], 
                color=self.colors['seltzer'], linewidth=3, label='Seltzer Market Share', marker='s')
        
        # Add trend lines
        ax2.plot(df['Date'], df['Seltzer_Share_Trend'], 
                color=self.colors['seltzer'], linestyle='--', alpha=0.7, label='Seltzer Trend')
        
        # Annotate key points
        if not pivot_points.empty:
            first_pivot = pivot_points.iloc[0]
            ax2.annotate(f'First Pivot: {first_pivot["Month_Name"]} {first_pivot["Year"]}\n'
                        f'Seltzer: {first_pivot["Seltzer_Market_Share"]:.1f}%',
                        xy=(first_pivot['Date'], first_pivot['Seltzer_Market_Share']),
                        xytext=(10, 20), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc=self.colors['seltzer'], alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        ax2.set_title('Market Share Evolution: The Seltzer Rise', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Market Share (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/pivot_point_analysis.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{self.output_dir}/pivot_point_analysis.pdf', bbox_inches='tight')
        plt.show()
        
        print("✅ Pivot point visualization created")
    
    def create_regional_heatmap(self):
        """
        Create regional performance heatmap showing geographic opportunities.
        """
        print("🗺️  Creating regional heatmap...")
        
        if 'regional_category_analysis' not in self.datasets:
            print("⚠️  Regional data not available")
            return
        
        df = self.datasets['regional_category_analysis']
        
        # Remove duplicates and prepare data for heatmap
        df_clean = df.drop_duplicates(subset=['Store_Region', 'Product_Category'])
        pivot_data = df_clean.pivot(index='Store_Region', columns='Product_Category', values='Category_Penetration')
        
        # Create figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Regional Market Analysis: Geographic Opportunities', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        # 1. Category Penetration Heatmap
        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlBu_r', 
                   ax=ax1, cbar_kws={'label': 'Market Penetration (%)'})
        ax1.set_title('Category Penetration by Region', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Region', fontsize=12)
        
        # 2. Revenue by Region (Seltzer focus)
        seltzer_regional = df_clean[df_clean['Product_Category'] == 'HARD SELTZER'].copy()
        seltzer_regional = seltzer_regional.sort_values('Regional_Revenue', ascending=True)
        
        bars = ax2.barh(seltzer_regional['Store_Region'], seltzer_regional['Regional_Revenue'], 
                       color=self.colors['seltzer'], alpha=0.8)
        ax2.set_title('Hard Seltzer Revenue by Region', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Revenue ($)', fontsize=12)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                    f'${width:,.0f}', ha='left', va='center', fontsize=10)
        
        # 3. Store Count vs Revenue Scatter
        beer_regional = df_clean[df_clean['Product_Category'] == 'BEER']
        ax3.scatter(beer_regional['Regional_Stores'], beer_regional['Regional_Revenue'],
                   color=self.colors['beer'], alpha=0.7, s=100, label='Beer')
        ax3.scatter(seltzer_regional['Regional_Stores'], seltzer_regional['Regional_Revenue'],
                   color=self.colors['seltzer'], alpha=0.7, s=100, label='Hard Seltzer')
        
        # Add region labels
        for _, row in seltzer_regional.iterrows():
            ax3.annotate(row['Store_Region'], 
                        (row['Regional_Stores'], row['Regional_Revenue']),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax3.set_title('Store Count vs Revenue by Region', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Number of Stores', fontsize=12)
        ax3.set_ylabel('Revenue ($)', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Revenue per Store Analysis
        df_clean['Revenue_Per_Store'] = df_clean['Regional_Revenue'] / df_clean['Regional_Stores']
        
        beer_rps = beer_regional['Revenue_Per_Store']
        seltzer_rps = seltzer_regional['Revenue_Per_Store']
        regions = beer_regional['Store_Region']
        
        x = np.arange(len(regions))
        width = 0.35
        
        ax4.bar(x - width/2, beer_rps, width, label='Beer', color=self.colors['beer'], alpha=0.8)
        ax4.bar(x + width/2, seltzer_rps, width, label='Hard Seltzer', color=self.colors['seltzer'], alpha=0.8)
        
        ax4.set_title('Revenue per Store by Region', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Revenue per Store ($)', fontsize=12)
        ax4.set_xlabel('Region', fontsize=12)
        ax4.set_xticks(x)
        ax4.set_xticklabels(regions, rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/regional_heatmap.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{self.output_dir}/regional_heatmap.pdf', bbox_inches='tight')
        plt.show()
        
        print("✅ Regional heatmap created")
    
    def create_executive_dashboard(self):
        """
        Create executive dashboard with key metrics and insights.
        """
        print("📊 Creating executive dashboard...")
        
        if 'category_performance' not in self.datasets:
            print("⚠️  Category performance data not available")
            return
        
        df = self.datasets['category_performance']
        
        # Create figure
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        fig.suptitle('EXECUTIVE DASHBOARD: Beer vs Hard Seltzer Strategic Analysis', 
                     fontsize=24, fontweight='bold', y=0.98)
        
        # 1. Market Share Pie Chart (Top Left)
        ax1 = fig.add_subplot(gs[0, 0])
        sizes = df['Market_Share_Revenue'].values
        labels = df['Product_Category'].values
        colors = [self.colors['beer'] if 'BEER' in label else self.colors['seltzer'] for label in labels]
        
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                          startangle=90, textprops={'fontsize': 12})
        ax1.set_title('Market Share\n(Revenue)', fontsize=14, fontweight='bold')
        
        # 2. Revenue Comparison (Top Center-Left)
        ax2 = fig.add_subplot(gs[0, 1])
        bars = ax2.bar(df['Product_Category'], df['Total_Category_Revenue'], 
                      color=[self.colors['beer'] if 'BEER' in cat else self.colors['seltzer'] 
                            for cat in df['Product_Category']], alpha=0.8)
        ax2.set_title('Total Revenue\nComparison', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Revenue ($)', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'${height:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 3. Brand Count Comparison (Top Center-Right)
        ax3 = fig.add_subplot(gs[0, 2])
        bars = ax3.bar(df['Product_Category'], df['Category_Brand_Count'], 
                      color=[self.colors['beer'] if 'BEER' in cat else self.colors['seltzer'] 
                            for cat in df['Product_Category']], alpha=0.8)
        ax3.set_title('Active Brands\nby Category', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Number of Brands', fontsize=12)
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 4. Geographic Reach (Top Right)
        ax4 = fig.add_subplot(gs[0, 3])
        bars = ax4.bar(df['Product_Category'], df['Category_Geographic_Reach'], 
                      color=[self.colors['beer'] if 'BEER' in cat else self.colors['seltzer'] 
                            for cat in df['Product_Category']], alpha=0.8)
        ax4.set_title('Geographic Reach\n(Regions)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Number of Regions', fontsize=12)
        ax4.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 5. Key Metrics Table (Middle Row)
        ax5 = fig.add_subplot(gs[1, :])
        ax5.axis('tight')
        ax5.axis('off')
        
        # Create metrics table
        metrics_data = []
        for _, row in df.iterrows():
            metrics_data.append([
                row['Product_Category'],
                f"${row['Total_Category_Revenue']:,.0f}",
                f"{row['Market_Share_Revenue']:.1f}%",
                f"{row['Total_Category_Units']:,.0f}",
                f"{row['Category_Brand_Count']:.0f}",
                f"${row['Avg_Category_Transaction']:.2f}",
                f"${row['Revenue_Per_Brand']:,.0f}"
            ])
        
        table = ax5.table(cellText=metrics_data,
                         colLabels=['Category', 'Total Revenue', 'Market Share', 'Units Sold', 
                                   'Brands', 'Avg Transaction', 'Revenue/Brand'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(df)):
            for j in range(7):
                if i == 0:  # Beer row
                    table[(i+1, j)].set_facecolor(self.colors['beer'])
                    table[(i+1, j)].set_alpha(0.3)
                else:  # Seltzer row
                    table[(i+1, j)].set_facecolor(self.colors['seltzer'])
                    table[(i+1, j)].set_alpha(0.3)
        
        # Header styling
        for j in range(7):
            table[(0, j)].set_facecolor('#34495E')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        # 6. Strategic Insights (Bottom Row)
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        # Calculate key insights
        beer_row = df[df['Product_Category'] == 'BEER'].iloc[0]
        seltzer_row = df[df['Product_Category'] == 'HARD SELTZER'].iloc[0]
        
        market_opportunity = 100 - seltzer_row['Market_Share_Revenue']
        revenue_ratio = beer_row['Total_Category_Revenue'] / seltzer_row['Total_Category_Revenue']
        
        insights_text = f"""
STRATEGIC INSIGHTS & RECOMMENDATIONS:

🎯 MARKET OPPORTUNITY: {market_opportunity:.1f}% untapped market share available for Hard Seltzer expansion

💰 REVENUE POTENTIAL: Beer generates {revenue_ratio:.1f}x more revenue - massive growth opportunity for Seltzer

📈 BRAND EFFICIENCY: Seltzer achieves ${seltzer_row['Revenue_Per_Brand']:,.0f} per brand vs Beer's ${beer_row['Revenue_Per_Brand']:,.0f}

🚀 RECOMMENDATION: IMMEDIATE MARKET ENTRY with focus on high-performing regions and optimal product portfolio

⏰ TIMING: Market momentum favors Seltzer - capitalize on identified pivot point trends
        """
        
        ax6.text(0.05, 0.95, insights_text, transform=ax6.transAxes, fontsize=14,
                verticalalignment='top', bbox=dict(boxstyle='round,pad=1', 
                facecolor=self.colors['seltzer'], alpha=0.1))
        
        plt.savefig(f'{self.output_dir}/executive_dashboard.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{self.output_dir}/executive_dashboard.pdf', bbox_inches='tight')
        plt.show()
        
        print("✅ Executive dashboard created")
    
    def create_interactive_plotly_charts(self):
        """
        Create interactive Plotly charts for web-based analysis.
        """
        print("🌐 Creating interactive Plotly charts...")
        
        if 'monthly_time_series' not in self.datasets or 'pivot_point_analysis' not in self.datasets:
            print("⚠️  Required data not available for interactive charts")
            return
        
        monthly_df = self.datasets['monthly_time_series']
        pivot_df = self.datasets['pivot_point_analysis']
        
        # 1. Interactive Time Series with Pivot Points
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue Trends', 'Market Share Evolution', 
                          'Growth Rate Comparison', 'Pivot Point Analysis'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Revenue trends
        beer_monthly = monthly_df[monthly_df['Product_Category'] == 'BEER']
        seltzer_monthly = monthly_df[monthly_df['Product_Category'] == 'HARD SELTZER']
        
        fig.add_trace(
            go.Scatter(x=beer_monthly['Date'], y=beer_monthly['Monthly_Revenue'],
                      mode='lines+markers', name='Beer Revenue',
                      line=dict(color=self.colors['beer'], width=3),
                      hovertemplate='<b>Beer Revenue</b><br>Date: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=seltzer_monthly['Date'], y=seltzer_monthly['Monthly_Revenue'],
                      mode='lines+markers', name='Seltzer Revenue',
                      line=dict(color=self.colors['seltzer'], width=3),
                      hovertemplate='<b>Seltzer Revenue</b><br>Date: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'),
            row=1, col=1
        )
        
        # Market share
        fig.add_trace(
            go.Scatter(x=beer_monthly['Date'], y=beer_monthly['Market_Share_Revenue'],
                      mode='lines', name='Beer Market Share', fill='tonexty',
                      line=dict(color=self.colors['beer']),
                      hovertemplate='<b>Beer Market Share</b><br>Date: %{x}<br>Share: %{y:.1f}%<extra></extra>'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=seltzer_monthly['Date'], y=seltzer_monthly['Market_Share_Revenue'],
                      mode='lines', name='Seltzer Market Share', fill='tozeroy',
                      line=dict(color=self.colors['seltzer']),
                      hovertemplate='<b>Seltzer Market Share</b><br>Date: %{x}<br>Share: %{y:.1f}%<extra></extra>'),
            row=1, col=2
        )
        
        # Growth rates
        fig.add_trace(
            go.Bar(x=beer_monthly['Date'], y=beer_monthly['MoM_Growth_Rate'],
                  name='Beer Growth', marker_color=self.colors['beer'], opacity=0.7,
                  hovertemplate='<b>Beer Growth</b><br>Date: %{x}<br>Growth: %{y:.1f}%<extra></extra>'),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(x=seltzer_monthly['Date'], y=seltzer_monthly['MoM_Growth_Rate'],
                  name='Seltzer Growth', marker_color=self.colors['seltzer'], opacity=0.7,
                  hovertemplate='<b>Seltzer Growth</b><br>Date: %{x}<br>Growth: %{y:.1f}%<extra></extra>'),
            row=2, col=1
        )
        
        # Pivot point analysis
        fig.add_trace(
            go.Scatter(x=pivot_df['Date'], y=pivot_df['Growth_Difference_MoM'],
                      mode='lines+markers', name='Growth Difference',
                      line=dict(color=self.colors['pivot'], width=3),
                      hovertemplate='<b>Growth Difference</b><br>Date: %{x}<br>Difference: %{y:.1f}%<extra></extra>'),
            row=2, col=2
        )
        
        # Highlight pivot points
        pivot_points = pivot_df[pivot_df['Pivot_Point_MoM'] == True]
        if not pivot_points.empty:
            fig.add_trace(
                go.Scatter(x=pivot_points['Date'], y=pivot_points['Growth_Difference_MoM'],
                          mode='markers', name='Pivot Points',
                          marker=dict(color=self.colors['pivot'], size=12, symbol='star'),
                          hovertemplate='<b>PIVOT POINT</b><br>Date: %{x}<br>Advantage: %{y:.1f}%<extra></extra>'),
                row=2, col=2
            )
        
        # Add zero line for pivot analysis
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title_text="Interactive Beer vs Hard Seltzer Market Analysis",
            title_x=0.5,
            title_font_size=20,
            showlegend=True,
            height=800,
            template="plotly_white"
        )
        
        # Save interactive chart
        fig.write_html(f'{self.output_dir}/interactive_analysis.html')
        
        print("✅ Interactive Plotly charts created")
    
    def create_brand_performance_analysis(self):
        """
        Create brand performance analysis visualization.
        """
        print("🏷️  Creating brand performance analysis...")
        
        if 'brand_performance' not in self.datasets:
            print("⚠️  Brand performance data not available")
            return
        
        df = self.datasets['brand_performance']
        
        # Create figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Brand Performance Analysis: Market Leaders & Opportunities', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        # 1. Top Seltzer Brands
        seltzer_brands = df[df['Product_Category'] == 'HARD SELTZER'].head(10)
        
        bars = ax1.barh(seltzer_brands['Product_Brand'], seltzer_brands['Brand_Revenue'], 
                       color=self.colors['seltzer'], alpha=0.8)
        ax1.set_title('Top Hard Seltzer Brands by Revenue', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Revenue ($)', fontsize=12)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                    f'${width:,.0f}', ha='left', va='center', fontsize=9)
        
        # 2. Top Beer Brands
        beer_brands = df[df['Product_Category'] == 'BEER'].head(10)
        
        bars = ax2.barh(beer_brands['Product_Brand'], beer_brands['Brand_Revenue'], 
                       color=self.colors['beer'], alpha=0.8)
        ax2.set_title('Top Beer Brands by Revenue', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Revenue ($)', fontsize=12)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                    f'${width:,.0f}', ha='left', va='center', fontsize=9)
        
        # 3. Brand Revenue Share within Category
        ax3.pie(seltzer_brands.head(5)['Brand_Revenue'], 
               labels=seltzer_brands.head(5)['Product_Brand'], 
               autopct='%1.1f%%', startangle=90)
        ax3.set_title('Top 5 Seltzer Brands\nMarket Share', fontsize=14, fontweight='bold')
        
        # 4. Geographic Reach vs Revenue
        ax4.scatter(df[df['Product_Category'] == 'BEER']['Brand_Geographic_Reach'], 
                   df[df['Product_Category'] == 'BEER']['Brand_Revenue'],
                   color=self.colors['beer'], alpha=0.6, s=60, label='Beer Brands')
        ax4.scatter(df[df['Product_Category'] == 'HARD SELTZER']['Brand_Geographic_Reach'], 
                   df[df['Product_Category'] == 'HARD SELTZER']['Brand_Revenue'],
                   color=self.colors['seltzer'], alpha=0.6, s=60, label='Seltzer Brands')
        
        ax4.set_title('Geographic Reach vs Revenue by Brand', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Geographic Reach (Regions)', fontsize=12)
        ax4.set_ylabel('Brand Revenue ($)', fontsize=12)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/brand_performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{self.output_dir}/brand_performance_analysis.pdf', bbox_inches='tight')
        plt.show()
        
        print("✅ Brand performance analysis created")
    
    def generate_all_visualizations(self):
        """
        Generate all visualizations in the suite.
        """
        print("🎨 Generating complete visualization suite...")
        print("=" * 80)
        
        try:
            # Load data
            self.load_datasets()
            
            # Create all visualizations
            self.create_time_series_comparison()
            self.create_pivot_point_visualization()
            self.create_regional_heatmap()
            self.create_executive_dashboard()
            self.create_brand_performance_analysis()
            self.create_interactive_plotly_charts()
            
            print(f"\n🎉 VISUALIZATION SUITE COMPLETED!")
            print(f"📁 All charts saved to: {self.output_dir}/")
            print(f"📊 Charts created:")
            print(f"   • time_series_comparison.png/pdf")
            print(f"   • pivot_point_analysis.png/pdf")
            print(f"   • regional_heatmap.png/pdf")
            print(f"   • executive_dashboard.png/pdf")
            print(f"   • brand_performance_analysis.png/pdf")
            print(f"   • interactive_analysis.html")
            
            print(f"\n💡 Usage:")
            print(f"   • Use PNG files for presentations and reports")
            print(f"   • Use PDF files for high-quality printing")
            print(f"   • Open HTML file in browser for interactive analysis")
            
        except Exception as e:
            print(f"❌ Error generating visualizations: {str(e)}")
            raise

def main():
    """Main execution function."""
    viz_suite = BeerSeltzerVisualizationSuite()
    viz_suite.generate_all_visualizations()

if __name__ == "__main__":
    main()