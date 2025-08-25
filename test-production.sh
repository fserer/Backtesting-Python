#!/bin/bash

echo "🔍 Verificando conectividad en producción"
echo "========================================="

echo ""
echo "1. 📦 Contenedores corriendo:"
docker ps

echo ""
echo "2. 🔌 Puertos en uso:"
netstat -tlnp | grep -E ':(80|3000|8000)' || echo "No se encontraron puertos"

echo ""
echo "3. 🌐 Verificando conectividad directa:"
echo "Backend (puerto 8000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/health || echo "❌ Backend no responde"

echo "Frontend (puerto 3000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000 || echo "❌ Frontend no responde"

echo ""
echo "4. 📋 Logs de contenedores (últimas 5 líneas):"
echo "Frontend logs:"
docker logs backtesting-frontend-prod --tail 5

echo ""
echo "Backend logs:"
docker logs backtesting-frontend-prod --tail 5

echo ""
echo "5. 🔍 Verificando configuración de Nginx:"
echo "Configuración actual:"
grep -A 5 -B 5 "proxy_pass" /etc/nginx/sites-available/backtest.bitcoinrocket.com || echo "No se encontró configuración"

echo ""
echo "6. 📊 Estado de Nginx:"
sudo systemctl status nginx --no-pager -l


