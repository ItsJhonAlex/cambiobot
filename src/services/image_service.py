"""
Servicio para manejo de imágenes y scraping
"""
import hashlib
import aiohttp
from pathlib import Path
from typing import Optional
from src.config.settings import IMAGES_DIR
from src.utils.logger import logger

class ImageService:
    """Servicio para manejo de imágenes"""
    
    def __init__(self):
        self.images_dir = IMAGES_DIR
    
    async def download_image(self, url: str, filename: str) -> Optional[Path]:
        """
        Descargar imagen desde una URL
        
        Args:
            url: URL de la imagen
            filename: Nombre del archivo para guardar
            
        Returns:
            Path del archivo descargado o None si falla
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image_path = self.images_dir / filename
                        
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
        """
        Obtener hash MD5 de una imagen
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Hash MD5 de la imagen
        """
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash de {image_path}: {e}")
            return ""
    
    def move_temp_to_final(self, temp_path: Path, final_filename: str) -> Path:
        """
        Mover archivo temporal al definitivo
        
        Args:
            temp_path: Ruta del archivo temporal
            final_filename: Nombre del archivo final
            
        Returns:
            Path del archivo final
        """
        final_path = self.images_dir / final_filename
        temp_path.rename(final_path)
        return final_path
    
    def image_exists(self, filename: str) -> bool:
        """
        Verificar si una imagen existe
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si existe, False en caso contrario
        """
        return (self.images_dir / filename).exists()
    
    def get_image_path(self, filename: str) -> Path:
        """
        Obtener la ruta completa de una imagen
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Path completo de la imagen
        """
        return self.images_dir / filename 