#!/bin/bash

# Script de deploy para Backtesting Python
# Uso: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}

echo "🚀 Iniciando deploy en modo: $ENVIRONMENT"

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado. Por favor, reinicia la sesión y ejecuta el script nuevamente."
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose instalado."
fi

# Parar contenedores existentes
echo "🛑 Parando contenedores existentes..."
docker-compose down

# Limpiar imágenes antiguas (opcional)
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "🧹 Limpiando imágenes antiguas..."
    docker system prune -f
fi

# Construir y levantar contenedores
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "🏗️ Construyendo contenedores de producción..."
    docker-compose -f docker-compose.prod.yml up --build -d
else
    echo "🏗️ Construyendo contenedores de desarrollo..."
    docker-compose up --build -d
fi

# Verificar que los contenedores estén funcionando
echo "🔍 Verificando estado de los contenedores..."
sleep 10
docker-compose ps

echo "✅ Deploy completado!"
echo "🌐 Frontend: http://localhost:3000 (dev) o http://localhost (prod)"
echo "🔧 Backend: http://localhost:8000"
echo "📊 Logs: docker-compose logs -f"
