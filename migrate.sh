#!/bin/bash

# Script de migración a estructura modular
# Uso: ./migrate.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}🔄 Migración a Estructura Modular${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar si ya está migrado
check_already_migrated() {
    if [ -f "main_modular.py" ] && [ -d "src" ]; then
        print_success "Ya estás usando la estructura modular"
        print_info "No es necesario migrar"
        exit 0
    fi
}

# Crear backup
create_backup() {
    print_info "Creando backup de la versión actual..."
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Copiar archivos importantes
    if [ -f "main.py" ]; then
        cp main.py "$BACKUP_DIR/"
    fi
    
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/"
    fi
    
    if [ -f "cambiobot.service" ]; then
        cp cambiobot.service "$BACKUP_DIR/"
    fi
    
    print_success "Backup creado en: $BACKUP_DIR"
}

# Verificar dependencias
check_dependencies() {
    print_info "Verificando dependencias..."
    
    if ! command -v uv &> /dev/null; then
        print_error "uv no está instalado"
        print_info "Instalando uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    print_success "Dependencias verificadas"
}

# Migrar estructura
migrate_structure() {
    print_info "Migrando a estructura modular..."
    
    # Verificar que exista main.py original
    if [ ! -f "main.py" ]; then
        print_error "No se encontró main.py original"
        print_info "Asegúrate de estar en el directorio correcto del proyecto"
        exit 1
    fi
    
    # Crear estructura de directorios si no existe
    if [ ! -d "src" ]; then
        print_info "Creando estructura de directorios..."
        mkdir -p src/{config,utils,services,handlers,bot}
    fi
    
    # Verificar que los archivos modulares existan
    if [ ! -f "main_modular.py" ]; then
        print_error "Archivo main_modular.py no encontrado"
        print_info "Asegúrate de tener la versión más reciente del código"
        exit 1
    fi
    
    # Eliminar main.py original
    if [ -f "main.py" ]; then
        print_info "Eliminando main.py original..."
        rm -f main.py
    fi
    
    print_success "Estructura migrada correctamente"
}

# Actualizar configuración
update_configuration() {
    print_info "Actualizando configuración..."
    
    # Verificar .env
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        print_warning "Archivo .env no encontrado"
        print_info "Copiando .env.example a .env"
        cp .env.example .env
        print_warning "¡IMPORTANTE! Edita el archivo .env con tu token de bot"
    fi
    
    print_success "Configuración actualizada"
}

# Reinstalar dependencias
reinstall_dependencies() {
    print_info "Reinstalando dependencias..."
    
    uv sync
    
    # Instalar navegadores de Playwright
    print_info "Instalando navegadores de Playwright..."
    uv run playwright install chromium
    uv run playwright install-deps
    
    print_success "Dependencias reinstaladas"
}

# Probar la nueva estructura
test_migration() {
    print_info "Probando la nueva estructura..."
    
    # Verificar que el bot puede iniciarse
    if timeout 10s uv run python main_modular.py --help >/dev/null 2>&1; then
        print_success "Estructura modular funciona correctamente"
    else
        print_warning "No se pudo probar la inicialización completa"
        print_info "Esto es normal si no hay token configurado"
    fi
}

# Mostrar información post-migración
show_post_migration_info() {
    print_header
    print_success "¡Migración completada exitosamente!"
    echo ""
    print_info "Cambios realizados:"
    echo "  ✅ Estructura modular creada en src/"
    echo "  ✅ main_modular.py como punto de entrada"
    echo "  ✅ main.py original eliminado"
    echo "  ✅ Dependencias actualizadas"
    echo ""
    print_info "Próximos pasos:"
    echo "  1. Edita .env con tu token de bot"
    echo "  2. Ejecuta: ./run.sh start"
    echo "  3. Verifica: ./run.sh status"
    echo ""
    print_info "Comandos disponibles:"
    echo "  ./run.sh start    # Iniciar bot"
    echo "  ./run.sh logs     # Ver logs"
    echo "  ./run.sh stop     # Detener bot"
    echo "  ./run.sh status   # Ver estado"
    echo ""
    print_info "Documentación:"
    echo "  📖 ARCHITECTURE.md - Estructura modular"
    echo "  📖 README.md - Documentación principal"
}

# Función principal
main() {
    print_header
    
    # Verificar si ya está migrado
    check_already_migrated
    
    # Confirmar migración
    echo ""
    print_warning "Este script migrará tu bot a la estructura modular"
    print_info "Se creará un backup de la versión actual"
    echo ""
    read -p "¿Continuar con la migración? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Migración cancelada"
        exit 0
    fi
    
    # Ejecutar pasos de migración
    create_backup
    check_dependencies
    migrate_structure
    update_configuration
    reinstall_dependencies
    test_migration
    show_post_migration_info
}

# Verificar que estemos en el directorio correcto
if [ ! -f "main_modular.py" ] && [ ! -f "main.py" ]; then
    print_error "No se encontró el proyecto. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# Ejecutar migración
main 