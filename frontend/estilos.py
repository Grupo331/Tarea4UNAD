# =============================================================================
# estilos.py — Tema y estilos corporativos para Tkinter
# =============================================================================
# Configura ttk.Style con la paleta de colores de Software FJ.
# Centraliza fuentes, colores y estilos de widgets reutilizables.
# =============================================================================

import tkinter as tk
from tkinter import ttk
from config import COLORES, FUENTES


def configurar_estilos(root: tk.Tk) -> None:
    """Configura todos los estilos ttk para la aplicación.

    Crea estilos personalizados con la paleta corporativa de Software FJ
    para que toda la aplicación mantenga consistencia visual.

    Args:
        root: Ventana raíz de Tkinter.
    """
    estilo = ttk.Style(root)

    # Intentar usar tema 'clam' como base (mejor para personalización)
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        estilo.theme_use("default")

    # ─── Frames ──────────────────────────────────────────────────────
    estilo.configure("Card.TFrame", background=COLORES["fondo_card"])
    estilo.configure("Sidebar.TFrame", background=COLORES["fondo_sidebar"])
    estilo.configure("Main.TFrame", background=COLORES["fondo"])
    estilo.configure("Header.TFrame", background=COLORES["primario"])

    # ─── Labels ──────────────────────────────────────────────────────
    estilo.configure(
        "Title.TLabel",
        font=FUENTES["titulo"],
        foreground=COLORES["texto"],
        background=COLORES["fondo"]
    )
    estilo.configure(
        "Subtitle.TLabel",
        font=FUENTES["subtitulo"],
        foreground=COLORES["texto"],
        background=COLORES["fondo"]
    )
    estilo.configure(
        "CardTitle.TLabel",
        font=FUENTES["subtitulo"],
        foreground=COLORES["primario"],
        background=COLORES["fondo_card"]
    )
    estilo.configure(
        "Body.TLabel",
        font=FUENTES["normal"],
        foreground=COLORES["texto"],
        background=COLORES["fondo"]
    )
    estilo.configure(
        "Small.TLabel",
        font=FUENTES["pequeña"],
        foreground=COLORES["texto_claro"],
        background=COLORES["fondo"]
    )
    estilo.configure(
        "Header.TLabel",
        font=FUENTES["titulo"],
        foreground="white",
        background=COLORES["primario"]
    )
    estilo.configure(
        "Sidebar.TLabel",
        font=FUENTES["sidebar"],
        foreground=COLORES["texto_sidebar"],
        background=COLORES["fondo_sidebar"]
    )
    estilo.configure(
        "Status.TLabel",
        font=FUENTES["pequeña"],
        foreground=COLORES["texto_claro"],
        background=COLORES["fondo"]
    )
    # Labels para métricas del dashboard
    estilo.configure(
        "MetricValue.TLabel",
        font=("Segoe UI", 28, "bold"),
        foreground=COLORES["primario"],
        background=COLORES["fondo_card"]
    )
    estilo.configure(
        "MetricLabel.TLabel",
        font=FUENTES["pequeña"],
        foreground=COLORES["texto_claro"],
        background=COLORES["fondo_card"]
    )

    # ─── Botones ─────────────────────────────────────────────────────
    estilo.configure(
        "Primary.TButton",
        font=FUENTES["boton"],
        foreground="white",
        background=COLORES["primario"],
        borderwidth=0,
        padding=(20, 10)
    )
    estilo.map(
        "Primary.TButton",
        background=[("active", COLORES["primario_hover"]),
                    ("disabled", "#9e9e9e")],
        foreground=[("disabled", "#e0e0e0")]
    )

    estilo.configure(
        "Accent.TButton",
        font=FUENTES["boton"],
        foreground="white",
        background=COLORES["acento"],
        borderwidth=0,
        padding=(20, 10)
    )
    estilo.map(
        "Accent.TButton",
        background=[("active", COLORES["acento_hover"])]
    )

    estilo.configure(
        "Danger.TButton",
        font=FUENTES["boton"],
        foreground="white",
        background=COLORES["error"],
        borderwidth=0,
        padding=(20, 10)
    )
    estilo.map(
        "Danger.TButton",
        background=[("active", "#b71c1c")]
    )

    estilo.configure(
        "Success.TButton",
        font=FUENTES["boton"],
        foreground="white",
        background=COLORES["exito"],
        borderwidth=0,
        padding=(20, 10)
    )
    estilo.map(
        "Success.TButton",
        background=[("active", "#1b5e20")]
    )

    estilo.configure(
        "Warning.TButton",
        font=FUENTES["boton"],
        foreground="white",
        background=COLORES.get("advertencia", "#f57f17"),
        borderwidth=0,
        padding=(20, 10)
    )
    estilo.map(
        "Warning.TButton",
        background=[("active", "#e65100")]
    )

    estilo.configure(
        "Secondary.TButton",
        font=FUENTES["boton"],
        foreground="white",
        background="#757575",
        borderwidth=0,
        padding=(20, 10)
    )
    estilo.map(
        "Secondary.TButton",
        background=[("active", "#616161")]
    )

    # ─── Entries ─────────────────────────────────────────────────────
    estilo.configure(
        "Custom.TEntry",
        font=FUENTES["normal"],
        fieldbackground="white",
        borderwidth=1,
        padding=8
    )

    # ─── Combobox ────────────────────────────────────────────────────
    estilo.configure(
        "Custom.TCombobox",
        font=FUENTES["normal"],
        fieldbackground="white",
        padding=8
    )

    # ─── Treeview (tablas) ───────────────────────────────────────────
    estilo.configure(
        "Custom.Treeview",
        font=FUENTES["tabla_body"],
        background="white",
        fieldbackground="white",
        foreground=COLORES["texto"],
        rowheight=35,
        borderwidth=0
    )
    estilo.configure(
        "Custom.Treeview.Heading",
        font=FUENTES["tabla_header"],
        background=COLORES["tabla_header"],
        foreground="white",
        borderwidth=0,
        padding=8
    )
    estilo.map(
        "Custom.Treeview",
        background=[("selected", COLORES["acento"])],
        foreground=[("selected", "white")]
    )

    # ─── Separator ───────────────────────────────────────────────────
    estilo.configure("Custom.TSeparator", background=COLORES["borde"])

    # ─── LabelFrame ──────────────────────────────────────────────────
    estilo.configure(
        "Card.TLabelframe",
        background=COLORES["fondo_card"],
        foreground=COLORES["primario"],
        font=FUENTES["subtitulo"],
        borderwidth=1,
        relief="solid"
    )
    estilo.configure(
        "Card.TLabelframe.Label",
        background=COLORES["fondo_card"],
        foreground=COLORES["primario"],
        font=FUENTES["subtitulo"]
    )
