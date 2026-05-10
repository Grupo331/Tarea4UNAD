# =============================================================================
# servicio_controller.py — Controlador de operaciones sobre Servicios
# =============================================================================
"""
Módulo controlador para la gestión de Servicios.

Este módulo implementa el patrón Fachada (Facade) sobre la clase CatalogoServicios.
Su propósito es proporcionar una interfaz limpia y unificada a la capa de 
presentación (interfaz gráfica) para consultar, crear y eliminar los distintos 
tipos de servicios (Salas, Equipos y Asesorías) sin exponer la complejidad 
subyacente del catálogo.
"""
# =============================================================================

from backend.models.catalogo import CatalogoServicios
from backend.models.servicio import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from backend.exceptions.excepciones import (
    ServicioValidacionError, ServicioNoEncontradoError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("controllers.servicio")


class ServicioController:
    """
    Controlador que actúa como fachada para gestionar el catálogo de servicios.

    Delega de manera transparente las operaciones CRUD al `CatalogoServicios`,
    centralizando además el manejo de logs y posibles excepciones en el flujo
    hacia la interfaz de usuario.

    Attributes:
        _catalogo (CatalogoServicios): Instancia centralizada del catálogo donde
                                       residen físicamente las colecciones de servicios.
    """

    def __init__(self, catalogo: CatalogoServicios):
        """
        Inicializa el controlador inyectando la dependencia del catálogo.

        Args:
            catalogo (CatalogoServicios): El catálogo central a utilizar.
        """
        self._catalogo = catalogo

    @property
    def catalogo(self) -> CatalogoServicios:
        """
        Obtiene acceso de lectura a la instancia del catálogo inyectado.

        Returns:
            CatalogoServicios: La instancia actual del catálogo de servicios.
        """
        return self._catalogo

    # ─── Consulta ────────────────────────────────────────────────────────

    def obtener_todos(self) -> list:
        """
        Recupera de manera agnóstica todos los servicios registrados.

        Returns:
            list[Servicio]: Lista combinada de todas las salas, equipos y asesorías.
        """
        return self._catalogo.todos_los_servicios

    def obtener_salas(self) -> list:
        """
        Obtiene exclusivamente el subconjunto de salas de reunión/coworking.

        Returns:
            list[ReservaSala]: Lista de salas disponibles en el catálogo.
        """
        return self._catalogo.salas

    def obtener_equipos(self) -> list:
        """
        Obtiene exclusivamente el subconjunto de equipos tecnológicos.

        Returns:
            list[AlquilerEquipo]: Lista de equipos disponibles para alquiler.
        """
        return self._catalogo.equipos

    def obtener_asesorias(self) -> list:
        """
        Obtiene exclusivamente el subconjunto de asesorías especializadas.

        Returns:
            list[AsesoriaEspecializada]: Lista de asesorías disponibles.
        """
        return self._catalogo.asesorias

    def buscar_por_id(self, servicio_id: str) -> Servicio:
        """
        Localiza un servicio específico utilizando su identificador único (UUID).

        Args:
            servicio_id (str): ID interno del servicio buscado.

        Returns:
            Servicio: El objeto del servicio encontrado (sea Sala, Equipo o Asesoría).

        Raises:
            ServicioNoEncontradoError: Si el ID no corresponde a ningún servicio en el catálogo.
        """
        return self._catalogo.buscar_servicio_por_id(servicio_id)

    def buscar_por_nombre(self, nombre: str) -> list:
        """
        Ejecuta una búsqueda parcial e insensible a mayúsculas/minúsculas 
        por el nombre de los servicios.

        Args:
            nombre (str): Subcadena de texto a buscar.

        Returns:
            list[Servicio]: Lista de servicios cuyos nombres contienen la subcadena.
        """
        return self._catalogo.buscar_servicio_por_nombre(nombre)

    # ─── CRUD Salas ──────────────────────────────────────────────────────

    def crear_sala(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                   capacidad: int, tipo_sala: str) -> ReservaSala:
        """
        Crea una nueva sala y la incorpora al catálogo de servicios.

        Args:
            nombre (str): Nombre descriptivo de la sala.
            tarifa_hora (float): Costo fraccional por hora (en COP).
            tarifa_dia (float): Costo fijo por día completo (en COP).
            capacidad (int): Número máximo de personas soportadas.
            tipo_sala (str): Categoría de la sala (e.g., 'Reuniones', 'Coworking').

        Returns:
            ReservaSala: El nuevo objeto sala creado y almacenado.

        Raises:
            OperacionError: Si ocurre un fallo en el proceso de creación.
            ServicioValidacionError: Si los datos provistos son semánticamente inválidos.
        """
        try:
            return self._catalogo.agregar_sala(
                nombre, tarifa_hora, tarifa_dia, capacidad, tipo_sala
            )
        except Exception as e:
            logger.error(f"Error al crear sala: {e}")
            raise

    def eliminar_sala(self, sala_id: str) -> None:
        """
        Elimina permanentemente una sala del catálogo.

        Args:
            sala_id (str): Identificador de la sala a remover.

        Raises:
            ServicioNoEncontradoError: Si el ID provisto no existe.
        """
        self._catalogo.eliminar_sala(sala_id)

    # ─── CRUD Equipos ────────────────────────────────────────────────────

    def crear_equipo(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                     tipo_equipo: str, stock: int = 100) -> AlquilerEquipo:
        """
        Crea un nuevo tipo de equipo tecnológico y lo incorpora al catálogo.

        Args:
            nombre (str): Nombre descriptivo del equipo.
            tarifa_hora (float): Costo fraccional por hora (en COP).
            tarifa_dia (float): Costo fijo por día completo (en COP).
            tipo_equipo (str): Categoría del hardware (e.g., 'Laptop', 'Proyector').
            stock (int, optional): Cantidad inicial de unidades disponibles. Por defecto 100.

        Returns:
            AlquilerEquipo: El nuevo objeto equipo creado y almacenado.

        Raises:
            OperacionError: Si ocurre un fallo en el proceso de creación.
            ServicioValidacionError: Si los datos provistos son inválidos.
        """
        try:
            return self._catalogo.agregar_equipo(
                nombre, tarifa_hora, tarifa_dia, tipo_equipo, stock
            )
        except Exception as e:
            logger.error(f"Error al crear equipo: {e}")
            raise

    def eliminar_equipo(self, equipo_id: str) -> None:
        """
        Elimina permanentemente un equipo del catálogo.

        Args:
            equipo_id (str): Identificador del equipo a remover.

        Raises:
            ServicioNoEncontradoError: Si el ID provisto no existe.
        """
        self._catalogo.eliminar_equipo(equipo_id)

    # ─── CRUD Asesorías ──────────────────────────────────────────────────

    def crear_asesoria(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                       area_tematica: str, asesor=None) -> AsesoriaEspecializada:
        """
        Crea una nueva línea de asesoría especializada en el catálogo.

        Args:
            nombre (str): Nombre del servicio de asesoría.
            tarifa_hora (float): Costo por hora de consultoría (en COP).
            tarifa_dia (float): Costo por día completo de consultoría (en COP).
            area_tematica (str): Disciplina de la asesoría (e.g., 'Legal', 'Técnica').
            asesor (Asesor, optional): Instancia del profesional que brindará 
                                       la asesoría. Puede asignarse posteriormente.

        Returns:
            AsesoriaEspecializada: El nuevo objeto asesoría creado.

        Raises:
            OperacionError: Si ocurre un fallo en el proceso de creación.
            ServicioValidacionError: Si los datos provistos son inválidos.
        """
        try:
            return self._catalogo.agregar_asesoria(
                nombre, tarifa_hora, tarifa_dia, area_tematica, asesor
            )
        except Exception as e:
            logger.error(f"Error al crear asesoría: {e}")
            raise

    def eliminar_asesoria(self, asesoria_id: str) -> None:
        """
        Elimina permanentemente una asesoría del catálogo.

        Args:
            asesoria_id (str): Identificador de la asesoría a remover.

        Raises:
            ServicioNoEncontradoError: Si el ID provisto no existe.
        """
        self._catalogo.eliminar_asesoria(asesoria_id)

    # ─── Estadísticas ────────────────────────────────────────────────────

    def obtener_resumen(self) -> dict:
        """
        Recupera el resumen cuantitativo de los servicios desde el catálogo.
        
        Útil para mostrar tableros de control (dashboards) sin iterar manualmente
        las colecciones.

        Returns:
            dict: Estructura con el conteo de servicios (total, salas, equipos, asesorias).
        """
        return self._catalogo.obtener_resumen()
