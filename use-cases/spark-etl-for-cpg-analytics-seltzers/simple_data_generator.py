#!/usr/bin/env python3
"""
Simple POS Data Generator - Creates minimal viable dataset for PySpark demo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

def create_products():
    """Create product catalog"""
    products = []
    
    # Beer products
    beer_brands = ["Budweiser", "Coors", "Miller", "Corona", "Heineken"]
    for i, brand in enumerate(beer_brands):
        for variant in ["Original", "Light"]:
            products.append({
                "SKU": f"BEER-{1000+i*2+len(variant)%2:04d}",
                "Brand": brand,
                "Product_Name": f"{brand} {variant}",
                "Category": "Beer",
                "ABV": 4.5 if "Light" in variant else 5.0,
                "Price_Per_Unit": np.random.uniform(1.00, 1.50)
            })
    
    # Seltzer products  
    seltzer_brands = ["White Claw", "Truly", "Bud Light Seltzer"]
    for i, brand in enumerate(seltzer_brands):
        for flavor in ["Cherry", "Lime"]:
            products.append({
                "SKU": f"SELT-{2000+i*2+len(flavor)%2:04d}",
                "Brand": brand,
                "Product_Name": f"{brand} {flavor}",
                "Category": "Hard Seltzer", 
                "ABV": 5.0,
                "Price_Per_Unit": np.random.uniform(1.25, 1.75)
            })
    
    return pd.DataFrame(products)

def create_locations():
    """Create retailer locations"""
    locations = []
    
    regions = ["Northeast", "Southeast", "Midwest", "West", "Southwest"]
    states = ["NY", "FL", "IL", "CA", "TX"]
    store_types = ["Grocery", "Convenience", "Liquor"]
    
    for i in range(50):  # 50 stores
        locations.append({
            "Retailer_ID": f"RTL-{3000+i:05d}",
            "Chain_Name": f"Store Chain {i%5+1}",
            "Store_Type": np.random.choice(store_types),
            "Region": regions[i%5],
            "State": states[i%5],
            "City": f"City {i%10+1}",
            "Store_Size": np.random.choice(["Small", "Medium", "Large"]),
            "Alcohol_License": True
        })
    
    return pd.DataFrame(locations)

def create_sales_transactions(products_df, locations_df):
    """Create sales transactions with beer plateau and seltzer growth"""
    transactions = []
    
    # 12 months of data
    start_date = datetime(2023, 1, 1)
    
    for month in range(12):
        current_date = start_date + timedelta(days=month*30)
        
        # Calculate trend multipliers
        if month <= 6:  # First 6 months - beer strong, seltzer weak
            beer_strength = 1.0
            seltzer_strength = 0.2
        else:  # Last 6 months - seltzer growth, beer plateau
            beer_strength = 1.0  # Plateau
            seltzer_strength = 0.2 + (month-6) * 0.3  # Growth
        
        # Generate transactions for this month
        for _, store in locations_df.iterrows():
            for day in range(30):  # 30 days per month
                trans_date = current_date + timedelta(days=day)
                
                # 5-10 transactions per store per day
                num_transactions = np.random.randint(5, 11)
                
                for _ in range(num_transactions):
                    # Choose category based on trend
                    total_strength = beer_strength + seltzer_strength
                    beer_prob = beer_strength / total_strength
                    
                    if np.random.random() < beer_prob:
                        category = "Beer"
                        available_products = products_df[products_df['Category'] == 'Beer']
                        trend_mult = beer_strength
                    else:
                        category = "Hard Seltzer"
                        available_products = products_df[products_df['Category'] == 'Hard Seltzer']
                        trend_mult = seltzer_strength
                    
                    # Select random product
                    product = available_products.sample(1).iloc[0]
                    
                    # Generate transaction
                    units = np.random.randint(1, 7)  # 1-6 units
                    units = int(units * trend_mult * np.random.uniform(0.8, 1.2))
                    units = max(1, units)
                    
                    revenue = units * product['Price_Per_Unit'] * np.random.uniform(0.9, 1.1)
                    
                    transactions.append({
                        "Transaction_ID": f"TXN-{len(transactions)+100000:08d}",
                        "Date": trans_date.strftime('%Y-%m-%d'),
                        "Retailer_ID": store['Retailer_ID'],
                        "SKU": product['SKU'],
                        "Product_Name": product['Product_Name'],
                        "Brand": product['Brand'],
                        "Category": category,
                        "Units_Sold": units,
                        "Unit_Price": round(product['Price_Per_Unit'], 2),
                        "Total_Revenue": round(revenue, 2),
                        "Store_Type": store['Store_Type'],
                        "Region": store['Region'],
                        "State": store['State']
                    })
    
    return pd.DataFrame(transactions)

def main():
    """Generate the datasets"""
    print("🍺 Simple POS Data Generator")
    print("=" * 40)
    
    # Create output directory
    os.makedirs("synthetic_data", exist_ok=True)
    
    # Generate datasets
    print("Generating products...")
    products_df = create_products()
    
    print("Generating locations...")
    locations_df = create_locations()
    
    print("Generating sales transactions...")
    sales_df = create_sales_transactions(products_df, locations_df)
    
    # Export to CSV
    print("Exporting CSV files...")
    products_df.to_csv("synthetic_data/products.csv", index=False)
    locations_df.to_csv("synthetic_data/locations.csv", index=False)
    sales_df.to_csv("synthetic_data/sales_transactions.csv", index=False)
    
    # Summary
    print(f"\n✅ Generated datasets:")
    print(f"   Products: {len(products_df)} records")
    print(f"   Locations: {len(locations_df)} records") 
    print(f"   Sales: {len(sales_df)} records")
    print(f"   Total Revenue: ${sales_df['Total_Revenue'].sum():,.2f}")
    
    # Show trend verification
    monthly_sales = sales_df.copy()
    monthly_sales['Month'] = pd.to_datetime(monthly_sales['Date']).dt.month
    trend_check = monthly_sales.groupby(['Month', 'Category'])['Total_Revenue'].sum().unstack(fill_value=0)
    
    print(f"\n📈 Trend Verification (Revenue by Month):")
    print(trend_check.round(2))
    
    print(f"\n📁 Files saved to synthetic_data/")

if __name__ == "__main__":
    main()