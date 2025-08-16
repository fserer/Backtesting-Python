import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Cargar variables de entorno desde .env
load_dotenv()

class Settings(BaseSettings):
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    
    # Configuración de la aplicación
    app_name: str = "Backtesting API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuración de CORS
    allowed_origins: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
