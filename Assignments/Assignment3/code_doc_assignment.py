#!/usr/bin/env python3
"""
Labor Market Task Analysis
This script analyzes task intensity trends across different countries using O*NET and Eurostat data.
"""

# =============================================================================
# 1. IMPORTS AND CONFIGURATION
# =============================================================================
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Configuration - all parameters in one place
CONFIG = {
    "data_dir": "Data",  # Directory containing data files
    "output_dir": "output",  # Directory for saving results
    "countries": ["Belgium", "Spain", "Poland"],
    "task_types": {
        "NRCA": {  # Non-routine cognitive analytical
            "columns": ["t_4A2a4", "t_4A2b2", "t_4A4a1"],
            "description": "Non-routine cognitive analytical tasks",
            "long_name": "Analyzing Data or Information, Thinking Creatively, Interpreting the Meaning of Information for Others"
        },
        "RM": {  # Routine manual
            "columns": ["t_4A3a3", "t_4C2d1i", "t_4C3d3"],
            "description": "Routine manual tasks",
            "long_name": "Controlling Machines and Processes, Spend Time Making Repetitive Motions, Pace Determined by Speed of Equipment"
        }
    },
    "isco_levels": 9,  # Number of ISCO categories (1-9)
    "isco_aggregation_level": 1,  # First digit of ISCO code
    "eurostat_filename": "Eurostat_employment_isco.xlsx",
    "onet_filename": "onet_tasks.csv"
}

# Ensure output directory exists
os.makedirs(CONFIG["output_dir"], exist_ok=True)

# =============================================================================
# 2. DATA LOADING FUNCTIONS
# =============================================================================
def load_onet_tasks(data_dir, filename=CONFIG["onet_filename"]):
    """
    Load O*NET tasks data cross-walked to ISCO-08 classification.
    
    Args:
        data_dir (str): Directory containing data files
        filename (str): Name of the O*NET tasks file
        
    Returns:
        pd.DataFrame: Processed task data
    """
    file_path = os.path.join(data_dir, filename)
    print(f"Loading O*NET tasks data from {file_path}...")
    
    task_data = pd.read_csv(file_path)
    
    # Convert ISCO codes to numeric format
    task_data["isco08"] = pd.to_numeric(task_data["isco08"], errors='coerce')
    
    return task_data

def load_eurostat_employment(data_dir, filename=CONFIG["eurostat_filename"], 
                            isco_levels=CONFIG["isco_levels"]):
    """
    Load Eurostat employment data by ISCO occupation.
    
    Args:
        data_dir (str): Directory containing data files
        filename (str): Name of the Eurostat employment file
        isco_levels (int): Number of ISCO categories to load
        
    Returns:
        tuple: (all_data, country_totals) where:
            - all_data is a DataFrame with combined employment data
            - country_totals is a dict of country-specific total employment
    """
    file_path = os.path.join(data_dir, filename)
    print(f"Loading Eurostat employment data from {file_path}...")
    
    # Read all relevant sheets from the Excel file
    all_sheets = []
    country_totals = {}
    
    for i in range(1, isco_levels + 1):
        sheet_name = f"ISCO{i}"
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Add ISCO category column
        df["ISCO"] = i
        
        all_sheets.append(df)
    
    # Combine all ISCO data into one DataFrame
    all_data = pd.concat(all_sheets, ignore_index=True)
    
    # Calculate country totals
    for country in CONFIG["countries"]:
        country_totals[country] = all_data.groupby("TIME")[country].sum()
    
    return all_data, country_totals

# =============================================================================
# 3. DATA PROCESSING FUNCTIONS
# =============================================================================
def process_isco_data(task_data, aggregation_level=CONFIG["isco_aggregation_level"]):
    """
    Process ISCO codes to extract the specified level of classification.
    
    Args:
        task_data (pd.DataFrame): Task data with ISCO codes
        aggregation_level (int): Level of ISCO aggregation (1 for major groups)
        
    Returns:
        tuple: (processed task_data, aggregated data)
    """
    print("Processing ISCO data...")
    
    # Extract the first digit of ISCO code for major groups
    task_data["isco08_1dig"] = task_data["isco08"].astype(str).str[:aggregation_level].astype(int)
    
    # Aggregate task data by ISCO major groups
    agg_data = task_data.groupby(["isco08_1dig"]).mean()
    agg_data = agg_data.drop(columns=["isco08"])
    
    return task_data, agg_data

def calculate_country_shares(all_data, country_totals, countries=CONFIG["countries"]):
    """
    Calculate employment shares for each country and occupation.
    
    Args:
        all_data (pd.DataFrame): Combined employment data
        country_totals (dict): Dictionary of country-specific total employment
        countries (list): List of countries to process
        
    Returns:
        pd.DataFrame: Data with share columns added
    """
    print("Calculating country employment shares...")
    
    # Create a copy to avoid modifying the original
    data = all_data.copy()
    
    # Calculate shares for each country
    for country in countries:
        total_col = f"total_{country}"
        share_col = f"share_{country}"
        
        # Repeat country totals for each occupation
        repeated_totals = pd.concat([country_totals[country]] * len(countries), ignore_index=True)
        
        # Add to data
        data[total_col] = repeated_totals
        data[share_col] = data[country] / data[total_col]
    
    return data

def standardize_task_values(combined, countries=CONFIG["countries"]):
    """
    Standardize task values for each country using employment shares as weights.
    
    Args:
        combined (pd.DataFrame): Combined data with task and employment information
        countries (list): List of countries to process
        
    Returns:
        pd.DataFrame: Data with standardized task values
    """
    print("Standardizing task values...")
    
    # Create a copy to avoid modifying the original
    data = combined.copy()
    
    # Process each task type
    for task_type, task_info in CONFIG["task_types"].items():
        task_columns = task_info["columns"]
        
        # Process each task column
        for col in task_columns:
            for country in countries:
                share_col = f"share_{country}"
                std_col = f"std_{country}_{col}"
                
                # Calculate weighted mean and standard deviation
                weights = data[share_col]
                values = data[col]
                
                # Skip if all weights are zero
                if weights.sum() == 0:
                    data[std_col] = 0
                    continue
                
                # Calculate weighted mean
                mean = np.average(values, weights=weights)
                
                # Calculate weighted standard deviation
                variance = np.average((values - mean)**2, weights=weights)
                std = np.sqrt(variance)
                
                # Standardize the values
                if std > 0:
                    data[std_col] = (values - mean) / std
                else:
                    data[std_col] = 0
    
    return data

def calculate_task_intensity(combined, countries=CONFIG["countries"]):
    """
    Calculate task intensity for each country and task type.
    
    Args:
        combined (pd.DataFrame): Combined data with standardized task values
        countries (list): List of countries to process
        
    Returns:
        pd.DataFrame: Data with task intensity values
    """
    print("Calculating task intensity...")
    
    # Create a copy to avoid modifying the original
    data = combined.copy()
    
    # Process each task type
    for task_type, task_info in CONFIG["task_types"].items():
        task_columns = task_info["columns"]
        
        # Calculate combined task intensity for each country
        for country in countries:
            # Create column names for the combined and standardized task intensity
            combined_col = f"{country}_{task_type}"
            std_col = f"std_{country}_{task_type}"
            
            # Sum the standardized task values
            data[combined_col] = sum(data[f"std_{country}_{col}"] for col in task_columns)
            
            # Standardize the combined task intensity
            share_col = f"share_{country}"
            weights = data[share_col]
            values = data[combined_col]
            
            # Skip if all weights are zero
            if weights.sum() == 0:
                data[std_col] = 0
                continue
            
            # Calculate weighted mean and standard deviation
            mean = np.average(values, weights=weights)
            variance = np.average((values - mean)**2, weights=weights)
            std = np.sqrt(variance)
            
            # Standardize the values
            if std > 0:
                data[std_col] = (values - mean) / std
            else:
                data[std_col] = 0
    
    return data

def calculate_time_trends(combined, countries=CONFIG["countries"]):
    """
    Calculate time trends in task intensity for each country.
    
    Args:
        combined (pd.DataFrame): Combined data with task intensity values
        countries (list): List of countries to process
        
    Returns:
        dict: Dictionary of trend DataFrames for each country and task type
    """
    print("Calculating time trends...")
    
    trends = {}
    
    # Process each task type
    for task_type in CONFIG["task_types"].keys():
        # Process each country
        for country in countries:
            std_col = f"std_{country}_{task_type}"
            multip_col = f"multip_{country}_{task_type}"
            
            # Create a copy with relevant columns
            country_data = combined[["TIME", std_col, f"share_{country}"]].copy()
            
            # Calculate weighted task intensity
            country_data[multip_col] = country_data[std_col] * country_data[f"share_{country}"]
            
            # Aggregate by time
            time_trends = country_data.groupby("TIME")[multip_col].sum().reset_index()
            
            # Store in trends dictionary
            if country not in trends:
                trends[country] = {}
            trends[country][task_type] = time_trends
    
    return trends

# =============================================================================
# 4. VISUALIZATION FUNCTIONS
# =============================================================================
def plot_task_trends(trends, task_type="NRCA"):
    """
    Plot task intensity trends across countries.
    
    Args:
        trends (dict): Trend data organized by country and task type
        task_type (str): Type of task to plot ("NRCA" or "RM")
    """
    plt.figure(figsize=(10, 6))
    
    for country, task_data in trends.items():
        if task_type in task_data:
            df = task_data[task_type]
            plt.plot(df["TIME"], df[f"multip_{country}_{task_type}"], label=country)
    
    # Format the plot
    plt.title(f"{CONFIG['task_types'][task_type]['description']} Intensity Trends\n({CONFIG['task_types'][task_type]['long_name']})")
    plt.xlabel("Year")
    plt.ylabel("Standardized Task Intensity")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Set x-axis ticks at regular intervals
    if len(df) > 0:
        plt.xticks(range(0, len(df), 3), df["TIME"].iloc[::3], rotation=45)
    
    # Save and show the plot
    plt.tight_layout()
    output_path = os.path.join(CONFIG["output_dir"], f"{task_type}_trends.png")
    plt.savefig(output_path, dpi=300)
    plt.show()
    
    print(f"Plot saved to {output_path}")

# =============================================================================
# 5. MAIN EXECUTION
# =============================================================================
def main():
    """Main function to execute the entire analysis pipeline."""
    print("Starting labor market task analysis...")
    
    # Load data
    task_data = load_onet_tasks(CONFIG["data_dir"])
    all_data, country_totals = load_eurostat_employment(CONFIG["data_dir"])
    
    # Process ISCO data
    task_data, agg_data = process_isco_data(task_data)
    
    # Merge employment and task data
    print("Merging employment and task data...")
    combined = pd.merge(all_data, agg_data, left_on='ISCO', right_on='isco08_1dig', how='left')
    
    # Calculate employment shares
    combined = calculate_country_shares(combined, country_totals)
    
    # Standardize task values
    combined = standardize_task_values(combined)
    
    # Calculate task intensity
    combined = calculate_task_intensity(combined)
    
    # Calculate time trends
    trends = calculate_time_trends(combined)
    
    # Generate visualizations
    print("Generating visualizations...")
    for task_type in CONFIG["task_types"].keys():
        plot_task_trends(trends, task_type)
    
    print("Analysis complete! Results saved to", CONFIG["output_dir"])

if __name__ == "__main__":
    main()