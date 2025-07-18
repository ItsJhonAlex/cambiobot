"""
Configuración de logging centralizada
"""
import logging
from src.config.settings import LOG_FORMAT, LOG_LEVEL

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Configurar y retornar un logger
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    # Configurar logging básico
    logging.basicConfig(
        format=LOG_FORMAT,
        level=getattr(logging, LOG_LEVEL.upper())
    )
    
    return logging.getLogger(name)

# Logger principal del bot
logger = setup_logger('cambiobot') 