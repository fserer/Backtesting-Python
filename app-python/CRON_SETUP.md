# 🔄 Configuración de Actualización Automática con Cron

Este documento explica cómo configurar la actualización automática de datasets usando cron.

## 📋 Opciones Disponibles

### **Opción 1: Script Bash (Recomendado para sistemas simples)**

**Archivo:** `update_datasets_curl.sh`

**Uso:**
```bash
./update_datasets_curl.sh
```

**Para cron (cada 25 minutos):**
```bash
*/25 * * * * /ruta/completa/a/update_datasets_curl.sh
```

**Ventajas:**
- ✅ No requiere dependencias adicionales
- ✅ Logging detallado automático
- ✅ Fácil de configurar

### **Opción 2: Script Python (Recomendado para sistemas robustos)**

**Archivo:** `update_datasets_cron.py`

**Uso:**
```bash
python3 update_datasets_cron.py
```

**Para cron (cada 25 minutos):**
```bash
*/25 * * * * /usr/bin/python3 /ruta/completa/a/update_datasets_cron.py
```

**Ventajas:**
- ✅ Manejo robusto de errores
- ✅ Timeout configurable
- ✅ Logging estructurado
- ✅ Verificación de conectividad

### **Opción 3: Comando curl directo (Más simple)**

**Comando:**
```bash
curl -s -X POST http://localhost:8000/api/datasets/update-all -H "Content-Type: application/json"
```

**Para cron (cada 25 minutos):**
```bash
*/25 * * * * curl -s -X POST http://localhost:8000/api/datasets/update-all -H "Content-Type: application/json" >> /tmp/dataset_update.log 2>&1
```

**Con timestamp:**
```bash
*/25 * * * * echo "$(date): Actualizando datasets..." >> /tmp/dataset_update.log && curl -s -X POST http://localhost:8000/api/datasets/update-all -H "Content-Type: application/json" >> /tmp/dataset_update.log 2>&1
```

## 🛠️ Configuración Paso a Paso

### **1. Obtener la ruta completa del script**

```bash
# Para el script bash
pwd
# Ejemplo: /Users/fserer/Library/CloudStorage/Dropbox/trabajo/BitcoinRocket/Andorra/Personal/Bactesting-Python/app-python

# La ruta completa sería:
/Users/fserer/Library/CloudStorage/Dropbox/trabajo/BitcoinRocket/Andorra/Personal/Bactesting-Python/app-python/update_datasets_curl.sh
```

### **2. Editar el crontab**

```bash
crontab -e
```

### **3. Añadir la línea de cron**

**Para actualización cada 25 minutos:**
```bash
*/25 * * * * /Users/fserer/Library/CloudStorage/Dropbox/trabajo/BitcoinRocket/Andorra/Personal/Bactesting-Python/app-python/update_datasets_curl.sh
```

**Para actualización cada hora:**
```bash
0 * * * * /Users/fserer/Library/CloudStorage/Dropbox/trabajo/BitcoinRocket/Andorra/Personal/Bactesting-Python/app-python/update_datasets_curl.sh
```

**Para actualización cada 30 minutos:**
```bash
*/30 * * * * /Users/fserer/Library/CloudStorage/Dropbox/trabajo/BitcoinRocket/Andorra/Personal/Bactesting-Python/app-python/update_datasets_curl.sh
```

### **4. Verificar que cron está funcionando**

```bash
# Ver el crontab actual
crontab -l

# Ver los logs de cron
tail -f /var/log/cron

# Ver los logs de nuestro script
tail -f /tmp/dataset_update.log
```

## 📊 Monitoreo y Logs

### **Ubicación de logs:**
- **Script bash:** `/tmp/dataset_update.log`
- **Script Python:** `/tmp/dataset_update.log` + salida estándar
- **Comando curl:** Depende de la configuración

### **Verificar logs:**
```bash
# Ver últimos 20 líneas
tail -20 /tmp/dataset_update.log

# Seguir logs en tiempo real
tail -f /tmp/dataset_update.log

# Buscar errores
grep "ERROR\|❌" /tmp/dataset_update.log
```

### **Ejemplo de log exitoso:**
```
[2025-08-19 10:42:55] 🚀 Iniciando actualización automática de datasets...
[2025-08-19 10:43:08] ✅ Actualización exitosa - 7 datasets procesados, 0 registros añadidos
[2025-08-19 10:43:08] 📋 Detalles por dataset:
[2025-08-19 10:43:08]   ✅ SOPR CP - Hour: 0 registros
[2025-08-19 10:43:08]   ✅ MVRV CP - Hour: 0 registros
[2025-08-19 10:43:08] 🎉 Actualización completada
```

## ⚠️ Consideraciones Importantes

### **1. Permisos de archivo**
```bash
chmod +x update_datasets_curl.sh
chmod +x update_datasets_cron.py
```

### **2. Variables de entorno**
Si el backend no está en `localhost:8000`, modifica la variable `BACKEND_URL` en los scripts.

### **3. Dependencias**
- **Script bash:** Solo requiere `curl` (normalmente instalado)
- **Script Python:** Requiere `requests` (`pip install requests`)

### **4. Timeout**
- **Script bash:** Sin timeout (usa el de curl por defecto)
- **Script Python:** 5 minutos de timeout configurable

### **5. Logs de rotación**
Para evitar que los logs crezcan demasiado:
```bash
# Añadir al crontab para limpiar logs antiguos
0 0 * * 0 find /tmp/dataset_update.log -mtime +7 -delete
```

## 🔧 Solución de Problemas

### **Problema: Script no se ejecuta**
```bash
# Verificar permisos
ls -la update_datasets_curl.sh

# Verificar que el archivo existe
which curl

# Probar manualmente
./update_datasets_curl.sh
```

### **Problema: Backend no disponible**
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/api/datasets

# Verificar puerto
netstat -an | grep 8000
```

### **Problema: Permisos de escritura en logs**
```bash
# Verificar permisos del directorio /tmp
ls -la /tmp/

# Cambiar ubicación del log si es necesario
# Editar el script y cambiar LOG_FILE
```

## 📈 Frecuencias Recomendadas

- **Cada 25 minutos:** Para datos horarios (recomendado)
- **Cada hora:** Para datos diarios
- **Cada 15 minutos:** Para datos muy frecuentes (solo si es necesario)

## 🎯 Recomendación Final

**Para la mayoría de casos, usa el script bash (`update_datasets_curl.sh`):**
- Es simple y confiable
- No requiere dependencias adicionales
- Proporciona logging detallado
- Fácil de mantener y debuggear
