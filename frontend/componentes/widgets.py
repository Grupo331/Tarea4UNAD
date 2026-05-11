# =============================================================================
# widgets.py — Widgets reutilizables para la interfaz
# =============================================================================
# Componentes genéricos: tablas con Treeview, formularios, diálogos
# de confirmación, tarjetas de métricas para el dashboard.
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORES, FUENTES


class TablaWidget(tk.Frame):
    """Tabla reutilizable basada en Treeview con scrollbar y búsqueda.

    Attributes:
        _treeview (ttk.Treeview): Widget de tabla.
        _columnas (list): Definición de columnas.
    """

    def __init__(self, parent, columnas: list, **kwargs):
        """Inicializa la tabla.

        Args:
            parent: Widget padre.
            columnas: Lista de tuplas (id, texto, ancho).
                      Ejemplo: [("id", "ID", 80), ("nombre", "Nombre", 200)]
        """
        super().__init__(parent, bg=COLORES["fondo"])
        self._columnas = columnas
        self._crear_tabla()

    def _crear_tabla(self) -> None:
        """Crea el Treeview con scrollbar."""
        # Frame contenedor
        frame_tabla = tk.Frame(self, bg="white", bd=1, relief="solid")
        frame_tabla.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Treeview
        ids_columnas = [c[0] for c in self._columnas]
        self._treeview = ttk.Treeview(
            frame_tabla,
            columns=ids_columnas,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.config(command=self._treeview.yview)

        # Configurar columnas
        for col_id, col_texto, col_ancho in self._columnas:
            self._treeview.heading(col_id, text=col_texto, anchor="w")
            self._treeview.column(col_id, width=col_ancho, anchor="w")

        self._treeview.pack(fill="both", expand=True)

        # Alternar colores de filas
        self._treeview.tag_configure("par", background=COLORES["tabla_row_alt"])
        self._treeview.tag_configure("impar", background="white")

    def cargar_datos(self, datos: list) -> None:
        """Carga datos en la tabla reemplazando los existentes.

        Args:
            datos: Lista de tuplas con los valores de cada fila.
        """
        # Limpiar tabla
        for item in self._treeview.get_children():
            self._treeview.delete(item)

        # Insertar nuevos datos con colores alternos
        for i, fila in enumerate(datos):
            tag = "par" if i % 2 == 0 else "impar"
            self._treeview.insert("", "end", values=fila, tags=(tag,))

    def obtener_seleccion(self):
        """Retorna los valores de la fila seleccionada o None."""
        seleccion = self._treeview.selection()
        if seleccion:
            return self._treeview.item(seleccion[0])["values"]
        return None

    def limpiar(self) -> None:
        """Elimina todas las filas de la tabla."""
        for item in self._treeview.get_children():
            self._treeview.delete(item)

    @property
    def treeview(self) -> ttk.Treeview:
        return self._treeview


class TarjetaMetrica(tk.Frame):
    """Tarjeta visual para mostrar una métrica en el dashboard.

    Muestra un valor numérico grande con una etiqueta descriptiva
    y un ícono opcional.
    """

    def __init__(self, parent, titulo: str, valor: str, icono: str = "📊",
                 color_valor: str = None, **kwargs):
        super().__init__(parent, bg=COLORES["fondo_card"], bd=1,
                         relief="solid", padx=20, pady=15, **kwargs)

        color = color_valor or COLORES["primario"]

        # Ícono
        tk.Label(
            self, text=icono, font=("Segoe UI", 24),
            bg=COLORES["fondo_card"]
        ).pack(anchor="w")

        # Valor
        self._label_valor = tk.Label(
            self, text=valor, font=("Segoe UI", 28, "bold"),
            fg=color, bg=COLORES["fondo_card"]
        )
        self._label_valor.pack(anchor="w", pady=(5, 0))

        # Título
        tk.Label(
            self, text=titulo, font=FUENTES["pequeña"],
            fg=COLORES["texto_claro"], bg=COLORES["fondo_card"]
        ).pack(anchor="w")

    def actualizar_valor(self, nuevo_valor: str) -> None:
        """Actualiza el valor mostrado en la tarjeta."""
        self._label_valor.configure(text=nuevo_valor)


class FormularioDialog(tk.Toplevel):
    """Ventana modal genérica para formularios de creación/edición.

    Proporciona un layout estándar con campos de entrada y
    botones de acción (Guardar/Cancelar).

    Attributes:
        _campos (dict): Mapeo nombre_campo → widget Entry/Combobox.
        _resultado (dict | None): Datos del formulario al guardar.
    """

    def __init__(self, parent, titulo: str, campos: list,
                 callback_guardar=None, datos_iniciales: dict = None):
        """Inicializa el diálogo de formulario.

        Args:
            parent: Ventana padre.
            titulo: Título de la ventana.
            campos: Lista de tuplas (nombre, etiqueta, tipo, opciones).
                    tipo: "text", "number", "combo"
                    opciones: lista de valores para combo, None para otros.
            callback_guardar: Función que recibe el dict de datos al guardar.
            datos_iniciales: Valores iniciales para edición.
        """
        super().__init__(parent)
        self.title(titulo)
        self.configure(bg=COLORES["fondo"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._campos_widgets: dict = {}
        self._callback_guardar = callback_guardar
        self._resultado = None

        self._crear_contenido(titulo, campos, datos_iniciales)
        self._centrar_ventana()

    def _crear_contenido(self, titulo: str, campos: list,
                         datos_iniciales: dict = None) -> None:
        """Crea el layout del formulario."""
        # Header
        header = tk.Frame(self, bg=COLORES["primario"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text=f"  {titulo}", font=FUENTES["subtitulo"],
            fg="white", bg=COLORES["primario"], anchor="w"
        ).pack(fill="x", padx=15, pady=10)

        # Campos
        frame_campos = tk.Frame(self, bg=COLORES["fondo"], padx=25, pady=20)
        frame_campos.pack(fill="both", expand=True)

        for nombre, etiqueta, tipo, opciones in campos:
            # Label
            tk.Label(
                frame_campos, text=etiqueta, font=FUENTES["normal"],
                fg=COLORES["texto"], bg=COLORES["fondo"], anchor="w"
            ).pack(fill="x", pady=(10, 3))

            # Widget de entrada según tipo
            if tipo == "combo" and opciones:
                widget = ttk.Combobox(
                    frame_campos, values=opciones, state="readonly",
                    font=FUENTES["normal"]
                )
                if datos_iniciales and nombre in datos_iniciales:
                    widget.set(datos_iniciales[nombre])
                elif opciones:
                    widget.set(opciones[0])
            else:
                widget = ttk.Entry(frame_campos, font=FUENTES["normal"])
                if datos_iniciales and nombre in datos_iniciales:
                    widget.insert(0, str(datos_iniciales[nombre]))

            widget.pack(fill="x", ipady=5)
            self._campos_widgets[nombre] = widget

        # Botones
        frame_botones = tk.Frame(self, bg=COLORES["fondo"], pady=15)
        frame_botones.pack(fill="x", padx=25)

        ttk.Button(
            frame_botones, text="Cancelar",
            command=self.destroy
        ).pack(side="right", padx=(10, 0))

        ttk.Button(
            frame_botones, text="💾 Guardar", style="Primary.TButton",
            command=self._guardar
        ).pack(side="right")

    def _guardar(self) -> None:
        """Recopila los datos y ejecuta el callback."""
        datos = {}
        for nombre, widget in self._campos_widgets.items():
            if isinstance(widget, ttk.Combobox):
                datos[nombre] = widget.get()
            else:
                datos[nombre] = widget.get().strip()

        # Validar que no haya campos vacíos
        vacios = [n for n, v in datos.items() if not v]
        if vacios:
            messagebox.showwarning(
                "Campos vacíos",
                f"Por favor complete los campos: {', '.join(vacios)}",
                parent=self
            )
            return

        self._resultado = datos
        if self._callback_guardar:
            self._callback_guardar(datos)
        self.destroy()

    def _centrar_ventana(self) -> None:
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        ancho = max(self.winfo_width(), 420)
        alto = max(self.winfo_height(), 300)
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    @property
    def resultado(self):
        return self._resultado
