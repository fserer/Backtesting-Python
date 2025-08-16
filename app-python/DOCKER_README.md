# 🐳 Deploy con Docker

Este proyecto está configurado para ejecutarse completamente en contenedores Docker.

## 🚀 Deploy Rápido

### Desarrollo (Local)
```bash
# Clonar el repositorio
git clone <tu-repo>
cd app-python

# Ejecutar con script automático
./deploy.sh dev

# O manualmente
docker-compose up --build -d
```

### Producción (Servidor Linux)
```bash
# En el servidor
git clone <tu-repo>
cd app-python

# Deploy de producción
./deploy.sh prod

# O manualmente
docker-compose -f docker-compose.prod.yml up --build -d
```

## 📁 Estructura de Archivos

```
app-python/
├── docker-compose.yml          # Desarrollo
├── docker-compose.prod.yml     # Producción
├── deploy.sh                   # Script de deploy
├── backend/
│   ├── Dockerfile              # Backend Python
│   └── ...
├── frontend/
│   ├── Dockerfile              # Desarrollo React
│   ├── Dockerfile.prod         # Producción con Nginx
│   ├── nginx.conf              # Configuración Nginx
│   └── ...
└── nginx/                      # Configuración Nginx (producción)
    └── nginx.conf
```

## 🔧 Comandos Útiles

### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### Parar servicios
```bash
docker-compose down
```

### Reconstruir
```bash
docker-compose up --build -d
```

### Acceder al contenedor
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh
```

## 🌐 Puertos

- **Frontend**: http://localhost:3000 (dev) / http://localhost (prod)
- **Backend**: http://localhost:8000
- **Base de datos**: SQLite en volumen Docker

## 📊 Volúmenes

- `sqlite_data`: Base de datos SQLite persistente
- `./backend:/app`: Código del backend (desarrollo)
- `./frontend:/app`: Código del frontend (desarrollo)

## 🔒 Seguridad

- **Desarrollo**: Volúmenes montados para hot-reload
- **Producción**: Imágenes optimizadas sin volúmenes de código
- **SSL**: Configurado en nginx.conf (requiere certificados)

## 🚀 Migración a Servidor

1. **Subir código a Git**
2. **En el servidor Linux**:
   ```bash
   git clone <tu-repo>
   cd app-python
   ./deploy.sh prod
   ```
3. **Configurar dominio y SSL** (opcional)

## 🛠️ Troubleshooting

### Error de puertos
```bash
# Verificar puertos en uso
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Parar servicios que usen esos puertos
sudo systemctl stop <servicio>
```

### Error de permisos
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Reiniciar sesión
```

### Limpiar Docker
```bash
# Limpiar contenedores e imágenes
docker system prune -a

# Limpiar volúmenes
docker volume prune
```
