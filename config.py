# =============================================================================
# config.py — Constantes globales del sistema Software FJ
# =============================================================================
# Centraliza tarifas, configuraciones y constantes para facilitar cambios
# sin modificar lógica de negocio. Todas las tarifas son en pesos colombianos.
# =============================================================================

import os

# ─── Información de la empresa ───────────────────────────────────────────────
NOMBRE_EMPRESA = "Software FJ"
VERSION_APP = "1.0.0"
TITULO_APP = f"{NOMBRE_EMPRESA} — Sistema Integral de Gestión"

# ─── Rutas del sistema ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# ─── Tarifas de Salas (COP) ─────────────────────────────────────────────────
TARIFAS_SALAS = {
    "reunión": {"hora": 50_000, "dia": 300_000, "capacidad_default": 10},
    "capacitación": {"hora": 60_000, "dia": 350_000, "capacidad_default": 25},
    "coworking": {"hora": 40_000, "dia": 250_000, "capacidad_default": 15},
}

# ─── Tarifas de Equipos (COP por día) ───────────────────────────────────────
TARIFAS_EQUIPOS = {
    "laptop": {"dia": 30_000, "stock_inicial": 100},
    "proyector": {"dia": 20_000, "stock_inicial": 100},
    "impresora": {"dia": 15_000, "stock_inicial": 100},
}

# ─── Tarifas de Asesorías (COP) ─────────────────────────────────────────────
TARIFAS_ASESORIAS = {
    "legal": {"hora": 80_000, "dia": 500_000},
    "contable": {"hora": 60_000, "dia": 400_000},
    "técnica": {"hora": 50_000, "dia": 350_000},
}

# ─── Impuesto por defecto (IVA Colombia) ────────────────────────────────────
IVA_DEFAULT = 0.19

# ─── Estados de reserva ─────────────────────────────────────────────────────
# Transiciones válidas: estado_actual -> [estados_permitidos]
TRANSICIONES_ESTADO = {
    "PENDIENTE": ["CONFIRMADA", "CANCELADA"],
    "CONFIRMADA": ["EN_CURSO", "CANCELADA", "NO_ASISTIO"],
    "EN_CURSO": ["COMPLETADA"],
    "COMPLETADA": [],
    "CANCELADA": [],
    "NO_ASISTIO": [],
}

# ─── Logging ─────────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(LOGS_DIR, "app.log")
LOG_MAX_BYTES = 5 * 1024 * 1024   # 5 MB
LOG_BACKUP_COUNT = 3
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ─── Colores corporativos (Tkinter) ─────────────────────────────────────────
COLORES = {
    "primario": "#1a237e",          # Azul oscuro profundo
    "primario_hover": "#283593",    # Azul oscuro más claro (hover)
    "acento": "#00bcd4",            # Cyan vibrante
    "acento_hover": "#00acc1",      # Cyan hover
    "exito": "#2e7d32",             # Verde éxito
    "advertencia": "#f57f17",       # Amarillo advertencia
    "error": "#c62828",             # Rojo error
    "fondo": "#f5f5f5",             # Gris muy claro
    "fondo_sidebar": "#0d1b2a",     # Azul noche sidebar
    "fondo_card": "#ffffff",        # Blanco cards
    "texto": "#212121",             # Texto principal
    "texto_claro": "#757575",       # Texto secundario
    "texto_sidebar": "#e0e0e0",     # Texto sidebar
    "texto_sidebar_activo": "#ffffff",
    "borde": "#e0e0e0",             # Bordes suaves
    "sidebar_activo": "#1a237e",    # Fondo botón activo sidebar
    "tabla_header": "#1a237e",      # Header de tablas
    "tabla_row_alt": "#f5f5f5",     # Fila alterna
}

# ─── Fuentes ─────────────────────────────────────────────────────────────────
FUENTES = {
    "titulo": ("Segoe UI", 18, "bold"),
    "subtitulo": ("Segoe UI", 14, "bold"),
    "normal": ("Segoe UI", 11),
    "pequeña": ("Segoe UI", 9),
    "sidebar": ("Segoe UI", 12),
    "sidebar_bold": ("Segoe UI", 12, "bold"),
    "boton": ("Segoe UI", 11, "bold"),
    "tabla_header": ("Segoe UI", 10, "bold"),
    "tabla_body": ("Segoe UI", 10),
    "monospace": ("Consolas", 10),
}

# ─── Dimensiones de la ventana ───────────────────────────────────────────────
VENTANA_ANCHO = 1280
VENTANA_ALTO = 720
SIDEBAR_ANCHO = 220
