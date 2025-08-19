#!/usr/bin/env python3
"""
Muestra los últimos 40 registros del dataset SOPR CP - Hour.
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.sqlite_client import get_dataset_by_name, load_ticks_by_dataset

def main():
    dataset_name = "SOPR CP - Hour"
    
    # Obtener el dataset
    dataset = get_dataset_by_name(dataset_name)
    if not dataset:
        print(f"❌ Dataset no encontrado: {dataset_name}")
        return
    
    print(f"📊 Dataset: {dataset['name']}")
    print(f"📈 Total de registros: {dataset['row_count']}")
    print()
    
    # Cargar los últimos 40 registros
    ticks = load_ticks_by_dataset(dataset['id'])
    if ticks.empty:
        print("❌ No se pudieron cargar los registros")
        return
    
    # Convertir timestamp a datetime y ordenar
    df = ticks.copy()
    df['t'] = pd.to_datetime(df['t'])
    df = df.sort_values('t')
    
    # Mostrar los últimos 40 registros
    last_40 = df.tail(40)
    
    print("📋 Últimos 40 registros:")
    print("=" * 80)
    print(f"{'Fecha':<20} {'Valor':<12} {'Precio USD':<15}")
    print("=" * 80)
    
    for _, row in last_40.iterrows():
        date_str = row['t'].strftime('%Y-%m-%d %H:%M')
        value_str = f"{row['v']:.6f}"
        price_str = f"{row['usd']:.2f}"
        print(f"{date_str:<20} {value_str:<12} {price_str:<15}")
    
    print("=" * 80)
    print(f"📅 Rango: {last_40['t'].min()} a {last_40['t'].max()}")
    print(f"📊 Registros mostrados: {len(last_40)}")

if __name__ == "__main__":
    main()
