"""
Bot principal de tasas de cambio de Cuba
"""
import asyncio
from datetime import timedelta
from telegram.ext import Application, CommandHandler, ContextTypes
from src.config.settings import BOT_TOKEN, UPDATE_INTERVAL
from src.services.image_service import ImageService
from src.services.rates_service import RatesService
from src.handlers.command_handlers import CommandHandlers
from src.utils.logger import logger

class CambioBot:
    """Bot principal para obtener tasas de cambio"""
    
    def __init__(self):
        if not BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN no está configurado")
        
        # Inicializar servicios
        self.image_service = ImageService()
        self.rates_service = RatesService(self.image_service)
        
        # Inicializar manejadores
        self.command_handlers = CommandHandlers(self.rates_service)
        
        # Inicializar aplicación de Telegram
        self.app = Application.builder().token(BOT_TOKEN).build()
        
        # Configurar manejadores
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configurar manejadores de comandos y botones"""
        # Comandos
        self.app.add_handler(CommandHandler("start", self.command_handlers.start_command))
        self.app.add_handler(CommandHandler("help", self.command_handlers.help_command))
        self.app.add_handler(CommandHandler("tasas", self.command_handlers.get_rates_command))
        self.app.add_handler(CommandHandler("crypto", self.command_handlers.get_crypto_command))
        self.app.add_handler(CommandHandler("trmi", self.command_handlers.get_trmi_command))
        self.app.add_handler(CommandHandler("status", self.command_handlers.status_command))
        
        # Botones interactivos eliminados
    
    async def setup_job_queue(self):
        """Configurar el job queue para actualizaciones automáticas"""
        # Conectar el bot app al rates service para notificaciones
        self.rates_service.bot_app = self.app
        
        job_queue = self.app.job_queue
        if job_queue:
            job_queue.run_repeating(
                self.check_updates_job,
                interval=timedelta(minutes=UPDATE_INTERVAL),
                first=timedelta(seconds=10)  # Primera ejecución en 10 segundos
            )
            logger.info(f"Job queue configurado para ejecutar cada {UPDATE_INTERVAL} minutos")
        else:
            logger.warning("Job queue no disponible")
    
    async def check_updates_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Job para verificar actualizaciones"""
        await self.rates_service.check_for_updates()
    
    async def run(self):
        """Ejecutar el bot"""
        logger.info("🤖 Iniciando bot de tasas de cambio de Cuba...")
        
        # Inicializar bot primero
        await self.app.initialize()
        await self.app.start()
        
        # Configurar job queue después de inicializar
        await self.setup_job_queue()
        
        # Inicializar hashes con las imágenes actuales
        self.rates_service.initialize_hashes()
        
        # Iniciar polling
        if self.app.updater:
            await self.app.updater.start_polling()
        else:
            logger.error("Updater no disponible")
        
        logger.info("✅ Bot iniciado correctamente!")
        logger.info(f"📱 Comandos disponibles: /start, /help, /tasas, /crypto, /trmi, /status")
        
        # Mantener el bot ejecutándose
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo bot...")
        finally:
            if self.app.updater:
                await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown() 