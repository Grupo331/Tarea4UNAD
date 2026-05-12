# =============================================================================
# app.py — Dashboard principal de Software FJ
# =============================================================================
"""
Módulo de la Interfaz Gráfica de Usuario (GUI) y Dashboard.

Este archivo define la clase DashboardApp, la cual orquesta la ventana 
principal, gestiona la navegación entre módulos (vistas) e inicializa 
los controladores del backend. Implementa un diseño de área central dinámica 
donde las vistas se cargan y destruyen según la interacción del usuario.

Utiliza un patrón de diseño orientado a objetos para encapsular la ventana 
de Tkinter, gestionando de manera centralizada los controladores de datos.
"""

# Importaciones de biblioteca estándar
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Importación de configuración y estilos globales
# Estas constantes definen la apariencia (colores, fuentes) y dimensiones de la app.
from config import COLORES, FUENTES, TITULO_APP, VENTANA_ANCHO, VENTANA_ALTO, SIDEBAR_ANCHO

# Importación de componentes visuales y vistas
from frontend.estilos import configurar_estilos
from frontend.componentes.sidebar import Sidebar
from frontend.componentes.widgets import TarjetaMetrica
from frontend.vistas.cliente_vista import ClienteVista
from frontend.vistas.servicio_vista import ServicioVista
from frontend.vistas.reserva_vista import ReservaVista
from frontend.vistas.asesor_vista import AsesorVista
from frontend.vistas.log_vista import LogVista

# Importación de la capa de Controladores (Backend)
from backend.controllers.cliente_controller import ClienteController
from backend.controllers.servicio_controller import ServicioController
from backend.controllers.reserva_controller import ReservaController
from backend.controllers.asesor_controller import AsesorController
from backend.models.catalogo import CatalogoServicios
from backend.utils.logger_config import obtener_logger

# Inicialización del logger para rastrear eventos de la interfaz
# Permite capturar errores de renderizado y trazas de navegación.
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
        """
        Inicializa la aplicación completa configurando la ventana principal,
        los estilos corporativos y el estado inicial de los controladores.
        """
        # 1. Configuración de la ventana raíz (Root Window)
        # self._root es la instancia principal de la ventana Tkinter.
        self._root = tk.Tk()
        self._root.title(TITULO_APP) # Título definido en config.py
        self._root.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}") # Dimensión inicial
        self._root.minsize(1024, 600) # Evita que la UI se rompa en pantallas muy pequeñas
        self._root.configure(bg=COLORES["fondo"])

        # 2. Lógica de posicionamiento: Se calcula el centro geométrico del monitor.
        self._centrar_ventana()

        # 3. Aplicar tema y estilos: Carga la paleta de colores corporativa en ttk.
        configurar_estilos(self._root)

        # 4. Inyección de Dependencias: Inicializar la lógica de negocio (Backend)
        # Se instancian los controladores para que vivan durante todo el ciclo de la app.
        self._catalogo = CatalogoServicios()
        self._cliente_ctrl = ClienteController() # Maneja CRUD de clientes
        self._servicio_ctrl = ServicioController(self._catalogo) # Maneja inventario de servicios
        self._reserva_ctrl = ReservaController() # Maneja lógica de estados de reserva
        self._asesor_ctrl = AsesorController() # Maneja personal especializado

        # 5. Estado de navegación: Mantiene referencia a la vista activa para poder destruirla
        self._vista_actual = None # Almacenará el frame de la pestaña activa (Clientes, Reservas, etc.)

        # 6. Construcción de la UI persistente
        self._crear_layout()

        # 7. Carga inicial: Inicia el dashboard de bienvenida.
        self._cambiar_vista("inicio")

        logger.info("Dashboard inicializado correctamente")

    def _centrar_ventana(self) -> None:
        """
        Calcula las coordenadas necesarias para que la ventana aparezca 
        exactamente en el centro de la resolución actual del monitor.
        """
        self._root.update_idletasks()
        # winfo_screenwidth(): Obtiene el ancho total del monitor del usuario.
        x = (self._root.winfo_screenwidth() - VENTANA_ANCHO) // 2
        # winfo_screenheight(): Obtiene el alto total del monitor del usuario.
        y = (self._root.winfo_screenheight() - VENTANA_ALTO) // 2
        self._root.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}+{x}+{y}")

    def _crear_layout(self) -> None:
        """
        Define la estructura espacial de la aplicación utilizando el gestor de geometría 'pack'.
        Divide la pantalla en: Panel Lateral (Sidebar), Área de Trabajo (Central) y Barra de Estado.
        """
        # Frame contenedor principal
        # Actúa como el lienzo base sobre el que se divide el Sidebar y el Contenido.
        frame_principal = tk.Frame(self._root, bg=COLORES["fondo"])
        frame_principal.pack(fill="both", expand=True)

        # ─── Sidebar ────────────────────────────────────────────────
        # self._sidebar: Panel de navegación izquierdo. Se pasa self._cambiar_vista como callback.
        self._sidebar = Sidebar(
            frame_principal,
            callback=self._cambiar_vista
        )
        self._sidebar.pack(side="left", fill="y", ipadx=10)
        self._sidebar.configure(width=SIDEBAR_ANCHO)
        self._sidebar.pack_propagate(False) # Mantiene el ancho fijo definido en config

        # ─── Área central ───────────────────────────────────────────
        # self._frame_central: Zona donde se cargan las vistas (pestañas) dinámicamente.
        self._frame_central = tk.Frame(frame_principal, bg=COLORES["fondo"])
        self._frame_central.pack(side="right", fill="both", expand=True)

        # ─── Barra de estado inferior ───────────────────────────────
        # barra_estado: Muestra información de versión y un reloj en tiempo real.
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

        # self._label_reloj: Etiqueta dinámica para la hora.
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
        """
        Actualiza la etiqueta de tiempo en la barra de estado.
        Utiliza el método .after() de Tkinter para crear un bucle de refresco 
        sin bloquear el hilo principal de la interfaz.
        """
        # Captura la hora actual del sistema operativo.
        ahora = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self._label_reloj.configure(text=ahora)
        # Se programa la ejecución de este mismo método en 1000ms (recursividad controlada).
        self._root.after(1000, self._actualizar_reloj)

    def _cambiar_vista(self, nombre_modulo: str) -> None:
        """Cambia la vista del área central según el módulo seleccionado.

        Destruye la vista actual y crea la nueva. Captura cualquier error
        para mantener la aplicación estable.

        Args:
            nombre_modulo: Nombre del módulo ("inicio", "clientes", etc.)
        """
        try:
            # LÓGICA DE LIMPIEZA: Elimina la vista anterior de la memoria y del GUI 
            # para evitar fugas de memoria y solapamientos visuales.
            if self._vista_actual is not None:
                self._vista_actual.destroy()
                self._vista_actual = None

            # LÓGICA DE ENRUTAMIENTO (Routing): Instancia la vista correspondiente pasando los controladores.
            # Cada vista recibe el frame central como padre y el controlador respectivo como fuente de datos.
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
        """
        Construye la pantalla de bienvenida (Dashboard). 
        
        Recopila datos estadísticos de todos los controladores para mostrar 
        un resumen ejecutivo del estado del sistema.

        Returns:
            tk.Frame: El frame de Tkinter que contiene el dashboard principal.
        """
        # Frame contenedor local para la vista de inicio
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

        # Recopilación de métricas: Se consultan los controladores para obtener datos reales.
        total_clientes = self._cliente_ctrl.total_clientes
        resumen_servicios = self._servicio_ctrl.obtener_resumen()
        resumen_reservas = self._reserva_ctrl.obtener_resumen()
        total_asesores = self._asesor_ctrl.total_asesores

        # Configuración de los widgets de métricas (Cards):
        # Estructura: (Nombre, Valor, Icono, Color)
        tarjetas_config = [
            ("Clientes Registrados", str(total_clientes), "👥", COLORES["primario"]),
            ("Servicios Disponibles", str(resumen_servicios["total_servicios"]), "🔧", COLORES["acento"]),
            ("Asesores", str(total_asesores), "👨‍💼", "#6a1b9a"),
            ("Reservas Totales", str(resumen_reservas["total"]), "📅", COLORES["exito"]),
            ("Ingresos", f"${resumen_reservas.get('ingresos_totales', 0):,.0f}", "💰", COLORES["advertencia"]),
        ]

        # Renderizado de Tarjetas: Se utiliza .grid() para permitir que las tarjetas se
        # distribuyan equitativamente en el ancho disponible.
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

        # Lista de mapeo entre etiquetas de botón y nombres de módulo internos.
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
            # Se usa un lambda con argumento predeterminado (m=modulo) para capturar el valor actual del bucle.
            btn = ttk.Button(
                frame_btns, text=texto, style="Accent.TButton",
                command=lambda m=modulo: self._navegar_desde_inicio(m)
            )
            btn.pack(side="left", padx=(0, 10), pady=5)

        # ─── Información del sistema ─────────────────────────────────
        frame_info = tk.Frame(frame, bg=COLORES["fondo"])
        frame_info.pack(fill="x", padx=30, pady=(0, 20))

        # Texto consolidado de inventario.
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
        """
        Permite la navegación desde los botones del cuerpo de la página de inicio, 
        asegurando que el estado visual del Sidebar se mantenga sincronizado.
        """
        # Notifica al sidebar que debe marcar como activo el nuevo botón.
        self._sidebar._actualizar_boton_activo(modulo)
        self._cambiar_vista(modulo)

    def ejecutar(self) -> None:
        """
        Arranca el ciclo de eventos de Tkinter (mainloop). 
        
        Este método es bloqueante y mantiene la ventana abierta interactuando 
        con el usuario hasta que se cierra explícitamente.
        """
        logger.info("Iniciando aplicación Software FJ")
        self._root.mainloop()
