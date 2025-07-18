"""
Servicio para manejo de tasas de cambio
"""
from datetime import datetime
from typing import Optional, Tuple
from src.config.settings import (
    CRYPTO_URL, TRMI_URL, CHAT_ID, CRYPTO_FILENAME, TRMI_FILENAME,
    CRYPTO_TEMP_FILENAME, TRMI_TEMP_FILENAME, CRYPTO_UPDATE_MESSAGE,
    TRMI_UPDATE_MESSAGE
)
from src.services.image_service import ImageService
from src.utils.logger import logger

class RatesService:
    """Servicio para manejo de tasas de cambio"""
    
    def __init__(self, image_service: ImageService, bot_app=None):
        self.image_service = image_service
        self.bot_app = bot_app
        self.last_crypto_hash: Optional[str] = None
        self.last_trmi_hash: Optional[str] = None
    
    async def get_both_rates(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Obtener ambas tasas de cambio
        
        Returns:
            Tuple con las rutas de las imágenes (crypto, trmi)
        """
        crypto_path = await self.image_service.download_image(
            CRYPTO_URL, CRYPTO_FILENAME
        )
        trmi_path = await self.image_service.download_image(
            TRMI_URL, TRMI_FILENAME
        )
        
        return crypto_path, trmi_path
    
    async def get_crypto_rate(self) -> Optional[str]:
        """
        Obtener solo la tasa de criptomonedas
        
        Returns:
            Ruta de la imagen de crypto o None
        """
        return await self.image_service.download_image(
            CRYPTO_URL, CRYPTO_FILENAME
        )
    
    async def get_trmi_rate(self) -> Optional[str]:
        """
        Obtener solo la tasa del mercado informal
        
        Returns:
            Ruta de la imagen de TRMI o None
        """
        return await self.image_service.download_image(
            TRMI_URL, TRMI_FILENAME
        )
    
    async def check_for_updates(self) -> bool:
        """
        Verificar si hay actualizaciones en las tasas
        
        Returns:
            True si se encontraron actualizaciones
        """
        try:
            # Descargar imágenes actuales
            crypto_path = await self.image_service.download_image(
                CRYPTO_URL, CRYPTO_TEMP_FILENAME
            )
            trmi_path = await self.image_service.download_image(
                TRMI_URL, TRMI_TEMP_FILENAME
            )
            
            updates_found = False
            
            # Verificar cambios en crypto
            if crypto_path:
                new_hash = self.image_service.get_image_hash(crypto_path)
                if self.last_crypto_hash and new_hash != self.last_crypto_hash:
                    await self.send_update_notification(
                        crypto_path, CRYPTO_UPDATE_MESSAGE
                    )
                    updates_found = True
                self.last_crypto_hash = new_hash
                
                # Mover archivo temporal al definitivo
                self.image_service.move_temp_to_final(
                    crypto_path, CRYPTO_FILENAME
                )
            
            # Verificar cambios en TRMI
            if trmi_path:
                new_hash = self.image_service.get_image_hash(trmi_path)
                if self.last_trmi_hash and new_hash != self.last_trmi_hash:
                    await self.send_update_notification(
                        trmi_path, TRMI_UPDATE_MESSAGE
                    )
                    updates_found = True
                self.last_trmi_hash = new_hash
                
                # Mover archivo temporal al definitivo
                self.image_service.move_temp_to_final(
                    trmi_path, TRMI_FILENAME
                )
            
            if updates_found:
                logger.info("Actualizaciones detectadas y enviadas")
            else:
                logger.info("No hay actualizaciones nuevas")
            
            return updates_found
        
        except Exception as e:
            logger.error(f"Error verificando actualizaciones: {e}")
            return False
    
    async def send_update_notification(self, image_path: str, caption: str):
        """
        Enviar notificación de actualización
        
        Args:
            image_path: Ruta de la imagen
            caption: Mensaje de la notificación
        """
        if CHAT_ID and self.bot_app:
            try:
                await self.bot_app.bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=open(image_path, 'rb'),
                    caption=f"{caption}\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info(f"Notificación enviada al chat {CHAT_ID}")
            except Exception as e:
                logger.error(f"Error enviando notificación: {e}")
    
    def initialize_hashes(self):
        """Inicializar hashes con las imágenes existentes"""
        crypto_path = self.image_service.get_image_path(CRYPTO_FILENAME)
        trmi_path = self.image_service.get_image_path(TRMI_FILENAME)
        
        if crypto_path.exists():
            self.last_crypto_hash = self.image_service.get_image_hash(crypto_path)
        if trmi_path.exists():
            self.last_trmi_hash = self.image_service.get_image_hash(trmi_path) 