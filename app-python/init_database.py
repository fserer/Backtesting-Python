#!/usr/bin/env python3
"""
Script para inicializar una base de datos SQLite vacía con la estructura correcta.
"""

import sqlite3
import os

def init_database():
    """Inicializa una base de datos SQLite vacía con la estructura correcta"""
    
    db_path = "backend/data/backtesting.db"
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"🔧 Inicializando base de datos: {db_path}")
    
    # Conectar a la base de datos (se creará si no existe)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            main_wallet TEXT,
            hyperliquid_wallet TEXT,
            api_secret_key TEXT
        )
    """)
    
    # Crear tabla de estrategias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            strategy_type TEXT NOT NULL,
            configuration TEXT NOT NULL,
            results TEXT,
            dataset_name TEXT,
            period_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Crear tabla de datasets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla de ticks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticks_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume REAL,
            FOREIGN KEY (dataset_id) REFERENCES datasets (id)
        )
    """)
    
    # Crear índices para mejorar el rendimiento
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticks_dataset_timestamp ON ticks_new (dataset_id, timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_strategies_user ON strategies (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)")
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("✅ Base de datos inicializada correctamente")
    print("📋 Tablas creadas:")
    print("   - users (usuarios y autenticación)")
    print("   - strategies (estrategias guardadas)")
    print("   - datasets (datasets subidos)")
    print("   - ticks_new (datos de ticks)")
    print("   - Índices para optimización")

if __name__ == "__main__":
    init_database()
