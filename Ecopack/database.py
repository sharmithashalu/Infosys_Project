import os
import pandas as pd
from sqlalchemy import create_engine, text

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ecopack.db')
COST_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'cost_model.joblib')
CO2_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'co2_model.joblib')

def get_engine():
    """Returns a SQLAlchemy engine based on DATABASE_URL or SQLite."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Standardize for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return create_engine(database_url)
    
    # Default to SQLite
    return create_engine(f"sqlite:///{DB_PATH}")

def get_db_connection():
    """Returns a connection from the engine."""
    return get_engine().connect()

def init_db(schema_path='scripts/schema.sql'):
    """Initialize the database using the SQL schema."""
    if not os.path.exists(schema_path):
        # Try finding it relative to package root
        schema_path = os.path.join(BASE_DIR, schema_path)
        if not os.path.exists(schema_path):
            print(f"Schema file {schema_path} not found.")
            return

    with open(schema_path, 'r') as f:
        schema = f.read()

    # Split into individual statements by semicolon
    statements = schema.split(';')
    engine = get_engine()
    is_postgres = os.environ.get('DATABASE_URL') is not None
    
    with engine.connect() as conn:
        for stmt in statements:
            if not stmt.strip():
                continue
            
            clean_stmt = stmt.strip()
            if not is_postgres:
                # Convert SERIAL for SQLite
                clean_stmt = clean_stmt.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            
            try:
                conn.execute(text(clean_stmt))
                conn.commit()
            except Exception as e:
                # Some statements like CREATE TABLE IF NOT EXISTS might not need a commit or might fail if already exists
                print(f"Note on executing statement: {e}")
    
    print("Database initialized successfully.")

def load_data_to_db(csv_path='data/processed/materials_engineered.csv'):
    """Load processed CSV data into the materials table."""
    if not os.path.exists(csv_path):
        csv_path = os.path.join(BASE_DIR, csv_path)
        if not os.path.exists(csv_path):
            print(f"Processed data {csv_path} not found.")
            return

    df = pd.read_csv(csv_path)
    engine = get_engine()
    
    # Save to SQL table
    try:
        df.to_sql('materials', engine, if_exists='replace', index=False)
        print(f"Loaded {len(df)} records into the 'materials' table.")
    except Exception as e:
        print(f"Failed to load data: {e}")

if __name__ == "__main__":
    init_db()
    load_data_to_db()
