# =============================================================================
# reserva_vista.py — Vista del módulo de Reservas
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORES, FUENTES, IVA_DEFAULT
from frontend.componentes.widgets import TablaWidget
from backend.models.reserva import EstadoReserva
from backend.models.servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from backend.exceptions.excepciones import (
    ReservaValidacionError, DisponibilidadError, TransicionEstadoError,
    SoftwareFJError
)


class ReservaVista(tk.Frame):
    """Vista para crear y gestionar reservas.

    Layout dividido: formulario de nueva reserva a la izquierda,
    tabla de reservas existentes a la derecha.
    """

    def __init__(self, parent, reserva_controller, cliente_controller,
                 servicio_controller, **kwargs):
        super().__init__(parent, bg=COLORES["fondo"], **kwargs)
        self._reserva_ctrl = reserva_controller
        self._cliente_ctrl = cliente_controller
        self._servicio_ctrl = servicio_controller
        self._crear_widgets()
        self._actualizar_tabla()

    def _crear_widgets(self) -> None:
        # Header
        header = tk.Frame(self, bg=COLORES["fondo"])
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(
            header, text="📅 Gestión de Reservas",
            font=FUENTES["titulo"], fg=COLORES["texto"], bg=COLORES["fondo"]
        ).pack(side="left")

        # Layout horizontal: formulario + tabla
        contenedor = tk.Frame(self, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ─── Panel izquierdo: Formulario de nueva reserva ────────────
        frame_form = tk.LabelFrame(
            contenedor, text=" Nueva Reserva ",
            font=FUENTES["subtitulo"], fg=COLORES["primario"],
            bg=COLORES["fondo_card"], padx=15, pady=10, bd=1, relief="solid"
        )
        frame_form.pack(side="left", fill="y", padx=(0, 10))

        # Cliente
        tk.Label(frame_form, text="Cliente (cédula):", font=FUENTES["normal"],
                 bg=COLORES["fondo_card"]).pack(anchor="w", pady=(5, 2))
        self._entry_cedula = ttk.Entry(frame_form, font=FUENTES["normal"], width=25)
        self._entry_cedula.pack(fill="x", ipady=4)

        # Servicio
        tk.Label(frame_form, text="Servicio:", font=FUENTES["normal"],
                 bg=COLORES["fondo_card"]).pack(anchor="w", pady=(10, 2))
        self._combo_servicio = ttk.Combobox(
            frame_form, font=FUENTES["normal"], state="readonly", width=23
        )
        self._combo_servicio.pack(fill="x")
        self._combo_servicio.bind("<<ComboboxSelected>>", self._on_servicio_cambio)
        self._actualizar_servicios()

        # Fecha
        tk.Label(frame_form, text="Fecha (AAAA-MM-DD):", font=FUENTES["normal"],
                 bg=COLORES["fondo_card"]).pack(anchor="w", pady=(10, 2))
        self._entry_fecha = ttk.Entry(frame_form, font=FUENTES["normal"], width=25)
        self._entry_fecha.pack(fill="x", ipady=4)

        # Duración
        tk.Label(frame_form, text="Duración:", font=FUENTES["normal"],
                 bg=COLORES["fondo_card"]).pack(anchor="w", pady=(10, 2))
        frame_dur = tk.Frame(frame_form, bg=COLORES["fondo_card"])
        frame_dur.pack(fill="x")
        self._entry_duracion = ttk.Entry(frame_dur, font=FUENTES["normal"], width=10)
        self._entry_duracion.pack(side="left", ipady=4)
        self._combo_unidad = ttk.Combobox(
            frame_dur, values=["hora", "dia"], state="readonly",
            font=FUENTES["normal"], width=8
        )
        self._combo_unidad.set("hora")
        self._combo_unidad.pack(side="left", padx=(5, 0))

        # Frame dinámico para campos adicionales según tipo de servicio
        self._frame_extra = tk.Frame(frame_form, bg=COLORES["fondo_card"])
        self._frame_extra.pack(fill="x", pady=(10, 0))

        # Hora inicio/fin (para salas)
        self._extra_widgets = {}

        # Opciones de costo
        tk.Label(frame_form, text="─── Opciones de costo ───", font=FUENTES["pequeña"],
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_card"]).pack(pady=(15, 5))

        self._var_impuesto = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_form, text=f"Aplicar IVA ({IVA_DEFAULT * 100:.0f}%)",
            variable=self._var_impuesto, font=FUENTES["normal"],
            bg=COLORES["fondo_card"]
        ).pack(anchor="w")

        frame_desc = tk.Frame(frame_form, bg=COLORES["fondo_card"])
        frame_desc.pack(fill="x", pady=(5, 0))
        tk.Label(frame_desc, text="Descuento (%):", font=FUENTES["normal"],
                 bg=COLORES["fondo_card"]).pack(side="left")
        self._entry_descuento = ttk.Entry(frame_desc, font=FUENTES["normal"], width=8)
        self._entry_descuento.insert(0, "0")
        self._entry_descuento.pack(side="left", padx=(5, 0), ipady=3)

        # Botón crear
        ttk.Button(
            frame_form, text="📅 Crear Reserva", style="Primary.TButton",
            command=self._crear_reserva
        ).pack(fill="x", pady=(20, 5))

        # ─── Panel derecho: Tabla de reservas ────────────────────────
        frame_derecho = tk.Frame(contenedor, bg=COLORES["fondo"])
        frame_derecho.pack(side="right", fill="both", expand=True)

        # Botones de estado
        frame_estados = tk.Frame(frame_derecho, bg=COLORES["fondo"])
        frame_estados.pack(fill="x", pady=(0, 10))

        ttk.Button(
            frame_estados, text="▶ Iniciar", style="Accent.TButton",
            command=lambda: self._cambiar_estado("iniciar")
        ).pack(side="left", padx=2)

        ttk.Button(
            frame_estados, text="✅ Completar", style="Success.TButton",
            command=lambda: self._cambiar_estado("completar")
        ).pack(side="left", padx=2)

        ttk.Button(
            frame_estados, text="❌ Cancelar", style="Danger.TButton",
            command=lambda: self._cambiar_estado("cancelar")
        ).pack(side="left", padx=2)

        ttk.Button(
            frame_estados, text="🚫 No Asistió", style="Secondary.TButton",
            command=lambda: self._cambiar_estado("no_asistio")
        ).pack(side="left", padx=2)

        ttk.Button(
            frame_estados, text="🔄 Actualizar", style="Primary.TButton",
            command=self._actualizar_tabla
        ).pack(side="right")

        # Tabla
        self._tabla = TablaWidget(frame_derecho, columnas=[
            ("id", "ID", 70), ("cliente", "Cliente", 140),
            ("servicio", "Servicio", 140), ("fecha", "Fecha", 100),
            ("duracion", "Duración", 80), ("estado", "Estado", 100),
            ("costo", "Costo", 110),
        ])
        self._tabla.pack(fill="both", expand=True)

        # Estado
        self._label_estado = tk.Label(
            frame_derecho, text="", font=FUENTES["pequeña"],
            fg=COLORES["texto_claro"], bg=COLORES["fondo"]
        )
        self._label_estado.pack(fill="x", pady=(5, 0))

    def _actualizar_servicios(self) -> None:
        """Actualiza la lista de servicios en el combobox."""
        servicios = self._servicio_ctrl.obtener_todos()
        self._servicios_map = {}
        nombres = []
        for s in servicios:
            nombre_display = f"{s.nombre} ({s.__class__.__name__})"
            nombres.append(nombre_display)
            self._servicios_map[nombre_display] = s
        self._combo_servicio["values"] = nombres

    def _on_servicio_cambio(self, event=None) -> None:
        """Muestra campos adicionales según el tipo de servicio."""
        for widget in self._frame_extra.winfo_children():
            widget.destroy()
        self._extra_widgets.clear()

        seleccion = self._combo_servicio.get()
        if not seleccion or seleccion not in self._servicios_map:
            return

        servicio = self._servicios_map[seleccion]

        if isinstance(servicio, ReservaSala):
            tk.Label(self._frame_extra, text="Hora inicio (HH:MM):", font=FUENTES["normal"],
                     bg=COLORES["fondo_card"]).pack(anchor="w", pady=(5, 2))
            e1 = ttk.Entry(self._frame_extra, font=FUENTES["normal"], width=10)
            e1.pack(anchor="w", ipady=3)
            self._extra_widgets["hora_inicio"] = e1

            tk.Label(self._frame_extra, text="Hora fin (HH:MM):", font=FUENTES["normal"],
                     bg=COLORES["fondo_card"]).pack(anchor="w", pady=(5, 2))
            e2 = ttk.Entry(self._frame_extra, font=FUENTES["normal"], width=10)
            e2.pack(anchor="w", ipady=3)
            self._extra_widgets["hora_fin"] = e2

        elif isinstance(servicio, AlquilerEquipo):
            tk.Label(self._frame_extra, text="Cantidad de unidades:", font=FUENTES["normal"],
                     bg=COLORES["fondo_card"]).pack(anchor="w", pady=(5, 2))
            e = ttk.Entry(self._frame_extra, font=FUENTES["normal"], width=10)
            e.insert(0, "1")
            e.pack(anchor="w", ipady=3)
            self._extra_widgets["cantidad"] = e

    def _crear_reserva(self) -> None:
        """Crea una nueva reserva con los datos del formulario."""
        try:
            # Obtener cliente
            cedula = self._entry_cedula.get().strip()
            if not cedula:
                messagebox.showwarning("Datos faltantes", "Ingrese la cédula del cliente.")
                return
            cliente = self._cliente_ctrl.buscar_por_cedula(cedula)

            # Obtener servicio
            seleccion = self._combo_servicio.get()
            if not seleccion or seleccion not in self._servicios_map:
                messagebox.showwarning("Datos faltantes", "Seleccione un servicio.")
                return
            servicio = self._servicios_map[seleccion]

            # Datos de la reserva
            fecha = self._entry_fecha.get().strip()
            duracion = float(self._entry_duracion.get().strip())
            unidad = self._combo_unidad.get()

            # Opciones de costo
            impuesto = IVA_DEFAULT if self._var_impuesto.get() else 0.0
            try:
                descuento = float(self._entry_descuento.get().strip()) / 100.0
            except ValueError:
                descuento = 0.0

            # Parámetros adicionales
            kwargs = {}
            for nombre, widget in self._extra_widgets.items():
                valor = widget.get().strip()
                if valor:
                    if nombre == "cantidad":
                        kwargs[nombre] = int(valor)
                    else:
                        kwargs[nombre] = valor

            # Crear reserva via controlador
            reserva = self._reserva_ctrl.crear_reserva(
                cliente, servicio, fecha, duracion, unidad,
                impuesto=impuesto, descuento=descuento, **kwargs
            )

            self._actualizar_tabla()
            self._actualizar_servicios()
            messagebox.showinfo(
                "Reserva Creada",
                f"Reserva [{reserva.id}] creada exitosamente.\n"
                f"Costo total: ${reserva.costo_total:,.0f}\n"
                f"Estado: {reserva.estado.value}"
            )
        except SoftwareFJError as e:
            messagebox.showerror("Error", str(e))
        except ValueError as e:
            messagebox.showerror("Error de datos", f"Dato numérico inválido: {e}")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    def _cambiar_estado(self, accion: str) -> None:
        """Cambia el estado de la reserva seleccionada."""
        sel = self._tabla.obtener_seleccion()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una reserva.")
            return

        reserva_id = str(sel[0])
        try:
            if accion == "iniciar":
                self._reserva_ctrl.iniciar_reserva(reserva_id)
            elif accion == "completar":
                self._reserva_ctrl.completar_reserva(reserva_id)
            elif accion == "cancelar":
                if messagebox.askyesno("Confirmar", "¿Cancelar esta reserva?"):
                    self._reserva_ctrl.cancelar_reserva(reserva_id)
                else:
                    return
            elif accion == "no_asistio":
                self._reserva_ctrl.marcar_no_asistio(reserva_id)

            self._actualizar_tabla()
            self._actualizar_servicios()
            messagebox.showinfo("Éxito", f"Estado actualizado correctamente.")
        except (TransicionEstadoError, SoftwareFJError) as e:
            messagebox.showerror("Error", str(e))

    def _actualizar_tabla(self) -> None:
        """Recarga la tabla de reservas."""
        reservas = self._reserva_ctrl.reservas
        datos = [
            (r.id, r.cliente.nombre, r.servicio.nombre,
             r.fecha_reserva, f"{r.duracion} {r.unidad_duracion}(s)",
             r.estado.value, f"${r.costo_total:,.0f}")
            for r in reservas
        ]
        self._tabla.cargar_datos(datos)

        resumen = self._reserva_ctrl.obtener_resumen()
        self._label_estado.configure(
            text=f"Total: {resumen['total']} | "
                 f"Ingresos: ${resumen.get('ingresos_totales', 0):,.0f}"
        )
