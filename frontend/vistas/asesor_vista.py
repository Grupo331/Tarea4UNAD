# =============================================================================
# asesor_vista.py — Vista del módulo de Asesores
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORES, FUENTES
from frontend.componentes.widgets import TablaWidget, FormularioDialog
from backend.exceptions.excepciones import ValidacionError, OperacionError


class AsesorVista(tk.Frame):
    """Vista CRUD para gestión de asesores.

    Muestra una tabla con todos los asesores registrados y botones
    para crear, editar y eliminar.

    Attributes:
        _controller: AsesorController para operaciones de negocio.
        _tabla: TablaWidget para mostrar asesores.
    """

    CAMPOS_FORMULARIO = [
        ("nombre", "Nombre completo", "text", None),
        ("cedula", "Cédula (documento)", "text", None),
        ("especialidad", "Especialidad", "combo", ["legal", "contable", "técnica", ""]),
    ]

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=COLORES["fondo"], **kwargs)
        self._controller = controller
        self._crear_widgets()
        self._actualizar_tabla()

    def _crear_widgets(self) -> None:
        """Crea el layout de la vista de asesores."""
        # ─── Header ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORES["fondo"])
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header, text="👨‍💼 Gestión de Asesores",
            font=FUENTES["titulo"], fg=COLORES["texto"], bg=COLORES["fondo"]
        ).pack(side="left")

        # Barra de búsqueda
        frame_busqueda = tk.Frame(header, bg=COLORES["fondo"])
        frame_busqueda.pack(side="right")

        self._entry_busqueda = ttk.Entry(frame_busqueda, font=FUENTES["normal"], width=25)
        self._entry_busqueda.pack(side="left", padx=(0, 5), ipady=4)
        self._entry_busqueda.insert(0, "Buscar por nombre...")
        self._entry_busqueda.bind("<FocusIn>", self._limpiar_placeholder)
        self._entry_busqueda.bind("<FocusOut>", self._restaurar_placeholder)
        self._entry_busqueda.bind("<KeyRelease>", self._buscar)

        # ─── Botones de acción ───────────────────────────────────────
        frame_acciones = tk.Frame(self, bg=COLORES["fondo"])
        frame_acciones.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Button(
            frame_acciones, text="➕ Nuevo Asesor", style="Primary.TButton",
            command=self._abrir_formulario_crear
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_acciones, text="✏️ Editar", style="Accent.TButton",
            command=self._abrir_formulario_editar
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_acciones, text="🗑️ Eliminar", style="Danger.TButton",
            command=self._eliminar_asesor
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_acciones, text="🔄 Actualizar",
            command=self._actualizar_tabla
        ).pack(side="right")

        # ─── Tabla ───────────────────────────────────────────────────
        self._tabla = TablaWidget(self, columnas=[
            ("id", "ID", 80),
            ("nombre", "Nombre Completo", 220),
            ("cedula", "Cédula", 120),
            ("especialidad", "Especialidad", 130),
            ("fecha_creacion", "Fecha Creación", 150),
            ("fecha_modificacion", "Última Modificación", 160),
        ])
        self._tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ─── Barra de estado ────────────────────────────────────────
        self._label_estado = tk.Label(
            self, text="", font=FUENTES["pequeña"],
            fg=COLORES["texto_claro"], bg=COLORES["fondo"], anchor="w"
        )
        self._label_estado.pack(fill="x", padx=20, pady=(0, 10))

    def _actualizar_tabla(self) -> None:
        """Recarga los datos de la tabla desde el controlador."""
        asesores = self._controller.asesores
        datos = [
            (a.id, a.nombre, a.cedula,
             a.especialidad.capitalize() if a.especialidad else "Sin asignar",
             a.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
             a.fecha_modificacion.strftime("%Y-%m-%d %H:%M"))
            for a in asesores
        ]
        self._tabla.cargar_datos(datos)
        self._label_estado.configure(
            text=f"Total de asesores registrados: {len(asesores)}"
        )

    def _abrir_formulario_crear(self) -> None:
        """Abre el formulario para crear un nuevo asesor."""
        FormularioDialog(
            self.winfo_toplevel(),
            "Nuevo Asesor",
            self.CAMPOS_FORMULARIO,
            callback_guardar=self._guardar_nuevo_asesor
        )

    def _guardar_nuevo_asesor(self, datos: dict) -> None:
        """Callback del formulario para crear asesor."""
        try:
            self._controller.crear_asesor(
                datos["nombre"], datos["cedula"],
                datos.get("especialidad", "")
            )
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", "Asesor creado exitosamente.")
        except (ValidacionError, OperacionError) as e:
            messagebox.showerror("Error", str(e))

    def _abrir_formulario_editar(self) -> None:
        """Abre el formulario para editar el asesor seleccionado."""
        seleccion = self._tabla.obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Selección", "Seleccione un asesor para editar.")
            return

        asesor_id = str(seleccion[0])
        try:
            from backend.controllers.asesor_controller import AsesorNoEncontradoError
            asesor = self._controller.buscar_por_id(asesor_id)
            datos_iniciales = {
                "nombre": asesor.nombre,
                "especialidad": asesor.especialidad.capitalize() if asesor.especialidad else "",
            }
            campos_editar = [
                ("nombre", "Nombre completo", "text", None),
                ("especialidad", "Especialidad", "combo",
                 ["legal", "contable", "técnica", ""]),
            ]
            FormularioDialog(
                self.winfo_toplevel(),
                "Editar Asesor",
                campos_editar,
                callback_guardar=lambda d: self._guardar_edicion(asesor_id, d),
                datos_iniciales=datos_iniciales
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _guardar_edicion(self, asesor_id: str, datos: dict) -> None:
        """Callback del formulario para editar asesor."""
        try:
            self._controller.actualizar_asesor(asesor_id, **datos)
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", "Asesor actualizado exitosamente.")
        except (ValidacionError, OperacionError) as e:
            messagebox.showerror("Error", str(e))

    def _eliminar_asesor(self) -> None:
        """Elimina el asesor seleccionado con confirmación."""
        seleccion = self._tabla.obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Selección", "Seleccione un asesor para eliminar.")
            return

        confirmado = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar al asesor '{seleccion[1]}'?"
        )
        if confirmado:
            try:
                self._controller.eliminar_asesor(str(seleccion[0]))
                self._actualizar_tabla()
                messagebox.showinfo("Éxito", "Asesor eliminado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _buscar(self, event=None) -> None:
        """Filtra la tabla por nombre."""
        texto = self._entry_busqueda.get().strip()
        if texto and texto != "Buscar por nombre...":
            resultados = self._controller.buscar_por_nombre(texto)
            datos = [
                (a.id, a.nombre, a.cedula,
                 a.especialidad.capitalize() if a.especialidad else "Sin asignar",
                 a.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
                 a.fecha_modificacion.strftime("%Y-%m-%d %H:%M"))
                for a in resultados
            ]
            self._tabla.cargar_datos(datos)
            self._label_estado.configure(text=f"Resultados: {len(resultados)}")
        else:
            self._actualizar_tabla()

    def _limpiar_placeholder(self, event) -> None:
        if self._entry_busqueda.get() == "Buscar por nombre...":
            self._entry_busqueda.delete(0, "end")

    def _restaurar_placeholder(self, event) -> None:
        if not self._entry_busqueda.get().strip():
            self._entry_busqueda.insert(0, "Buscar por nombre...")
