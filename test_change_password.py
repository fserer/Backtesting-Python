#!/usr/bin/env python3
"""
Script de prueba para verificar el endpoint de cambio de contraseña.
"""

import requests
import json

def test_change_password():
    """Prueba el endpoint de cambio de contraseña"""
    
    # URL base
    base_url = "http://localhost:8000"
    
    print("🧪 Script de Prueba - Cambio de Contraseña")
    print("=" * 50)
    
    # Paso 1: Login para obtener token
    print("1️⃣ Intentando login...")
    
    login_data = {
        "username": "fserer",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get("access_token")
            print(f"   ✅ Login exitoso - Token obtenido")
            print(f"   Usuario: {login_result.get('user', {}).get('username')}")
        else:
            print(f"   ❌ Login fallido: {login_response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return
    
    # Paso 2: Verificar token
    print("\n2️⃣ Verificando token...")
    
    try:
        verify_response = requests.get(
            f"{base_url}/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"   Status Code: {verify_response.status_code}")
        
        if verify_response.status_code == 200:
            print("   ✅ Token válido")
        else:
            print(f"   ❌ Token inválido: {verify_response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error verificando token: {e}")
        return
    
    # Paso 3: Probar cambio de contraseña
    print("\n3️⃣ Probando cambio de contraseña...")
    
    change_password_data = {
        "current_password": "password123",
        "new_password": "test123456"
    }
    
    try:
        change_response = requests.post(
            f"{base_url}/api/auth/change-password",
            data=change_password_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {token}"
            }
        )
        
        print(f"   Status Code: {change_response.status_code}")
        print(f"   Response Headers: {dict(change_response.headers)}")
        
        if change_response.status_code == 200:
            result = change_response.json()
            print(f"   ✅ Cambio de contraseña exitoso: {result}")
        else:
            print(f"   ❌ Error en cambio de contraseña:")
            print(f"   Response: {change_response.text}")
            
            # Intentar parsear como JSON
            try:
                error_data = change_response.json()
                print(f"   Error Detail: {error_data.get('detail', 'No detail')}")
            except:
                print(f"   Raw Response: {change_response.text}")
                
    except Exception as e:
        print(f"   ❌ Error en cambio de contraseña: {e}")
    
    # Paso 4: Probar login con nueva contraseña
    print("\n4️⃣ Probando login con nueva contraseña...")
    
    new_login_data = {
        "username": "fserer",
        "password": "test123456"
    }
    
    try:
        new_login_response = requests.post(
            f"{base_url}/api/auth/login",
            json=new_login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {new_login_response.status_code}")
        
        if new_login_response.status_code == 200:
            print("   ✅ Login con nueva contraseña exitoso")
        else:
            print(f"   ❌ Login con nueva contraseña fallido: {new_login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en login con nueva contraseña: {e}")
    
    # Paso 5: Restaurar contraseña original
    print("\n5️⃣ Restaurando contraseña original...")
    
    restore_data = {
        "current_password": "test123456",
        "new_password": "password123"
    }
    
    try:
        restore_response = requests.post(
            f"{base_url}/api/auth/change-password",
            data=restore_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {token}"
            }
        )
        
        print(f"   Status Code: {restore_response.status_code}")
        
        if restore_response.status_code == 200:
            print("   ✅ Contraseña restaurada exitosamente")
        else:
            print(f"   ❌ Error restaurando contraseña: {restore_response.text}")
            
    except Exception as e:
        print(f"   ❌ Error restaurando contraseña: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Prueba completada")

if __name__ == "__main__":
    test_change_password()
