#!/bin/bash

# Script para gestionar el bot de tasas de cambio de Cuba
# Uso: ./run.sh [comando]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuración
BOT_NAME="cambiobot"
LOG_FILE="bot.log"
PID_FILE="bot.pid"
MAIN_FILE="main_modular.py"  # Cambiado a la versión modular

# Funciones de utilidad
print_header() {
    echo -e "${PURPLE}🇨🇺 Bot de Tasas de Cambio Cuba${NC}"
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

# Verificar si uv está instalado
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv no está instalado. Instalando..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        print_success "uv instalado correctamente"
    fi
}

# Verificar archivo .env
check_env() {
    if [ ! -f ".env" ]; then
        print_warning "Archivo .env no encontrado"
        if [ -f ".env.example" ]; then
            print_info "Copiando .env.example a .env"
            cp .env.example .env
            print_warning "¡IMPORTANTE! Edita el archivo .env con tu token de bot"
            print_info "Usa: nano .env"
            return 1
        else
            print_error "Archivo .env.example no encontrado"
            return 1
        fi
    fi
}

# Verificar estructura modular
check_modular_structure() {
    if [ ! -f "$MAIN_FILE" ]; then
        print_error "Archivo $MAIN_FILE no encontrado"
        print_info "Asegúrate de estar usando la versión modular del bot"
        return 1
    fi
    
    if [ ! -d "src" ]; then
        print_error "Directorio src/ no encontrado"
        print_info "Asegúrate de estar usando la versión modular del bot"
        return 1
    fi
}

# Actualizar desde GitHub
pull_updates() {
    print_header
    print_info "Actualizando desde GitHub..."
    
    # Verificar si es un repositorio git
    if [ ! -d ".git" ]; then
        print_error "No es un repositorio git"
        return 1
    fi
    
    # Verificar si hay cambios locales
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Hay cambios locales sin commit"
        read -p "¿Quieres hacer stash de los cambios? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash
            print_info "Cambios guardados en stash"
        else
            print_error "Actualización cancelada"
            return 1
        fi
    fi
    
    # Hacer pull
    git pull origin main || git pull origin master
    
    print_success "Actualización completada"
    
    # Reinstalar dependencias si es necesario
    if [ -f "pyproject.toml" ] && [ "$(stat -c %Y pyproject.toml)" -gt "$(stat -c %Y uv.lock 2>/dev/null || echo 0)" ]; then
        print_info "Dependencias actualizadas, reinstalando..."
        install_deps
    fi
}

# Instalar dependencias
install_deps() {
    print_info "Instalando dependencias..."
    check_uv
    
    # Instalar dependencias de Python
    uv sync
    
    # Instalar navegadores de Playwright
    print_info "Instalando navegadores de Playwright..."
    uv run playwright install chromium
    uv run playwright install-deps
    
    print_success "Dependencias instaladas correctamente"
}

# Ejecutar el bot
run_bot() {
    print_header
    check_env || return 1
    check_modular_structure || return 1
    
    print_info "Iniciando bot (versión modular)..."
    export PATH="$HOME/.local/bin:$PATH"
    uv run python "$MAIN_FILE"
}

# Ejecutar el bot en background
run_background() {
    print_header
    check_env || return 1
    check_modular_structure || return 1
    
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
        print_warning "El bot ya está ejecutándose (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    print_info "Iniciando bot en background (versión modular)..."
    export PATH="$HOME/.local/bin:$PATH"
    nohup uv run python "$MAIN_FILE" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    print_success "Bot iniciado en background (PID: $!)"
    print_info "Ver logs: ./run.sh logs"
    print_info "Detener: ./run.sh stop"
}

# Detener el bot
stop_bot() {
    print_header
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "Archivo PID no encontrado"
        # Intentar matar por nombre de proceso
        pkill -f "python $MAIN_FILE" && print_success "Bot detenido" || print_error "No se pudo detener el bot"
        return
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$PID_FILE"
        print_success "Bot detenido (PID: $PID)"
    else
        print_warning "El proceso ya no existe"
        rm -f "$PID_FILE"
    fi
}

# Ver logs
view_logs() {
    print_header
    
    if [ ! -f "$LOG_FILE" ]; then
        print_error "Archivo de log no encontrado"
        return 1
    fi
    
    print_info "Mostrando logs (Ctrl+C para salir)..."
    tail -f "$LOG_FILE"
}

# Ver estado
show_status() {
    print_header
    
    # Verificar si está ejecutándose
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
        PID=$(cat "$PID_FILE")
        print_success "Bot ejecutándose (PID: $PID)"
        
        # Mostrar información del proceso
        ps -p "$PID" -o pid,ppid,pcpu,pmem,start,command 2>/dev/null || true
        
        # Mostrar últimas líneas del log
        if [ -f "$LOG_FILE" ]; then
            echo ""
            print_info "Últimas líneas del log:"
            tail -n 5 "$LOG_FILE"
        fi
    else
        print_warning "Bot no está ejecutándose"
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
    fi
    
    # Mostrar configuración
    echo ""
    print_info "Configuración:"
    if [ -f ".env" ]; then
        echo "✅ Archivo .env: encontrado"
        grep -E "^(UPDATE_INTERVAL|CRYPTO_URL|TRMI_URL)" .env 2>/dev/null || true
    else
        echo "❌ Archivo .env: no encontrado"
    fi
    
    # Mostrar información de la estructura modular
    echo ""
    print_info "Estructura modular:"
    if [ -d "src" ]; then
        echo "✅ Directorio src/: encontrado"
        echo "✅ $MAIN_FILE: encontrado"
        echo "📁 Módulos disponibles:"
        ls -la src/ 2>/dev/null || true
    else
        echo "❌ Estructura modular: no encontrada"
    fi
}

# Test de conexión
test_connection() {
    print_header
    check_env || return 1
    
    print_info "Probando conexión a URLs..."
    
    CRYPTO_URL=$(grep CRYPTO_URL .env | cut -d'=' -f2)
    TRMI_URL=$(grep TRMI_URL .env | cut -d'=' -f2)
    
    # Test crypto URL
    if curl -s -I "$CRYPTO_URL" | grep -q "200\|302"; then
        print_success "Crypto URL accesible: $CRYPTO_URL"
    else
        print_error "Crypto URL no accesible: $CRYPTO_URL"
    fi
    
    # Test TRMI URL
    if curl -s -I "$TRMI_URL" | grep -q "200\|302"; then
        print_success "TRMI URL accesible: $TRMI_URL"
    else
        print_error "TRMI URL no accesible: $TRMI_URL"
    fi
}

# Limpiar archivos temporales
clean() {
    print_header
    print_info "Limpiando archivos temporales..."
    
    rm -f "$LOG_FILE" "$PID_FILE"
    rm -rf images/*.png
    
    # Limpiar archivo main.py original si existe
    if [ -f "main.py" ]; then
        print_warning "Eliminando main.py original (ya no necesario)"
        rm -f main.py
    fi
    
    print_success "Limpieza completada"
}

# Migrar a estructura modular
migrate_to_modular() {
    print_header
    print_info "Migrando a estructura modular..."
    
    # Verificar si ya está migrado
    if [ -f "$MAIN_FILE" ] && [ -d "src" ]; then
        print_success "Ya estás usando la estructura modular"
        return 0
    fi
    
    # Verificar si existe main.py original
    if [ ! -f "main.py" ]; then
        print_error "No se encontró main.py original"
        return 1
    fi
    
    # Crear backup del main.py original
    cp main.py main.py.backup
    print_info "Backup creado: main.py.backup"
    
    # Eliminar main.py original
    rm -f main.py
    print_success "Migración completada"
    print_info "Ahora usa: ./run.sh run"
}

# Mostrar ayuda
show_help() {
    print_header
    echo ""
    echo "Uso: ./run.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  install     - Instalar dependencias"
    echo "  pull        - Actualizar desde GitHub"
    echo "  run         - Ejecutar bot (modo interactivo)"
    echo "  start       - Ejecutar bot en background"
    echo "  stop        - Detener bot"
    echo "  restart     - Reiniciar bot"
    echo "  status      - Ver estado del bot"
    echo "  logs        - Ver logs en tiempo real"
    echo "  test        - Probar conexión a URLs"
    echo "  clean       - Limpiar archivos temporales"
    echo "  migrate     - Migrar a estructura modular"
    echo "  help        - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./run.sh install    # Primera instalación"
    echo "  ./run.sh pull       # Actualizar desde GitHub"
    echo "  ./run.sh start      # Iniciar en background"
    echo "  ./run.sh logs       # Ver logs"
    echo "  ./run.sh stop       # Detener bot"
    echo ""
    echo "Estructura modular:"
    echo "  ✅ Usando main_modular.py"
    echo "  ✅ Código organizado en src/"
    echo "  ✅ Mejor mantenibilidad y escalabilidad"
}

# Función principal
main() {
    case "${1:-help}" in
        "install")
            install_deps
            ;;
        "pull")
            pull_updates
            ;;
        "run")
            run_bot
            ;;
        "start")
            run_background
            ;;
        "stop")
            stop_bot
            ;;
        "restart")
            stop_bot
            sleep 2
            run_background
            ;;
        "status")
            show_status
            ;;
        "logs")
            view_logs
            ;;
        "test")
            test_connection
            ;;
        "clean")
            clean
            ;;
        "migrate")
            migrate_to_modular
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Verificar que estemos en el directorio correcto
if [ ! -f "$MAIN_FILE" ] && [ ! -f "main.py" ]; then
    print_error "Archivo principal no encontrado. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# Ejecutar función principal
main "$@" 