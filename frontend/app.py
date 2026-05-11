# =============================================================================
# app.py — Dashboard principal de Software FJ
# =============================================================================
# Ventana principal con sidebar de navegación y área central dinámica.
# Orquesta los controladores y las vistas de cada módulo.
# =============================================================================

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config import COLORES, FUENTES, TITULO_APP, VENTANA_ANCHO, VENTANA_ALTO, SIDEBAR_ANCHO
from frontend.estilos import configurar_estilos
from frontend.componentes.sidebar import Sidebar
from frontend.componentes.widgets import TarjetaMetrica
from frontend.vistas.cliente_vista import ClienteVista
from frontend.vistas.servicio_vista import ServicioVista
from frontend.vistas.reserva_vista import ReservaVista
from frontend.vistas.asesor_vista import AsesorVista
from frontend.vistas.log_vista import LogVista
from backend.controllers.cliente_controller import ClienteController
from backend.controllers.servicio_controller import ServicioController
from backend.controllers.reserva_controller import ReservaController
from backend.controllers.asesor_controller import AsesorController
from backend.models.catalogo import CatalogoServicios
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("frontend.app")


class DashboardApp:
    """Aplicación principal del Sistema de Gestión de Software FJ.

    Crea la ventana raíz, inicializa controladores, y gestiona la
    navegación entre módulos mediante el sidebar.

    Attributes:
        _root (tk.Tk): Ventana raíz.
        _cliente_ctrl (ClienteController): Controlador de clientes.
        _servicio_ctrl (ServicioController): Controlador de servicios.
        _reserva_ctrl (ReservaController): Controlador de reservas.
        _asesor_ctrl (AsesorController): Controlador de asesores.
        _frame_central (tk.Frame): Área donde se renderizan las vistas.
        _vista_actual: Vista actualmente mostrada.
    """

    def __init__(self):
        """Inicializa la aplicación completa."""
        # Crear ventana raíz
        self._root = tk.Tk()
        self._root.title(TITULO_APP)
        self._root.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}")
        self._root.minsize(1024, 600)
        self._root.configure(bg=COLORES["fondo"])

        # Centrar ventana
        self._centrar_ventana()

        # Configurar estilos
        configurar_estilos(self._root)

        # Inicializar controladores (backend)
        self._catalogo = CatalogoServicios()
        self._cliente_ctrl = ClienteController()
        self._servicio_ctrl = ServicioController(self._catalogo)
        self._reserva_ctrl = ReservaController()
        self._asesor_ctrl = AsesorController()

        # Variable para la vista actual
        self._vista_actual = None

        # Crear layout
        self._crear_layout()

        # Mostrar vista de inicio por defecto
        self._cambiar_vista("inicio")

        logger.info("Dashboard inicializado correctamente")

    def _centrar_ventana(self) -> None:
        """Centra la ventana en la pantalla."""
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth() - VENTANA_ANCHO) // 2
        y = (self._root.winfo_screenheight() - VENTANA_ALTO) // 2
        self._root.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}+{x}+{y}")

    def _crear_layout(self) -> None:
        """Crea el layout principal: sidebar + área central + barra de estado."""
        # Frame contenedor principal
        frame_principal = tk.Frame(self._root, bg=COLORES["fondo"])
        frame_principal.pack(fill="both", expand=True)

        # ─── Sidebar ────────────────────────────────────────────────
        self._sidebar = Sidebar(
            frame_principal,
            callback=self._cambiar_vista
        )
        self._sidebar.pack(side="left", fill="y", ipadx=10)
        self._sidebar.configure(width=SIDEBAR_ANCHO)
        self._sidebar.pack_propagate(False)

        # ─── Área central ───────────────────────────────────────────
        self._frame_central = tk.Frame(frame_principal, bg=COLORES["fondo"])
        self._frame_central.pack(side="right", fill="both", expand=True)

        # ─── Barra de estado inferior ───────────────────────────────
        barra_estado = tk.Frame(self._root, bg=COLORES["primario"], height=28)
        barra_estado.pack(fill="x", side="bottom")
        barra_estado.pack_propagate(False)

        tk.Label(
            barra_estado,
            text=f"  💻 Software FJ v1.0.0  |  Sistema Integral de Gestión",
            font=("Segoe UI", 9),
            fg="#b0bec5",
            bg=COLORES["primario"],
            anchor="w"
        ).pack(side="left", padx=10)

        self._label_reloj = tk.Label(
            barra_estado,
            text="",
            font=("Segoe UI", 9),
            fg="#b0bec5",
            bg=COLORES["primario"],
            anchor="e"
        )
        self._label_reloj.pack(side="right", padx=10)
        self._actualizar_reloj()

    def _actualizar_reloj(self) -> None:
        """Actualiza el reloj de la barra de estado cada segundo."""
        ahora = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self._label_reloj.configure(text=ahora)
        self._root.after(1000, self._actualizar_reloj)

    def _cambiar_vista(self, nombre_modulo: str) -> None:
        """Cambia la vista del área central según el módulo seleccionado.

        Destruye la vista actual y crea la nueva. Captura cualquier error
        para mantener la aplicación estable.

        Args:
            nombre_modulo: Nombre del módulo ("inicio", "clientes", etc.)
        """
        try:
            # Destruir vista actual
            if self._vista_actual is not None:
                self._vista_actual.destroy()
                self._vista_actual = None

            # Crear nueva vista según módulo
            if nombre_modulo == "inicio":
                self._vista_actual = self._crear_vista_inicio()
            elif nombre_modulo == "clientes":
                self._vista_actual = ClienteVista(
                    self._frame_central, self._cliente_ctrl
                )
            elif nombre_modulo == "servicios":
                self._vista_actual = ServicioVista(
                    self._frame_central, self._servicio_ctrl,
                    asesor_ctrl=self._asesor_ctrl
                )
            elif nombre_modulo == "asesores":
                self._vista_actual = AsesorVista(
                    self._frame_central, self._asesor_ctrl
                )
            elif nombre_modulo == "reservas":
                self._vista_actual = ReservaVista(
                    self._frame_central,
                    self._reserva_ctrl,
                    self._cliente_ctrl,
                    self._servicio_ctrl
                )
            elif nombre_modulo == "logs":
                self._vista_actual = LogVista(self._frame_central)
            else:
                logger.warning(f"Módulo desconocido: {nombre_modulo}")
                return

            if self._vista_actual:
                self._vista_actual.pack(fill="both", expand=True)

            logger.debug(f"Vista cambiada a: {nombre_modulo}")

        except Exception as e:
            logger.error(f"Error al cambiar a vista '{nombre_modulo}': {e}")
            # Mostrar mensaje de error en el área central
            self._vista_actual = tk.Frame(self._frame_central, bg=COLORES["fondo"])
            self._vista_actual.pack(fill="both", expand=True)
            tk.Label(
                self._vista_actual,
                text=f"❌ Error al cargar el módulo: {e}",
                font=FUENTES["normal"],
                fg=COLORES["error"],
                bg=COLORES["fondo"],
                wraplength=600
            ).pack(expand=True)

    def _crear_vista_inicio(self) -> tk.Frame:
        """Crea la vista de inicio con tarjetas de métricas y bienvenida."""
        frame = tk.Frame(self._frame_central, bg=COLORES["fondo"])

        # ─── Bienvenida ─────────────────────────────────────────────
        frame_bienvenida = tk.Frame(frame, bg=COLORES["fondo"])
        frame_bienvenida.pack(fill="x", padx=30, pady=(30, 10))

        tk.Label(
            frame_bienvenida,
            text="Bienvenido al Sistema de Gestión",
            font=("Segoe UI", 22, "bold"),
            fg=COLORES["primario"],
            bg=COLORES["fondo"]
        ).pack(anchor="w")

        tk.Label(
            frame_bienvenida,
            text="Software FJ — Panel de control principal",
            font=FUENTES["normal"],
            fg=COLORES["texto_claro"],
            bg=COLORES["fondo"]
        ).pack(anchor="w", pady=(5, 0))

        # Separador
        ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=30, pady=15)

        # ─── Tarjetas de métricas ────────────────────────────────────
        frame_tarjetas = tk.Frame(frame, bg=COLORES["fondo"])
        frame_tarjetas.pack(fill="x", padx=30, pady=(0, 20))

        # Obtener métricas
        total_clientes = self._cliente_ctrl.total_clientes
        resumen_servicios = self._servicio_ctrl.obtener_resumen()
        resumen_reservas = self._reserva_ctrl.obtener_resumen()

        total_asesores = self._asesor_ctrl.total_asesores

        tarjetas_config = [
            ("Clientes Registrados", str(total_clientes), "👥", COLORES["primario"]),
            ("Servicios Disponibles", str(resumen_servicios["total_servicios"]), "🔧", COLORES["acento"]),
            ("Asesores", str(total_asesores), "👨‍💼", "#6a1b9a"),
            ("Reservas Totales", str(resumen_reservas["total"]), "📅", COLORES["exito"]),
            ("Ingresos", f"${resumen_reservas.get('ingresos_totales', 0):,.0f}", "💰", COLORES["advertencia"]),
        ]

        for i, (titulo, valor, icono, color) in enumerate(tarjetas_config):
            tarjeta = TarjetaMetrica(
                frame_tarjetas, titulo=titulo, valor=valor,
                icono=icono, color_valor=color
            )
            tarjeta.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            frame_tarjetas.columnconfigure(i, weight=1)

        # ─── Accesos rápidos ─────────────────────────────────────────
        frame_accesos = tk.LabelFrame(
            frame, text=" Accesos Rápidos ",
            font=FUENTES["subtitulo"], fg=COLORES["primario"],
            bg=COLORES["fondo_card"], bd=1, relief="solid",
            padx=20, pady=15
        )
        frame_accesos.pack(fill="x", padx=30, pady=(0, 20))

        accesos = [
            ("👥 Gestionar Clientes", "clientes"),
            ("🔧 Ver Servicios", "servicios"),
            ("👨‍💼 Asesores", "asesores"),
            ("📅 Nueva Reserva", "reservas"),
            ("📋 Ver Logs", "logs"),
        ]

        frame_btns = tk.Frame(frame_accesos, bg=COLORES["fondo_card"])
        frame_btns.pack(fill="x")

        for texto, modulo in accesos:
            btn = ttk.Button(
                frame_btns, text=texto, style="Accent.TButton",
                command=lambda m=modulo: self._navegar_desde_inicio(m)
            )
            btn.pack(side="left", padx=(0, 10), pady=5)

        # ─── Información del sistema ─────────────────────────────────
        frame_info = tk.Frame(frame, bg=COLORES["fondo"])
        frame_info.pack(fill="x", padx=30, pady=(0, 20))

        info_texto = (
            f"📊 Resumen: {resumen_servicios['total_salas']} salas | "
            f"{resumen_servicios['total_equipos']} tipos de equipos | "
            f"{resumen_servicios['total_asesorias']} tipos de asesorías | "
            f"{total_asesores} asesores"
        )
        tk.Label(
            frame_info, text=info_texto,
            font=FUENTES["normal"], fg=COLORES["texto_claro"], bg=COLORES["fondo"]
        ).pack(anchor="w")

        return frame

    def _navegar_desde_inicio(self, modulo: str) -> None:
        """Navega a un módulo actualizando también el sidebar."""
        self._sidebar._actualizar_boton_activo(modulo)
        self._cambiar_vista(modulo)

    def ejecutar(self) -> None:
        """Inicia el bucle principal de la aplicación."""
        logger.info("Iniciando aplicación Software FJ")
        self._root.mainloop()
