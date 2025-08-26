#!/usr/bin/env python3
"""
Script para resetear la contraseña de un usuario específico.
Muestra la lista de usuarios disponibles y permite elegir cuál cambiar.
"""

import sqlite3
import sys
import os
from passlib.context import CryptContext

# Configuración de la base de datos
db_path = "/app/data/backtesting.db"

# Configuración de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def get_users():
    """Obtiene la lista de usuarios de la base de datos"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, is_active
            FROM users 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        conn.close()
        return users
        
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return []

def update_user_password(user_id: int, new_password: str) -> bool:
    """Actualiza la contraseña de un usuario específico"""
    try:
        hashed_password = get_password_hash(new_password)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET hashed_password = ? 
            WHERE id = ? AND is_active = 1
        """, (hashed_password, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        print(f"Contraseña actualizada exitosamente para usuario ID {user_id}")
        return True
        
    except Exception as e:
        print(f"Error actualizando contraseña: {e}")
        return False

def main():
    print("🔐 Script de Reset de Contraseña")
    print("=" * 40)
    
    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"❌ Error: No se encuentra la base de datos en {db_path}")
        print("Asegúrate de ejecutar este script dentro del contenedor Docker")
        sys.exit(1)
    
    # Obtener lista de usuarios
    print("📋 Usuarios disponibles:")
    print("-" * 40)
    
    users = get_users()
    if not users:
        print("❌ No se encontraron usuarios en la base de datos")
        sys.exit(1)
    
    # Mostrar usuarios
    for user_id, username, email, is_active in users:
        status = "✅ Activo" if is_active else "❌ Inactivo"
        print(f"ID {user_id}: {username} ({email}) - {status}")
    
    print("-" * 40)
    
    # Pedir ID del usuario
    while True:
        try:
            user_id_input = input("🔢 Ingresa el ID del usuario para cambiar contraseña: ").strip()
            user_id = int(user_id_input)
            
            # Verificar que el usuario existe
            user_exists = any(user[0] == user_id for user in users)
            if not user_exists:
                print(f"❌ Error: No existe un usuario con ID {user_id}")
                continue
            
            # Verificar que el usuario está activo
            user_active = any(user[0] == user_id and user[3] for user in users)
            if not user_active:
                print(f"❌ Error: El usuario con ID {user_id} está inactivo")
                continue
            
            break
            
        except ValueError:
            print("❌ Error: Por favor ingresa un número válido")
        except KeyboardInterrupt:
            print("\n👋 Operación cancelada")
            sys.exit(0)
    
    # Obtener información del usuario seleccionado
    selected_user = next(user for user in users if user[0] == user_id)
    username = selected_user[1]
    
    print(f"\n🎯 Usuario seleccionado: {username} (ID: {user_id})")
    
    # Confirmar la operación
    while True:
        confirm = input("¿Estás seguro de que quieres cambiar la contraseña a 'password123'? (s/n): ").strip().lower()
        if confirm in ['s', 'si', 'sí', 'y', 'yes']:
            break
        elif confirm in ['n', 'no']:
            print("👋 Operación cancelada")
            sys.exit(0)
        else:
            print("Por favor responde 's' o 'n'")
    
    # Actualizar contraseña
    print(f"\n🔄 Actualizando contraseña para {username}...")
    
    success = update_user_password(user_id, "password123")
    
    if success:
        print(f"✅ ¡Éxito! La contraseña de '{username}' ha sido cambiada a 'password123'")
        print(f"🔑 Usuario: {username}")
        print(f"🔑 Contraseña: password123")
    else:
        print(f"❌ Error: No se pudo actualizar la contraseña de '{username}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
