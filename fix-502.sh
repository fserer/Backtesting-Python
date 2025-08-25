#!/bin/bash

echo "🔍 Diagnóstico del error 502 Bad Gateway"
echo "========================================"

# 1. Verificar contenedores Docker
echo ""
echo "1. 📦 Verificando contenedores Docker:"
docker ps

# 2. Verificar puertos en uso
echo ""
echo "2. 🔌 Verificando puertos en uso:"
netstat -tlnp | grep -E ':(80|3000|5173|8000)'

# 3. Verificar conectividad directa
echo ""
echo "3. 🌐 Verificando conectividad directa:"
echo "Backend (puerto 8000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/health || echo "❌ Backend no responde"

echo "Frontend (puerto 5173):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5173 || echo "❌ Frontend no responde"

# 4. Verificar logs de Nginx
echo ""
echo "4. 📋 Logs de Nginx (últimas 10 líneas):"
sudo tail -10 /var/log/nginx/error.log

# 5. Verificar configuración de Nginx
echo ""
echo "5. ⚙️ Verificando configuración de Nginx:"
sudo nginx -t

echo ""
echo "🔧 Soluciones posibles:"
echo "======================"
echo ""
echo "Si los contenedores están corriendo pero Nginx da 502:"
echo "1. Copiar la configuración corregida:"
echo "   sudo cp nginx-backtest.conf /etc/nginx/sites-available/backtest.bitcoinrocket.com"
echo ""
echo "2. Recargar Nginx:"
echo "   sudo systemctl reload nginx"
echo ""
echo "3. Si usas SSL, actualizar la configuración SSL:"
echo "   sudo certbot --nginx -d backtest.bitcoinrocket.com"
echo ""
echo "4. Verificar que los puertos coincidan:"
echo "   - Frontend: puerto 5173 (desarrollo) o 3000 (producción)"
echo "   - Backend: puerto 8000"


