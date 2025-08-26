#!/usr/bin/env python3
"""
Script para migrar las API Secret Keys existentes de texto plano a cifrado
"""

import sqlite3
import sys
import os
from cryptography.fernet import Fernet
import base64

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Importar la configuración de cifrado
from services.auth_service import get_encryption_key, fernet

def migrate_api_secret_keys():
    """Migra las API Secret Keys existentes de texto plano a cifrado"""
    
    db_path = "backend/data/backtesting.db"
    
    print("🔐 Iniciando migración de API Secret Keys...")
    print(f"📁 Base de datos: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todos los usuarios con API Secret Keys en texto plano
        cursor.execute("""
            SELECT id, username, api_secret_key 
            FROM users 
            WHERE api_secret_key IS NOT NULL 
            AND api_secret_key != ''
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("✅ No hay API Secret Keys para migrar")
            return
        
        print(f"📊 Encontrados {len(users)} usuarios con API Secret Keys")
        
        # Migrar cada API Secret Key
        for user_id, username, plain_api_secret_key in users:
            try:
                # Verificar si ya está cifrada (intentar descifrar)
                try:
                    fernet.decrypt(plain_api_secret_key.encode())
                    print(f"✅ Usuario {username}: API Secret Key ya está cifrada")
                    continue
                except:
                    # No está cifrada, proceder con la migración
                    pass
                
                # Cifrar la API Secret Key
                encrypted_api_secret_key = fernet.encrypt(plain_api_secret_key.encode()).decode()
                
                # Actualizar en la base de datos
                cursor.execute("""
                    UPDATE users 
                    SET api_secret_key = ? 
                    WHERE id = ?
                """, (encrypted_api_secret_key, user_id))
                
                print(f"🔐 Usuario {username}: API Secret Key cifrada exitosamente")
                
            except Exception as e:
                print(f"❌ Error migrando usuario {username}: {e}")
                continue
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print("✅ Migración completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_api_secret_keys()
