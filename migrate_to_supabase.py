"""
Migration script to transfer existing snipe data from snipes_data.json to Supabase.
Run this script once before deploying to Northflank.

Usage:
    python migrate_to_supabase.py
"""

import json
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def migrate_data():
    """Migrate snipe counts from JSON file to Supabase."""
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Check if old data file exists
    data_file = "snipes_data.json"
    if not os.path.exists(data_file):
        print(f"No {data_file} found. Nothing to migrate.")
        return
    
    # Load old data
    print(f"Loading data from {data_file}...")
    with open(data_file, 'r') as f:
        try:
            old_data = json.load(f)
        except json.JSONDecodeError:
            print("Error: Could not parse JSON file")
            return
    
    if not old_data:
        print("No data to migrate.")
        return
    
    print(f"Found {len(old_data)} users to migrate...")
    
    # Migrate to Supabase
    success_count = 0
    error_count = 0
    
    for user_id, count in old_data.items():
        try:
            supabase.table("snipes").upsert({
                "user_id": user_id,
                "count": count
            }).execute()
            print(f"✓ Migrated {user_id}: {count} snipes")
            success_count += 1
        except Exception as e:
            print(f"✗ Error migrating {user_id}: {e}")
            error_count += 1
    
    print("\n" + "="*50)
    print(f"Migration complete!")
    print(f"Successfully migrated: {success_count}")
    print(f"Errors: {error_count}")
    print("="*50)
    
    if error_count == 0:
        print(f"\nYou can now safely delete {data_file}")

if __name__ == "__main__":
    migrate_data()

