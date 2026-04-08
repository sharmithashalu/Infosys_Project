import sys
import os

# Add backend to path so we can import database
sys.path.append(os.path.abspath('backend'))

from database import init_db, load_data_to_db

if __name__ == "__main__":
    print("Starting database initialization...")
    init_db('scripts/schema.sql')
    load_data_to_db('data/processed/materials_engineered.csv')
    print("Database initialization complete.")
