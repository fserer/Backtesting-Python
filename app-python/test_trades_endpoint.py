#!/usr/bin/env python3
"""
Script para probar el endpoint de trades directamente
"""

import requests
import json

def test_trades_endpoint():
    """Prueba el endpoint de trades"""
    
    # URL del endpoint
    url = "http://localhost:8000/api/hyperliquid/trades"
    
    # Parámetros
    params = {
        'limit': 50
    }
    
    print(f"Probando endpoint: {url}")
    print(f"Parámetros: {params}")
    print("-" * 50)
    
    try:
        # Hacer la petición
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            trades = data.get('trades', [])
            print(f"✅ Trades obtenidos: {len(trades)}")
            
            if trades:
                print("\nPrimeros 3 trades:")
                for i, trade in enumerate(trades[:3]):
                    print(f"  {i+1}. {trade.get('coin', 'UNKNOWN')} - {trade.get('side', 'UNKNOWN')} - ${trade.get('price', 0):.2f} - {trade.get('date', 'N/A')}")
                
                print(f"\nÚltimos 3 trades:")
                for i, trade in enumerate(trades[-3:]):
                    print(f"  {i+1}. {trade.get('coin', 'UNKNOWN')} - {trade.get('side', 'UNKNOWN')} - ${trade.get('price', 0):.2f} - {trade.get('date', 'N/A')}")
            else:
                print("❌ No se encontraron trades")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_trades_endpoint()

