# 🇨🇺 Bot de Telegram - Tasas de Cambio Cuba

Bot automatizado que obtiene las tasas de cambio de Cuba desde [El Toque](https://eltoque.com/tasas-de-cambio-de-moneda-en-cuba-hoy) y las envía via Telegram.

## 📋 Características

- 📊 **TRMCC**: Tasa Representativa del Mercado de Criptomonedas en Cuba
- 📈 **TRMI**: Tasa Representativa del Mercado Informal
- 🤖 **Comandos interactivos** via Telegram
- 🔄 **Actualizaciones automáticas** cada X minutos
- 🚨 **Notificaciones** cuando hay cambios en las tasas
- 📱 **Interfaz amigable** con emojis y mensajes claros

## 🚀 Instalación

### Prerrequisitos

- Python 3.11+
- uv (gestor de paquetes moderno)
- Token de bot de Telegram

### 1. Clonar y configurar

```bash
# Si no tienes uv instalado:
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Navegar al directorio del proyecto
cd cambiobot

# Instalar dependencias
uv add python-telegram-bot playwright aiohttp pillow python-dotenv

# Instalar navegadores de Playwright
uv run playwright install chromium
uv run playwright install-deps
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
nano .env
```

### 3. Obtener token del bot

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot` y sigue las instrucciones
3. Copia el token que te da BotFather
4. Pégalo en tu archivo `.env`

### 4. Ejecutar el bot

```bash
# Activar entorno virtual y ejecutar
uv run python main.py
```

## ⚙️ Configuración

Edita el archivo `.env` con tus configuraciones:

```env
# Token del bot (OBLIGATORIO)
TELEGRAM_BOT_TOKEN=123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# ID del chat para notificaciones automáticas (OPCIONAL)
CHAT_ID=12345678

# ID del grupo para notificaciones automáticas
GROUP_ID=4664753197

# ID del canal para notificaciones automáticas
CHANNEL_ID=2821523577

# Intervalo de verificación en minutos (default: 30)
UPDATE_INTERVAL=30

# URLs de las imágenes (ya configuradas)
CRYPTO_URL=https://wa.cambiocuba.money/real_crypto_trmi.png
TRMI_URL=https://wa.cambiocuba.money/trmi.png
```

### 🔍 Encontrar tus IDs

1. **Para CHAT_ID**: Envía un mensaje a tu bot y ve a: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
2. **Para GROUP_ID**: Agrega el bot al grupo y busca el `"id"` del grupo en getUpdates
3. **Para CHANNEL_ID**: Agrega el bot al canal como admin y busca el `"id"` del canal

## 📱 Comandos y Botones disponibles

### ⌨️ **Comandos de Texto**
| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar el bot |
| `/help` | Mostrar ayuda y comandos disponibles |
| `/tasas` | Obtener ambas tasas (CRYPTO + TRMI) |
| `/crypto` | Obtener solo tasa de criptomonedas (TRMCC) |
| `/trmi` | Obtener solo tasa del mercado informal (TRMI) |
| `/status` | Ver estado del bot y configuración |

## 🔄 Funcionamiento automático

- **Verificación periódica**: El bot verifica cada X minutos si hay nuevas tasas
- **Detección de cambios**: Usa hash MD5 para detectar si las imágenes cambiaron
- **Notificaciones automáticas**: Si tienes `CHAT_ID`, `GROUP_ID` o `CHANNEL_ID` configurados, te enviará las actualizaciones
- **Almacenamiento local**: Las imágenes se guardan en la carpeta `images/`

## 📁 Estructura del proyecto

```
cambiobot/
├── main.py              # Código principal del bot
├── .env                 # Variables de entorno (crear desde .env.example)
├── .env.example         # Ejemplo de configuración
├── README.md           # Esta documentación
├── pyproject.toml      # Configuración del proyecto
├── uv.lock            # Lock file de dependencias
└── images/            # Directorio para imágenes (se crea automáticamente)
    ├── real_crypto_trmi.png
    └── trmi.png
```

## 🛠️ Scripts útiles

### Ejecutar el bot
```bash
uv run python main.py
```

### Ejecutar en background (Linux/macOS)
```bash
nohup uv run python main.py > bot.log 2>&1 &
```

### Ver logs en tiempo real
```bash
tail -f bot.log
```

### Detener bot en background
```bash
# Encontrar el proceso
ps aux | grep python

# Matar el proceso (reemplaza PID)
kill <PID>
```

## 🐳 Docker (Opcional)

Si prefieres usar Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copiar archivos
COPY . .

# Instalar dependencias
RUN uv sync
RUN uv run playwright install chromium
RUN uv run playwright install-deps

# Ejecutar
CMD ["uv", "run", "python", "main.py"]
```

```bash
# Construir y ejecutar
docker build -t cambiobot .
docker run -d --name cambiobot --env-file .env cambiobot
```

## 🔧 Solución de problemas

### Error: "TELEGRAM_BOT_TOKEN no está configurado"
- Verifica que el archivo `.env` existe
- Verifica que el token está correcto y sin espacios

### Error: "Timeout" o problemas de conexión
- Verifica tu conexión a internet
- Las URLs de las imágenes pueden haber cambiado
- Aumenta el `TIMEOUT` en `.env`

### Error: Playwright no funciona
```bash
# Reinstalar navegadores
uv run playwright install chromium
uv run playwright install-deps
```

### El bot no responde
- Verifica que el token es correcto
- Verifica que el bot está ejecutándose (`ps aux | grep python`)
- Revisa los logs para errores

## 📄 Licencia

MIT License - Puedes usar, modificar y distribuir libremente.

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! 

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas:

1. Revisa esta documentación
2. Verifica que todas las dependencias están instaladas
3. Revisa los logs del bot
4. Abre un issue en GitHub con detalles del problema

---

¡Disfruta tu bot de tasas de cambio! 🇨🇺✨
