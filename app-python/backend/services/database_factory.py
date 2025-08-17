import os
import logging
from typing import Union

logger = logging.getLogger(__name__)

class DatabaseFactory:
    """Factory para crear instancias de base de datos según la configuración."""
    
    @staticmethod
    def get_database_type() -> str:
        """Obtiene el tipo de base de datos desde las variables de entorno."""
        return os.getenv('DATABASE_TYPE', 'sqlite').lower()
    
    @staticmethod
    def get_database_client():
        """Obtiene el cliente de base de datos apropiado."""
        db_type = DatabaseFactory.get_database_type()
        
        if db_type == 'postgresql':
            try:
                from .postgres_client import postgres_client
                logger.info("Usando cliente PostgreSQL")
                return postgres_client
            except ImportError as e:
                logger.error(f"Error importando cliente PostgreSQL: {str(e)}")
                logger.info("Fallback a SQLite")
                from .sqlite_client import sqlite_client
                return sqlite_client
        else:
            logger.info("Usando cliente SQLite")
            from .sqlite_client import sqlite_client
            return sqlite_client
    
    @staticmethod
    def get_database_functions():
        """Obtiene las funciones de base de datos apropiadas."""
        db_type = DatabaseFactory.get_database_type()
        
        if db_type == 'postgresql':
            try:
                from . import postgres_client
                logger.info("Usando funciones PostgreSQL")
                return postgres_client
            except ImportError as e:
                logger.error(f"Error importando funciones PostgreSQL: {str(e)}")
                logger.info("Fallback a SQLite")
                from . import sqlite_client
                return sqlite_client
        else:
            logger.info("Usando funciones SQLite")
            from . import sqlite_client
            return sqlite_client
