#!/bin/bash

echo "🚀 Iniciando despliegue de Backtesting App en producción..."

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: No se encuentra docker-compose.prod.yml"
    echo "Asegúrate de estar en el directorio app-python"
    exit 1
fi

# Crear directorio de datos si no existe
mkdir -p data

# Parar contenedores existentes si están corriendo
echo "🛑 Parando contenedores existentes..."
docker-compose -f docker-compose.prod.yml down

# Obtener los últimos cambios del repositorio
echo "📥 Obteniendo últimos cambios..."
git pull origin main

# Construir las imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Levantar los servicios
echo "🚀 Levantando servicios..."
docker-compose -f docker-compose.prod.yml up -d

# Esperar un momento para que los servicios se inicien
echo "⏳ Esperando que los servicios se inicien..."
sleep 10

# Verificar el estado de los servicios
echo "✅ Verificando estado de servicios..."
docker-compose -f docker-compose.prod.yml ps

# Verificar que los servicios estén respondiendo
echo "🔍 Verificando conectividad..."
echo "Backend (puerto 8000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/health || echo "Backend no responde"

echo "Frontend (puerto 3000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000 || echo "Frontend no responde"

echo ""
echo "🎉 Despliegue completado!"
echo "🌐 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "📋 Comandos útiles:"
echo "  Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Ver estado: docker-compose -f docker-compose.prod.yml ps"
echo "  Parar servicios: docker-compose -f docker-compose.prod.yml down"

