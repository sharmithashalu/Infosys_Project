import sys
import os

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from database import get_engine
from sqlalchemy import text

def test_connection():
    engine = get_engine()
    print(f"Testing connection to: {engine.url}")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Successfully connected to the database!")
            print(f"Result of SELECT 1: {result.fetchone()}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_connection()
