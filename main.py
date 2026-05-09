# =============================================================================
# main.py — Punto de entrada del Sistema de Gestión Software FJ
# =============================================================================
# Inicializa el logging y lanza el dashboard principal.
# =============================================================================

import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.logger_config import configurar_logging, obtener_logger
from frontend.app import DashboardApp


def main():
    """Punto de entrada principal de la aplicación."""
    # 1. Inicializar sistema de logging
    configurar_logging()
    logger = obtener_logger("main")
    logger.info("=" * 60)
    logger.info("INICIO DE APLICACIÓN — Software FJ v1.0.0")
    logger.info("=" * 60)

    try:
        # 2. Crear e iniciar la aplicación
        app = DashboardApp()
        app.ejecutar()

    except Exception as e:
        logger.critical(f"Error fatal al iniciar la aplicación: {e}", exc_info=True)
        print(f"\n❌ Error fatal: {e}")
        print("Revise el archivo de logs para más detalles.")
        sys.exit(1)

    finally:
        logger.info("=" * 60)
        logger.info("FIN DE APLICACIÓN — Software FJ")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
