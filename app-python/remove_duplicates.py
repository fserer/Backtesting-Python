#!/usr/bin/env python3
"""
Elimina duplicados del dataset SOPR CP - Hour.
"""

import sys
import os
import sqlite3
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.sqlite_client import get_dataset_by_name

def main():
    dataset_name = "SOPR CP - Hour"
    
    # Obtener el dataset
    dataset = get_dataset_by_name(dataset_name)
    if not dataset:
        print(f"❌ Dataset no encontrado: {dataset_name}")
        return
    
    print(f"📊 Dataset: {dataset['name']}")
    print(f"📈 Registros antes: {dataset['row_count']}")
    
    # Conectar a la base de datos
    db_path = "backtesting.db"
    conn = sqlite3.connect(db_path)
    
    try:
        # Cargar todos los registros
        query = '''
            SELECT id, t, v, usd
            FROM ticks_new
            WHERE dataset_id = ?
            ORDER BY t ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=(dataset['id'],))
        print(f"📊 Registros cargados: {len(df)}")
        
        # Convertir timestamp
        df['t'] = pd.to_datetime(df['t'])
        
        # Identificar duplicados (mismo timestamp, valor y precio)
        df['duplicate'] = df.duplicated(subset=['t', 'v', 'usd'], keep='first')
        duplicates = df[df['duplicate']]
        
        print(f"🔍 Duplicados encontrados: {len(duplicates)}")
        
        if len(duplicates) > 0:
            print("📋 Duplicados a eliminar:")
            for _, row in duplicates.iterrows():
                print(f"  - {row['t']}: v={row['v']}, usd={row['usd']} (ID: {row['id']})")
            
            # Eliminar duplicados
            duplicate_ids = duplicates['id'].tolist()
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM ticks_new WHERE id IN ({})'.format(','.join('?' * len(duplicate_ids))),
                duplicate_ids
            )
            
            # Actualizar contador de registros
            cursor.execute('''
                UPDATE datasets 
                SET row_count = (SELECT COUNT(*) FROM ticks_new WHERE dataset_id = ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (dataset['id'], dataset['id']))
            
            conn.commit()
            print(f"✅ Eliminados {len(duplicate_ids)} registros duplicados")
            
            # Verificar resultado
            cursor.execute('SELECT COUNT(*) FROM ticks_new WHERE dataset_id = ?', (dataset['id'],))
            new_count = cursor.fetchone()[0]
            print(f"📈 Registros después: {new_count}")
            
        else:
            print("✅ No hay duplicados para eliminar")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
