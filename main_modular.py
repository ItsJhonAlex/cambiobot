#!/usr/bin/env python3
"""
Bot de Telegram para obtener tasas de cambio de Cuba
Versión modularizada para mejor escalabilidad
"""

import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.cambio_bot import CambioBot
from utils.logger import logger

async def main():
    """Función principal"""
    try:
        bot = CambioBot()
        await bot.run()
    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        logger.error("Por favor edita el archivo .env con tu token de bot")
        logger.error("Obtén tu token desde @BotFather en Telegram")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 