#!/usr/bin/env python3
"""
Test script for PostgreSQL + TimescaleDB setup
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_postgresql_setup():
    """Test PostgreSQL + TimescaleDB setup"""
    
    print("=== TESTING POSTGRESQL + TIMESCALEDB SETUP ===")
    
    try:
        # Test database factory
        from services.database_factory import DatabaseFactory
        
        print(f"Database type: {DatabaseFactory.get_database_type()}")
        
        # Get database functions
        db_functions = DatabaseFactory.get_database_functions()
        
        # Test creating a dataset
        print("\n--- Testing dataset creation ---")
        dataset = db_functions.create_dataset("Test Dataset PostgreSQL", "Test dataset for PostgreSQL")
        print(f"Created dataset: {dataset}")
        
        # Test saving ticks
        print("\n--- Testing ticks insertion ---")
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='1H')
        sample_data = pd.DataFrame({
            't': dates,
            'v': np.random.random(len(dates)),
            'usd': 20000 + np.random.random(len(dates)) * 10000
        })
        
        rows_inserted = db_functions.save_ticks(dataset['id'], sample_data)
        print(f"Inserted {rows_inserted} rows")
        
        # Test loading ticks
        print("\n--- Testing ticks loading ---")
        loaded_data = db_functions.load_ticks_by_dataset(dataset['id'])
        print(f"Loaded {len(loaded_data)} rows")
        print(f"Date range: {loaded_data['t'].min()} to {loaded_data['t'].max()}")
        
        # Test getting all datasets
        print("\n--- Testing dataset listing ---")
        datasets = db_functions.get_all_datasets()
        print(f"Found {len(datasets)} datasets")
        
        # Test getting dataset by ID
        print("\n--- Testing dataset retrieval ---")
        retrieved_dataset = db_functions.get_dataset_by_id(dataset['id'])
        print(f"Retrieved dataset: {retrieved_dataset}")
        
        # Test getting dataset stats (PostgreSQL specific)
        if hasattr(db_functions, 'get_dataset_stats'):
            print("\n--- Testing dataset stats ---")
            stats = db_functions.get_dataset_stats(dataset['id'])
            print(f"Dataset stats: {stats}")
        
        # Test updating dataset
        print("\n--- Testing dataset update ---")
        updated_dataset = db_functions.update_dataset(dataset['id'], "Updated Test Dataset", "Updated description")
        print(f"Updated dataset: {updated_dataset}")
        
        # Test deleting dataset
        print("\n--- Testing dataset deletion ---")
        db_functions.delete_dataset(dataset['id'])
        print("Dataset deleted successfully")
        
        print("\n=== ALL TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_postgresql_setup()
    sys.exit(0 if success else 1)
