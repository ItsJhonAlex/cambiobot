"""
Manejadores de comandos del bot de Telegram
"""
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.config.settings import (
    WELCOME_MESSAGE, HELP_MESSAGE, UPDATE_INTERVAL,
    CRYPTO_CAPTION, TRMI_CAPTION, CRYPTO_SIMPLE_CAPTION, TRMI_SIMPLE_CAPTION,
    IMAGES_DIR, CRYPTO_URL, TRMI_URL
)
from src.services.rates_service import RatesService
from src.utils.logger import logger

class CommandHandlers:
    """Manejadores de comandos del bot"""
    
    def __init__(self, rates_service: RatesService, button_handlers=None):
        self.rates_service = rates_service
        self.button_handlers = button_handlers
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        if self.button_handlers:
            await update.message.reply_text(
                WELCOME_MESSAGE,
                reply_markup=self.button_handlers.get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text(WELCOME_MESSAGE)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = HELP_MESSAGE.format(UPDATE_INTERVAL)
        if self.button_handlers:
            await update.message.reply_text(
                help_text,
                reply_markup=self.button_handlers.get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text(help_text)
    
    async def get_rates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /tasas - obtener ambas tasas"""
        await update.message.reply_text("🔄 Obteniendo las tasas de cambio...")
        
        try:
            crypto_path, trmi_path = await self.rates_service.get_both_rates()
            
            if crypto_path and trmi_path:
                await update.message.reply_photo(
                    photo=open(crypto_path, 'rb'),
                    caption=CRYPTO_SIMPLE_CAPTION
                )
                await update.message.reply_photo(
                    photo=open(trmi_path, 'rb'),
                    caption=TRMI_SIMPLE_CAPTION
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
            image_path = await self.rates_service.get_crypto_rate()
            if image_path:
                await update.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=CRYPTO_CAPTION
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
            image_path = await self.rates_service.get_trmi_rate()
            if image_path:
                await update.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=TRMI_CAPTION
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