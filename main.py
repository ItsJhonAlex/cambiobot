#!/usr/bin/env python3
"""
Bot de Telegram para obtener tasas de cambio de Cuba
Scrapea imágenes de eltoque.com y las envía via Telegram
"""

import asyncio
import logging
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import aiohttp
from PIL import Image
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 30))
CRYPTO_URL = os.getenv('CRYPTO_URL', 'https://wa.cambiocuba.money/crypto_trmi.png')
TRMI_URL = os.getenv('TRMI_URL', 'https://wa.cambiocuba.money/trmi.png')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
TIMEOUT = int(os.getenv('TIMEOUT', 30000))

# Directorio para imágenes
IMAGES_DIR = Path('images')
IMAGES_DIR.mkdir(exist_ok=True)

class CambioBot:
    """Bot principal para obtener tasas de cambio"""
    
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.last_crypto_hash: Optional[str] = None
        self.last_trmi_hash: Optional[str] = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configurar manejadores de comandos"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("tasas", self.get_rates_command))
        self.app.add_handler(CommandHandler("crypto", self.get_crypto_command))
        self.app.add_handler(CommandHandler("trmi", self.get_trmi_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_text = """
🇨🇺 ¡Hola! Soy tu bot de tasas de cambio de Cuba 

Puedo ayudarte a obtener las últimas tasas de:
📊 TRMCC (Tasa Representativa del Mercado de Criptomonedas)
📈 TRMI (Tasa Representativa del Mercado Informal)

Usa /help para ver todos los comandos disponibles.
        """
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = """
🤖 Comandos disponibles:

/start - Iniciar el bot
/help - Mostrar esta ayuda
/tasas - Obtener ambas tasas (CRYPTO + TRMI)
/crypto - Obtener solo tasa de criptomonedas (TRMCC)
/trmi - Obtener solo tasa del mercado informal (TRMI)
/status - Ver estado del bot

Las tasas se actualizan automáticamente cada {} minutos.
        """.format(UPDATE_INTERVAL)
        await update.message.reply_text(help_text)
    
    async def get_rates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /tasas - obtener ambas tasas"""
        await update.message.reply_text("🔄 Obteniendo las tasas de cambio...")
        
        try:
            crypto_path = await self.scrape_image(CRYPTO_URL, 'crypto_trmi.png')
            trmi_path = await self.scrape_image(TRMI_URL, 'trmi.png')
            
            if crypto_path and trmi_path:
                await update.message.reply_photo(
                    photo=open(crypto_path, 'rb'),
                    caption="📊 TRMCC - Tasa de Criptomonedas en Cuba"
                )
                await update.message.reply_photo(
                    photo=open(trmi_path, 'rb'),
                    caption="📈 TRMI - Tasa del Mercado Informal"
                )
            else:
                await update.message.reply_text("❌ Error al obtener las tasas. Inténtalo de nuevo.")
        
        except Exception as e:
            logger.error(f"Error en get_rates_command: {e}")
            await update.message.reply_text("❌ Error al procesar tu solicitud.")
    
    async def get_crypto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /crypto - obtener solo tasa de criptomonedas"""
        await update.message.reply_text("🔄 Obteniendo tasa de criptomonedas...")
        
        try:
            image_path = await self.scrape_image(CRYPTO_URL, 'crypto_trmi.png')
            if image_path:
                await update.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption="📊 TRMCC - Tasa Representativa del Mercado de Criptomonedas en Cuba"
                )
            else:
                await update.message.reply_text("❌ Error al obtener la tasa de criptomonedas.")
        
        except Exception as e:
            logger.error(f"Error en get_crypto_command: {e}")
            await update.message.reply_text("❌ Error al procesar tu solicitud.")
    
    async def get_trmi_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /trmi - obtener solo tasa del mercado informal"""
        await update.message.reply_text("🔄 Obteniendo tasa del mercado informal...")
        
        try:
            image_path = await self.scrape_image(TRMI_URL, 'trmi.png')
            if image_path:
                await update.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption="📈 TRMI - Tasa Representativa del Mercado Informal"
                )
            else:
                await update.message.reply_text("❌ Error al obtener la tasa del mercado informal.")
        
        except Exception as e:
            logger.error(f"Error en get_trmi_command: {e}")
            await update.message.reply_text("❌ Error al procesar tu solicitud.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - ver estado del bot"""
        now = datetime.now()
        status_text = f"""
🤖 Estado del Bot

🕐 Hora actual: {now.strftime('%Y-%m-%d %H:%M:%S')}
⏱️ Intervalo de actualización: {UPDATE_INTERVAL} minutos
📂 Directorio de imágenes: {IMAGES_DIR.absolute()}
🔗 URL Crypto: {CRYPTO_URL}
🔗 URL TRMI: {TRMI_URL}

✅ Bot funcionando correctamente
        """
        await update.message.reply_text(status_text)
    
    async def scrape_image(self, url: str, filename: str) -> Optional[Path]:
        """Descargar imagen directamente desde la URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image_path = IMAGES_DIR / filename
                        
                        # Guardar imagen
                        with open(image_path, 'wb') as f:
                            f.write(image_data)
                        
                        logger.info(f"Imagen descargada: {filename}")
                        return image_path
                    else:
                        logger.error(f"Error HTTP {response.status} al descargar {url}")
                        return None
        
        except Exception as e:
            logger.error(f"Error descargando imagen {url}: {e}")
            return None
    
    def get_image_hash(self, image_path: Path) -> str:
        """Obtener hash de una imagen para detectar cambios"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash de {image_path}: {e}")
            return ""
    
    async def check_for_updates(self, context: ContextTypes.DEFAULT_TYPE):
        """Verificar si hay actualizaciones en las tasas"""
        try:
            # Descargar imágenes actuales
            crypto_path = await self.scrape_image(CRYPTO_URL, 'crypto_trmi_temp.png')
            trmi_path = await self.scrape_image(TRMI_URL, 'trmi_temp.png')
            
            updates_found = False
            
            # Verificar cambios en crypto
            if crypto_path:
                new_hash = self.get_image_hash(crypto_path)
                if self.last_crypto_hash and new_hash != self.last_crypto_hash:
                    await self.send_update_notification(
                        crypto_path,
                        "🚨 Nueva actualización en TRMCC (Criptomonedas)"
                    )
                    updates_found = True
                self.last_crypto_hash = new_hash
                
                # Mover archivo temporal al definitivo
                final_crypto_path = IMAGES_DIR / 'crypto_trmi.png'
                crypto_path.rename(final_crypto_path)
            
            # Verificar cambios en TRMI
            if trmi_path:
                new_hash = self.get_image_hash(trmi_path)
                if self.last_trmi_hash and new_hash != self.last_trmi_hash:
                    await self.send_update_notification(
                        trmi_path,
                        "🚨 Nueva actualización en TRMI (Mercado Informal)"
                    )
                    updates_found = True
                self.last_trmi_hash = new_hash
                
                # Mover archivo temporal al definitivo
                final_trmi_path = IMAGES_DIR / 'trmi.png'
                trmi_path.rename(final_trmi_path)
            
            if updates_found:
                logger.info("Actualizaciones detectadas y enviadas")
            else:
                logger.info("No hay actualizaciones nuevas")
        
        except Exception as e:
            logger.error(f"Error verificando actualizaciones: {e}")
    
    async def send_update_notification(self, image_path: Path, caption: str):
        """Enviar notificación de actualización si hay CHAT_ID configurado"""
        if CHAT_ID:
            try:
                await self.app.bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=open(image_path, 'rb'),
                    caption=f"{caption}\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info(f"Notificación enviada al chat {CHAT_ID}")
            except Exception as e:
                logger.error(f"Error enviando notificación: {e}")
    
    async def setup_job_queue(self):
        """Configurar el job queue para actualizaciones automáticas"""
        job_queue = self.app.job_queue
        job_queue.run_repeating(
            self.check_for_updates,
            interval=timedelta(minutes=UPDATE_INTERVAL),
            first=timedelta(seconds=10)  # Primera ejecución en 10 segundos
        )
        logger.info(f"Job queue configurado para ejecutar cada {UPDATE_INTERVAL} minutos")
    
    async def run(self):
        """Ejecutar el bot"""
        if not BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN no está configurado")
            logger.error("Por favor edita el archivo .env con tu token de bot")
            logger.error("Obtén tu token desde @BotFather en Telegram")
            return
        
        logger.info("🤖 Iniciando bot de tasas de cambio de Cuba...")
        
        # Iniciar bot primero
        await self.app.initialize()
        await self.app.start()
        
        # Configurar job queue después de inicializar
        await self.setup_job_queue()
        
        # Inicializar hashes con las imágenes actuales
        crypto_path = IMAGES_DIR / 'crypto_trmi.png'
        trmi_path = IMAGES_DIR / 'trmi.png'
        
        if crypto_path.exists():
            self.last_crypto_hash = self.get_image_hash(crypto_path)
        if trmi_path.exists():
            self.last_trmi_hash = self.get_image_hash(trmi_path)
        
        # Iniciar polling
        await self.app.updater.start_polling()
        
        logger.info("✅ Bot iniciado correctamente!")
        logger.info(f"📱 Comandos disponibles: /start, /help, /tasas, /crypto, /trmi, /status")
        
        # Mantener el bot ejecutándose
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo bot...")
        finally:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()

async def main():
    """Función principal"""
    bot = CambioBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
