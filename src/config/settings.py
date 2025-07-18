"""
Configuración centralizada del bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del bot
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 30))

# URLs de las tasas de cambio
CRYPTO_URL = os.getenv('CRYPTO_URL', 'https://wa.cambiocuba.money/crypto_trmi.png')
TRMI_URL = os.getenv('TRMI_URL', 'https://wa.cambiocuba.money/trmi.png')

# Configuración de scraping
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
TIMEOUT = int(os.getenv('TIMEOUT', 30000))

# Directorios
IMAGES_DIR = Path('images')
IMAGES_DIR.mkdir(exist_ok=True)

# Configuración de logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Mensajes del bot
WELCOME_MESSAGE = """
🇨🇺 ¡Hola! Soy tu bot de tasas de cambio de Cuba 

Puedo ayudarte a obtener las últimas tasas de:
📊 TRMCC (Tasa Representativa del Mercado de Criptomonedas)
📈 TRMI (Tasa Representativa del Mercado Informal)

Usa /help para ver todos los comandos disponibles.
"""

HELP_MESSAGE = """
🤖 Comandos disponibles:

/start - Iniciar el bot
/help - Mostrar esta ayuda
/tasas - Obtener ambas tasas (CRYPTO + TRMI)
/crypto - Obtener solo tasa de criptomonedas (TRMCC)
/trmi - Obtener solo tasa del mercado informal (TRMI)
/status - Ver estado del bot

Las tasas se actualizan automáticamente cada {} minutos.
"""

# Captions para las imágenes
CRYPTO_CAPTION = "📊 TRMCC - Tasa Representativa del Mercado de Criptomonedas en Cuba"
TRMI_CAPTION = "📈 TRMI - Tasa Representativa del Mercado Informal"
CRYPTO_SIMPLE_CAPTION = "📊 TRMCC - Tasa de Criptomonedas en Cuba"
TRMI_SIMPLE_CAPTION = "📈 TRMI - Tasa del Mercado Informal"

# Mensajes de notificación
CRYPTO_UPDATE_MESSAGE = "🚨 Nueva actualización en TRMCC (Criptomonedas)"
TRMI_UPDATE_MESSAGE = "🚨 Nueva actualización en TRMI (Mercado Informal)"

# Nombres de archivos
CRYPTO_FILENAME = 'crypto_trmi.png'
TRMI_FILENAME = 'trmi.png'
CRYPTO_TEMP_FILENAME = 'crypto_trmi_temp.png'
TRMI_TEMP_FILENAME = 'trmi_temp.png' 