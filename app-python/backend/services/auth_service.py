"""
Servicio de autenticación para la aplicación de backtesting.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import logging
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_larga_y_segura_aqui_cambiala_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 365  # 1 año

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave de cifrado para API Secret Keys (usar la misma SECRET_KEY como base)
def get_encryption_key():
    """Genera una clave de cifrado basada en SECRET_KEY"""
    # Usar SECRET_KEY como base y generar una clave de 32 bytes para Fernet
    key_base = SECRET_KEY.encode()
    # Asegurar que tenga exactamente 32 bytes
    key = base64.urlsafe_b64encode(key_base[:32].ljust(32, b'0'))
    return key

# Inicializar Fernet para cifrado
fernet = Fernet(get_encryption_key())

class AuthService:
    def __init__(self, db_path: str = "data/backtesting.db"):
        self.db_path = db_path
        self._init_users_table()
    
    def _init_users_table(self):
        """Inicializa la tabla de usuarios si no existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    hashed_password TEXT NOT NULL,
                    main_wallet TEXT,
                    hyperliquid_wallet TEXT,
                    api_secret_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Agregar las nuevas columnas si no existen (para compatibilidad con tablas existentes)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN main_wallet TEXT")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN hyperliquid_wallet TEXT")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN api_secret_key TEXT")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
            
            conn.commit()
            conn.close()
            logger.info("Tabla de usuarios inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando tabla de usuarios: {e}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def verify_current_password(self, user_id: int, plain_password: str) -> bool:
        """Verifica la contraseña actual de un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hashed_password
                FROM users 
                WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                return False
            
            hashed_password = user_data[0]
            return self.verify_password(plain_password, hashed_password)
            
        except Exception as e:
            logger.error(f"Error verificando contraseña actual: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Genera el hash de una contraseña"""
        return pwd_context.hash(password)
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Cambia la contraseña de un usuario"""
        try:
            hashed_password = self.get_password_hash(new_password)
            
            conn = sqlite3.connect(self.db_path)
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
            
            logger.info(f"Contraseña cambiada exitosamente para usuario {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            return False
    
    def _encrypt_api_secret_key(self, api_secret_key: str) -> str:
        """Cifra la API Secret Key usando Fernet"""
        try:
            encrypted = fernet.encrypt(api_secret_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Error cifrando API Secret Key: {e}")
            raise
    
    def _decrypt_api_secret_key(self, encrypted_api_secret_key: str) -> str:
        """Descifra la API Secret Key usando Fernet"""
        try:
            decrypted = fernet.decrypt(encrypted_api_secret_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error descifrando API Secret Key: {e}")
            raise
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Crea un nuevo usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya existe"
                )
            
            # Verificar si el email ya existe (si se proporciona)
            if email:
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El email ya está registrado"
                    )
            
            # Crear el usuario
            hashed_password = self.get_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Usuario creado exitosamente: {username}")
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "created_at": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar usuario por username o email
            cursor.execute("""
                SELECT id, username, email, hashed_password, is_active
                FROM users 
                WHERE (username = ? OR email = ?) AND is_active = 1
            """, (username, username))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            user_id, db_username, email, hashed_password, is_active = user_data
            
            # Verificar contraseña
            if not self.verify_password(password, hashed_password):
                return None
            
            # Actualizar último login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Usuario autenticado exitosamente: {db_username}")
            return {
                "id": user_id,
                "username": db_username,
                "email": email,
                "is_active": bool(is_active)
            }
            
        except Exception as e:
            logger.error(f"Error autenticando usuario: {e}")
            return None
    
    def create_access_token(self, data: dict) -> str:
        """Crea un token JWT de acceso"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            
            # Verificar que el usuario aún existe y está activo
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, is_active
                FROM users 
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                return None
            
            user_id, db_username, email, is_active = user_data
            return {
                "id": user_id,
                "username": db_username,
                "email": email,
                "is_active": bool(is_active)
            }
            
        except JWTError:
            return None
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, created_at, last_login, is_active
                FROM users 
                WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                return None
            
            user_id, username, email, created_at, last_login, is_active = user_data
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "created_at": created_at,
                "last_login": last_login,
                "is_active": bool(is_active)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
    
    def update_hyperliquid_settings(self, user_id: int, main_wallet: str, hyperliquid_wallet: str, api_secret_key: str) -> bool:
        """Actualiza la configuración de Hyperliquid de un usuario"""
        try:
            # Cifrar la API Secret Key antes de almacenarla
            encrypted_api_secret_key = self._encrypt_api_secret_key(api_secret_key)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET main_wallet = ?, hyperliquid_wallet = ?, api_secret_key = ?
                WHERE id = ?
            """, (main_wallet, hyperliquid_wallet, encrypted_api_secret_key, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Configuración de Hyperliquid actualizada para usuario {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando configuración de Hyperliquid: {e}")
            return False
    
    def get_hyperliquid_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene la configuración de Hyperliquid de un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT main_wallet, hyperliquid_wallet, api_secret_key
                FROM users 
                WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                return None
            
            main_wallet, hyperliquid_wallet, encrypted_api_secret_key = user_data
            
            # Descifrar la API Secret Key si existe
            api_secret_key = None
            if encrypted_api_secret_key:
                try:
                    api_secret_key = self._decrypt_api_secret_key(encrypted_api_secret_key)
                except Exception as e:
                    logger.error(f"Error descifrando API Secret Key para usuario {user_id}: {e}")
                    # Si no se puede descifrar, devolver None para la API Secret Key
                    api_secret_key = None
            
            return {
                "main_wallet": main_wallet,
                "hyperliquid_wallet": hyperliquid_wallet,
                "api_secret_key": api_secret_key
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo configuración de Hyperliquid: {e}")
            return None
