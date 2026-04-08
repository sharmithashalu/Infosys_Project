import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from xgboost import XGBRegressor
import os

def train_models():
    # Load processed data
    data_path = 'data/processed/materials_engineered.csv'
    if not os.path.exists(data_path):
        print(f"File {data_path} not found. Running data processing first...")
        return

    df = pd.read_csv(data_path)

    # Features for predicting outcomes
    # For a real scenario, we might predict material based on product requirements.
    # But the milestone says: 
    # - Random Forest (Cost Prediction)
    # - XGBoost (CO2 Footprint Prediction)
    
    # We will use material properties to predict these values for hypothetical new materials or for validation.
    # Features: strength, weight_capacity, biodegradability, recyclability, durability
    feature_cols = ['strength', 'weight_capacity', 'biodegradability', 'recyclability', 'durability']
    X = df[feature_cols]
    
    # 1. Cost Prediction
    y_cost = df['cost']
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_cost, test_size=0.2, random_state=42)
    
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train_c, y_train_c)
    
    cost_preds = rf_model.predict(X_test_c)
    print("--- Cost Prediction (Random Forest) ---")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test_c, cost_preds)):.4f}")
    print(f"MAE: {mean_absolute_error(y_test_c, cost_preds):.4f}")
    print(f"R2 Score: {r2_score(y_test_c, cost_preds):.4f}")
    
    # 2. CO2 Prediction
    y_co2 = df['co2_emission']
    X_train_co2, X_test_co2, y_train_co2, y_test_co2 = train_test_split(X, y_co2, test_size=0.2, random_state=42)
    
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    xgb_model.fit(X_train_co2, y_train_co2)
    
    co2_preds = xgb_model.predict(X_test_co2)
    print("\n--- CO2 Footprint Prediction (XGBoost) ---")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test_co2, co2_preds)):.4f}")
    print(f"MAE: {mean_absolute_error(y_test_co2, co2_preds):.4f}")
    print(f"R2 Score: {r2_score(y_test_co2, co2_preds):.4f}")
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(rf_model, 'models/cost_model.joblib')
    joblib.dump(xgb_model, 'models/co2_model.joblib')
    print("\nModels saved to models/")

if __name__ == "__main__":
    train_models()
