import sqlite3
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class HyperliquidService:
    def __init__(self, db_path: str = "app/data/backtesting.db"):
        self.db_path = db_path
        self._init_hyperliquid_table()
    
    def _init_hyperliquid_table(self):
        """Inicializa la tabla de configuraciones de Hyperliquid"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hyperliquid_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    api_wallet_name TEXT NOT NULL,
                    api_wallet_address TEXT NOT NULL,
                    api_private_key TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Tabla hyperliquid_settings inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando tabla hyperliquid_settings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def save_hyperliquid_settings(self, user_id: int, username: str, api_wallet_name: str, 
                                 api_wallet_address: str, api_private_key: str) -> Dict[str, Any]:
        """Guarda o actualiza la configuración de Hyperliquid de un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si ya existe configuración para este usuario
            cursor.execute("""
                SELECT id FROM hyperliquid_settings WHERE user_id = ?
            """, (user_id,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar configuración existente
                cursor.execute("""
                    UPDATE hyperliquid_settings 
                    SET api_wallet_name = ?, api_wallet_address = ?, api_private_key = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (api_wallet_name, api_wallet_address, api_private_key, user_id))
                
                setting_id = existing[0]
            else:
                # Crear nueva configuración
                cursor.execute("""
                    INSERT INTO hyperliquid_settings 
                    (user_id, username, api_wallet_name, api_wallet_address, api_private_key)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, api_wallet_name, api_wallet_address, api_private_key))
                
                setting_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Configuración de Hyperliquid guardada exitosamente para {username}")
            return {
                "id": setting_id,
                "user_id": user_id,
                "username": username,
                "api_wallet_name": api_wallet_name,
                "api_wallet_address": api_wallet_address,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error guardando configuración de Hyperliquid: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def get_hyperliquid_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene la configuración de Hyperliquid de un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, username, api_wallet_name, api_wallet_address, 
                       api_private_key, is_active, created_at, updated_at
                FROM hyperliquid_settings 
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "api_wallet_name": row[3],
                    "api_wallet_address": row[4],
                    "api_private_key": row[5],
                    "is_active": bool(row[6]),
                    "created_at": row[7],
                    "updated_at": row[8]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo configuración de Hyperliquid: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def delete_hyperliquid_settings(self, user_id: int) -> bool:
        """Elimina la configuración de Hyperliquid de un usuario (soft delete)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE hyperliquid_settings 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected_rows > 0:
                logger.info(f"Configuración de Hyperliquid eliminada para usuario {user_id}")
                return True
            else:
                logger.warning(f"No se encontró configuración de Hyperliquid para usuario {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando configuración de Hyperliquid: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def get_all_hyperliquid_settings(self) -> List[Dict[str, Any]]:
        """Obtiene todas las configuraciones activas de Hyperliquid (para administración)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, username, api_wallet_name, api_wallet_address, 
                       is_active, created_at, updated_at
                FROM hyperliquid_settings 
                WHERE is_active = 1
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "api_wallet_name": row[3],
                    "api_wallet_address": row[4],
                    "is_active": bool(row[5]),
                    "created_at": row[6],
                    "updated_at": row[7]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo todas las configuraciones de Hyperliquid: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
