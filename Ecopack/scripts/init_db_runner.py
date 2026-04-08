import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.insert(0, ROOT_DIR)

from database import init_db, load_data_to_db

if __name__ == "__main__":
    print("Starting database initialization...")
    init_db('scripts/schema.sql')
    load_data_to_db('data/processed/materials_engineered.csv')
    print("Database initialization complete.")
