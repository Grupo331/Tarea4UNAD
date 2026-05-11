# =============================================================================
# log_vista.py — Visor de logs en tiempo real
# =============================================================================

import os
import tkinter as tk
from tkinter import ttk
from config import COLORES, FUENTES, LOG_FILE


class LogVista(tk.Frame):
    """Visor de logs en tiempo real dentro del dashboard.

    Lee el archivo app.log y lo muestra en un widget Text con
    resaltado de colores según nivel de log.
    """

    # Colores por nivel de log
    COLORES_NIVEL = {
        "DEBUG": "#9e9e9e",
        "INFO": "#2196f3",
        "WARNING": "#ff9800",
        "ERROR": "#f44336",
        "CRITICAL": "#d32f2f",
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORES["fondo"], **kwargs)
        self._crear_widgets()
        self._cargar_logs()

    def _crear_widgets(self) -> None:
        # Header
        header = tk.Frame(self, bg=COLORES["fondo"])
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header, text="📋 Visor de Logs",
            font=FUENTES["titulo"], fg=COLORES["texto"], bg=COLORES["fondo"]
        ).pack(side="left")

        ttk.Button(
            header, text="🔄 Actualizar",
            command=self._cargar_logs
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            header, text="🗑️ Limpiar Vista",
            command=self._limpiar_vista
        ).pack(side="right")

        # Filtro por nivel
        frame_filtro = tk.Frame(self, bg=COLORES["fondo"])
        frame_filtro.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(frame_filtro, text="Filtrar por nivel:", font=FUENTES["normal"],
                 bg=COLORES["fondo"]).pack(side="left", padx=(0, 5))

        self._combo_filtro = ttk.Combobox(
            frame_filtro,
            values=["TODOS", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            state="readonly", font=FUENTES["normal"], width=12
        )
        self._combo_filtro.set("TODOS")
        self._combo_filtro.pack(side="left")
        self._combo_filtro.bind("<<ComboboxSelected>>", lambda e: self._cargar_logs())

        # Área de texto con scrollbar
        frame_texto = tk.Frame(self, bg="white", bd=1, relief="solid")
        frame_texto.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        scrollbar = ttk.Scrollbar(frame_texto, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self._texto = tk.Text(
            frame_texto,
            font=FUENTES["monospace"],
            bg="#1e1e1e",  # Fondo oscuro estilo terminal
            fg="#d4d4d4",
            insertbackground="white",
            wrap="word",
            yscrollcommand=scrollbar.set,
            state="disabled",
            padx=10, pady=10
        )
        scrollbar.config(command=self._texto.yview)
        self._texto.pack(fill="both", expand=True)

        # Configurar tags de colores
        for nivel, color in self.COLORES_NIVEL.items():
            self._texto.tag_configure(nivel, foreground=color)

        # Barra de estado
        self._label_estado = tk.Label(
            self, text="", font=FUENTES["pequeña"],
            fg=COLORES["texto_claro"], bg=COLORES["fondo"]
        )
        self._label_estado.pack(fill="x", padx=20, pady=(0, 10))

    def _cargar_logs(self) -> None:
        """Lee el archivo de log y lo muestra en el widget."""
        self._texto.configure(state="normal")
        self._texto.delete("1.0", "end")

        filtro = self._combo_filtro.get()
        lineas_mostradas = 0

        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    lineas = f.readlines()

                # Mostrar las últimas 500 líneas máximo
                lineas = lineas[-500:]

                for linea in lineas:
                    # Determinar nivel
                    nivel_detectado = None
                    for nivel in self.COLORES_NIVEL:
                        if f"[{nivel}]" in linea:
                            nivel_detectado = nivel
                            break

                    # Aplicar filtro
                    if filtro != "TODOS" and nivel_detectado != filtro:
                        continue

                    # Insertar con color
                    tag = nivel_detectado if nivel_detectado else "INFO"
                    self._texto.insert("end", linea, (tag,))
                    lineas_mostradas += 1

                self._label_estado.configure(
                    text=f"Mostrando {lineas_mostradas} de {len(lineas)} líneas | "
                         f"Archivo: {LOG_FILE}"
                )
            else:
                self._texto.insert("end", "No se encontró el archivo de log.\n")
                self._texto.insert("end", f"Ruta esperada: {LOG_FILE}\n")
                self._label_estado.configure(text="Archivo de log no encontrado")

        except Exception as e:
            self._texto.insert("end", f"Error al leer logs: {e}\n", ("ERROR",))
            self._label_estado.configure(text=f"Error: {e}")

        self._texto.configure(state="disabled")
        self._texto.see("end")  # Scroll al final

    def _limpiar_vista(self) -> None:
        """Limpia el contenido del visor (no el archivo)."""
        self._texto.configure(state="normal")
        self._texto.delete("1.0", "end")
        self._texto.configure(state="disabled")
        self._label_estado.configure(text="Vista limpiada")
