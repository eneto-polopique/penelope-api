#!/usr/bin/env python3
"""
Script to load data from JSON files into PostgreSQL database (schema_v2).
Inserts data from:
- final_wovens_data_20260120_150126.json into woven_info table
- final_variants_data_similarities_clip.json into variant_info table
- knn_pantone.json into pantone_colors table
- final_stock_mapping.json into stock_info table
"""

import json
import base64
import os
from sqlalchemy import create_engine, text
from pathlib import Path
import sys

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'penelope_db'),
    'user': os.getenv('DB_USER', 'penelope'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Build SQLAlchemy connection string (using pg8000 - pure Python driver)
DB_URL = f"postgresql+pg8000://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Paths to JSON files
DATASET_DIR = Path(__file__).parent.parent / 'dataset'
WOVENS_JSON = DATASET_DIR / 'final_wovens_data_20260120_150126.json'
VARIANTS_JSON = DATASET_DIR / 'final_variants_data_similarities_clip.json'
PANTONE_JSON = DATASET_DIR / 'knn_pantone.json'
STOCK_JSON = DATASET_DIR / 'final_stock_mapping.json'


def load_json_file(filepath):
    """Load and parse a JSON file."""
    print(f"Loading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def insert_woven_info(connection, data):
    """Insert data into woven_info table."""
    print(f"Inserting {len(data)} records into woven_info table...")
    
    insert_query = text("""
        INSERT INTO woven_info (id, draw, finishing, reference, date, composition, variants, yarns)
        VALUES (:id, :draw, :finishing, :reference, :date, :composition, :variants, :yarns)
        ON CONFLICT (id) DO UPDATE SET
            draw = EXCLUDED.draw,
            finishing = EXCLUDED.finishing,
            reference = EXCLUDED.reference,
            date = EXCLUDED.date,
            composition = EXCLUDED.composition,
            variants = EXCLUDED.variants,
            yarns = EXCLUDED.yarns
    """)
    
    records = []
    for item in data:
        records.append({
            'id': item['id'],
            'draw': item.get('draw'),
            'finishing': item.get('finishing'),
            'reference': item.get('reference'),
            'date': item.get('date'),
            'composition': item.get('composition'),
            'variants': item.get('variants', []),
            'yarns': json.dumps(item.get('yarns', []))  # Convert to JSONB
        })
    
    # Insert in batches for better performance
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        connection.execute(insert_query, batch)
    
    print(f"Successfully inserted {len(records)} records into woven_info.")


def insert_variant_info(connection, data):
    """Insert data into variant_info table."""
    print(f"Processing {len(data)} variant records...")
    
    # Get valid woven IDs
    woven_query = text("SELECT id FROM woven_info")
    woven_rows = connection.execute(woven_query).fetchall()
    valid_woven_ids = set(row[0] for row in woven_rows)
    
    print(f"Found {len(valid_woven_ids)} valid woven IDs")
    
    insert_query = text("""
        INSERT INTO variant_info (id, woven_id, variant_ref, filename, thumbnail, category, color_name, color_hex, similarity)
        VALUES (:id, :woven_id, :variant_ref, :filename, :thumbnail, :category, :color_name, :color_hex, :similarity)
        ON CONFLICT (woven_id, variant_ref) DO UPDATE SET
            filename = EXCLUDED.filename,
            thumbnail = EXCLUDED.thumbnail,
            category = EXCLUDED.category,
            color_name = EXCLUDED.color_name,
            color_hex = EXCLUDED.color_hex,
            similarity = EXCLUDED.similarity
    """)
    
    records = []
    skipped = 0
    
    for variant in data:
        woven_id = variant.get('woven_id')
        
        # Skip if woven doesn't exist
        if woven_id not in valid_woven_ids:
            skipped += 1
            continue
        
        records.append({
            'id': variant['id'],
            'woven_id': woven_id,
            'variant_ref': variant.get('variant_ref', '000'),
            'filename': variant.get('filename'),
            'thumbnail': variant.get('thumbnail'),
            'category': variant.get('category'),
            'color_name': variant.get('color_name', []),
            'color_hex': variant.get('color_hex', []),
            'similarity': json.dumps(variant.get('similarity', []))
        })
    
    # Insert in batches
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        connection.execute(insert_query, batch)
    
    print(f"Successfully inserted {len(records)} records into variant_info.")
    if skipped > 0:
        print(f"Skipped {skipped} variants (woven not found)")


def insert_pantone_colors(connection, data):
    """Insert data into pantone_colors table."""
    print(f"Inserting {len(data)} records into pantone_colors table...")
    
    insert_query = text("""
        INSERT INTO pantone_colors (name, hex, nearests)
        VALUES (:name, :hex, :nearests)
        ON CONFLICT (name) DO UPDATE SET
            hex = EXCLUDED.hex,
            nearests = EXCLUDED.nearests
    """)
    
    records = []
    for item in data:
        records.append({
            'name': item['name'],
            'hex': item['hex'],
            'nearests': item.get('nearests', [])
        })
    
    # Insert in batches for better performance
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        connection.execute(insert_query, batch)
    
    print(f"Successfully inserted {len(records)} records into pantone_colors.")


def insert_stock_info(connection, data):
    """Insert data into stock_info table."""
    print(f"Processing {len(data)} stock records...")
    
    # Get valid variant IDs
    variant_query = text("SELECT id FROM variant_info")
    variant_rows = connection.execute(variant_query).fetchall()
    valid_variant_ids = set(row[0] for row in variant_rows)
    
    print(f"Found {len(valid_variant_ids)} valid variant IDs")
    
    # Note: id field is SERIAL (auto-increment), so we don't insert it
    insert_query = text("""
        INSERT INTO stock_info (variant_id, description, quantity, perfect_match)
        VALUES (:variant_id, :description, :quantity, :perfect_match)
    """)
    
    records = []
    skipped = 0
    
    for stock in data:
        variant_id = stock['variant_id']
        
        if variant_id not in valid_variant_ids:
            skipped += 1
            continue
        
        # Handle empty quantity values
        quantity = stock.get('quantity')
        if quantity == '' or quantity is None:
            quantity = None
        
        records.append({
            'variant_id': variant_id,
            'description': stock.get('description'),
            'quantity': quantity,
            'perfect_match': stock.get('perfect_match', False)
        })
    
    # Insert in batches
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        connection.execute(insert_query, batch)
    
    print(f"Successfully inserted {len(records)} records into stock_info.")
    if skipped > 0:
        print(f"Skipped {skipped} stock records (variant not found)")


def main():
    """Main function to orchestrate the data loading process."""
    try:
        # Check if JSON files exist
        if not WOVENS_JSON.exists():
            print(f"Error: {WOVENS_JSON} not found!")
            sys.exit(1)
        
        if not VARIANTS_JSON.exists():
            print(f"Error: {VARIANTS_JSON} not found!")
            sys.exit(1)
        
        if not PANTONE_JSON.exists():
            print(f"Error: {PANTONE_JSON} not found!")
            sys.exit(1)
        
        if not STOCK_JSON.exists():
            print(f"Error: {STOCK_JSON} not found!")
            sys.exit(1)
        
        # Load JSON data
        print("Loading JSON files...")
        wovens_data = load_json_file(WOVENS_JSON)
        variants_data = load_json_file(VARIANTS_JSON)
        pantone_data = load_json_file(PANTONE_JSON)
        stock_data = load_json_file(STOCK_JSON)
        
        # Create SQLAlchemy engine
        print("\nConnecting to PostgreSQL database...")
        engine = create_engine(DB_URL)
        
        # Use connection context manager for automatic transaction handling
        with engine.begin() as connection:
            try:
                # Insert data into tables (in order of dependencies)
                print("\n" + "="*60)
                insert_woven_info(connection, wovens_data)
                
                print("\n" + "="*60)
                insert_variant_info(connection, variants_data)
                
                print("\n" + "="*60)
                insert_pantone_colors(connection, pantone_data)
                
                print("\n" + "="*60)
                insert_stock_info(connection, stock_data)
                
                print("\n" + "="*60)
                print("All data loaded successfully!")
                print("="*60)
                
            except Exception as e:
                print(f"\nError during data insertion: {e}")
                raise
        
        print("\nDatabase connection closed.")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
