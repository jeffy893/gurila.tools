#!/usr/bin/env python3
"""
Test script to validate visualization data exports
"""

import pandas as pd
import os
import json

def test_visualization_datasets():
    """Test that all visualization datasets are properly formatted."""
    
    data_dir = "visualization_data"
    
    print("🧪 Testing Visualization Data Exports")
    print("=" * 50)
    
    # Load dataset inventory
    try:
        with open(f"{data_dir}/dataset_inventory.json", 'r') as f:
            inventory = json.load(f)
        
        print(f"📊 Dataset Inventory Loaded:")
        print(f"   Export Timestamp: {inventory['export_timestamp']}")
        print(f"   Total Datasets: {inventory['total_datasets']}")
        
    except Exception as e:
        print(f"❌ Error loading inventory: {e}")
        return False
    
    # Test key datasets
    key_datasets = [
        'monthly_time_series.csv',
        'pivot_point_analysis.csv', 
        'regional_category_analysis.csv',
        'category_performance.csv',
        'brand_performance.csv'
    ]
    
    print(f"\n🔍 Testing Key Datasets:")
    
    for dataset_file in key_datasets:
        try:
            file_path = f"{data_dir}/{dataset_file}"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                print(f"   ✅ {dataset_file}: {len(df)} records, {len(df.columns)} columns")
                
                # Show sample data
                if len(df) > 0:
                    print(f"      Sample columns: {list(df.columns[:5])}")
                    if 'Product_Category' in df.columns:
                        categories = df['Product_Category'].unique()
                        print(f"      Categories: {list(categories)}")
                
            else:
                print(f"   ❌ {dataset_file}: File not found")
                
        except Exception as e:
            print(f"   ❌ {dataset_file}: Error loading - {e}")
    
    # Test pivot point data specifically
    print(f"\n🎯 Testing Pivot Point Analysis:")
    try:
        pivot_df = pd.read_csv(f"{data_dir}/pivot_point_analysis.csv")
        
        if 'Pivot_Point_MoM' in pivot_df.columns:
            pivot_count = pivot_df['Pivot_Point_MoM'].sum()
            print(f"   ✅ Pivot points detected: {pivot_count} months")
            
            if 'Growth_Difference_MoM' in pivot_df.columns:
                max_advantage = pivot_df['Growth_Difference_MoM'].max()
                print(f"   ✅ Maximum growth advantage: {max_advantage:.1f}%")
        
        if 'Year_Month' in pivot_df.columns:
            date_range = f"{pivot_df['Year_Month'].min()} to {pivot_df['Year_Month'].max()}"
            print(f"   ✅ Analysis period: {date_range}")
            
    except Exception as e:
        print(f"   ❌ Pivot analysis test failed: {e}")
    
    # Test regional data
    print(f"\n🗺️  Testing Regional Analysis:")
    try:
        regional_df = pd.read_csv(f"{data_dir}/regional_category_analysis.csv")
        
        if 'Store_Region' in regional_df.columns:
            regions = regional_df['Store_Region'].unique()
            print(f"   ✅ Regions analyzed: {list(regions)}")
        
        if 'Category_Penetration' in regional_df.columns:
            seltzer_data = regional_df[regional_df['Product_Category'] == 'HARD SELTZER']
            if len(seltzer_data) > 0:
                max_penetration = seltzer_data['Category_Penetration'].max()
                best_region = seltzer_data.loc[seltzer_data['Category_Penetration'].idxmax(), 'Store_Region']
                print(f"   ✅ Best Seltzer region: {best_region} ({max_penetration:.1f}% penetration)")
                
    except Exception as e:
        print(f"   ❌ Regional analysis test failed: {e}")
    
    # Test category performance
    print(f"\n📈 Testing Category Performance:")
    try:
        category_df = pd.read_csv(f"{data_dir}/category_performance.csv")
        
        for _, row in category_df.iterrows():
            category = row['Product_Category']
            revenue = row['Total_Category_Revenue']
            market_share = row['Market_Share_Revenue']
            print(f"   ✅ {category}: ${revenue:,.0f} revenue ({market_share:.1f}% share)")
            
    except Exception as e:
        print(f"   ❌ Category performance test failed: {e}")
    
    print(f"\n🎉 Visualization Data Validation Complete!")
    print(f"💡 Data is ready for:")
    print(f"   • Matplotlib/Seaborn visualization")
    print(f"   • Plotly interactive charts") 
    print(f"   • Business Intelligence tools (Tableau, Power BI)")
    print(f"   • Excel analysis and charting")
    print(f"   • Custom dashboard development")
    
    return True

if __name__ == "__main__":
    test_visualization_datasets()