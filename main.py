# Aporte realizado por: Alejandra Rojas.
# =============================================================================
# main.py — Punto de entrada del Sistema de Gestión Software FJ
# =============================================================================
"""
Módulo principal del Sistema de Gestión Software FJ.

Este script actúa como el punto de entrada de la aplicación. Su responsabilidad
principal es configurar el entorno inicial (como el sistema de logging) y
lanzar la interfaz de usuario principal (DashboardApp).
"""
# =============================================================================

import sys
import os

# Asegurar que el directorio raíz esté en el path de Python para permitir
# importaciones absolutas desde los paquetes backend y frontend.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.logger_config import configurar_logging, obtener_logger
from frontend.app import DashboardApp


def main():
    """
    Punto de entrada principal de la aplicación.
    
    Esta función orquesta el inicio del sistema realizando las siguientes operaciones:
    1. Inicializa y configura el sistema de registro de eventos (logging).
    2. Registra el inicio de la sesión en los logs.
    3. Instancia e inicia la aplicación gráfica principal (DashboardApp).
    4. Captura y gestiona cualquier excepción no controlada a nivel global.
    
    Returns:
        None
    """
    # 1. Inicializar sistema de logging centralizado
    configurar_logging()
    logger = obtener_logger("main")
    
    # Registrar cabecera de inicio en el archivo de log
    logger.info("=" * 60)
    logger.info("INICIO DE APLICACIÓN — Software FJ v1.0.0")
    logger.info("=" * 60)

    try:
        # 2. Crear e iniciar la aplicación gráfica (interfaz de usuario)
        app = DashboardApp()
        app.ejecutar()

    except Exception as e:
        # Capturar cualquier error inesperado y registrar el traceback completo
        logger.critical(f"Error fatal al iniciar la aplicación: {e}", exc_info=True)
        
        # Proveer feedback básico por consola en caso de fallo crítico
        print(f"\n❌ Error fatal: {e}")
        print("Revise el archivo de logs para más detalles.")
        
        # Terminar la ejecución con un código de salida indicando error (1)
        sys.exit(1)

    finally:
        # Asegurar que el mensaje de fin de ejecución siempre se registre
        logger.info("=" * 60)
        logger.info("FIN DE APLICACIÓN — Software FJ")
        logger.info("=" * 60)


# Verificar si el script se está ejecutando directamente
if __name__ == "__main__":
    main()
