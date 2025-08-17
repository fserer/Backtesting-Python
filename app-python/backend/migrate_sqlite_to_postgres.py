#!/usr/bin/env python3
"""
Script para migrar datos de SQLite a PostgreSQL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import sqlite3
import pandas as pd
from datetime import datetime

def migrate_sqlite_to_postgres():
    """Migra datos de SQLite a PostgreSQL"""
    
    print("=== MIGRACIÓN DE SQLITE A POSTGRESQL ===")
    
    try:
        # Conectar a SQLite
        sqlite_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'backtesting.db')
        if not os.path.exists(sqlite_path):
            print(f"❌ No se encontró la base de datos SQLite en: {sqlite_path}")
            return False
            
        sqlite_conn = sqlite3.connect(sqlite_path)
        print(f"✅ Conectado a SQLite: {sqlite_path}")
        
        # Obtener datasets de SQLite
        datasets_query = "SELECT id, name, description, created_at, updated_at, row_count FROM datasets"
        datasets_df = pd.read_sql_query(datasets_query, sqlite_conn)
        
        print(f"📊 Encontrados {len(datasets_df)} datasets en SQLite")
        
        if datasets_df.empty:
            print("ℹ️ No hay datasets para migrar")
            return True
        
        # Importar funciones de PostgreSQL
        from services.database_factory import DatabaseFactory
        db_functions = DatabaseFactory.get_database_functions()
        
        # Migrar cada dataset
        for _, dataset in datasets_df.iterrows():
            print(f"\n--- Migrando dataset: {dataset['name']} ---")
            
            # Crear dataset en PostgreSQL
            try:
                new_dataset = db_functions.create_dataset(
                    name=dataset['name'],
                    description=dataset['description']
                )
                print(f"✅ Dataset creado en PostgreSQL con ID: {new_dataset['id']}")
                
                # Obtener ticks de SQLite
                ticks_query = f"SELECT t, v, usd FROM ticks WHERE dataset_id = {dataset['id']}"
                ticks_df = pd.read_sql_query(ticks_query, sqlite_conn)
                
                if not ticks_df.empty:
                    # Convertir timestamp si es necesario
                    if 't' in ticks_df.columns:
                        ticks_df['t'] = pd.to_datetime(ticks_df['t'])
                    
                    # Guardar ticks en PostgreSQL
                    rows_inserted = db_functions.save_ticks(new_dataset['id'], ticks_df)
                    print(f"✅ Migrados {rows_inserted} ticks")
                else:
                    print("ℹ️ No hay ticks para migrar")
                    
            except Exception as e:
                print(f"❌ Error migrando dataset {dataset['name']}: {str(e)}")
                continue
        
        sqlite_conn.close()
        print("\n=== MIGRACIÓN COMPLETADA ===")
        return True
        
    except Exception as e:
        print(f"❌ Error en la migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_sqlite_to_postgres()
    sys.exit(0 if success else 1)
