# =============================================================================
# servicio_controller.py — Controlador de operaciones sobre Servicios
# =============================================================================
# Delega al CatalogoServicios para CRUD de salas, equipos y asesorías.
# =============================================================================

from backend.models.catalogo import CatalogoServicios
from backend.models.servicio import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from backend.exceptions.excepciones import (
    ServicioValidacionError, ServicioNoEncontradoError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("controllers.servicio")


class ServicioController:
    """Controlador que gestiona el catálogo de servicios.

    Actúa como fachada sobre CatalogoServicios para exponer
    operaciones a la capa de interfaz gráfica.

    Attributes:
        _catalogo (CatalogoServicios): Catálogo centralizado de servicios.
    """

    def __init__(self, catalogo: CatalogoServicios):
        self._catalogo = catalogo

    @property
    def catalogo(self) -> CatalogoServicios:
        return self._catalogo

    # ─── Consulta ────────────────────────────────────────────────────────

    def obtener_todos(self) -> list:
        """Retorna todos los servicios del catálogo."""
        return self._catalogo.todos_los_servicios

    def obtener_salas(self) -> list:
        return self._catalogo.salas

    def obtener_equipos(self) -> list:
        return self._catalogo.equipos

    def obtener_asesorias(self) -> list:
        return self._catalogo.asesorias

    def buscar_por_id(self, servicio_id: str) -> Servicio:
        """Busca un servicio por ID.

        Raises:
            ServicioNoEncontradoError: Si no existe.
        """
        return self._catalogo.buscar_servicio_por_id(servicio_id)

    def buscar_por_nombre(self, nombre: str) -> list:
        """Busca servicios por nombre (parcial)."""
        return self._catalogo.buscar_servicio_por_nombre(nombre)

    # ─── CRUD Salas ──────────────────────────────────────────────────────

    def crear_sala(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                   capacidad: int, tipo_sala: str) -> ReservaSala:
        """Crea una nueva sala en el catálogo.

        Raises:
            OperacionError: Si falla la creación.
        """
        try:
            return self._catalogo.agregar_sala(
                nombre, tarifa_hora, tarifa_dia, capacidad, tipo_sala
            )
        except Exception as e:
            logger.error(f"Error al crear sala: {e}")
            raise

    def eliminar_sala(self, sala_id: str) -> None:
        self._catalogo.eliminar_sala(sala_id)

    # ─── CRUD Equipos ────────────────────────────────────────────────────

    def crear_equipo(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                     tipo_equipo: str, stock: int = 100) -> AlquilerEquipo:
        """Crea un nuevo tipo de equipo.

        Raises:
            OperacionError: Si falla la creación.
        """
        try:
            return self._catalogo.agregar_equipo(
                nombre, tarifa_hora, tarifa_dia, tipo_equipo, stock
            )
        except Exception as e:
            logger.error(f"Error al crear equipo: {e}")
            raise

    def eliminar_equipo(self, equipo_id: str) -> None:
        self._catalogo.eliminar_equipo(equipo_id)

    # ─── CRUD Asesorías ──────────────────────────────────────────────────

    def crear_asesoria(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                       area_tematica: str, asesor=None) -> AsesoriaEspecializada:
        """Crea una nueva asesoría.

        Args:
            asesor: Objeto Asesor a asignar (opcional, puede asignarse después).

        Raises:
            OperacionError: Si falla la creación.
        """
        try:
            return self._catalogo.agregar_asesoria(
                nombre, tarifa_hora, tarifa_dia, area_tematica, asesor
            )
        except Exception as e:
            logger.error(f"Error al crear asesoría: {e}")
            raise

    def eliminar_asesoria(self, asesoria_id: str) -> None:
        self._catalogo.eliminar_asesoria(asesoria_id)

    # ─── Estadísticas ────────────────────────────────────────────────────

    def obtener_resumen(self) -> dict:
        """Resumen del catálogo para el dashboard."""
        return self._catalogo.obtener_resumen()
