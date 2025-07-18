"""
Manejadores de botones interactivos del bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.config.settings import (
    CRYPTO_CAPTION, TRMI_CAPTION, CRYPTO_SIMPLE_CAPTION, TRMI_SIMPLE_CAPTION
)
from src.services.rates_service import RatesService
from src.utils.logger import logger

class ButtonHandlers:
    """Manejadores de botones interactivos"""
    
    def __init__(self, rates_service: RatesService):
        self.rates_service = rates_service
    
    def get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Crear teclado del menú principal"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Ambas Tasas", callback_data="rates_both"),
                InlineKeyboardButton("💎 Crypto", callback_data="rates_crypto")
            ],
            [
                InlineKeyboardButton("📈 TRMI", callback_data="rates_trmi"),
                InlineKeyboardButton("ℹ️ Ayuda", callback_data="help")
            ],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="refresh"),
                InlineKeyboardButton("📊 Estado", callback_data="status")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_rates_keyboard(self) -> InlineKeyboardMarkup:
        """Crear teclado para mostrar tasas"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Ambas Tasas", callback_data="rates_both"),
                InlineKeyboardButton("💎 Solo Crypto", callback_data="rates_crypto")
            ],
            [
                InlineKeyboardButton("📈 Solo TRMI", callback_data="rates_trmi"),
                InlineKeyboardButton("🔄 Actualizar", callback_data="refresh")
            ],
            [
                InlineKeyboardButton("🏠 Menú Principal", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_quick_actions_keyboard(self) -> InlineKeyboardMarkup:
        """Crear teclado de acciones rápidas"""
        keyboard = [
            [
                InlineKeyboardButton("❤️", callback_data="like"),
                InlineKeyboardButton("👍", callback_data="thumbs_up"),
                InlineKeyboardButton("👎", callback_data="thumbs_down")
            ],
            [
                InlineKeyboardButton("💤", callback_data="sleep"),
                InlineKeyboardButton("📸📻", callback_data="media")
            ],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="refresh"),
                InlineKeyboardButton("🏠 Menú", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar callbacks de botones"""
        query = update.callback_query
        await query.answer()  # Responder al callback
        
        try:
            if query.data == "main_menu":
                await self.show_main_menu(query)
            elif query.data == "rates_both":
                await self.show_both_rates(query)
            elif query.data == "rates_crypto":
                await self.show_crypto_rate(query)
            elif query.data == "rates_trmi":
                await self.show_trmi_rate(query)
            elif query.data == "refresh":
                await self.refresh_rates(query)
            elif query.data == "status":
                await self.show_status(query)
            elif query.data == "help":
                await self.show_help(query)
            elif query.data == "like":
                await self.handle_like(query)
            elif query.data == "thumbs_up":
                await self.handle_thumbs_up(query)
            elif query.data == "thumbs_down":
                await self.handle_thumbs_down(query)
            elif query.data == "sleep":
                await self.handle_sleep(query)
            elif query.data == "media":
                await self.handle_media(query)
            else:
                await query.edit_message_text("❌ Comando no reconocido")
        
        except Exception as e:
            logger.error(f"Error en callback {query.data}: {e}")
            await query.edit_message_text("❌ Error procesando tu solicitud")
    
    async def show_main_menu(self, query):
        """Mostrar menú principal"""
        welcome_text = """
🇨🇺 **Bot de Tasas de Cambio Cuba**

Selecciona una opción:
        """
        await query.edit_message_text(
            welcome_text,
            reply_markup=self.get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    async def show_both_rates(self, query):
        """Mostrar ambas tasas"""
        await query.edit_message_text("🔄 Obteniendo las tasas de cambio...")
        
        try:
            crypto_path, trmi_path = await self.rates_service.get_both_rates()
            
            if crypto_path and trmi_path:
                # Enviar ambas imágenes
                await query.message.reply_photo(
                    photo=open(crypto_path, 'rb'),
                    caption=CRYPTO_SIMPLE_CAPTION
                )
                await query.message.reply_photo(
                    photo=open(trmi_path, 'rb'),
                    caption=TRMI_SIMPLE_CAPTION
                )
                
                # Mostrar teclado de acciones
                await query.edit_message_text(
                    "✅ Tasas obtenidas exitosamente",
                    reply_markup=self.get_quick_actions_keyboard()
                )
            else:
                await query.edit_message_text(
                    "❌ Error al obtener las tasas",
                    reply_markup=self.get_rates_keyboard()
                )
        
        except Exception as e:
            logger.error(f"Error en show_both_rates: {e}")
            await query.edit_message_text(
                "❌ Error al procesar tu solicitud",
                reply_markup=self.get_rates_keyboard()
            )
    
    async def show_crypto_rate(self, query):
        """Mostrar solo tasa de crypto"""
        await query.edit_message_text("🔄 Obteniendo tasa de criptomonedas...")
        
        try:
            image_path = await self.rates_service.get_crypto_rate()
            if image_path:
                await query.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=CRYPTO_CAPTION
                )
                await query.edit_message_text(
                    "✅ Tasa de crypto obtenida",
                    reply_markup=self.get_quick_actions_keyboard()
                )
            else:
                await query.edit_message_text(
                    "❌ Error al obtener la tasa de crypto",
                    reply_markup=self.get_rates_keyboard()
                )
        
        except Exception as e:
            logger.error(f"Error en show_crypto_rate: {e}")
            await query.edit_message_text(
                "❌ Error al procesar tu solicitud",
                reply_markup=self.get_rates_keyboard()
            )
    
    async def show_trmi_rate(self, query):
        """Mostrar solo tasa TRMI"""
        await query.edit_message_text("🔄 Obteniendo tasa del mercado informal...")
        
        try:
            image_path = await self.rates_service.get_trmi_rate()
            if image_path:
                await query.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=TRMI_CAPTION
                )
                await query.edit_message_text(
                    "✅ Tasa TRMI obtenida",
                    reply_markup=self.get_quick_actions_keyboard()
                )
            else:
                await query.edit_message_text(
                    "❌ Error al obtener la tasa TRMI",
                    reply_markup=self.get_rates_keyboard()
                )
        
        except Exception as e:
            logger.error(f"Error en show_trmi_rate: {e}")
            await query.edit_message_text(
                "❌ Error al procesar tu solicitud",
                reply_markup=self.get_rates_keyboard()
            )
    
    async def refresh_rates(self, query):
        """Actualizar tasas"""
        await query.edit_message_text("🔄 Actualizando tasas...")
        
        try:
            # Forzar actualización
            crypto_path, trmi_path = await self.rates_service.get_both_rates()
            
            if crypto_path and trmi_path:
                await query.edit_message_text(
                    "✅ Tasas actualizadas exitosamente",
                    reply_markup=self.get_quick_actions_keyboard()
                )
            else:
                await query.edit_message_text(
                    "❌ Error al actualizar las tasas",
                    reply_markup=self.get_rates_keyboard()
                )
        
        except Exception as e:
            logger.error(f"Error en refresh_rates: {e}")
            await query.edit_message_text(
                "❌ Error al actualizar",
                reply_markup=self.get_rates_keyboard()
            )
    
    async def show_status(self, query):
        """Mostrar estado del bot"""
        from datetime import datetime
        from src.config.settings import UPDATE_INTERVAL, IMAGES_DIR, CRYPTO_URL, TRMI_URL
        
        now = datetime.now()
        status_text = f"""
🤖 **Estado del Bot**

🕐 Hora actual: {now.strftime('%Y-%m-%d %H:%M:%S')}
⏱️ Intervalo de actualización: {UPDATE_INTERVAL} minutos
📂 Directorio de imágenes: {IMAGES_DIR.absolute()}
🔗 URL Crypto: {CRYPTO_URL}
🔗 URL TRMI: {TRMI_URL}

✅ Bot funcionando correctamente
        """
        
        await query.edit_message_text(
            status_text,
            reply_markup=self.get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    async def show_help(self, query):
        """Mostrar ayuda"""
        from src.config.settings import UPDATE_INTERVAL
        
        help_text = f"""
🤖 **Comandos disponibles:**

📊 **Tasas de Cambio:**
• Ambas Tasas - TRMCC + TRMI
• Solo Crypto - Tasa de criptomonedas
• Solo TRMI - Tasa del mercado informal

🔄 **Actualización automática:** cada {UPDATE_INTERVAL} minutos

📱 **Botones interactivos:**
• ❤️ - Me gusta
• 👍 - Thumbs up
• 👎 - Thumbs down
• 💤 - Modo sleep
• 📸📻 - Media

✅ Bot funcionando correctamente
        """
        
        await query.edit_message_text(
            help_text,
            reply_markup=self.get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    # Handlers para botones de reacción
    async def handle_like(self, query):
        """Manejar botón de like"""
        await query.edit_message_text(
            "❤️ ¡Gracias por tu like!",
            reply_markup=self.get_quick_actions_keyboard()
        )
    
    async def handle_thumbs_up(self, query):
        """Manejar botón thumbs up"""
        await query.edit_message_text(
            "👍 ¡Excelente!",
            reply_markup=self.get_quick_actions_keyboard()
        )
    
    async def handle_thumbs_down(self, query):
        """Manejar botón thumbs down"""
        await query.edit_message_text(
            "👎 ¿Algo no te gustó?",
            reply_markup=self.get_quick_actions_keyboard()
        )
    
    async def handle_sleep(self, query):
        """Manejar botón sleep"""
        await query.edit_message_text(
            "💤 Modo descanso activado",
            reply_markup=self.get_quick_actions_keyboard()
        )
    
    async def handle_media(self, query):
        """Manejar botón media"""
        await query.edit_message_text(
            "📸📻 Funcionalidad de media próximamente",
            reply_markup=self.get_quick_actions_keyboard()
        ) 