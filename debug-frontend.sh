#!/bin/bash

echo "🔍 Diagnóstico del Frontend"
echo "==========================="

echo ""
echo "1. 📦 Estado del contenedor frontend:"
docker ps | grep frontend

echo ""
echo "2. 📋 Logs completos del frontend:"
docker logs backtesting-frontend-prod

echo ""
echo "3. 🔍 Verificar variables de entorno:"
docker exec backtesting-frontend-prod env | grep -E "(NODE_ENV|VITE_|PORT)"

echo ""
echo "4. 🔌 Verificar puertos internos:"
docker exec backtesting-frontend-prod netstat -tlnp 2>/dev/null || echo "netstat no disponible en el contenedor"

echo ""
echo "5. 📁 Verificar archivos en el contenedor:"
docker exec backtesting-frontend-prod ls -la /app

echo ""
echo "6. 🔍 Verificar proceso principal:"
docker exec backtesting-frontend-prod ps aux

echo ""
echo "7. 🌐 Intentar curl desde dentro del contenedor:"
docker exec backtesting-frontend-prod curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000 || echo "curl no disponible o error"

echo ""
echo "8. 📊 Recursos del contenedor:"
docker stats backtesting-frontend-prod --no-stream


