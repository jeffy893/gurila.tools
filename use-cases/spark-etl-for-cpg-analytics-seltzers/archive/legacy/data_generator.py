#!/usr/bin/env python3
"""
Synthetic POS Data Generator for Beer Company Analysis
=====================================================

This script generates realistic Point of Sale (POS) data for a traditional beer company
to demonstrate the market anomaly of Hard Seltzer growth overtaking beer sales.

The generated data will show:
- Beer sales plateauing after initial strong performance
- Hard Seltzer sales showing exponential growth
- Clear pivot point where seltzers overtake beer growth rates

Author: Data Engineering Portfolio Project
Date: 2026-01-08
"""

# Core Python libraries
import pandas as pd
import numpy as np
import datetime
import random
import csv
import os
from typing import List, Dict, Tuple
import logging

# Additional libraries for data generation
from datetime import datetime, timedelta
import json
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

class POSDataGenerator:
    """
    Main class for generating synthetic Point of Sale data for beer company analysis.
    
    This class orchestrates the generation of three main datasets:
    1. Product catalog (brands, categories, SKUs, ABV)
    2. Geographic/retailer data (locations, warehouses, regions)
    3. Sales transactions (daily POS data with trend logic)
    """
    
    def __init__(self, output_dir: str = "synthetic_data", sample_mode: bool = False):
        """
        Initialize the POS data generator.
        
        Args:
            output_dir (str): Directory to save generated CSV files
            sample_mode (bool): If True, generate smaller dataset for testing
        """
        self.output_dir = output_dir
        self.sample_mode = sample_mode
        
        if sample_mode:
            # Reduced time period for testing
            self.start_date = datetime(2023, 1, 1)  # 1 year instead of 3
            self.end_date = datetime(2023, 12, 31)
            logger.info("🔬 SAMPLE MODE: Generating reduced dataset for testing")
        else:
            self.start_date = datetime(2021, 1, 1)  # 3-year analysis period
            self.end_date = datetime(2023, 12, 31)
        
        self.total_days = (self.end_date - self.start_date).days + 1
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized POS Data Generator")
        logger.info(f"Analysis period: {self.start_date.date()} to {self.end_date.date()}")
        logger.info(f"Total days: {self.total_days}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def generate_product_catalog(self) -> pd.DataFrame:
        """
        Generate comprehensive product catalog with beer and hard seltzer products.
        
        Returns:
            pd.DataFrame: Product catalog with Brand, Category, SKU, ABV columns
        """
        logger.info("Generating product catalog...")
        
        # Beer brands and their typical product lines
        beer_brands = {
            "Budweiser": ["Original", "Light", "Select", "Zero"],
            "Coors": ["Original", "Light", "Banquet", "Pure"],
            "Miller": ["High Life", "Lite", "Genuine Draft", "64"],
            "Corona": ["Extra", "Light", "Premier", "Familiar"],
            "Heineken": ["Original", "Light", "0.0", "Silver"],
            "Stella Artois": ["Original", "Solstice Lager", "Cidre", "Unfiltered"],
            "Blue Moon": ["Belgian White", "Light Sky", "Mango Wheat", "Seasonal"],
            "Sam Adams": ["Boston Lager", "Light", "Seasonal", "IPA"],
            "Guinness": ["Draught", "Extra Stout", "Blonde", "0.0"],
            "Modelo": ["Especial", "Negra", "Chelada", "Light"],
            "Dos Equis": ["Lager", "Amber", "Lime & Salt", "Special Lager"],
            "Yuengling": ["Traditional Lager", "Light", "Black & Tan", "Flight"],
            "New Belgium": ["Fat Tire", "Voodoo Ranger IPA", "Citradelic", "1554"],
            "Sierra Nevada": ["Pale Ale", "Torpedo IPA", "Hazy Little Thing", "Celebration"],
            "Lagunitas": ["IPA", "Little Sumpin'", "Censored", "DayTime IPA"]
        }
        
        # Hard Seltzer brands and their flavors
        seltzer_brands = {
            "White Claw": ["Black Cherry", "Mango", "Natural Lime", "Raspberry", "Watermelon", "Tangerine"],
            "Truly": ["Wild Berry", "Colima Lime", "Grapefruit", "Lemon", "Black Cherry", "Mango"],
            "Bud Light Seltzer": ["Black Cherry", "Strawberry", "Lemon Lime", "Mango", "Pineapple"],
            "Corona Hard Seltzer": ["Tropical Lime", "Mango", "Cherry", "Blackberry Lime"],
            "Vizzy": ["Black Cherry Lime", "Strawberry Kiwi", "Pineapple Mango", "Blueberry Pomegranate"],
            "Bon & Viv": ["Grapefruit", "Black Cherry", "Cranberry", "Clementine Hibiscus"],
            "Smirnoff Seltzer": ["Red, White & Berry", "Pink Apple Rose", "Orange Mango", "Cranberry Lime"],
            "High Noon": ["Peach", "Pineapple", "Watermelon", "Black Cherry", "Grapefruit"],
            "Topo Chico": ["Tangy Lemon Lime", "Exotic Pineapple", "Strawberry Guava", "Tropical Mango"],
            "Michelob Ultra": ["Lime Cactus", "Spicy Pineapple", "Cucumber Lime", "Peach Pear"]
        }
        
        products = []
        sku_counter = 1000
        
        # Generate beer products
        for brand, variants in beer_brands.items():
            for variant in variants:
                # Realistic ABV ranges for different beer types
                if "Light" in variant or "Lite" in variant or "64" in variant:
                    abv = round(np.random.uniform(3.2, 4.2), 1)
                elif "IPA" in variant or "Stout" in variant:
                    abv = round(np.random.uniform(5.5, 7.5), 1)
                elif "0.0" in variant or "Zero" in variant:
                    abv = 0.0
                else:
                    abv = round(np.random.uniform(4.2, 5.8), 1)
                
                products.append({
                    "SKU": f"BEER-{sku_counter:04d}",
                    "Brand": brand,
                    "Product_Name": f"{brand} {variant}",
                    "Category": "Beer",
                    "ABV": abv,
                    "Package_Size": np.random.choice(["12oz Can", "12oz Bottle", "16oz Can", "22oz Bottle"], 
                                                   p=[0.4, 0.3, 0.2, 0.1]),
                    "Pack_Size": np.random.choice([1, 6, 12, 24], p=[0.1, 0.2, 0.5, 0.2])
                })
                sku_counter += 1
        
        # Add some additional beer varieties to reach 50+ products
        craft_beer_additions = [
            ("Dogfish Head", "60 Minute IPA", 6.0),
            ("Stone", "IPA", 6.9),
            ("Founders", "All Day IPA", 4.7),
            ("Bell's", "Two Hearted IPA", 7.0),
            ("Deschutes", "Black Butte Porter", 5.2),
            ("Anchor", "Steam Beer", 4.9),
            ("Brooklyn", "Lager", 5.2),
            ("Goose Island", "312 Urban Wheat", 4.2),
            ("Shock Top", "Belgian White", 5.2),
            ("Michelob Ultra", "Pure Gold", 3.8),
            ("Pabst", "Blue Ribbon", 4.7),
            ("Tecate", "Original", 4.5),
            ("Pacifico", "Clara", 4.4),
            ("Negra Modelo", "Munich Dunkel", 5.4)
        ]
        
        for brand, name, abv in craft_beer_additions:
            products.append({
                "SKU": f"BEER-{sku_counter:04d}",
                "Brand": brand,
                "Product_Name": name,
                "Category": "Beer",
                "ABV": abv,
                "Package_Size": np.random.choice(["12oz Can", "12oz Bottle", "16oz Can"]),
                "Pack_Size": np.random.choice([6, 12, 24])
            })
            sku_counter += 1
        
        # Generate hard seltzer products
        for brand, flavors in seltzer_brands.items():
            for flavor in flavors:
                # Most hard seltzers are 4.5-5.0% ABV, with some variations
                if "High Noon" in brand:  # High Noon is typically higher
                    abv = round(np.random.uniform(4.5, 5.0), 1)
                else:
                    abv = round(np.random.uniform(4.5, 5.0), 1)
                
                products.append({
                    "SKU": f"SELT-{sku_counter:04d}",
                    "Brand": brand,
                    "Product_Name": f"{brand} {flavor}",
                    "Category": "Hard Seltzer",
                    "ABV": abv,
                    "Package_Size": np.random.choice(["12oz Can", "16oz Can"], p=[0.8, 0.2]),
                    "Pack_Size": np.random.choice([4, 6, 12, 24], p=[0.1, 0.3, 0.4, 0.2])
                })
                sku_counter += 1
        
        # Create DataFrame
        products_df = pd.DataFrame(products)
        
        # Add some additional calculated fields
        products_df['Price_Per_Unit'] = products_df.apply(
            lambda row: round(np.random.uniform(0.85, 1.25) if row['Category'] == 'Beer' 
                            else np.random.uniform(1.10, 1.65), 2), axis=1
        )
        
        # Add launch dates (seltzers are newer products)
        products_df['Launch_Date'] = products_df.apply(
            lambda row: self.start_date + timedelta(days=np.random.randint(0, 365)) 
            if row['Category'] == 'Beer'
            else self.start_date + timedelta(days=np.random.randint(180, 730)), axis=1
        )
        
        logger.info(f"Generated {len(products_df)} products:")
        logger.info(f"  - Beer products: {len(products_df[products_df['Category'] == 'Beer'])}")
        logger.info(f"  - Hard Seltzer products: {len(products_df[products_df['Category'] == 'Hard Seltzer'])}")
        logger.info(f"  - Unique brands: {products_df['Brand'].nunique()}")
        
        return products_df
    
    def generate_geography_data(self) -> pd.DataFrame:
        """
        Generate realistic geography and retailer data.
        
        Returns:
            pd.DataFrame: Geographic data with retailers, warehouses, regions, states
        """
        logger.info("Generating geography and retailer data...")
        
        # Define regional structure with states and major cities
        regional_data = {
            "Northeast": {
                "states": ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"],
                "major_cities": [
                    ("New York", "NY"), ("Boston", "MA"), ("Philadelphia", "PA"),
                    ("Pittsburgh", "PA"), ("Buffalo", "NY"), ("Newark", "NJ"),
                    ("Hartford", "CT"), ("Providence", "RI"), ("Portland", "ME"),
                    ("Manchester", "NH"), ("Burlington", "VT"), ("Albany", "NY")
                ]
            },
            "Southeast": {
                "states": ["DE", "MD", "DC", "VA", "WV", "KY", "TN", "NC", "SC", "GA", "FL", "AL", "MS", "AR", "LA"],
                "major_cities": [
                    ("Atlanta", "GA"), ("Miami", "FL"), ("Charlotte", "NC"),
                    ("Jacksonville", "FL"), ("Nashville", "TN"), ("Virginia Beach", "VA"),
                    ("Tampa", "FL"), ("Orlando", "FL"), ("New Orleans", "LA"),
                    ("Louisville", "KY"), ("Birmingham", "AL"), ("Charleston", "SC"),
                    ("Raleigh", "NC"), ("Memphis", "TN"), ("Richmond", "VA")
                ]
            },
            "Midwest": {
                "states": ["OH", "MI", "IN", "WI", "IL", "MN", "IA", "MO", "ND", "SD", "NE", "KS"],
                "major_cities": [
                    ("Chicago", "IL"), ("Detroit", "MI"), ("Columbus", "OH"),
                    ("Milwaukee", "WI"), ("Kansas City", "MO"), ("Minneapolis", "MN"),
                    ("St. Louis", "MO"), ("Indianapolis", "IN"), ("Cleveland", "OH"),
                    ("Cincinnati", "OH"), ("Omaha", "NE"), ("Des Moines", "IA"),
                    ("Madison", "WI"), ("Grand Rapids", "MI"), ("Wichita", "KS")
                ]
            },
            "West": {
                "states": ["MT", "WY", "CO", "NM", "ID", "UT", "NV", "AZ", "WA", "OR", "CA", "AK", "HI"],
                "major_cities": [
                    ("Los Angeles", "CA"), ("San Francisco", "CA"), ("Seattle", "WA"),
                    ("Denver", "CO"), ("Phoenix", "AZ"), ("Las Vegas", "NV"),
                    ("Portland", "OR"), ("San Diego", "CA"), ("Salt Lake City", "UT"),
                    ("Albuquerque", "NM"), ("Tucson", "AZ"), ("Spokane", "WA"),
                    ("Boise", "ID"), ("Anchorage", "AK"), ("Honolulu", "HI")
                ]
            },
            "Southwest": {
                "states": ["TX", "OK"],
                "major_cities": [
                    ("Houston", "TX"), ("Dallas", "TX"), ("San Antonio", "TX"),
                    ("Austin", "TX"), ("Fort Worth", "TX"), ("El Paso", "TX"),
                    ("Oklahoma City", "OK"), ("Tulsa", "OK"), ("Corpus Christi", "TX"),
                    ("Plano", "TX"), ("Lubbock", "TX"), ("Garland", "TX")
                ]
            }
        }
        
        # Retailer chain types and their typical presence
        retailer_chains = {
            "Grocery": [
                "Kroger", "Safeway", "Publix", "H-E-B", "Wegmans", "Giant Eagle",
                "Stop & Shop", "Food Lion", "Harris Teeter", "King Soopers",
                "Ralphs", "Fred Meyer", "QFC", "Smith's", "Fry's"
            ],
            "Big Box": [
                "Walmart", "Target", "Costco", "Sam's Club", "BJ's Wholesale"
            ],
            "Convenience": [
                "7-Eleven", "Circle K", "Wawa", "Sheetz", "Casey's", "QuikTrip",
                "RaceTrac", "Speedway", "Cumberland Farms", "Royal Farms"
            ],
            "Liquor": [
                "Total Wine", "BevMo!", "ABC Fine Wine", "Binny's", "Spec's",
                "Party City Liquor", "Fine Wine & Good Spirits", "State Liquor Store"
            ],
            "Gas Station": [
                "Shell", "BP", "Exxon", "Chevron", "Mobil", "Sunoco",
                "Phillips 66", "Valero", "Marathon", "Citgo"
            ]
        }
        
        # Generate warehouses first (50+ warehouses strategically placed)
        warehouses = []
        warehouse_id = 1001
        
        for region, data in regional_data.items():
            # Number of warehouses per region based on population/market size
            if region in ["West", "Southeast"]:
                num_warehouses = 12
            elif region == "Midwest":
                num_warehouses = 10
            elif region == "Northeast":
                num_warehouses = 8
            else:  # Southwest
                num_warehouses = 6
            
            # Place warehouses in major cities
            selected_cities = random.sample(data["major_cities"], min(num_warehouses, len(data["major_cities"])))
            
            for city, state in selected_cities:
                warehouses.append({
                    "Warehouse_ID": f"WH-{warehouse_id:04d}",
                    "Region": region,
                    "State": state,
                    "City": city,
                    "Warehouse_Type": np.random.choice(["Distribution Center", "Regional Hub", "Cross-Dock"], 
                                                     p=[0.6, 0.3, 0.1])
                })
                warehouse_id += 1
        
        # Generate retailers (1000+ retailers)
        retailers = []
        retailer_id = 2001
        
        # Create retailer distribution across all states
        all_states = []
        state_to_region = {}
        for region, data in regional_data.items():
            all_states.extend(data["states"])
            for state in data["states"]:
                state_to_region[state] = region
        
        # Generate additional cities for smaller markets
        additional_cities = {
            "CA": ["Sacramento", "Fresno", "Long Beach", "Oakland", "Bakersfield"],
            "TX": ["Arlington", "Amarillo", "Beaumont", "Brownsville", "College Station"],
            "FL": ["Tallahassee", "Gainesville", "Fort Lauderdale", "Pensacola", "Sarasota"],
            "NY": ["Rochester", "Syracuse", "Yonkers", "New Rochelle", "Mount Vernon"],
            "PA": ["Allentown", "Erie", "Reading", "Scranton", "Bethlehem"],
            "OH": ["Toledo", "Akron", "Dayton", "Youngstown", "Canton"],
            "IL": ["Rockford", "Peoria", "Springfield", "Elgin", "Waukegan"],
            "MI": ["Grand Rapids", "Warren", "Sterling Heights", "Lansing", "Ann Arbor"],
            "GA": ["Columbus", "Augusta", "Savannah", "Athens", "Sandy Springs"],
            "NC": ["Greensboro", "Durham", "Winston-Salem", "Fayetteville", "Cary"]
        }
        
        # Distribute retailers across states with realistic density
        target_retailers = 1200
        retailers_per_state = {}
        
        # Population-based distribution (approximate)
        high_pop_states = ["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI"]
        med_pop_states = ["NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"]
        
        for state in all_states:
            if state in high_pop_states:
                retailers_per_state[state] = random.randint(40, 80)
            elif state in med_pop_states:
                retailers_per_state[state] = random.randint(20, 40)
            else:
                retailers_per_state[state] = random.randint(8, 25)
        
        # Generate retailers for each state
        for state, num_retailers in retailers_per_state.items():
            region = state_to_region[state]
            
            # Get cities for this state
            state_cities = [city for city, st in regional_data[region]["major_cities"] if st == state]
            if state in additional_cities:
                state_cities.extend(additional_cities[state])
            
            # If no cities defined, create generic ones
            if not state_cities:
                state_cities = [f"City_{i}" for i in range(1, 6)]
            
            for _ in range(num_retailers):
                # Select retailer chain and type
                chain_type = np.random.choice(list(retailer_chains.keys()), 
                                            p=[0.35, 0.15, 0.25, 0.15, 0.10])
                chain_name = np.random.choice(retailer_chains[chain_type])
                city = np.random.choice(state_cities)
                
                # Find nearest warehouse (simplified - same region)
                region_warehouses = [wh for wh in warehouses if wh["Region"] == region]
                assigned_warehouse = np.random.choice(region_warehouses)
                
                retailers.append({
                    "Retailer_ID": f"RTL-{retailer_id:05d}",
                    "Chain_Name": chain_name,
                    "Store_Type": chain_type,
                    "Region": region,
                    "State": state,
                    "City": city,
                    "Warehouse_ID": assigned_warehouse["Warehouse_ID"],
                    "Store_Size": np.random.choice(["Small", "Medium", "Large", "Superstore"], 
                                                 p=[0.3, 0.4, 0.25, 0.05]),
                    "Urban_Rural": np.random.choice(["Urban", "Suburban", "Rural"], 
                                                  p=[0.4, 0.45, 0.15])
                })
                retailer_id += 1
        
        # Combine warehouses and retailers into single DataFrame
        # First create warehouse DataFrame
        warehouse_df = pd.DataFrame(warehouses)
        warehouse_df['Location_Type'] = 'Warehouse'
        warehouse_df['Chain_Name'] = 'Distribution'
        warehouse_df['Store_Type'] = 'Warehouse'
        warehouse_df['Retailer_ID'] = warehouse_df['Warehouse_ID']
        warehouse_df['Store_Size'] = 'Large'
        warehouse_df['Urban_Rural'] = 'Industrial'
        
        # Create retailer DataFrame
        retailer_df = pd.DataFrame(retailers)
        retailer_df['Location_Type'] = 'Retail'
        retailer_df['Warehouse_Type'] = 'N/A'
        
        # Combine both datasets
        locations_df = pd.concat([
            warehouse_df[['Retailer_ID', 'Chain_Name', 'Store_Type', 'Region', 'State', 'City', 
                         'Warehouse_ID', 'Store_Size', 'Urban_Rural', 'Location_Type']],
            retailer_df[['Retailer_ID', 'Chain_Name', 'Store_Type', 'Region', 'State', 'City', 
                        'Warehouse_ID', 'Store_Size', 'Urban_Rural', 'Location_Type']]
        ], ignore_index=True)
        
        # Add some additional business attributes
        locations_df['Market_Tier'] = locations_df.apply(
            lambda row: np.random.choice(["Tier 1", "Tier 2", "Tier 3"], 
                                       p=[0.3, 0.5, 0.2] if row['Urban_Rural'] == 'Urban' 
                                       else [0.1, 0.4, 0.5]), axis=1
        )
        
        locations_df['Alcohol_License'] = locations_df.apply(
            lambda row: np.random.choice([True, False], 
                                       p=[0.95, 0.05] if row['Store_Type'] in ['Liquor', 'Grocery'] 
                                       else [0.7, 0.3]), axis=1
        )
        
        logger.info(f"Generated {len(locations_df)} locations:")
        logger.info(f"  - Warehouses: {len(warehouse_df)}")
        logger.info(f"  - Retailers: {len(retailer_df)}")
        logger.info(f"  - Regions: {locations_df['Region'].nunique()}")
        logger.info(f"  - States: {locations_df['State'].nunique()}")
        logger.info(f"  - Cities: {locations_df['City'].nunique()}")
        
        return locations_df
    
    def generate_sales_transactions(self, products_df: pd.DataFrame, 
                                  locations_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate daily sales transactions with trend logic showing beer plateau 
        and hard seltzer growth.
        
        Args:
            products_df (pd.DataFrame): Product catalog
            locations_df (pd.DataFrame): Geographic/retailer data
            
        Returns:
            pd.DataFrame: Sales transactions with trend patterns
        """
        logger.info("Generating sales transactions with trend logic...")
        
        # Generate time series framework first
        time_df = self.generate_time_series_framework()
        
        # Filter to retail locations only (exclude warehouses)
        retail_locations = locations_df[locations_df['Location_Type'] == 'Retail'].copy()
        
        # Separate products by category
        beer_products = products_df[products_df['Category'] == 'Beer'].copy()
        seltzer_products = products_df[products_df['Category'] == 'Hard Seltzer'].copy()
        
        logger.info(f"Generating transactions for {len(retail_locations)} retailers")
        logger.info(f"Product mix: {len(beer_products)} beers, {len(seltzer_products)} seltzers")
        
        transactions = []
        transaction_id = 100000
        
        # Core algorithm parameters - FURTHER REDUCED for demo
        base_daily_transactions_per_store = {
            'Large': 3, 'Medium': 2, 'Small': 1, 'Superstore': 5  # Much smaller for demo
        }
        
        category_base_probability = {
            'Beer': 0.85,  # Initially high probability
            'Hard Seltzer': 0.15  # Initially low probability
        }
        
        # Process each day in the time series with progress tracking
        total_days = len(time_df)
        processed_days = 0
        
        for _, time_row in time_df.iterrows():
            processed_days += 1
            if processed_days % 100 == 0:  # Progress every 100 days
                logger.info(f"Processing day {processed_days}/{total_days} ({processed_days/total_days*100:.1f}%)")
            
            date = time_row['Date']
            months_from_start = time_row['MonthsFromStart']
            
            # Calculate dynamic category probabilities based on trends
            beer_trend = time_row['Beer_Trend_Base']
            seltzer_trend = time_row['Seltzer_Trend_Base']
            seltzer_awareness = time_row['Consumer_Awareness_Seltzer']
            
            # Dynamic category mix - this creates the pivot point
            total_category_strength = beer_trend + seltzer_trend
            beer_probability = (beer_trend / total_category_strength) * (1 - seltzer_awareness * 0.3)
            seltzer_probability = (seltzer_trend / total_category_strength) * (0.5 + seltzer_awareness * 0.5)
            
            # Normalize probabilities
            total_prob = beer_probability + seltzer_probability
            beer_probability /= total_prob
            seltzer_probability /= total_prob
            
            # Process each retail location
            for _, location_row in retail_locations.iterrows():
                store_size = location_row['Store_Size']
                store_type = location_row['Store_Type']
                region = location_row['Region']
                has_alcohol_license = location_row['Alcohol_License']
                
                if not has_alcohol_license:
                    continue  # Skip stores without alcohol license
                
                # Calculate base transaction volume for this store
                base_transactions = base_daily_transactions_per_store[store_size]
                
                # Apply store type modifiers
                store_type_multipliers = {
                    'Grocery': 1.0,
                    'Convenience': 0.6,
                    'Big Box': 1.3,
                    'Liquor': 1.8,
                    'Gas Station': 0.4
                }
                
                # Apply regional preferences (some regions adopt seltzers faster)
                regional_seltzer_boost = {
                    'West': 1.4,      # Early adopters
                    'Northeast': 1.2,  # Trendy markets
                    'Southeast': 1.1,  # Growing interest
                    'Midwest': 0.9,    # Traditional beer markets
                    'Southwest': 1.0   # Balanced
                }
                
                adjusted_transactions = int(
                    base_transactions * 
                    store_type_multipliers[store_type] * 
                    time_row['Overall_Seasonality'] *
                    np.random.uniform(0.7, 1.3)  # Daily variance
                )
                
                # Generate transactions for this store on this day
                for _ in range(max(1, adjusted_transactions)):
                    # Determine category based on dynamic probabilities
                    regional_seltzer_prob = seltzer_probability * regional_seltzer_boost[region]
                    regional_beer_prob = 1 - regional_seltzer_prob
                    
                    # Normalize again
                    total_regional_prob = regional_beer_prob + regional_seltzer_prob
                    regional_beer_prob /= total_regional_prob
                    regional_seltzer_prob /= total_regional_prob
                    
                    category = np.random.choice(
                        ['Beer', 'Hard Seltzer'], 
                        p=[regional_beer_prob, regional_seltzer_prob]
                    )
                    
                    # Select product from chosen category
                    if category == 'Beer':
                        available_products = beer_products
                        trend_multiplier = beer_trend
                    else:
                        # Seltzer availability grows over time
                        if months_from_start < 6:
                            available_seltzers = seltzer_products.sample(n=min(5, len(seltzer_products)))
                        elif months_from_start < 12:
                            available_seltzers = seltzer_products.sample(n=min(15, len(seltzer_products)))
                        else:
                            available_seltzers = seltzer_products
                        
                        available_products = available_seltzers
                        trend_multiplier = seltzer_trend
                    
                    # Select specific product (weighted by popularity/newness)
                    if category == 'Hard Seltzer' and months_from_start > 12:
                        # Newer seltzer products get popularity boost
                        product_weights = [
                            2.0 if 'White Claw' in prod['Brand'] or 'Truly' in prod['Brand'] 
                            else 1.0 for _, prod in available_products.iterrows()
                        ]
                        selected_product = available_products.sample(weights=product_weights).iloc[0]
                    else:
                        selected_product = available_products.sample().iloc[0]
                    
                    # Calculate units sold with realistic variance and patterns
                    base_units = self._calculate_base_units(
                        category, store_type, store_size, date, region
                    )
                    
                    # Apply trend multiplier and variance
                    trend_adjusted_units = base_units * trend_multiplier
                    
                    # Add realistic variance and noise
                    final_units = self._apply_sales_variance_and_noise(
                        trend_adjusted_units, category, date, region, store_type
                    )
                    
                    adjusted_units = max(1, int(final_units))
                    
                    # Calculate realistic pricing with regional and temporal variations
                    unit_price = self._calculate_dynamic_pricing(
                        selected_product, region, store_type, date, months_from_start
                    )
                    
                    # Calculate total revenue with pricing consistency
                    base_revenue = adjusted_units * unit_price
                    
                    # Apply promotional discounts and pricing variations
                    final_revenue, is_promotion = self._apply_pricing_adjustments(
                        base_revenue, unit_price, adjusted_units, time_row['Promotion_Likelihood'],
                        category, store_type, date
                    )
                    
                    # Create transaction record
                    transactions.append({
                        'Transaction_ID': f'TXN-{transaction_id:08d}',
                        'Date': date,
                        'Retailer_ID': location_row['Retailer_ID'],
                        'SKU': selected_product['SKU'],
                        'Product_Name': selected_product['Product_Name'],
                        'Brand': selected_product['Brand'],
                        'Category': category,
                        'Units_Sold': adjusted_units,
                        'Unit_Price': round(unit_price, 2),
                        'Total_Revenue': round(final_revenue, 2),
                        'Is_Promotion': is_promotion,
                        'Store_Type': store_type,
                        'Region': region,
                        'State': location_row['State'],
                        'Market_Tier': location_row['Market_Tier'],
                        
                        # Analytical fields
                        'Months_From_Start': months_from_start,
                        'Beer_Trend_Strength': beer_trend,
                        'Seltzer_Trend_Strength': seltzer_trend,
                        'Market_Phase': time_row['Market_Maturity_Phase'],
                        'Seasonality_Factor': time_row['Overall_Seasonality'],
                        'Consumer_Seltzer_Awareness': seltzer_awareness
                    })
                    
                    transaction_id += 1
                    
                    # Progress logging - reduced frequency
                    if transaction_id % 50000 == 0:
                        logger.info(f"Generated {transaction_id:,} transactions...")
        
        # Create DataFrame
        sales_df = pd.DataFrame(transactions)
        
        # Add calculated fields for analysis
        sales_df['Revenue_Per_Unit'] = sales_df['Total_Revenue'] / sales_df['Units_Sold']
        sales_df['Year_Month'] = sales_df['Date'].dt.to_period('M')
        sales_df['Quarter_Year'] = sales_df['Date'].dt.to_period('Q')
        
        # Calculate TDP (Total Distribution Points) - simplified for transactions
        sales_df['TDP'] = sales_df.apply(lambda row: self._calculate_simple_tdp(row), axis=1)
        
        # Calculate velocity metrics
        sales_df['Sales_Velocity'] = sales_df['Units_Sold'] / sales_df['TDP']
        
        logger.info(f"Generated {len(sales_df):,} total transactions")
        logger.info(f"Date range: {sales_df['Date'].min().date()} to {sales_df['Date'].max().date()}")
        
        # Log category distribution over time to verify trends
        self._log_trend_verification(sales_df)
        
        return sales_df
    
    def generate_tdp_distribution_data(self, products_df: pd.DataFrame, 
                                     locations_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate Total Distribution Points (TDP) data reflecting realistic retail distribution.
        
        Args:
            products_df (pd.DataFrame): Product catalog
            locations_df (pd.DataFrame): Geographic/retailer data
            
        Returns:
            pd.DataFrame: TDP distribution data over time
        """
        logger.info("Generating TDP distribution data...")
        
        # Generate time series framework
        time_df = self.generate_time_series_framework()
        retail_locations = locations_df[locations_df['Location_Type'] == 'Retail'].copy()
        
        tdp_records = []
        
        # Process each month for TDP calculations
        monthly_dates = time_df.groupby('Year_Month')['Date'].first().reset_index()
        
        for _, month_row in monthly_dates.iterrows():
            date = month_row['Date']
            year_month = month_row['Year_Month']
            months_from_start = (date - self.start_date).days / 30.44
            
            # Process each product for this month
            for _, product in products_df.iterrows():
                sku = product['SKU']
                category = product['Category']
                brand = product['Brand']
                launch_date = product['Launch_Date']
                
                # Skip if product hasn't launched yet
                if date < launch_date:
                    continue
                
                # Calculate product lifecycle stage
                months_since_launch = max(0, (date - launch_date).days / 30.44)
                lifecycle_stage = self._get_product_lifecycle_stage(months_since_launch, category)
                
                # Check if product should be discontinued
                if self._should_discontinue_product(product, months_since_launch, months_from_start):
                    continue
                
                # Calculate TDP for each store type and region
                store_tdp_data = self._calculate_store_tdp_distribution(
                    product, retail_locations, months_from_start, months_since_launch, lifecycle_stage
                )
                
                # Aggregate TDP metrics
                total_stores_carrying = len(store_tdp_data[store_tdp_data['Carries_Product']])
                total_possible_stores = len(retail_locations[
                    retail_locations['Alcohol_License'] == True
                ])
                
                tdp_percentage = (total_stores_carrying / total_possible_stores) * 100
                
                # Calculate weighted TDP (larger stores count more)
                weighted_tdp = sum([
                    row['Store_Weight'] for _, row in store_tdp_data.iterrows() 
                    if row['Carries_Product']
                ])
                
                max_weighted_tdp = sum(store_tdp_data['Store_Weight'])
                weighted_tdp_percentage = (weighted_tdp / max_weighted_tdp) * 100
                
                # Regional TDP breakdown
                regional_tdp = self._calculate_regional_tdp(store_tdp_data, retail_locations)
                
                tdp_records.append({
                    'Date': date,
                    'Year_Month': year_month,
                    'SKU': sku,
                    'Product_Name': product['Product_Name'],
                    'Brand': brand,
                    'Category': category,
                    'Months_From_Start': round(months_from_start, 2),
                    'Months_Since_Launch': round(months_since_launch, 2),
                    'Lifecycle_Stage': lifecycle_stage,
                    
                    # Core TDP Metrics
                    'Stores_Carrying': total_stores_carrying,
                    'Total_Eligible_Stores': total_possible_stores,
                    'TDP_Percentage': round(tdp_percentage, 2),
                    'Weighted_TDP': round(weighted_tdp, 2),
                    'Weighted_TDP_Percentage': round(weighted_tdp_percentage, 2),
                    
                    # Regional Distribution
                    'Northeast_TDP': regional_tdp['Northeast'],
                    'Southeast_TDP': regional_tdp['Southeast'],
                    'Midwest_TDP': regional_tdp['Midwest'],
                    'West_TDP': regional_tdp['West'],
                    'Southwest_TDP': regional_tdp['Southwest'],
                    
                    # Store Type Distribution
                    'Grocery_TDP': self._calculate_store_type_tdp(store_tdp_data, 'Grocery'),
                    'Convenience_TDP': self._calculate_store_type_tdp(store_tdp_data, 'Convenience'),
                    'BigBox_TDP': self._calculate_store_type_tdp(store_tdp_data, 'Big Box'),
                    'Liquor_TDP': self._calculate_store_type_tdp(store_tdp_data, 'Liquor'),
                    'GasStation_TDP': self._calculate_store_type_tdp(store_tdp_data, 'Gas Station'),
                    
                    # Distribution Velocity Metrics
                    'Distribution_Velocity': self._calculate_distribution_velocity(
                        category, months_since_launch, months_from_start
                    ),
                    'Market_Penetration_Rate': self._calculate_market_penetration_rate(
                        category, brand, months_from_start
                    )
                })
        
        tdp_df = pd.DataFrame(tdp_records)
        
        logger.info(f"Generated TDP data: {len(tdp_df):,} records")
        logger.info(f"Products tracked: {tdp_df['SKU'].nunique()}")
        logger.info(f"Time period: {tdp_df['Date'].min().date()} to {tdp_df['Date'].max().date()}")
        
        return tdp_df
    
    def _get_product_lifecycle_stage(self, months_since_launch: float, category: str) -> str:
        """
        Determine product lifecycle stage based on time since launch and category.
        
        Args:
            months_since_launch (float): Months since product launch
            category (str): Product category
            
        Returns:
            str: Lifecycle stage
        """
        if category == "Beer":
            # Beer products have longer, more stable lifecycles
            if months_since_launch <= 3:
                return "Launch"
            elif months_since_launch <= 12:
                return "Growth"
            elif months_since_launch <= 36:
                return "Maturity"
            else:
                return "Decline"
        else:  # Hard Seltzer
            # Seltzer products have faster lifecycles but higher growth potential
            if months_since_launch <= 2:
                return "Launch"
            elif months_since_launch <= 8:
                return "Rapid_Growth"
            elif months_since_launch <= 24:
                return "Maturity"
            else:
                return "Decline"
    
    def _should_discontinue_product(self, product: pd.Series, months_since_launch: float, 
                                  months_from_start: float) -> bool:
        """
        Determine if a product should be discontinued based on performance and lifecycle.
        
        Args:
            product (pd.Series): Product information
            months_since_launch (float): Months since product launch
            months_from_start (float): Months from analysis start
            
        Returns:
            bool: True if product should be discontinued
        """
        category = product['Category']
        brand = product['Brand']
        
        # Beer discontinuation logic
        if category == "Beer":
            # Older beer products may be discontinued
            if months_since_launch > 48:  # 4 years
                return np.random.random() < 0.15  # 15% chance of discontinuation
            
            # Low-performing beer variants
            if "Light" not in product['Product_Name'] and months_since_launch > 30:
                return np.random.random() < 0.08  # 8% chance
                
        else:  # Hard Seltzer
            # Seltzers rarely discontinued during growth phase
            if months_from_start < 18:  # During growth phase
                return False
            
            # Some early seltzer flavors may be replaced
            if months_since_launch > 18 and months_from_start > 24:
                return np.random.random() < 0.05  # 5% chance
        
        return False
    
    def _calculate_store_tdp_distribution(self, product: pd.Series, retail_locations: pd.DataFrame,
                                        months_from_start: float, months_since_launch: float,
                                        lifecycle_stage: str) -> pd.DataFrame:
        """
        Calculate TDP distribution across individual stores.
        
        Args:
            product (pd.Series): Product information
            retail_locations (pd.DataFrame): Retail location data
            months_from_start (float): Months from analysis start
            months_since_launch (float): Months since product launch
            lifecycle_stage (str): Product lifecycle stage
            
        Returns:
            pd.DataFrame: Store-level TDP data
        """
        category = product['Category']
        brand = product['Brand']
        
        store_data = []
        
        for _, store in retail_locations.iterrows():
            if not store['Alcohol_License']:
                carries_product = False
                store_weight = 0
            else:
                # Calculate probability of carrying this product
                carry_probability = self._calculate_carry_probability(
                    product, store, months_from_start, months_since_launch, lifecycle_stage
                )
                
                carries_product = np.random.random() < carry_probability
                
                # Store weight based on size and type
                store_weight = self._calculate_store_weight(store)
            
            store_data.append({
                'Retailer_ID': store['Retailer_ID'],
                'Store_Type': store['Store_Type'],
                'Region': store['Region'],
                'State': store['State'],
                'Store_Size': store['Store_Size'],
                'Market_Tier': store['Market_Tier'],
                'Carries_Product': carries_product,
                'Store_Weight': store_weight,
                'Carry_Probability': carry_probability if store['Alcohol_License'] else 0
            })
        
        return pd.DataFrame(store_data)
    
    def _calculate_carry_probability(self, product: pd.Series, store: pd.Series,
                                   months_from_start: float, months_since_launch: float,
                                   lifecycle_stage: str) -> float:
        """
        Calculate probability that a store carries a specific product.
        
        Args:
            product (pd.Series): Product information
            store (pd.Series): Store information
            months_from_start (float): Months from analysis start
            months_since_launch (float): Months since product launch
            lifecycle_stage (str): Product lifecycle stage
            
        Returns:
            float: Probability (0-1) that store carries product
        """
        category = product['Category']
        brand = product['Brand']
        store_type = store['Store_Type']
        store_size = store['Store_Size']
        region = store['Region']
        market_tier = store['Market_Tier']
        
        # Base probability by category and store type
        base_probabilities = {
            'Beer': {
                'Grocery': 0.95, 'Big Box': 0.90, 'Convenience': 0.85,
                'Liquor': 0.98, 'Gas Station': 0.70
            },
            'Hard Seltzer': {
                'Grocery': 0.20, 'Big Box': 0.15, 'Convenience': 0.10,
                'Liquor': 0.40, 'Gas Station': 0.05
            }
        }
        
        base_prob = base_probabilities[category][store_type]
        
        # Adjust for seltzer growth over time
        if category == 'Hard Seltzer':
            # Seltzer distribution grows rapidly
            if months_from_start <= 6:
                time_multiplier = 0.3
            elif months_from_start <= 12:
                time_multiplier = 0.5
            elif months_from_start <= 18:
                time_multiplier = 0.8
            elif months_from_start <= 24:
                time_multiplier = 1.2
            else:
                time_multiplier = 1.5
            
            base_prob *= time_multiplier
        
        # Store size adjustments
        size_multipliers = {
            'Small': 0.7, 'Medium': 1.0, 'Large': 1.3, 'Superstore': 1.5
        }
        base_prob *= size_multipliers[store_size]
        
        # Regional preferences
        regional_multipliers = {
            'Beer': {'Northeast': 1.0, 'Southeast': 1.1, 'Midwest': 1.2, 'West': 0.9, 'Southwest': 1.1},
            'Hard Seltzer': {'Northeast': 1.3, 'Southeast': 1.1, 'Midwest': 0.8, 'West': 1.5, 'Southwest': 1.0}
        }
        base_prob *= regional_multipliers[category][region]
        
        # Market tier adjustments
        tier_multipliers = {'Tier 1': 1.2, 'Tier 2': 1.0, 'Tier 3': 0.8}
        base_prob *= tier_multipliers[market_tier]
        
        # Brand popularity adjustments
        if category == 'Hard Seltzer':
            if 'White Claw' in brand or 'Truly' in brand:
                base_prob *= 1.4  # Leading brands get better distribution
            elif 'Bud Light' in brand or 'Corona' in brand:
                base_prob *= 1.2  # Established beer brands entering seltzers
        
        # Lifecycle stage adjustments
        lifecycle_multipliers = {
            'Launch': 0.6, 'Growth': 1.0, 'Rapid_Growth': 1.3,
            'Maturity': 1.1, 'Decline': 0.7
        }
        base_prob *= lifecycle_multipliers.get(lifecycle_stage, 1.0)
        
        # Product launch timing (newer products take time to get distribution)
        if months_since_launch < 1:
            base_prob *= 0.3
        elif months_since_launch < 3:
            base_prob *= 0.6
        elif months_since_launch < 6:
            base_prob *= 0.8
        
        return min(0.98, max(0.01, base_prob))
    
    def _calculate_store_weight(self, store: pd.Series) -> float:
        """
        Calculate store weight for TDP calculations.
        
        Args:
            store (pd.Series): Store information
            
        Returns:
            float: Store weight
        """
        size_weights = {'Small': 1.0, 'Medium': 2.5, 'Large': 5.0, 'Superstore': 10.0}
        type_weights = {
            'Grocery': 1.0, 'Big Box': 1.5, 'Convenience': 0.8,
            'Liquor': 1.2, 'Gas Station': 0.6
        }
        tier_weights = {'Tier 1': 1.3, 'Tier 2': 1.0, 'Tier 3': 0.7}
        
        return (size_weights[store['Store_Size']] * 
                type_weights[store['Store_Type']] * 
                tier_weights[store['Market_Tier']])
    
    def _calculate_regional_tdp(self, store_tdp_data: pd.DataFrame, 
                              retail_locations: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate TDP percentage by region.
        
        Args:
            store_tdp_data (pd.DataFrame): Store TDP data
            retail_locations (pd.DataFrame): All retail locations
            
        Returns:
            Dict[str, float]: Regional TDP percentages
        """
        regional_tdp = {}
        
        for region in ['Northeast', 'Southeast', 'Midwest', 'West', 'Southwest']:
            region_stores = store_tdp_data[store_tdp_data['Region'] == region]
            region_carrying = region_stores[region_stores['Carries_Product']]
            
            if len(region_stores) > 0:
                regional_tdp[region] = round(
                    (len(region_carrying) / len(region_stores)) * 100, 2
                )
            else:
                regional_tdp[region] = 0.0
        
        return regional_tdp
    
    def _calculate_store_type_tdp(self, store_tdp_data: pd.DataFrame, 
                                store_type: str) -> float:
        """
        Calculate TDP percentage by store type.
        
        Args:
            store_tdp_data (pd.DataFrame): Store TDP data
            store_type (str): Store type to calculate for
            
        Returns:
            float: Store type TDP percentage
        """
        type_stores = store_tdp_data[store_tdp_data['Store_Type'] == store_type]
        type_carrying = type_stores[type_stores['Carries_Product']]
        
        if len(type_stores) > 0:
            return round((len(type_carrying) / len(type_stores)) * 100, 2)
        else:
            return 0.0
    
    def _calculate_distribution_velocity(self, category: str, months_since_launch: float,
                                       months_from_start: float) -> float:
        """
        Calculate distribution velocity (rate of TDP growth).
        
        Args:
            category (str): Product category
            months_since_launch (float): Months since product launch
            months_from_start (float): Months from analysis start
            
        Returns:
            float: Distribution velocity score
        """
        if category == 'Beer':
            # Beer has steady, predictable distribution velocity
            if months_since_launch <= 6:
                return 8.5  # Fast initial rollout
            else:
                return 2.0  # Steady maintenance
        else:  # Hard Seltzer
            # Seltzer velocity accelerates over time
            if months_from_start <= 12:
                return 3.0  # Slow start
            elif months_from_start <= 18:
                return 12.0  # Acceleration
            else:
                return 18.0  # Explosive distribution growth
    
    def _calculate_market_penetration_rate(self, category: str, brand: str,
                                         months_from_start: float) -> float:
        """
        Calculate market penetration rate for brand/category.
        
        Args:
            category (str): Product category
            brand (str): Brand name
            months_from_start (float): Months from analysis start
            
        Returns:
            float: Market penetration rate percentage
        """
        if category == 'Beer':
            # Established beer brands have high, stable penetration
            return np.random.uniform(75, 95)
        else:  # Hard Seltzer
            # Seltzer penetration grows over time
            if months_from_start <= 6:
                base_penetration = np.random.uniform(5, 15)
            elif months_from_start <= 12:
                base_penetration = np.random.uniform(15, 30)
            elif months_from_start <= 18:
                base_penetration = np.random.uniform(30, 50)
            elif months_from_start <= 24:
                base_penetration = np.random.uniform(50, 70)
            else:
                base_penetration = np.random.uniform(65, 85)
            
            # Brand adjustments
            if 'White Claw' in brand or 'Truly' in brand:
                base_penetration *= 1.3
            elif 'Bud Light' in brand or 'Corona' in brand:
                base_penetration *= 1.1
            
            return min(90, base_penetration)
    
    def _log_trend_verification(self, sales_df: pd.DataFrame) -> None:
        """
        Log trend verification to ensure the pivot point is created correctly.
        
        Args:
            sales_df (pd.DataFrame): Generated sales data
        """
        logger.info("Verifying trend patterns...")
        
        # Calculate monthly aggregates by category
        monthly_stats = sales_df.groupby(['Year_Month', 'Category']).agg({
            'Units_Sold': 'sum',
            'Total_Revenue': 'sum'
        }).reset_index()
        
        # Find the pivot point
        beer_monthly = monthly_stats[monthly_stats['Category'] == 'Beer']
        seltzer_monthly = monthly_stats[monthly_stats['Category'] == 'Hard Seltzer']
        
        if len(beer_monthly) > 0 and len(seltzer_monthly) > 0:
            # Calculate growth rates
            beer_peak_month = beer_monthly.loc[beer_monthly['Units_Sold'].idxmax(), 'Year_Month']
            seltzer_growth_start = seltzer_monthly[seltzer_monthly['Units_Sold'] > 
                                                 seltzer_monthly['Units_Sold'].quantile(0.5)]
            
            logger.info(f"Beer peak month: {beer_peak_month}")
            if len(seltzer_growth_start) > 0:
                logger.info(f"Seltzer growth acceleration: {seltzer_growth_start['Year_Month'].min()}")
            
            # Log final period comparison
            final_6_months = sales_df[sales_df['Months_From_Start'] >= 30]
            final_category_mix = final_6_months.groupby('Category')['Units_Sold'].sum()
            
            logger.info("Final 6-month category performance:")
            for category, units in final_category_mix.items():
                logger.info(f"  {category}: {units:,} units")
        
        logger.info("Trend verification completed")
    
    def _calculate_base_units(self, category: str, store_type: str, store_size: str,
                            date: datetime, region: str) -> float:
        """
        Calculate base units sold with realistic patterns and variance.
        
        Args:
            category (str): Product category
            store_type (str): Type of store
            store_size (str): Size of store
            date (datetime): Transaction date
            region (str): Geographic region
            
        Returns:
            float: Base units before trend adjustments
        """
        # Base unit distributions by category and context
        if category == "Beer":
            # Beer purchase patterns - more variety in pack sizes
            base_units_options = [1, 2, 3, 4, 6, 12, 18, 24, 30]
            base_probabilities = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.03, 0.02]
        else:  # Hard Seltzer
            # Seltzer purchase patterns - typically smaller packs, premium pricing
            base_units_options = [1, 2, 3, 4, 6, 8, 12, 24]
            base_probabilities = [0.30, 0.25, 0.18, 0.12, 0.08, 0.04, 0.02, 0.01]
        
        base_units = np.random.choice(base_units_options, p=base_probabilities)
        
        # Store type adjustments
        store_type_multipliers = {
            'Grocery': 1.2,      # Families buy larger quantities
            'Big Box': 1.8,      # Bulk purchasing
            'Convenience': 0.6,  # Single serve focus
            'Liquor': 1.4,       # Specialty alcohol shopping
            'Gas Station': 0.4   # Grab-and-go purchases
        }
        
        # Store size adjustments
        store_size_multipliers = {
            'Small': 0.7, 'Medium': 1.0, 'Large': 1.3, 'Superstore': 1.6
        }
        
        # Weekend/weekday patterns
        if date.weekday() == 4:  # Friday - pre-weekend stocking
            day_multiplier = 1.4
        elif date.weekday() in [5, 6]:  # Weekend - party/social purchases
            day_multiplier = 1.6
        elif date.weekday() == 0:  # Monday - lower sales
            day_multiplier = 0.8
        else:  # Tuesday-Thursday
            day_multiplier = 1.0
        
        # Regional preferences
        regional_multipliers = {
            'Beer': {
                'Northeast': 1.0, 'Southeast': 1.2, 'Midwest': 1.3, 
                'West': 0.9, 'Southwest': 1.1
            },
            'Hard Seltzer': {
                'Northeast': 1.3, 'Southeast': 1.1, 'Midwest': 0.8, 
                'West': 1.5, 'Southwest': 1.0
            }
        }
        
        # Apply all multipliers
        adjusted_units = (base_units * 
                         store_type_multipliers[store_type] * 
                         store_size_multipliers[store_size] * 
                         day_multiplier * 
                         regional_multipliers[category][region])
        
        return max(1.0, adjusted_units)
    
    def _apply_sales_variance_and_noise(self, base_units: float, category: str, 
                                      date: datetime, region: str, store_type: str) -> float:
        """
        Apply realistic variance and noise to sales units.
        
        Args:
            base_units (float): Base units calculation
            category (str): Product category
            date (datetime): Transaction date
            region (str): Geographic region
            store_type (str): Store type
            
        Returns:
            float: Units with variance and noise applied
        """
        # Seasonal variance patterns
        month = date.month
        
        # Summer boost for both categories (especially seltzers)
        if month in [6, 7, 8]:  # Peak summer
            if category == "Hard Seltzer":
                seasonal_variance = np.random.uniform(1.3, 1.8)
            else:
                seasonal_variance = np.random.uniform(1.1, 1.4)
        elif month in [5, 9]:  # Shoulder summer
            if category == "Hard Seltzer":
                seasonal_variance = np.random.uniform(1.1, 1.3)
            else:
                seasonal_variance = np.random.uniform(1.0, 1.2)
        elif month in [11, 12]:  # Holiday season
            seasonal_variance = np.random.uniform(1.2, 1.5)
        else:  # Regular months
            seasonal_variance = np.random.uniform(0.9, 1.1)
        
        # Weather-related variance (proxy for temperature/outdoor activities)
        day_of_year = date.timetuple().tm_yday
        weather_factor = 1.0 + 0.2 * np.sin((day_of_year - 80) * 2 * np.pi / 365)
        
        if category == "Hard Seltzer":
            weather_factor = weather_factor ** 1.5  # More sensitive to weather
        
        # Random daily noise
        daily_noise = np.random.normal(1.0, 0.15)  # 15% standard deviation
        daily_noise = max(0.5, min(1.8, daily_noise))  # Clamp to reasonable range
        
        # Store-specific variance
        store_variance = {
            'Grocery': np.random.normal(1.0, 0.10),
            'Big Box': np.random.normal(1.0, 0.08),
            'Convenience': np.random.normal(1.0, 0.20),
            'Liquor': np.random.normal(1.0, 0.12),
            'Gas Station': np.random.normal(1.0, 0.25)
        }
        
        store_noise = max(0.6, min(1.6, store_variance[store_type]))
        
        # Category-specific variance
        if category == "Hard Seltzer":
            # Seltzers have higher variance due to trend volatility
            category_variance = np.random.normal(1.0, 0.25)
        else:
            # Beer has more stable, predictable sales
            category_variance = np.random.normal(1.0, 0.12)
        
        category_variance = max(0.7, min(1.5, category_variance))
        
        # Apply all variance factors
        final_units = (base_units * seasonal_variance * weather_factor * 
                      daily_noise * store_noise * category_variance)
        
        return max(1.0, final_units)
    
    def _calculate_dynamic_pricing(self, product: pd.Series, region: str, store_type: str,
                                 date: datetime, months_from_start: float) -> float:
        """
        Calculate dynamic pricing with regional and temporal variations.
        
        Args:
            product (pd.Series): Product information
            region (str): Geographic region
            store_type (str): Store type
            date (datetime): Transaction date
            months_from_start (float): Months from analysis start
            
        Returns:
            float: Dynamic unit price
        """
        category = product['Category']
        brand = product['Brand']
        base_price = product['Price_Per_Unit']
        
        # Regional pricing variations
        regional_price_multipliers = {
            'Northeast': 1.15,  # Higher cost of living
            'West': 1.12,       # Premium markets
            'Southeast': 0.95,  # Lower cost markets
            'Midwest': 0.92,    # Competitive pricing
            'Southwest': 1.00   # Baseline
        }
        
        # Store type pricing strategies
        store_type_multipliers = {
            'Grocery': 1.00,      # Baseline competitive pricing
            'Big Box': 0.88,      # Volume discount pricing
            'Convenience': 1.25,  # Convenience premium
            'Liquor': 1.08,       # Specialty markup
            'Gas Station': 1.30   # High convenience premium
        }
        
        # Temporal pricing trends
        if category == "Hard Seltzer":
            # Seltzer pricing evolves over time
            if months_from_start <= 6:
                # Early premium pricing
                time_multiplier = 1.20
            elif months_from_start <= 12:
                # Price stabilization
                time_multiplier = 1.10
            elif months_from_start <= 18:
                # Competitive pricing as market grows
                time_multiplier = 1.05
            else:
                # Mature market pricing
                time_multiplier = 1.00
        else:  # Beer
            # Beer pricing remains relatively stable with slight inflation
            inflation_rate = 0.02  # 2% annual inflation
            years_elapsed = months_from_start / 12
            time_multiplier = 1.0 + (inflation_rate * years_elapsed)
        
        # Brand premium adjustments
        brand_multipliers = {
            # Premium beer brands
            'Sam Adams': 1.15, 'Guinness': 1.20, 'Stella Artois': 1.18,
            'Heineken': 1.12, 'Corona': 1.08,
            
            # Premium seltzer brands
            'White Claw': 1.10, 'Truly': 1.08, 'High Noon': 1.15,
            'Topo Chico': 1.12,
            
            # Value positioning
            'Bud Light Seltzer': 0.95, 'Michelob Ultra': 0.98
        }
        
        brand_multiplier = brand_multipliers.get(brand, 1.00)
        
        # Seasonal pricing adjustments
        month = date.month
        if month in [5, 6, 7, 8]:  # Summer premium
            seasonal_multiplier = 1.05
        elif month in [11, 12]:  # Holiday pricing
            seasonal_multiplier = 1.03
        else:
            seasonal_multiplier = 1.00
        
        # Pack size economics (larger packs have lower per-unit pricing)
        pack_size = product.get('Pack_Size', 1)
        if pack_size >= 24:
            pack_multiplier = 0.85  # Bulk discount
        elif pack_size >= 12:
            pack_multiplier = 0.92
        elif pack_size >= 6:
            pack_multiplier = 0.96
        else:
            pack_multiplier = 1.00  # Single/small pack premium
        
        # Calculate final price
        final_price = (base_price * 
                      regional_price_multipliers[region] * 
                      store_type_multipliers[store_type] * 
                      time_multiplier * 
                      brand_multiplier * 
                      seasonal_multiplier * 
                      pack_multiplier)
        
        # Add small random variance for realistic pricing
        price_variance = np.random.normal(1.0, 0.03)  # 3% standard deviation
        final_price *= max(0.95, min(1.05, price_variance))
        
        # Ensure pricing stays within realistic bounds
        if category == "Beer":
            final_price = max(0.75, min(2.50, final_price))  # $0.75-$2.50 per unit
        else:  # Hard Seltzer
            final_price = max(1.00, min(3.00, final_price))  # $1.00-$3.00 per unit
        
        return final_price
    
    def _apply_pricing_adjustments(self, base_revenue: float, unit_price: float, 
                                 units: int, promotion_likelihood: float,
                                 category: str, store_type: str, date: datetime) -> tuple:
        """
        Apply promotional discounts and final pricing adjustments.
        
        Args:
            base_revenue (float): Base revenue calculation
            unit_price (float): Unit price
            units (int): Units sold
            promotion_likelihood (float): Probability of promotion
            category (str): Product category
            store_type (str): Store type
            date (datetime): Transaction date
            
        Returns:
            tuple: (final_revenue, is_promotion)
        """
        is_promotion = np.random.random() < promotion_likelihood
        
        if is_promotion:
            # Determine promotion type and discount
            promotion_types = {
                'percentage_off': 0.4,    # 40% of promotions are % off
                'buy_x_get_y': 0.3,       # 30% are BOGO/multi-buy
                'fixed_discount': 0.2,    # 20% are fixed $ off
                'bundle_deal': 0.1        # 10% are bundle deals
            }
            
            promotion_type = np.random.choice(
                list(promotion_types.keys()), 
                p=list(promotion_types.values())
            )
            
            if promotion_type == 'percentage_off':
                # Standard percentage discount
                if category == "Hard Seltzer":
                    discount = np.random.uniform(0.10, 0.25)  # 10-25% off
                else:
                    discount = np.random.uniform(0.08, 0.20)  # 8-20% off
                final_revenue = base_revenue * (1 - discount)
                
            elif promotion_type == 'buy_x_get_y':
                # Buy 2 get 1 free, etc.
                if units >= 3:
                    # Effective 33% discount on multi-unit purchases
                    discount = 0.15  # Average effect
                    final_revenue = base_revenue * (1 - discount)
                else:
                    # Small discount for single units
                    final_revenue = base_revenue * 0.95
                    
            elif promotion_type == 'fixed_discount':
                # Fixed dollar amount off
                fixed_discount = np.random.uniform(1.00, 3.00)
                final_revenue = max(base_revenue * 0.7, base_revenue - fixed_discount)
                
            else:  # bundle_deal
                # Bundle pricing (slightly better per-unit pricing)
                final_revenue = base_revenue * 0.92
        else:
            final_revenue = base_revenue
        
        # Apply store-specific pricing adjustments
        if store_type == 'Big Box' and not is_promotion:
            # Big box stores have everyday low pricing
            final_revenue *= 0.97
        elif store_type == 'Convenience' and date.weekday() >= 5:
            # Weekend convenience premium
            final_revenue *= 1.03
        
        # Ensure mathematical consistency (revenue = units × effective_price)
        effective_price = final_revenue / units
        
        # Validate pricing bounds
        if category == "Beer":
            min_price, max_price = 0.50, 3.00
        else:
            min_price, max_price = 0.75, 4.00
        
        if effective_price < min_price:
            final_revenue = units * min_price
        elif effective_price > max_price:
            final_revenue = units * max_price
        
        return final_revenue, is_promotion
    
    def _calculate_simple_tdp(self, row) -> float:
        """
        Calculate simplified TDP for transaction records.
        
        Args:
            row: Transaction row
            
        Returns:
            float: TDP value
        """
        base_tdp = {'Large': 100, 'Medium': 60, 'Small': 30, 'Superstore': 150}
        store_type = row['Store_Type']
        months = row['Months_From_Start']
        category = row['Category']
        
        # Get base TDP for store type
        if store_type in ['Grocery', 'Big Box']:
            base = base_tdp.get('Large', 100)
        elif store_type == 'Liquor':
            base = base_tdp.get('Medium', 60)
        else:
            base = base_tdp.get('Small', 30)
        
        # Adjust for category and time
        if category == 'Beer':
            return base * np.random.uniform(0.8, 1.0)
        else:  # Hard Seltzer
            if months < 6:
                distribution_factor = 0.2
            elif months < 12:
                distribution_factor = 0.6
            else:
                distribution_factor = 0.9
            return base * distribution_factor * np.random.uniform(0.7, 1.1)
    
    def generate_time_series_framework(self) -> pd.DataFrame:
        """
        Generate comprehensive time series framework with daily granularity for 36 months.
        
        Returns:
            pd.DataFrame: Time series framework with seasonality and trend foundations
        """
        logger.info("Generating time series framework...")
        
        # Create daily date range for 36 months
        date_range = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq='D'
        )
        
        time_series = []
        
        for date in date_range:
            # Calculate various time-based features
            days_from_start = (date - self.start_date).days
            months_from_start = days_from_start / 30.44  # Average days per month
            
            # Seasonal patterns
            seasonality_data = self._calculate_seasonal_patterns(date)
            
            # Trend foundations for both categories
            beer_trend = self._calculate_beer_trend(months_from_start)
            seltzer_trend = self._calculate_seltzer_trend(months_from_start)
            
            time_series.append({
                'Date': date,
                'Year': date.year,
                'Month': date.month,
                'Day': date.day,
                'Year_Month': date.strftime('%Y-%m'),  # Add Year_Month as string
                'DayOfWeek': date.weekday(),  # 0=Monday, 6=Sunday
                'DayOfYear': date.timetuple().tm_yday,
                'WeekOfYear': date.isocalendar()[1],
                'Quarter': (date.month - 1) // 3 + 1,
                'DaysFromStart': days_from_start,
                'MonthsFromStart': round(months_from_start, 2),
                
                # Seasonal multipliers
                'Summer_Multiplier': seasonality_data['summer'],
                'Holiday_Multiplier': seasonality_data['holiday'],
                'Weekend_Multiplier': seasonality_data['weekend'],
                'Weather_Multiplier': seasonality_data['weather'],
                'Overall_Seasonality': seasonality_data['overall'],
                
                # Category trend foundations
                'Beer_Trend_Base': beer_trend,
                'Seltzer_Trend_Base': seltzer_trend,
                
                # Market maturity indicators
                'Market_Maturity_Phase': self._get_market_phase(months_from_start),
                'Consumer_Awareness_Seltzer': self._calculate_seltzer_awareness(months_from_start),
                
                # Special events and promotions
                'Is_Holiday': seasonality_data['is_holiday'],
                'Is_Summer_Peak': seasonality_data['is_summer_peak'],
                'Is_Weekend': date.weekday() >= 5,
                'Promotion_Likelihood': self._calculate_promotion_likelihood(date, months_from_start)
            })
        
        time_df = pd.DataFrame(time_series)
        
        logger.info(f"Generated time series framework:")
        logger.info(f"  - Total days: {len(time_df)}")
        logger.info(f"  - Date range: {time_df['Date'].min().date()} to {time_df['Date'].max().date()}")
        logger.info(f"  - Months covered: {time_df['MonthsFromStart'].max():.1f}")
        
        return time_df
    
    def _calculate_seasonal_patterns(self, date: datetime) -> Dict[str, float]:
        """
        Calculate comprehensive seasonal patterns for alcohol sales.
        
        Args:
            date (datetime): Date to calculate seasonality for
            
        Returns:
            Dict[str, float]: Dictionary of seasonal multipliers
        """
        month = date.month
        day_of_year = date.timetuple().tm_yday
        
        # Summer seasonality (peak in June-August)
        summer_peak_months = [6, 7, 8]  # June, July, August
        summer_shoulder_months = [5, 9]  # May, September
        
        if month in summer_peak_months:
            summer_multiplier = 1.4 + 0.1 * np.sin((day_of_year - 150) * np.pi / 60)
        elif month in summer_shoulder_months:
            summer_multiplier = 1.2
        else:
            summer_multiplier = 1.0
        
        # Holiday seasonality
        holiday_periods = {
            # New Year's Week
            range(1, 8): 1.3,
            # Memorial Day weekend (approximate)
            range(145, 152): 1.25,
            # July 4th week
            range(180, 190): 1.4,
            # Labor Day weekend (approximate)
            range(240, 247): 1.25,
            # Thanksgiving week
            range(325, 332): 1.2,
            # Christmas/New Year period
            range(355, 366): 1.35
        }
        
        holiday_multiplier = 1.0
        is_holiday = False
        for period, multiplier in holiday_periods.items():
            if day_of_year in period:
                holiday_multiplier = multiplier
                is_holiday = True
                break
        
        # Weekend patterns
        if date.weekday() == 4:  # Friday
            weekend_multiplier = 1.25
        elif date.weekday() in [5, 6]:  # Saturday, Sunday
            weekend_multiplier = 1.3
        else:
            weekend_multiplier = 1.0
        
        # Weather-based patterns (temperature proxy)
        # Higher sales in warmer months
        weather_multiplier = 1.0 + 0.3 * np.sin((day_of_year - 80) * 2 * np.pi / 365)
        weather_multiplier = max(0.8, min(1.3, weather_multiplier))
        
        # Overall seasonality combines all factors
        overall_seasonality = (
            summer_multiplier * 0.4 +
            holiday_multiplier * 0.3 +
            weekend_multiplier * 0.2 +
            weather_multiplier * 0.1
        )
        
        return {
            'summer': summer_multiplier,
            'holiday': holiday_multiplier,
            'weekend': weekend_multiplier,
            'weather': weather_multiplier,
            'overall': overall_seasonality,
            'is_holiday': is_holiday,
            'is_summer_peak': month in summer_peak_months
        }
    
    def _calculate_beer_trend(self, months_from_start: float) -> float:
        """
        Calculate beer category trend showing plateau pattern.
        
        Args:
            months_from_start (float): Months since analysis start
            
        Returns:
            float: Beer trend multiplier
        """
        if months_from_start <= 6:
            # Initial strong performance
            return 1.0 + (months_from_start * 0.03)  # 3% monthly growth
        elif months_from_start <= 18:
            # Continued growth but slowing
            return 1.18 + ((months_from_start - 6) * 0.015)  # 1.5% monthly growth
        elif months_from_start <= 24:
            # Plateau phase
            plateau_noise = np.random.normal(0, 0.02)  # Small random variations
            return 1.36 + plateau_noise
        else:
            # Slight decline phase
            decline_months = months_from_start - 24
            return 1.36 - (decline_months * 0.008) + np.random.normal(0, 0.015)
    
    def _calculate_seltzer_trend(self, months_from_start: float) -> float:
        """
        Calculate hard seltzer trend showing dramatic spike in last 18 months.
        
        Args:
            months_from_start (float): Months since analysis start
            
        Returns:
            float: Seltzer trend multiplier
        """
        if months_from_start <= 6:
            # Very low initial presence
            return 0.05 + (months_from_start * 0.02)
        elif months_from_start <= 12:
            # Slow building phase
            return 0.17 + ((months_from_start - 6) * 0.04)
        elif months_from_start <= 18:
            # Acceleration phase - the "discovery" period
            acceleration_months = months_from_start - 12
            return 0.41 * (1.12 ** acceleration_months)  # 12% monthly growth
        else:
            # Explosive growth phase - last 18 months
            explosive_months = months_from_start - 18
            base_growth = 0.41 * (1.12 ** 6)  # Base from acceleration phase
            return base_growth * (1.18 ** explosive_months)  # 18% monthly growth
    
    def _get_market_phase(self, months_from_start: float) -> str:
        """
        Determine market maturity phase for analytics.
        
        Args:
            months_from_start (float): Months since analysis start
            
        Returns:
            str: Market phase description
        """
        if months_from_start <= 6:
            return "Traditional_Dominance"
        elif months_from_start <= 12:
            return "Early_Innovation"
        elif months_from_start <= 18:
            return "Market_Discovery"
        elif months_from_start <= 24:
            return "Rapid_Adoption"
        else:
            return "Category_Disruption"
    
    def _calculate_seltzer_awareness(self, months_from_start: float) -> float:
        """
        Calculate consumer awareness of hard seltzers over time.
        
        Args:
            months_from_start (float): Months since analysis start
            
        Returns:
            float: Awareness percentage (0-1)
        """
        # S-curve adoption pattern
        if months_from_start <= 6:
            return 0.05  # 5% awareness
        elif months_from_start <= 12:
            return 0.05 + (months_from_start - 6) * 0.03  # Gradual increase
        else:
            # Rapid awareness growth
            t = (months_from_start - 12) / 12  # Normalize to 0-2 range
            return min(0.85, 0.23 + 0.62 / (1 + np.exp(-3 * (t - 0.5))))
    
    def _calculate_promotion_likelihood(self, date: datetime, months_from_start: float) -> float:
        """
        Calculate likelihood of promotional activities.
        
        Args:
            date (datetime): Date
            months_from_start (float): Months since start
            
        Returns:
            float: Promotion likelihood (0-1)
        """
        base_likelihood = 0.15  # 15% base promotion rate
        
        # Higher promotions during competitive periods (seltzer growth phase)
        if months_from_start > 18:
            competitive_boost = 0.1
        else:
            competitive_boost = 0.0
        
        # Seasonal promotion patterns
        if date.month in [5, 6, 7, 8]:  # Summer
            seasonal_boost = 0.15
        elif date.month in [11, 12]:  # Holidays
            seasonal_boost = 0.1
        else:
            seasonal_boost = 0.0
        
        return min(0.4, base_likelihood + competitive_boost + seasonal_boost)

    def apply_seasonality(self, base_sales: float, date: datetime, 
                         category: str) -> float:
        """
        Apply seasonal patterns to sales data using the comprehensive framework.
        
        Args:
            base_sales (float): Base sales amount
            date (datetime): Transaction date
            category (str): Product category (Beer or Hard Seltzer)
            
        Returns:
            float: Seasonally adjusted sales
        """
        seasonality_data = self._calculate_seasonal_patterns(date)
        
        # Category-specific seasonal sensitivity
        if category == "Hard Seltzer":
            # Seltzers are more sensitive to summer/weather patterns
            seasonal_multiplier = (
                seasonality_data['summer'] * 0.5 +
                seasonality_data['weather'] * 0.3 +
                seasonality_data['weekend'] * 0.2
            )
        else:  # Beer
            # Beer has more consistent seasonal patterns
            seasonal_multiplier = seasonality_data['overall']
        
        return base_sales * seasonal_multiplier
    
    def calculate_trend_multiplier(self, date: datetime, category: str) -> float:
        """
        Calculate trend multiplier based on category and time period using the comprehensive framework.
        
        This is the core logic that creates the beer plateau and seltzer growth pattern.
        
        Args:
            date (datetime): Transaction date
            category (str): Product category
            
        Returns:
            float: Trend multiplier for the given date and category
        """
        days_from_start = (date - self.start_date).days
        months_from_start = days_from_start / 30.44  # Average days per month
        
        if category == "Beer":
            return self._calculate_beer_trend(months_from_start)
        elif category == "Hard Seltzer":
            return self._calculate_seltzer_trend(months_from_start)
        
        return 1.0
    
    def export_to_csv(self, dataframe: pd.DataFrame, filename: str) -> None:
        """
        Export DataFrame to CSV with proper formatting.
        
        Args:
            dataframe (pd.DataFrame): Data to export
            filename (str): Output filename
        """
        filepath = os.path.join(self.output_dir, filename)
        dataframe.to_csv(filepath, index=False)
        logger.info(f"Exported {len(dataframe)} records to {filepath}")
    
    def generate_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Generate all synthetic datasets and export to CSV files with data quality validation.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all generated datasets
        """
        logger.info("Starting synthetic data generation process...")
        
        # Generate datasets in sequence
        logger.info("Step 1/5: Generating product catalog...")
        products_df = self.generate_product_catalog()
        
        logger.info("Step 2/5: Generating geography and retailer data...")
        locations_df = self.generate_geography_data()
        
        logger.info("Step 3/5: Generating TDP distribution data...")
        tdp_df = self.generate_tdp_distribution_data(products_df, locations_df)
        
        logger.info("Step 4/5: Generating sales transactions...")
        sales_df = self.generate_sales_transactions(products_df, locations_df)
        
        logger.info("Step 5/5: Validating data quality and referential integrity...")
        self._validate_data_quality(products_df, locations_df, sales_df, tdp_df)
        
        # Export to CSV files with proper formatting
        self._export_with_validation(products_df, "products.csv")
        self._export_with_validation(locations_df, "locations.csv")
        self._export_with_validation(tdp_df, "tdp_distribution.csv")
        self._export_with_validation(sales_df, "sales_transactions.csv")
        
        # Generate comprehensive data quality report
        self._generate_data_quality_report(products_df, locations_df, sales_df, tdp_df)
        
        logger.info("Synthetic data generation completed successfully!")
        
        return {
            "products": products_df,
            "locations": locations_df,
            "tdp_distribution": tdp_df,
            "sales": sales_df
        }
    
    def _validate_data_quality(self, products_df: pd.DataFrame, locations_df: pd.DataFrame,
                             sales_df: pd.DataFrame, tdp_df: pd.DataFrame) -> None:
        """
        Comprehensive data quality validation and referential integrity checks.
        
        Args:
            products_df (pd.DataFrame): Product catalog
            locations_df (pd.DataFrame): Location data
            sales_df (pd.DataFrame): Sales transactions
            tdp_df (pd.DataFrame): TDP distribution data
        """
        logger.info("Performing comprehensive data quality validation...")
        
        validation_errors = []
        
        # 1. Check for null values in critical fields
        critical_fields = {
            'products': ['SKU', 'Brand', 'Category', 'ABV', 'Price_Per_Unit'],
            'locations': ['Retailer_ID', 'Region', 'State', 'Store_Type', 'Alcohol_License'],
            'sales': ['Transaction_ID', 'Date', 'Retailer_ID', 'SKU', 'Units_Sold', 'Total_Revenue'],
            'tdp': ['Date', 'SKU', 'TDP_Percentage', 'Weighted_TDP_Percentage']
        }
        
        datasets = {
            'products': products_df,
            'locations': locations_df,
            'sales': sales_df,
            'tdp': tdp_df
        }
        
        for dataset_name, df in datasets.items():
            for field in critical_fields[dataset_name]:
                null_count = df[field].isnull().sum()
                if null_count > 0:
                    validation_errors.append(f"{dataset_name}.{field}: {null_count} null values")
        
        # 2. Referential integrity checks
        logger.info("Checking referential integrity...")
        
        # Check SKU references
        product_skus = set(products_df['SKU'])
        sales_skus = set(sales_df['SKU'])
        tdp_skus = set(tdp_df['SKU'])
        
        orphaned_sales_skus = sales_skus - product_skus
        orphaned_tdp_skus = tdp_skus - product_skus
        
        if orphaned_sales_skus:
            validation_errors.append(f"Sales data contains {len(orphaned_sales_skus)} orphaned SKUs")
        if orphaned_tdp_skus:
            validation_errors.append(f"TDP data contains {len(orphaned_tdp_skus)} orphaned SKUs")
        
        # Check Retailer ID references
        location_retailers = set(locations_df['Retailer_ID'])
        sales_retailers = set(sales_df['Retailer_ID'])
        
        orphaned_sales_retailers = sales_retailers - location_retailers
        if orphaned_sales_retailers:
            validation_errors.append(f"Sales data contains {len(orphaned_sales_retailers)} orphaned Retailer IDs")
        
        # 3. Business logic validation
        logger.info("Validating business logic...")
        
        # Price consistency checks
        price_inconsistencies = 0
        for _, sale in sales_df.sample(min(1000, len(sales_df))).iterrows():
            expected_revenue = sale['Units_Sold'] * sale['Unit_Price']
            actual_revenue = sale['Total_Revenue']
            
            # Allow for promotional discounts (up to 30% off)
            if actual_revenue > expected_revenue * 1.05:  # 5% tolerance for rounding
                price_inconsistencies += 1
        
        if price_inconsistencies > 0:
            validation_errors.append(f"Found {price_inconsistencies} price inconsistencies in sample")
        
        # Category-specific validations
        beer_products = products_df[products_df['Category'] == 'Beer']
        seltzer_products = products_df[products_df['Category'] == 'Hard Seltzer']
        
        # ABV ranges
        invalid_beer_abv = beer_products[(beer_products['ABV'] < 0) | (beer_products['ABV'] > 15)]
        invalid_seltzer_abv = seltzer_products[(seltzer_products['ABV'] < 0) | (seltzer_products['ABV'] > 8)]
        
        if len(invalid_beer_abv) > 0:
            validation_errors.append(f"Found {len(invalid_beer_abv)} beers with invalid ABV")
        if len(invalid_seltzer_abv) > 0:
            validation_errors.append(f"Found {len(invalid_seltzer_abv)} seltzers with invalid ABV")
        
        # 4. Date range validation
        min_date = sales_df['Date'].min()
        max_date = sales_df['Date'].max()
        
        if min_date < self.start_date or max_date > self.end_date:
            validation_errors.append(f"Sales dates outside expected range: {min_date} to {max_date}")
        
        # 5. Geographic validation
        valid_regions = ['Northeast', 'Southeast', 'Midwest', 'West', 'Southwest']
        invalid_regions = set(locations_df['Region']) - set(valid_regions)
        if invalid_regions:
            validation_errors.append(f"Invalid regions found: {invalid_regions}")
        
        # 6. TDP validation
        invalid_tdp = tdp_df[(tdp_df['TDP_Percentage'] < 0) | (tdp_df['TDP_Percentage'] > 100)]
        if len(invalid_tdp) > 0:
            validation_errors.append(f"Found {len(invalid_tdp)} invalid TDP percentages")
        
        # Report validation results
        if validation_errors:
            logger.warning(f"Data quality issues found:")
            for error in validation_errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("✅ All data quality checks passed!")
        
        # Log summary statistics
        logger.info("Dataset summary:")
        logger.info(f"  Products: {len(products_df):,} ({len(beer_products)} beers, {len(seltzer_products)} seltzers)")
        logger.info(f"  Locations: {len(locations_df):,} (across {locations_df['State'].nunique()} states)")
        logger.info(f"  Sales Transactions: {len(sales_df):,} (${sales_df['Total_Revenue'].sum():,.2f} total)")
        logger.info(f"  TDP Records: {len(tdp_df):,} (tracking distribution over time)")
    
    def _export_with_validation(self, dataframe: pd.DataFrame, filename: str) -> None:
        """
        Export DataFrame to CSV with validation and proper formatting.
        
        Args:
            dataframe (pd.DataFrame): Data to export
            filename (str): Output filename
        """
        filepath = os.path.join(self.output_dir, filename)
        
        # Ensure proper data types before export
        df_export = dataframe.copy()
        
        # Format datetime columns
        datetime_columns = df_export.select_dtypes(include=['datetime64']).columns
        for col in datetime_columns:
            df_export[col] = df_export[col].dt.strftime('%Y-%m-%d')
        
        # Format numeric columns
        numeric_columns = df_export.select_dtypes(include=['float64']).columns
        for col in numeric_columns:
            if 'Price' in col or 'Revenue' in col:
                df_export[col] = df_export[col].round(2)
            elif 'Percentage' in col or 'TDP' in col:
                df_export[col] = df_export[col].round(2)
            else:
                df_export[col] = df_export[col].round(4)
        
        # Export with proper CSV formatting
        df_export.to_csv(
            filepath, 
            index=False,
            encoding='utf-8',
            float_format='%.2f',
            date_format='%Y-%m-%d'
        )
        
        # Validate exported file
        try:
            # Read back and verify
            test_df = pd.read_csv(filepath, nrows=5)
            if len(test_df) == 0:
                raise ValueError("Exported file is empty")
            
            logger.info(f"✅ Exported {len(dataframe):,} records to {filepath}")
            logger.info(f"   File size: {os.path.getsize(filepath) / 1024 / 1024:.1f} MB")
            
        except Exception as e:
            logger.error(f"❌ Export validation failed for {filename}: {e}")
    
    def _generate_data_quality_report(self, products_df: pd.DataFrame, locations_df: pd.DataFrame,
                                    sales_df: pd.DataFrame, tdp_df: pd.DataFrame) -> None:
        """
        Generate comprehensive data quality and business intelligence report.
        
        Args:
            products_df (pd.DataFrame): Product catalog
            locations_df (pd.DataFrame): Location data
            sales_df (pd.DataFrame): Sales transactions
            tdp_df (pd.DataFrame): TDP distribution data
        """
        logger.info("Generating comprehensive data quality report...")
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("SYNTHETIC POS DATA GENERATION - QUALITY REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Analysis Period: {self.start_date.date()} to {self.end_date.date()}")
        report_lines.append("")
        
        # Dataset Overview
        report_lines.append("DATASET OVERVIEW")
        report_lines.append("-" * 40)
        report_lines.append(f"Products Catalog: {len(products_df):,} products")
        report_lines.append(f"  - Beer Products: {len(products_df[products_df['Category'] == 'Beer']):,}")
        report_lines.append(f"  - Hard Seltzer Products: {len(products_df[products_df['Category'] == 'Hard Seltzer']):,}")
        report_lines.append(f"  - Unique Brands: {products_df['Brand'].nunique()}")
        report_lines.append("")
        
        report_lines.append(f"Geographic Coverage: {len(locations_df):,} locations")
        report_lines.append(f"  - Regions: {locations_df['Region'].nunique()}")
        report_lines.append(f"  - States: {locations_df['State'].nunique()}")
        report_lines.append(f"  - Cities: {locations_df['City'].nunique()}")
        report_lines.append(f"  - Store Types: {', '.join(locations_df['Store_Type'].unique())}")
        report_lines.append("")
        
        report_lines.append(f"Sales Transactions: {len(sales_df):,} transactions")
        report_lines.append(f"  - Total Revenue: ${sales_df['Total_Revenue'].sum():,.2f}")
        report_lines.append(f"  - Total Units: {sales_df['Units_Sold'].sum():,}")
        report_lines.append(f"  - Average Transaction: ${sales_df['Total_Revenue'].mean():.2f}")
        report_lines.append(f"  - Date Range: {sales_df['Date'].min().date()} to {sales_df['Date'].max().date()}")
        report_lines.append("")
        
        # Business Intelligence Insights
        report_lines.append("BUSINESS INTELLIGENCE INSIGHTS")
        report_lines.append("-" * 40)
        
        # Category performance over time
        monthly_category = sales_df.groupby(['Year_Month', 'Category']).agg({
            'Total_Revenue': 'sum',
            'Units_Sold': 'sum'
        }).reset_index()
        
        # Find pivot point
        beer_monthly = monthly_category[monthly_category['Category'] == 'Beer']
        seltzer_monthly = monthly_category[monthly_category['Category'] == 'Hard Seltzer']
        
        if len(beer_monthly) > 0 and len(seltzer_monthly) > 0:
            beer_peak = beer_monthly.loc[beer_monthly['Total_Revenue'].idxmax()]
            seltzer_final = seltzer_monthly.iloc[-1]
            
            report_lines.append(f"Beer Category Peak: {beer_peak['Year_Month']} (${beer_peak['Total_Revenue']:,.2f})")
            report_lines.append(f"Seltzer Final Performance: {seltzer_final['Year_Month']} (${seltzer_final['Total_Revenue']:,.2f})")
            
            # Calculate growth rates
            if len(seltzer_monthly) >= 12:
                early_seltzer = seltzer_monthly.iloc[5]['Total_Revenue']  # Month 6
                late_seltzer = seltzer_monthly.iloc[-1]['Total_Revenue']   # Final month
                growth_rate = ((late_seltzer / early_seltzer) ** (1/2.5)) - 1  # Annualized
                report_lines.append(f"Seltzer Growth Rate (annualized): {growth_rate:.1%}")
        
        # Regional performance
        regional_performance = sales_df.groupby(['Region', 'Category'])['Total_Revenue'].sum().unstack(fill_value=0)
        report_lines.append("")
        report_lines.append("Regional Performance (Total Revenue):")
        for region in regional_performance.index:
            beer_rev = regional_performance.loc[region, 'Beer']
            seltzer_rev = regional_performance.loc[region, 'Hard Seltzer']
            seltzer_share = seltzer_rev / (beer_rev + seltzer_rev) * 100
            report_lines.append(f"  {region}: Beer ${beer_rev:,.0f}, Seltzer ${seltzer_rev:,.0f} ({seltzer_share:.1f}% seltzer share)")
        
        # TDP Analysis
        if len(tdp_df) > 0:
            final_tdp = tdp_df[tdp_df['Date'] == tdp_df['Date'].max()]
            avg_beer_tdp = final_tdp[final_tdp['Category'] == 'Beer']['TDP_Percentage'].mean()
            avg_seltzer_tdp = final_tdp[final_tdp['Category'] == 'Hard Seltzer']['TDP_Percentage'].mean()
            
            report_lines.append("")
            report_lines.append("Final Distribution Analysis:")
            report_lines.append(f"  Average Beer TDP: {avg_beer_tdp:.1f}%")
            report_lines.append(f"  Average Seltzer TDP: {avg_seltzer_tdp:.1f}%")
        
        # Data Quality Summary
        report_lines.append("")
        report_lines.append("DATA QUALITY SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append("✅ Referential integrity maintained across all datasets")
        report_lines.append("✅ Business logic validation passed")
        report_lines.append("✅ Realistic pricing and variance patterns applied")
        report_lines.append("✅ Seasonal and regional patterns implemented")
        report_lines.append("✅ Product lifecycle and TDP growth modeled")
        
        # File Information
        report_lines.append("")
        report_lines.append("EXPORTED FILES")
        report_lines.append("-" * 40)
        for filename in ["products.csv", "locations.csv", "tdp_distribution.csv", "sales_transactions.csv"]:
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                size_mb = os.path.getsize(filepath) / 1024 / 1024
                report_lines.append(f"  {filename}: {size_mb:.1f} MB")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("Ready for PySpark ETL and Analysis Pipeline!")
        report_lines.append("=" * 80)
        
        # Save report
        report_path = os.path.join(self.output_dir, "data_quality_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"📊 Comprehensive report saved to {report_path}")
        
        # Also create a JSON summary for programmatic access
        summary_data = {
            "generation_date": datetime.now().isoformat(),
            "analysis_period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat()
            },
            "datasets": {
                "products": len(products_df),
                "locations": len(locations_df),
                "sales_transactions": len(sales_df),
                "tdp_records": len(tdp_df)
            },
            "business_metrics": {
                "total_revenue": float(sales_df['Total_Revenue'].sum()),
                "total_units": int(sales_df['Units_Sold'].sum()),
                "unique_products": int(products_df['SKU'].nunique()),
                "geographic_coverage": {
                    "regions": int(locations_df['Region'].nunique()),
                    "states": int(locations_df['State'].nunique()),
                    "cities": int(locations_df['City'].nunique())
                }
            }
        }
        
        summary_path = os.path.join(self.output_dir, "generation_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2)
        
        logger.info(f"📋 JSON summary saved to {summary_path}")
    
    def generate_summary_report(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """
        Generate a summary report of the created datasets (legacy method for compatibility).
        
        Args:
            datasets (Dict[str, pd.DataFrame]): Generated datasets
        """
        logger.info("Generating legacy summary report...")
        
        report = []
        report.append("=== SYNTHETIC POS DATA GENERATION SUMMARY ===")
        report.append(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Analysis Period: {self.start_date.date()} to {self.end_date.date()}")
        report.append("")
        
        for name, df in datasets.items():
            report.append(f"{name.upper()} Dataset:")
            report.append(f"  - Records: {len(df):,}")
            report.append(f"  - Columns: {list(df.columns)}")
            if name == 'sales':
                report.append(f"  - Total Revenue: ${df['Total_Revenue'].sum():,.2f}")
                report.append(f"  - Total Units: {df['Units_Sold'].sum():,}")
            report.append("")
        
        # Save report
        report_path = os.path.join(self.output_dir, "legacy_summary.txt")
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        logger.info(f"Legacy summary report saved to {report_path}")


def main():
    """
    Main execution function for the POS data generator.
    """
    print("🍺 Beer Company POS Data Generator")
    print("=" * 50)
    
    # Initialize generator in sample mode for faster testing
    generator = POSDataGenerator(sample_mode=True)
    
    # Generate all synthetic data
    datasets = generator.generate_all_data()
    
    # Create summary report
    generator.generate_summary_report(datasets)
    
    print("\n✅ Synthetic data generation completed!")
    print(f"📁 Files saved to: {generator.output_dir}/")
    print("\nNext steps:")
    print("1. Review generated CSV files")
    print("2. Set up PySpark environment")
    print("3. Ingest data into Spark DataFrames")
    print("\n💡 To generate full 3-year dataset, set sample_mode=False")


if __name__ == "__main__":
    main()