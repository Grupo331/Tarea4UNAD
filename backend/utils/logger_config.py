# =============================================================================
# logger_config.py — Configuración del sistema de logging de Software FJ
# =============================================================================
# Usa la librería estándar logging con RotatingFileHandler para archivos
# y StreamHandler para consola durante desarrollo.
# =============================================================================

import os
import logging
from logging.handlers import RotatingFileHandler
from config import LOGS_DIR, LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOG_FORMAT, LOG_DATE_FORMAT


def configurar_logging(nivel_consola: int = logging.WARNING, nivel_archivo: int = logging.DEBUG) -> None:
    """Configura el sistema de logging global de la aplicación.

    Crea el directorio de logs si no existe y configura dos handlers:
    - RotatingFileHandler: registra TODO (DEBUG+) en archivo con rotación
    - StreamHandler: muestra WARNING+ en consola (configurable)

    Args:
        nivel_consola: Nivel mínimo para mostrar en consola.
        nivel_archivo: Nivel mínimo para registrar en archivo.
    """
    # Crear directorio de logs si no existe
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Obtener el logger raíz de la aplicación
    logger_raiz = logging.getLogger("softwarefj")
    logger_raiz.setLevel(logging.DEBUG)  # Captura todo; los handlers filtran

    # Evitar duplicar handlers si se llama múltiples veces
    if logger_raiz.handlers:
        return

    # Formatter unificado
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Handler de archivo con rotación
    try:
        handler_archivo = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        handler_archivo.setLevel(nivel_archivo)
        handler_archivo.setFormatter(formatter)
        logger_raiz.addHandler(handler_archivo)
    except (OSError, PermissionError) as e:
        # Si no se puede crear el archivo de log, al menos logear en consola
        print(f"[ADVERTENCIA] No se pudo crear el archivo de log: {e}")

    # Handler de consola
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(nivel_consola)
    handler_consola.setFormatter(formatter)
    logger_raiz.addHandler(handler_consola)

    logger_raiz.info("Sistema de logging inicializado correctamente")


def obtener_logger(nombre_modulo: str) -> logging.Logger:
    """Obtiene un logger hijo del logger raíz de la aplicación.

    Cada módulo debe llamar a esta función para obtener su propio logger,
    lo que permite identificar en el log de dónde proviene cada mensaje.

    Args:
        nombre_modulo: Nombre del módulo (ej: 'models.cliente', 'controllers.reserva')

    Returns:
        Logger configurado como hijo de 'softwarefj'
    
    Ejemplo:
        >>> logger = obtener_logger("models.cliente")
        >>> logger.info("Cliente creado: Juan Pérez")
    """
    return logging.getLogger(f"softwarefj.{nombre_modulo}")
