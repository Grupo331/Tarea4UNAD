# =============================================================================
# servicio_vista.py — Vista del módulo de Servicios
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORES, FUENTES
from frontend.componentes.widgets import TablaWidget, FormularioDialog
from backend.exceptions.excepciones import ServicioValidacionError, OperacionError


class ServicioVista(tk.Frame):
    """Vista para gestión de servicios (salas, equipos, asesorías).

    Incluye pestañas (Notebook) para separar los tres tipos de servicio,
    cada uno con su propia tabla y botones CRUD.
    """

    def __init__(self, parent, controller, asesor_ctrl=None, **kwargs):
        super().__init__(parent, bg=COLORES["fondo"], **kwargs)
        self._controller = controller
        self._asesor_ctrl = asesor_ctrl
        self._crear_widgets()
        self._actualizar_todas_las_tablas()

    def _crear_widgets(self) -> None:
        # Header
        header = tk.Frame(self, bg=COLORES["fondo"])
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(
            header, text="🔧 Gestión de Servicios",
            font=FUENTES["titulo"], fg=COLORES["texto"], bg=COLORES["fondo"]
        ).pack(side="left")

        # Notebook con pestañas
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Pestaña Salas
        self._tab_salas = tk.Frame(self._notebook, bg=COLORES["fondo"])
        self._notebook.add(self._tab_salas, text="  🏢 Salas  ")
        self._crear_tab_salas()

        # Pestaña Equipos
        self._tab_equipos = tk.Frame(self._notebook, bg=COLORES["fondo"])
        self._notebook.add(self._tab_equipos, text="  💻 Equipos  ")
        self._crear_tab_equipos()

        # Pestaña Asesorías
        self._tab_asesorias = tk.Frame(self._notebook, bg=COLORES["fondo"])
        self._notebook.add(self._tab_asesorias, text="  📚 Asesorías  ")
        self._crear_tab_asesorias()

    # ─── Tab Salas ───────────────────────────────────────────────────────

    def _crear_tab_salas(self) -> None:
        frame_btn = tk.Frame(self._tab_salas, bg=COLORES["fondo"])
        frame_btn.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            frame_btn, text="➕ Nueva Sala", style="Primary.TButton",
            command=self._crear_sala
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_btn, text="🗑️ Eliminar Sala", style="Danger.TButton",
            command=self._eliminar_sala
        ).pack(side="left")

        self._tabla_salas = TablaWidget(self._tab_salas, columnas=[
            ("id", "ID", 80), ("nombre", "Nombre", 180),
            ("tipo", "Tipo", 120), ("capacidad", "Capacidad", 90),
            ("tarifa_hora", "$/Hora", 100), ("tarifa_dia", "$/Día", 100),
            ("reservas", "Reservas", 80),
        ])
        self._tabla_salas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _crear_sala(self) -> None:
        campos = [
            ("nombre", "Nombre de la sala", "text", None),
            ("tipo_sala", "Tipo de sala", "combo", ["reunión", "capacitación", "coworking"]),
            ("capacidad", "Capacidad (personas)", "number", None),
            ("tarifa_hora", "Tarifa por hora (COP)", "number", None),
            ("tarifa_dia", "Tarifa por día (COP)", "number", None),
        ]
        FormularioDialog(
            self.winfo_toplevel(), "Nueva Sala", campos,
            callback_guardar=self._guardar_sala
        )

    def _guardar_sala(self, datos: dict) -> None:
        try:
            self._controller.crear_sala(
                datos["nombre"], float(datos["tarifa_hora"]),
                float(datos["tarifa_dia"]), int(datos["capacidad"]),
                datos["tipo_sala"]
            )
            self._actualizar_tabla_salas()
            messagebox.showinfo("Éxito", "Sala creada exitosamente.")
        except (ServicioValidacionError, OperacionError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def _eliminar_sala(self) -> None:
        sel = self._tabla_salas.obtener_seleccion()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una sala.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar sala '{sel[1]}'?"):
            try:
                self._controller.eliminar_sala(str(sel[0]))
                self._actualizar_tabla_salas()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _actualizar_tabla_salas(self) -> None:
        salas = self._controller.obtener_salas()
        datos = [
            (s.id, s.nombre, s.tipo_sala, s.capacidad,
             f"${s.tarifa_hora:,.0f}", f"${s.tarifa_dia:,.0f}",
             len(s.reservas_horario))
            for s in salas
        ]
        self._tabla_salas.cargar_datos(datos)

    # ─── Tab Equipos ─────────────────────────────────────────────────────

    def _crear_tab_equipos(self) -> None:
        frame_btn = tk.Frame(self._tab_equipos, bg=COLORES["fondo"])
        frame_btn.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            frame_btn, text="➕ Nuevo Equipo", style="Primary.TButton",
            command=self._crear_equipo
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_btn, text="🗑️ Eliminar Equipo", style="Danger.TButton",
            command=self._eliminar_equipo
        ).pack(side="left")

        self._tabla_equipos = TablaWidget(self._tab_equipos, columnas=[
            ("id", "ID", 80), ("nombre", "Nombre", 150),
            ("tipo", "Tipo", 120), ("stock_disp", "Disponible", 90),
            ("stock_total", "Stock Total", 90),
            ("tarifa_dia", "$/Día", 100),
        ])
        self._tabla_equipos.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _crear_equipo(self) -> None:
        campos = [
            ("nombre", "Nombre del equipo", "text", None),
            ("tipo_equipo", "Tipo de equipo", "text", None),
            ("tarifa_dia", "Tarifa por día (COP)", "number", None),
            ("stock", "Stock total", "number", None),
        ]
        FormularioDialog(
            self.winfo_toplevel(), "Nuevo Equipo", campos,
            callback_guardar=self._guardar_equipo
        )

    def _guardar_equipo(self, datos: dict) -> None:
        try:
            tarifa_dia = float(datos["tarifa_dia"])
            self._controller.crear_equipo(
                datos["nombre"], tarifa_dia / 8, tarifa_dia,
                datos["tipo_equipo"], int(datos["stock"])
            )
            self._actualizar_tabla_equipos()
            messagebox.showinfo("Éxito", "Equipo creado exitosamente.")
        except (ServicioValidacionError, OperacionError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def _eliminar_equipo(self) -> None:
        sel = self._tabla_equipos.obtener_seleccion()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione un equipo.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar equipo '{sel[1]}'?"):
            try:
                self._controller.eliminar_equipo(str(sel[0]))
                self._actualizar_tabla_equipos()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _actualizar_tabla_equipos(self) -> None:
        equipos = self._controller.obtener_equipos()
        datos = [
            (e.id, e.nombre, e.tipo_equipo, e.stock_disponible,
             e.stock_total, f"${e.tarifa_dia:,.0f}")
            for e in equipos
        ]
        self._tabla_equipos.cargar_datos(datos)

    # ─── Tab Asesorías ───────────────────────────────────────────────────

    def _crear_tab_asesorias(self) -> None:
        frame_btn = tk.Frame(self._tab_asesorias, bg=COLORES["fondo"])
        frame_btn.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            frame_btn, text="➕ Nueva Asesoría", style="Primary.TButton",
            command=self._crear_asesoria
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_btn, text="👨‍💼 Asignar Asesor", style="Accent.TButton",
            command=self._asignar_asesor
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_btn, text="🚫 Remover Asesor", style="Secondary.TButton",
            command=self._remover_asesor
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_btn, text="🗑️ Eliminar Asesoría", style="Danger.TButton",
            command=self._eliminar_asesoria
        ).pack(side="left")

        self._tabla_asesorias = TablaWidget(self._tab_asesorias, columnas=[
            ("id", "ID", 80), ("nombre", "Nombre", 170),
            ("area", "Área", 100), ("asesor", "Asesor Asignado", 180),
            ("tarifa_hora", "$/Hora", 100), ("tarifa_dia", "$/Día", 100),
        ])
        self._tabla_asesorias.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _crear_asesoria(self) -> None:
        campos = [
            ("nombre", "Nombre de la asesoría", "text", None),
            ("area_tematica", "Área temática", "combo", ["legal", "contable", "técnica"]),
            ("tarifa_hora", "Tarifa por hora (COP)", "number", None),
            ("tarifa_dia", "Tarifa por día (COP)", "number", None),
        ]
        FormularioDialog(
            self.winfo_toplevel(), "Nueva Asesoría", campos,
            callback_guardar=self._guardar_asesoria
        )

    def _guardar_asesoria(self, datos: dict) -> None:
        try:
            self._controller.crear_asesoria(
                datos["nombre"], float(datos["tarifa_hora"]),
                float(datos["tarifa_dia"]), datos["area_tematica"]
            )
            self._actualizar_tabla_asesorias()
            messagebox.showinfo("Éxito", "Asesoría creada exitosamente.\n"
                               "Use 'Asignar Asesor' para vincular un asesor.")
        except (ServicioValidacionError, OperacionError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def _asignar_asesor(self) -> None:
        """Abre un diálogo para asignar un asesor a la asesoría seleccionada.
        Filtra los asesores disponibles por la especialidad de la asesoría."""
        sel = self._tabla_asesorias.obtener_seleccion()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una asesoría para asignar un asesor.")
            return

        if self._asesor_ctrl is None:
            messagebox.showwarning("Error", "El controlador de asesores no está disponible.")
            return

        asesoria_id = str(sel[0])
        area_asesoria = str(sel[2]).lower()  # Área temática de la asesoría

        try:
            asesoria = self._controller.buscar_por_id(asesoria_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Filtrar asesores por especialidad
        asesores_filtrados = self._asesor_ctrl.buscar_por_especialidad(area_asesoria)
        # También incluir asesores sin especialidad definida
        asesores_sin_esp = [a for a in self._asesor_ctrl.asesores if not a.especialidad]
        asesores_disponibles = asesores_filtrados + asesores_sin_esp

        if not asesores_disponibles:
            messagebox.showinfo(
                "Sin asesores disponibles",
                f"No hay asesores con especialidad '{area_asesoria}' registrados.\n"
                f"Vaya a 'Asesores' en el menú lateral para crear uno."
            )
            return

        # Crear ventana de selección
        ventana = tk.Toplevel(self.winfo_toplevel())
        ventana.title(f"Asignar Asesor a: {asesoria.nombre}")
        ventana.configure(bg=COLORES["fondo"])
        ventana.resizable(False, False)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        # Header
        header = tk.Frame(ventana, bg=COLORES["primario"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text=f"  Asignar Asesor ({area_asesoria.capitalize()})",
            font=FUENTES["subtitulo"], fg="white", bg=COLORES["primario"]
        ).pack(fill="x", padx=15, pady=10)

        # Info
        frame_info = tk.Frame(ventana, bg=COLORES["fondo"], padx=20, pady=10)
        frame_info.pack(fill="x")
        tk.Label(
            frame_info,
            text=f"Asesoría: {asesoria.nombre}\n"
                 f"Área: {area_asesoria.capitalize()}\n"
                 f"Asesor actual: {asesoria.asesor_nombre}",
            font=FUENTES["normal"], fg=COLORES["texto"], bg=COLORES["fondo"],
            justify="left"
        ).pack(anchor="w")

        # Lista de asesores disponibles
        tk.Label(
            frame_info, text="\nSeleccione un asesor:",
            font=FUENTES["normal"], fg=COLORES["texto"], bg=COLORES["fondo"]
        ).pack(anchor="w", pady=(10, 5))

        mapa_asesores = {}
        nombres_display = []
        for a in asesores_disponibles:
            esp_txt = f" [{a.especialidad}]" if a.especialidad else " [General]"
            display = f"{a.nombre} (Céd: {a.cedula}){esp_txt}"
            nombres_display.append(display)
            mapa_asesores[display] = a

        combo_asesor = ttk.Combobox(
            frame_info, values=nombres_display, state="readonly",
            font=FUENTES["normal"], width=40
        )
        combo_asesor.pack(fill="x", ipady=4)
        if nombres_display:
            combo_asesor.set(nombres_display[0])

        # Botones
        frame_btns = tk.Frame(ventana, bg=COLORES["fondo"], pady=15)
        frame_btns.pack(fill="x", padx=20)

        def confirmar():
            seleccion = combo_asesor.get()
            if seleccion and seleccion in mapa_asesores:
                asesor_obj = mapa_asesores[seleccion]
                try:
                    asesoria.asignar_asesor(asesor_obj)
                    self._actualizar_tabla_asesorias()
                    messagebox.showinfo(
                        "Éxito",
                        f"Asesor '{asesor_obj.nombre}' asignado a '{asesoria.nombre}'."
                    )
                    ventana.destroy()
                except ServicioValidacionError as e:
                    messagebox.showerror("Error de validación", str(e))

        ttk.Button(
            frame_btns, text="Cancelar", command=ventana.destroy
        ).pack(side="right", padx=(10, 0))

        ttk.Button(
            frame_btns, text="✅ Asignar", style="Primary.TButton",
            command=confirmar
        ).pack(side="right")

        # Centrar ventana
        ventana.update_idletasks()
        ancho = max(ventana.winfo_width(), 480)
        alto = max(ventana.winfo_height(), 350)
        x = (ventana.winfo_screenwidth() - ancho) // 2
        y = (ventana.winfo_screenheight() - alto) // 2
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _remover_asesor(self) -> None:
        """Remueve el asesor asignado de la asesoría seleccionada."""
        sel = self._tabla_asesorias.obtener_seleccion()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una asesoría.")
            return

        asesoria_id = str(sel[0])
        try:
            asesoria = self._controller.buscar_por_id(asesoria_id)
            if asesoria.asesor_nombre == "Sin asignar":
                messagebox.showinfo("Info", "Esta asesoría no tiene asesor asignado.")
                return

            if messagebox.askyesno(
                "Confirmar",
                f"¿Remover al asesor '{asesoria.asesor_nombre}' de '{asesoria.nombre}'?"
            ):
                asesoria.remover_asesor()
                self._actualizar_tabla_asesorias()
                messagebox.showinfo("Éxito", "Asesor removido exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar_asesoria(self) -> None:
        sel = self._tabla_asesorias.obtener_seleccion()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una asesoría.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar asesoría '{sel[1]}'?"):
            try:
                self._controller.eliminar_asesoria(str(sel[0]))
                self._actualizar_tabla_asesorias()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _actualizar_tabla_asesorias(self) -> None:
        asesorias = self._controller.obtener_asesorias()
        datos = [
            (a.id, a.nombre, a.area_tematica, a.asesor_nombre,
             f"${a.tarifa_hora:,.0f}", f"${a.tarifa_dia:,.0f}")
            for a in asesorias
        ]
        self._tabla_asesorias.cargar_datos(datos)

    # ─── Actualizar todo ─────────────────────────────────────────────────

    def _actualizar_todas_las_tablas(self) -> None:
        self._actualizar_tabla_salas()
        self._actualizar_tabla_equipos()
        self._actualizar_tabla_asesorias()
