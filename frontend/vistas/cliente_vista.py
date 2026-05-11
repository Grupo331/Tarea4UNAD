# =============================================================================
# cliente_vista.py — Vista del módulo de Clientes
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORES, FUENTES
from frontend.componentes.widgets import TablaWidget, FormularioDialog
from backend.exceptions.excepciones import ClienteValidacionError, ClienteNoEncontradoError, OperacionError


class ClienteVista(tk.Frame):
    """Vista CRUD para gestión de clientes.

    Muestra una tabla con todos los clientes registrados y botones
    para crear, editar y eliminar.

    Attributes:
        _controller: ClienteController para operaciones de negocio.
        _tabla: TablaWidget para mostrar clientes.
    """

    CAMPOS_FORMULARIO = [
        ("nombre", "Nombre completo", "text", None),
        ("cedula", "Cédula (documento)", "text", None),
        ("telefono", "Teléfono", "text", None),
        ("email", "Correo electrónico", "text", None),
    ]

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=COLORES["fondo"], **kwargs)
        self._controller = controller
        self._crear_widgets()
        self._actualizar_tabla()

    def _crear_widgets(self) -> None:
        """Crea el layout de la vista de clientes."""
        # ─── Header ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORES["fondo"])
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header, text="👥 Gestión de Clientes",
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
            frame_acciones, text="➕ Nuevo Cliente", style="Primary.TButton",
            command=self._abrir_formulario_crear
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_acciones, text="✏️ Editar", style="Accent.TButton",
            command=self._abrir_formulario_editar
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_acciones, text="🗑️ Eliminar", style="Danger.TButton",
            command=self._eliminar_cliente
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_acciones, text="🔄 Actualizar",
            command=self._actualizar_tabla
        ).pack(side="right")

        # ─── Tabla ───────────────────────────────────────────────────
        self._tabla = TablaWidget(self, columnas=[
            ("id", "ID", 80),
            ("nombre", "Nombre", 200),
            ("cedula", "Cédula", 120),
            ("telefono", "Teléfono", 120),
            ("email", "Email", 200),
            ("fecha", "Fecha Registro", 150),
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
        clientes = self._controller.clientes
        datos = [
            (c.id, c.nombre, c.cedula, c.telefono, c.email,
             c.fecha_creacion.strftime("%Y-%m-%d %H:%M"))
            for c in clientes
        ]
        self._tabla.cargar_datos(datos)
        self._label_estado.configure(
            text=f"Total de clientes registrados: {len(clientes)}"
        )

    def _abrir_formulario_crear(self) -> None:
        """Abre el formulario para crear un nuevo cliente."""
        FormularioDialog(
            self.winfo_toplevel(),
            "Nuevo Cliente",
            self.CAMPOS_FORMULARIO,
            callback_guardar=self._guardar_nuevo_cliente
        )

    def _guardar_nuevo_cliente(self, datos: dict) -> None:
        """Callback del formulario para crear cliente."""
        try:
            self._controller.crear_cliente(
                datos["nombre"], datos["cedula"],
                datos["telefono"], datos["email"]
            )
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", "Cliente creado exitosamente.")
        except (ClienteValidacionError, OperacionError) as e:
            messagebox.showerror("Error", str(e))

    def _abrir_formulario_editar(self) -> None:
        """Abre el formulario para editar el cliente seleccionado."""
        seleccion = self._tabla.obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Selección", "Seleccione un cliente para editar.")
            return

        cliente_id = str(seleccion[0])
        try:
            cliente = self._controller.buscar_por_id(cliente_id)
            datos_iniciales = {
                "nombre": cliente.nombre,
                "cedula": cliente.cedula,
                "telefono": cliente.telefono,
                "email": cliente.email,
            }
            # Campos sin cédula (no editable)
            campos_editar = [
                ("nombre", "Nombre completo", "text", None),
                ("telefono", "Teléfono", "text", None),
                ("email", "Correo electrónico", "text", None),
            ]
            FormularioDialog(
                self.winfo_toplevel(),
                "Editar Cliente",
                campos_editar,
                callback_guardar=lambda d: self._guardar_edicion(cliente_id, d),
                datos_iniciales=datos_iniciales
            )
        except ClienteNoEncontradoError as e:
            messagebox.showerror("Error", str(e))

    def _guardar_edicion(self, cliente_id: str, datos: dict) -> None:
        """Callback del formulario para editar cliente."""
        try:
            self._controller.actualizar_cliente(cliente_id, **datos)
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", "Cliente actualizado exitosamente.")
        except (ClienteValidacionError, ClienteNoEncontradoError) as e:
            messagebox.showerror("Error", str(e))

    def _eliminar_cliente(self) -> None:
        """Elimina el cliente seleccionado con confirmación."""
        seleccion = self._tabla.obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Selección", "Seleccione un cliente para eliminar.")
            return

        confirmado = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar al cliente '{seleccion[1]}'?"
        )
        if confirmado:
            try:
                self._controller.eliminar_cliente(str(seleccion[0]))
                self._actualizar_tabla()
                messagebox.showinfo("Éxito", "Cliente eliminado exitosamente.")
            except ClienteNoEncontradoError as e:
                messagebox.showerror("Error", str(e))

    def _buscar(self, event=None) -> None:
        """Filtra la tabla por nombre."""
        texto = self._entry_busqueda.get().strip()
        if texto and texto != "Buscar por nombre...":
            resultados = self._controller.buscar_por_nombre(texto)
            datos = [
                (c.id, c.nombre, c.cedula, c.telefono, c.email,
                 c.fecha_creacion.strftime("%Y-%m-%d %H:%M"))
                for c in resultados
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
