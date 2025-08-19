#!/usr/bin/env python3
"""
Script temporal para mostrar los últimos 20 registros de MVRV CP - Hour
"""

from services.sqlite_client import get_dataset_by_name, load_ticks_by_dataset
import pandas as pd

def main():
    # Obtener el dataset
    dataset = get_dataset_by_name('MVRV CP - Hour')
    print(f"Dataset: {dataset}")
    
    if not dataset:
        print("❌ Dataset no encontrado")
        return
    
    # Cargar todos los ticks
    ticks = load_ticks_by_dataset(dataset['id'])
    print(f"Total ticks: {len(ticks)}")
    
    if ticks.empty:
        print("❌ No hay ticks para mostrar")
        return
    
    # Mostrar los últimos 20 registros
    last_20 = ticks.tail(20)
    print(f"\n📊 Últimos {len(last_20)} registros de MVRV CP - Hour:")
    print("=" * 80)
    
    # Formatear para mejor visualización
    print(f"{'Fecha':<20} {'Valor':<15} {'Precio USD':<15}")
    print("-" * 50)
    
    for _, row in last_20.iterrows():
        timestamp = pd.to_datetime(row['t']).strftime('%Y-%m-%d %H:%M:%S')
        value = f"{row['v']:.6f}" if pd.notna(row['v']) else "N/A"
        price = f"{row['usd']:.2f}" if pd.notna(row['usd']) else "N/A"
        
        print(f"{timestamp:<20} {value:<15} {price:<15}")
    
    print("-" * 50)
    print(f"📊 Mostrados {len(last_20)} registros de {dataset['name']}")

if __name__ == "__main__":
    main()
