#!/usr/bin/env python3
"""
Script to load data from JSON files into PostgreSQL database.
Inserts data from final_penelope_dataset.json into woven_info table
and data from knn_pantone.json into pantone_colors table.
"""

import json
from sqlalchemy import create_engine, text
from pathlib import Path
import sys

# Database configuration - Update these variables with your database credentials
DB_CONFIG = {
    'host': None,          # Database server IP/hostname
    'port': None,                          # PostgreSQL port (default: 5432)
    'database': None,             # Database name
    'user': None,                    # Database user
    'password': None               # Database password
}

# Build SQLAlchemy connection string (using pg8000 - pure Python driver)
DB_URL = f"postgresql+pg8000://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Paths to JSON files
DATASET_DIR = Path(__file__).parent.parent / 'dataset'
PENELOPE_JSON = DATASET_DIR / 'final_penelope_dataset.json'
PANTONE_JSON = DATASET_DIR / 'knn_pantone.json'


def load_json_file(filepath):
    """Load and parse a JSON file."""
    print(f"Loading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def insert_woven_info(connection, data):
    """Insert data into woven_info table."""
    print(f"Inserting {len(data)} records into woven_info table...")
    
    insert_query = text("""
        INSERT INTO woven_info (id, filename, category, color_name, color_hex, similarity)
        VALUES (:id, :filename, :category, :color_name, :color_hex, :similarity)
        ON CONFLICT (id) DO UPDATE SET
            filename = EXCLUDED.filename,
            category = EXCLUDED.category,
            color_name = EXCLUDED.color_name,
            color_hex = EXCLUDED.color_hex,
            similarity = EXCLUDED.similarity
    """)
    
    records = []
    for item in data:
        records.append({
            'id': item['id'],
            'filename': F'{item['filename']}',
            'category': item['category'],
            'color_name': item['color_name'],
            'color_hex': item['color_hex'],
            'similarity': json.dumps(item['similarity'])  # Convert similarity array to JSONB
        })
    
    # Insert in batches for better performance
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        connection.execute(insert_query, batch)
    
    print(f"Successfully inserted {len(records)} records into woven_info.")


def insert_pantone_colors(connection, data):
    """Insert data into pantone_colors table."""
    print(f"Inserting {len(data)} records into pantone_colors table...")
    
    insert_query = text("""
        INSERT INTO pantone_colors (name, hex, nearest)
        VALUES (:name, :hex, :nearest)
        ON CONFLICT (name) DO UPDATE SET
            hex = EXCLUDED.hex,
            nearest = EXCLUDED.nearest
    """)
    
    records = []
    for item in data:
        records.append({
            'name': item['name'],
            'hex': item['hex'],
            'nearest': item['nearests']  # Note: JSON uses 'nearests', DB uses 'nearest'
        })
    
    # Insert in batches for better performance
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        connection.execute(insert_query, batch)
    
    print(f"Successfully inserted {len(records)} records into pantone_colors.")


def main():
    """Main function to orchestrate the data loading process."""
    try:
        # Check if JSON files exist
        if not PENELOPE_JSON.exists():
            print(f"Error: {PENELOPE_JSON} not found!")
            sys.exit(1)
        
        if not PANTONE_JSON.exists():
            print(f"Error: {PANTONE_JSON} not found!")
            sys.exit(1)
        
        # Load JSON data
        woven_data = load_json_file(PENELOPE_JSON)
        #pantone_data = load_json_file(PANTONE_JSON)
        
        # Create SQLAlchemy engine
        print("Connecting to PostgreSQL database...")
        engine = create_engine(DB_URL)
        
        # Use connection context manager for automatic transaction handling
        with engine.begin() as connection:
            try:
                # Insert data into tables
                insert_woven_info(connection, woven_data)
                #insert_pantone_colors(connection, pantone_data)
                
                print("\nAll data loaded successfully!")
                
            except Exception as e:
                print(f"\nError during data insertion: {e}")
                raise
        
        print("Database connection closed.")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
