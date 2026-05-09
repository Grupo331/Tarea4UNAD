# =============================================================================
# catalogo.py — Catálogos en memoria para gestión dinámica
# =============================================================================
# Permite crear y eliminar tipos de equipos, áreas de asesoría y salas
# sin necesidad de bases de datos. Opera como un registro centralizado.
# =============================================================================

from config import TARIFAS_SALAS, TARIFAS_EQUIPOS, TARIFAS_ASESORIAS
from backend.models.servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from backend.exceptions.excepciones import (
    ServicioValidacionError, ServicioNoEncontradoError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("models.catalogo")


class CatalogoServicios:
    """Catálogo centralizado de todos los servicios disponibles.

    Gestiona tres listas de servicios (salas, equipos, asesorías)
    y permite operaciones CRUD sobre ellos. Los servicios iniciales
    se cargan desde config.py.

    Attributes:
        _salas (list[ReservaSala]): Lista de salas disponibles.
        _equipos (list[AlquilerEquipo]): Lista de tipos de equipos.
        _asesorias (list[AsesoriaEspecializada]): Lista de asesorías.
    """

    def __init__(self):
        """Inicializa el catálogo con los servicios predeterminados."""
        self._salas: list = []
        self._equipos: list = []
        self._asesorias: list = []
        self._cargar_datos_iniciales()

    def _cargar_datos_iniciales(self) -> None:
        """Carga los servicios iniciales desde la configuración."""
        # Crear salas predeterminadas
        for tipo, datos in TARIFAS_SALAS.items():
            sala = ReservaSala(
                nombre=f"Sala {tipo.capitalize()} A",
                tarifa_hora=datos["hora"],
                tarifa_dia=datos["dia"],
                capacidad=datos["capacidad_default"],
                tipo_sala=tipo
            )
            self._salas.append(sala)

        # Crear equipos predeterminados
        for tipo, datos in TARIFAS_EQUIPOS.items():
            equipo = AlquilerEquipo(
                nombre=f"{tipo.capitalize()}",
                tarifa_hora=datos["dia"] / 8,  # Tarifa hora = dia/8 (jornada)
                tarifa_dia=datos["dia"],
                tipo_equipo=tipo,
                stock_total=datos["stock_inicial"]
            )
            self._equipos.append(equipo)

        # Crear asesorías predeterminadas
        for area, datos in TARIFAS_ASESORIAS.items():
            asesoria = AsesoriaEspecializada(
                nombre=f"Asesoría {area.capitalize()}",
                tarifa_hora=datos["hora"],
                tarifa_dia=datos["dia"],
                area_tematica=area
            )
            self._asesorias.append(asesoria)

        logger.info(
            f"Catálogo inicializado: {len(self._salas)} salas, "
            f"{len(self._equipos)} equipos, {len(self._asesorias)} asesorías"
        )

    # ─── Acceso a servicios ──────────────────────────────────────────────

    @property
    def salas(self) -> list:
        return self._salas.copy()

    @property
    def equipos(self) -> list:
        return self._equipos.copy()

    @property
    def asesorias(self) -> list:
        return self._asesorias.copy()

    @property
    def todos_los_servicios(self) -> list:
        """Retorna todos los servicios en una sola lista."""
        return self._salas + self._equipos + self._asesorias

    # ─── Búsqueda ────────────────────────────────────────────────────────

    def buscar_servicio_por_id(self, servicio_id: str):
        """Busca un servicio por su ID en todas las categorías.

        Args:
            servicio_id: ID del servicio a buscar.

        Returns:
            El servicio encontrado.

        Raises:
            ServicioNoEncontradoError: Si no se encuentra el servicio.
        """
        for servicio in self.todos_los_servicios:
            if servicio.id == servicio_id:
                return servicio
        raise ServicioNoEncontradoError(servicio_id)

    def buscar_servicio_por_nombre(self, nombre: str):
        """Busca servicios cuyo nombre contenga el texto dado."""
        nombre_lower = nombre.lower()
        return [
            s for s in self.todos_los_servicios
            if nombre_lower in s.nombre.lower()
        ]

    # ─── CRUD de Salas ───────────────────────────────────────────────────

    def agregar_sala(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                     capacidad: int, tipo_sala: str) -> ReservaSala:
        """Crea y agrega una nueva sala al catálogo.

        Returns:
            La sala creada.

        Raises:
            ServicioValidacionError: Si los datos son inválidos.
        """
        try:
            sala = ReservaSala(nombre, tarifa_hora, tarifa_dia, capacidad, tipo_sala)
            self._salas.append(sala)
            logger.info(f"Sala agregada al catálogo: {nombre}")
            return sala
        except Exception as e:
            raise OperacionError(f"Error al crear sala: {e}", "agregar_sala") from e

    def eliminar_sala(self, sala_id: str) -> None:
        """Elimina una sala del catálogo por su ID."""
        for i, sala in enumerate(self._salas):
            if sala.id == sala_id:
                eliminada = self._salas.pop(i)
                logger.info(f"Sala eliminada del catálogo: {eliminada.nombre}")
                return
        raise ServicioNoEncontradoError(sala_id)

    # ─── CRUD de Equipos ─────────────────────────────────────────────────

    def agregar_equipo(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                       tipo_equipo: str, stock_total: int = 100) -> AlquilerEquipo:
        """Crea y agrega un nuevo tipo de equipo al catálogo."""
        try:
            equipo = AlquilerEquipo(nombre, tarifa_hora, tarifa_dia, tipo_equipo, stock_total)
            self._equipos.append(equipo)
            logger.info(f"Equipo agregado al catálogo: {nombre}")
            return equipo
        except Exception as e:
            raise OperacionError(f"Error al crear equipo: {e}", "agregar_equipo") from e

    def eliminar_equipo(self, equipo_id: str) -> None:
        """Elimina un tipo de equipo del catálogo por su ID."""
        for i, equipo in enumerate(self._equipos):
            if equipo.id == equipo_id:
                eliminado = self._equipos.pop(i)
                logger.info(f"Equipo eliminado del catálogo: {eliminado.nombre}")
                return
        raise ServicioNoEncontradoError(equipo_id)

    # ─── CRUD de Asesorías ───────────────────────────────────────────────

    def agregar_asesoria(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                         area_tematica: str, asesor=None) -> AsesoriaEspecializada:
        """Crea y agrega una nueva asesoría al catálogo.

        Args:
            asesor: Objeto Asesor a asignar (opcional, puede asignarse después).
        """
        try:
            asesoria = AsesoriaEspecializada(
                nombre, tarifa_hora, tarifa_dia, area_tematica, asesor
            )
            self._asesorias.append(asesoria)
            logger.info(f"Asesoría agregada al catálogo: {nombre}")
            return asesoria
        except Exception as e:
            raise OperacionError(f"Error al crear asesoría: {e}", "agregar_asesoria") from e

    def eliminar_asesoria(self, asesoria_id: str) -> None:
        """Elimina una asesoría del catálogo por su ID."""
        for i, asesoria in enumerate(self._asesorias):
            if asesoria.id == asesoria_id:
                eliminada = self._asesorias.pop(i)
                logger.info(f"Asesoría eliminada del catálogo: {eliminada.nombre}")
                return
        raise ServicioNoEncontradoError(asesoria_id)

    # ─── Estadísticas ────────────────────────────────────────────────────

    def obtener_resumen(self) -> dict:
        """Retorna un resumen del catálogo para el dashboard."""
        return {
            "total_salas": len(self._salas),
            "total_equipos": len(self._equipos),
            "total_asesorias": len(self._asesorias),
            "total_servicios": len(self.todos_los_servicios),
        }
