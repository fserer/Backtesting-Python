#!/bin/bash

# Script para limpiar archivos de base de datos del historial de Git
# Esto evita que los datos de producción se sobrescriban con git pull

echo "🧹 Limpiando archivos de base de datos del historial de Git..."

# Verificar si git-filter-repo está instalado
if ! command -v git-filter-repo &> /dev/null; then
    echo "❌ git-filter-repo no está instalado."
    echo "📦 Instalando git-filter-repo..."
    
    if command -v pip3 &> /dev/null; then
        pip3 install git-filter-repo
    elif command -v pip &> /dev/null; then
        pip install git-filter-repo
    else
        echo "❌ No se pudo instalar git-filter-repo. Instálalo manualmente:"
        echo "   pip install git-filter-repo"
        exit 1
    fi
fi

# Crear backup del repositorio actual
echo "💾 Creando backup del repositorio..."
cp -r .git .git.backup.$(date +%Y%m%d_%H%M%S)

# Limpiar archivos de base de datos del historial
echo "🗑️  Eliminando archivos de base de datos del historial..."
git filter-repo --path backend/data/backtesting.db --invert-paths --force
git filter-repo --path backend/backtesting.db --invert-paths --force

# Verificar que se eliminaron
echo "✅ Verificando que se eliminaron los archivos..."
if git log --name-only --oneline | grep -E "\.(db|sqlite|sqlite3)$"; then
    echo "⚠️  Aún hay archivos de base de datos en el historial:"
    git log --name-only --oneline | grep -E "\.(db|sqlite|sqlite3)$"
else
    echo "✅ No se encontraron más archivos de base de datos en el historial."
fi

echo "🎉 Limpieza completada!"
echo "📝 Recuerda hacer push force para actualizar el repositorio remoto:"
echo "   git push origin main --force"
echo ""
echo "⚠️  ADVERTENCIA: Esto reescribirá el historial de Git."
echo "   Asegúrate de que todos los colaboradores estén sincronizados."
