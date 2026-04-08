import pandas as pd
import numpy as np
import os

def clean_data(df):
    """Clean the dataset."""
    if df.isnull().values.any():
        # Fill numeric with mean, categorical with 'Unknown'
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].mean())
        df = df.fillna('Unknown')
    
    df = df.drop_duplicates()
    return df

def feature_engineering(df):
    """Apply feature engineering to derive sustainability metrics."""
    
    # Make a copy to avoid warnings
    df = df.copy()
    
    # Ensure numeric columns are converted
    numeric_cols = ['co2_emission', 'cost', 'biodegradability', 'recyclability', 'strength', 'co2_emission_raw', 'recyclability_raw']
    for col in numeric_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            except:
                pass
    
    # Create co2_emission if not exist
    if 'co2_emission' not in df.columns:
        df['co2_emission'] = df['co2_emission_raw'] if 'co2_emission_raw' in df.columns else 0
    
    if 'cost' not in df.columns:
        df['cost'] = 0
    
    # 1. CO2 Impact Index
    max_co2 = df['co2_emission'].max()
    min_co2 = df['co2_emission'].min()
    if max_co2 != min_co2:
        df['co2_impact_index'] = df['co2_emission'].apply(lambda x: round(((max_co2 - x) / (max_co2 - min_co2)) * 10, 2))
    else:
        df['co2_impact_index'] = 5.0
    
    # 2. Cost Efficiency Index
    max_cost = df['cost'].max()
    min_cost = df['cost'].min()
    if max_cost != min_cost:
        df['cost_efficiency_index'] = df['cost'].apply(lambda x: round(((max_cost - x) / (max_cost - min_cost)) * 10, 2))
    else:
        df['cost_efficiency_index'] = 5.0
    
    # 3. Material Suitability Score
    if 'biodegradability' not in df.columns:
        df['biodegradability'] = 5.0
    if 'recyclability' not in df.columns:
        df['recyclability'] = 50.0
    if 'strength' not in df.columns:
        df['strength'] = 5.0
        
    df['suitability_score'] = (
        (df['biodegradability'].astype(float) * 1.0) * 0.3 + 
        (df['recyclability'].astype(float) / 10.0) * 0.3 + 
        (df['strength'].astype(float) * 1.0) * 0.2 + 
        (df['co2_impact_index'].astype(float) * 1.0) * 0.2
    ).round(2)
    
    return df

def process_raw_data():
    """Main function to process and merge raw CSV files."""
    materials_raw_path = 'data/raw/materials.csv'
    attributes_raw_path = 'data/raw/product_attributes.csv'
    output_path = 'data/processed/materials_engineered.csv'

    if not os.path.exists(materials_raw_path) or not os.path.exists(attributes_raw_path):
        print("Missing raw data files.")
        return

    # Load raw data
    m_df = pd.read_csv(materials_raw_path)
    a_df = pd.read_csv(attributes_raw_path)

    # Truncate to match sizes - use the smaller dataframe size as reference
    min_rows = min(len(m_df), len(a_df))
    m_df = m_df.iloc[:min_rows].reset_index(drop=True)
    a_df = a_df.iloc[:min_rows].reset_index(drop=True)

    # Simple column mapping and merge
    combined_df = pd.concat([m_df, a_df], axis=1)

    # Rename columns to match project schema
    rename_map = {
        'Material_Type': 'material',
        'Strength': 'strength',
        'CO2Emission': 'co2_emission_raw',
        'Recyclability': 'recyclability_raw',
        'Cost': 'cost',
        'Product Type': 'industry',
        'Weight Capacity (kg)': 'weight_capacity',
        'Lifecycle CO2 Emission (kg CO2)': 'co2_emission',
        'Durability (years)': 'durability',
        'Recyclability (%)': 'recyclability'
    }
    combined_df = combined_df.rename(columns=rename_map)

    # Clean and Engineer
    cleaned_df = clean_data(combined_df)
    engineered_df = feature_engineering(cleaned_df)

    # Keep only necessary columns for the materials table
    target_cols = [
        'material', 'strength', 'weight_capacity', 'biodegradability', 
        'co2_emission', 'recyclability', 'cost', 'durability', 'industry', 
        'co2_impact_index', 'cost_efficiency_index', 'suitability_score'
    ]
    # Ensure they exist
    existing_cols = [c for c in target_cols if c in engineered_df.columns]
    final_df = engineered_df[existing_cols]

    # Add 'type' column if it doesn't exist (can use material name)
    if 'type' not in final_df.columns:
        final_df['type'] = final_df['material']

    os.makedirs('data/processed', exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    process_raw_data()
