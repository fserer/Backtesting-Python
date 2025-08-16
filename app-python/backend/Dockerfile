FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorio para la base de datos
RUN mkdir -p /app/data

# Copiar código de la aplicación
COPY . .

# Crear archivo de base de datos SQLite vacío
RUN touch /app/data/backtesting.db

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
