import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

materials_data = [
    {"material": "Cardboard", "type": "Cellulose", "strength": 6, "weight_capacity": 15, "biodegradability": 9, "co2_emission": 0.5, "recyclability": 90, "cost": 0.2, "durability": 5, "industry": "General"},
    {"material": "Recycled Paper", "type": "Cellulose", "strength": 4, "weight_capacity": 5, "biodegradability": 10, "co2_emission": 0.3, "recyclability": 100, "cost": 0.15, "durability": 3, "industry": "General"},
    {"material": "Bioplastic (PLA)", "type": "Bio-polymer", "strength": 7, "weight_capacity": 10, "biodegradability": 8, "co2_emission": 1.2, "recyclability": 0, "cost": 0.6, "durability": 6, "industry": "Food"},
    {"material": "Mushroom Packaging", "type": "Fungi", "strength": 5, "weight_capacity": 8, "biodegradability": 10, "co2_emission": 0.1, "recyclability": 0, "cost": 0.8, "durability": 4, "industry": "Electronics"},
    {"material": "Recycled Plastic (rPET)", "type": "Recycled Polymer", "strength": 8, "weight_capacity": 20, "biodegradability": 2, "co2_emission": 1.5, "recyclability": 85, "cost": 0.4, "durability": 8, "industry": "Cosmetics"},
    {"material": "Bamboo", "type": "Natural Fiber", "strength": 9, "weight_capacity": 25, "biodegradability": 10, "co2_emission": 0.2, "recyclability": 0, "cost": 1.2, "durability": 9, "industry": "General"},
    {"material": "Wood", "type": "Natural Fiber", "strength": 8, "weight_capacity": 30, "biodegradability": 9, "co2_emission": 0.4, "recyclability": 50, "cost": 1.5, "durability": 9, "industry": "Industrial"},
    {"material": "Glass", "type": "Inorganic", "strength": 5, "weight_capacity": 15, "biodegradability": 0, "co2_emission": 1.8, "recyclability": 100, "cost": 0.9, "durability": 7, "industry": "Cosmetics"},
    {"material": "Cornstarch", "type": "Bio-polymer", "strength": 3, "weight_capacity": 3, "biodegradability": 10, "co2_emission": 0.4, "recyclability": 0, "cost": 0.5, "durability": 2, "industry": "Food"},
    {"material": "Honeycomb Paper", "type": "Cellulose", "strength": 7, "weight_capacity": 12, "biodegradability": 9, "co2_emission": 0.4, "recyclability": 95, "cost": 0.3, "durability": 6, "industry": "Electronics"}
]

# Create more synthetic data based on these templates to reach 100 rows for ML training later
data = []
for _ in range(10):
    for base in materials_data:
        entry = base.copy()
        # Add some noise
        entry['strength'] = max(1, min(10, entry['strength'] + np.random.randint(-1, 2)))
        entry['weight_capacity'] = max(1, entry['weight_capacity'] + np.random.randint(-2, 3))
        entry['co2_emission'] = max(0.05, round(entry['co2_emission'] + np.random.uniform(-0.1, 0.1), 2))
        entry['cost'] = max(0.05, round(entry['cost'] + np.random.uniform(-0.05, 0.05), 2))
        data.append(entry)

df = pd.DataFrame(data)
df.to_csv('data/raw/materials.csv', index=False)
print("Generated materials.csv with 100 rows.")
