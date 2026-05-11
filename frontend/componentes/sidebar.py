# =============================================================================
# sidebar.py — Panel lateral de navegación del Dashboard
# =============================================================================
# Implementa el sidebar con botones de navegación estilizados que
# controlan qué vista se muestra en el área central.
# =============================================================================

import tkinter as tk
from config import COLORES, FUENTES


class Sidebar(tk.Frame):
    """Panel lateral de navegación con botones estilizados.

    Cada botón representa un módulo del sistema. Al hacer clic,
    invoca un callback que cambia el contenido del área central.

    Attributes:
        _botones (dict): Mapeo nombre → widget Button.
        _boton_activo (str): Nombre del botón actualmente seleccionado.
        _callback (callable): Función a invocar al seleccionar un módulo.
    """

    # Emojis como íconos simples (funciona en Windows 10/11)
    MODULOS = [
        ("🏠  Inicio", "inicio"),
        ("👥  Clientes", "clientes"),
        ("🔧  Servicios", "servicios"),
        ("👨‍💼  Asesores", "asesores"),
        ("📅  Reservas", "reservas"),
        ("📋  Logs", "logs"),
    ]

    def __init__(self, parent, callback, **kwargs):
        """Inicializa el sidebar.

        Args:
            parent: Widget padre.
            callback: Función que recibe el nombre del módulo seleccionado.
        """
        super().__init__(parent, bg=COLORES["fondo_sidebar"], **kwargs)
        self._callback = callback
        self._botones: dict = {}
        self._boton_activo: str = "inicio"
        self._crear_widgets()

    def _crear_widgets(self) -> None:
        """Crea el logo y los botones de navegación."""
        # ─── Logo / Título ───────────────────────────────────────────
        frame_logo = tk.Frame(self, bg=COLORES["fondo_sidebar"])
        frame_logo.pack(fill="x", padx=15, pady=(25, 5))

        tk.Label(
            frame_logo,
            text="💻",
            font=("Segoe UI", 32),
            bg=COLORES["fondo_sidebar"],
            fg="white"
        ).pack()

        tk.Label(
            frame_logo,
            text="Software FJ",
            font=("Segoe UI", 16, "bold"),
            bg=COLORES["fondo_sidebar"],
            fg="white"
        ).pack()

        tk.Label(
            frame_logo,
            text="Sistema de Gestión",
            font=("Segoe UI", 9),
            bg=COLORES["fondo_sidebar"],
            fg=COLORES["texto_sidebar"]
        ).pack(pady=(0, 15))

        # Separador
        separador = tk.Frame(self, bg=COLORES["primario"], height=2)
        separador.pack(fill="x", padx=20, pady=5)

        # ─── Botones de navegación ───────────────────────────────────
        frame_nav = tk.Frame(self, bg=COLORES["fondo_sidebar"])
        frame_nav.pack(fill="both", expand=True, padx=10, pady=10)

        for texto, nombre in self.MODULOS:
            btn = tk.Button(
                frame_nav,
                text=texto,
                font=FUENTES["sidebar"],
                fg=COLORES["texto_sidebar"],
                bg=COLORES["fondo_sidebar"],
                activeforeground="white",
                activebackground=COLORES["primario_hover"],
                bd=0,
                anchor="w",
                padx=15,
                pady=10,
                cursor="hand2",
                command=lambda n=nombre: self._on_click(n)
            )
            btn.pack(fill="x", pady=2)
            self._botones[nombre] = btn

            # Efecto hover
            btn.bind("<Enter>", lambda e, b=btn, n=nombre: self._on_hover(b, n, True))
            btn.bind("<Leave>", lambda e, b=btn, n=nombre: self._on_hover(b, n, False))

        # ─── Footer con versión ──────────────────────────────────────
        frame_footer = tk.Frame(self, bg=COLORES["fondo_sidebar"])
        frame_footer.pack(fill="x", side="bottom", padx=15, pady=15)

        tk.Label(
            frame_footer,
            text="v1.0.0",
            font=("Segoe UI", 8),
            bg=COLORES["fondo_sidebar"],
            fg="#546e7a"
        ).pack()

        # Activar botón inicio por defecto
        self._actualizar_boton_activo("inicio")

    def _on_click(self, nombre: str) -> None:
        """Maneja el clic en un botón de navegación."""
        if nombre != self._boton_activo:
            self._actualizar_boton_activo(nombre)
            self._callback(nombre)

    def _on_hover(self, boton: tk.Button, nombre: str, entrando: bool) -> None:
        """Efecto hover: cambia el fondo del botón."""
        if nombre == self._boton_activo:
            return  # No modificar el botón activo
        if entrando:
            boton.configure(bg=COLORES["primario_hover"], fg="white")
        else:
            boton.configure(bg=COLORES["fondo_sidebar"], fg=COLORES["texto_sidebar"])

    def _actualizar_boton_activo(self, nombre: str) -> None:
        """Resalta el botón activo y resetea los demás."""
        # Resetear todos
        for n, btn in self._botones.items():
            btn.configure(
                bg=COLORES["fondo_sidebar"],
                fg=COLORES["texto_sidebar"],
                font=FUENTES["sidebar"]
            )
        # Resaltar el activo
        if nombre in self._botones:
            self._botones[nombre].configure(
                bg=COLORES["sidebar_activo"],
                fg=COLORES["texto_sidebar_activo"],
                font=FUENTES["sidebar_bold"]
            )
        self._boton_activo = nombre
