# =============================================================================
# asesor_controller.py — Controlador de operaciones sobre Asesores
# =============================================================================
# Gestiona la lista de asesores en memoria y expone operaciones CRUD.
# =============================================================================

from backend.models.asesor import Asesor
from backend.exceptions.excepciones import (
    ValidacionError, EntidadNoEncontradaError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("controllers.asesor")


class AsesorNoEncontradoError(EntidadNoEncontradaError):
    """El asesor buscado no existe en el sistema."""

    def __init__(self, identificador: str = ""):
        super().__init__("Asesor no encontrado", identificador)
        self.codigo = "ERR_ASESOR_NO_ENCONTRADO"


class AsesorController:
    """Controlador que gestiona las operaciones CRUD sobre asesores.

    Mantiene una lista en memoria de todos los asesores registrados
    y proporciona métodos para crear, buscar, actualizar y eliminar.

    Attributes:
        _asesores (list[Asesor]): Lista de asesores registrados.
    """

    def __init__(self):
        self._asesores: list = []

    @property
    def asesores(self) -> list:
        """Lista de todos los asesores (copia para seguridad)."""
        return self._asesores.copy()

    @property
    def total_asesores(self) -> int:
        return len(self._asesores)

    def crear_asesor(self, nombre: str, cedula: str,
                     especialidad: str = "") -> Asesor:
        """Crea un nuevo asesor con validación completa.

        Args:
            nombre: Nombre completo.
            cedula: Documento de identidad.
            especialidad: Área de especialidad (opcional).

        Returns:
            El asesor creado.

        Raises:
            ValidacionError: Si los datos son inválidos.
            OperacionError: Si la cédula ya está registrada.
        """
        operacion = "crear_asesor"
        try:
            # Verificar que la cédula no esté duplicada
            cedula_limpia = cedula.strip()
            for a in self._asesores:
                if a.cedula == cedula_limpia:
                    raise OperacionError(
                        f"Ya existe un asesor con cédula {cedula_limpia}",
                        operacion
                    )

            asesor = Asesor(nombre, cedula, especialidad)
            self._asesores.append(asesor)
            return asesor

        except (ValidacionError, OperacionError):
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear asesor: {e}")
            raise OperacionError(
                f"Error inesperado: {e}", operacion
            ) from e
        finally:
            logger.info(f"[FINALLY] Operación '{operacion}' finalizada")

    def buscar_por_id(self, asesor_id: str) -> Asesor:
        """Busca un asesor por su ID.

        Raises:
            AsesorNoEncontradoError: Si no se encuentra.
        """
        for asesor in self._asesores:
            if asesor.id == asesor_id:
                return asesor
        raise AsesorNoEncontradoError(asesor_id)

    def buscar_por_cedula(self, cedula: str) -> Asesor:
        """Busca un asesor por su cédula.

        Raises:
            AsesorNoEncontradoError: Si no se encuentra.
        """
        cedula = cedula.strip()
        for asesor in self._asesores:
            if asesor.cedula == cedula:
                return asesor
        raise AsesorNoEncontradoError(cedula)

    def buscar_por_nombre(self, nombre: str) -> list:
        """Busca asesores cuyo nombre contenga el texto dado."""
        nombre_lower = nombre.lower()
        return [a for a in self._asesores if nombre_lower in a.nombre.lower()]

    def buscar_por_especialidad(self, especialidad: str) -> list:
        """Busca asesores por especialidad."""
        esp_lower = especialidad.lower()
        return [a for a in self._asesores if a.especialidad == esp_lower]

    def actualizar_asesor(self, asesor_id: str, **kwargs) -> Asesor:
        """Actualiza los datos de un asesor existente.

        Args:
            asesor_id: ID del asesor a actualizar.
            **kwargs: Campos a actualizar (nombre, especialidad).

        Returns:
            El asesor actualizado.

        Raises:
            AsesorNoEncontradoError: Si no se encuentra.
            ValidacionError: Si los nuevos datos son inválidos.
        """
        asesor = self.buscar_por_id(asesor_id)

        try:
            if "nombre" in kwargs and kwargs["nombre"]:
                asesor.nombre = kwargs["nombre"]
            if "especialidad" in kwargs:
                asesor.especialidad = kwargs["especialidad"]
            logger.info(f"Asesor actualizado: {asesor.nombre} (ID: {asesor_id})")
        except ValidacionError:
            raise
        except Exception as e:
            raise ValidacionError(
                f"Error al actualizar asesor: {e}", ""
            ) from e

        return asesor

    def eliminar_asesor(self, asesor_id: str) -> Asesor:
        """Elimina un asesor del sistema.

        Args:
            asesor_id: ID del asesor a eliminar.

        Returns:
            El asesor eliminado.

        Raises:
            AsesorNoEncontradoError: Si no se encuentra.
        """
        for i, asesor in enumerate(self._asesores):
            if asesor.id == asesor_id:
                eliminado = self._asesores.pop(i)
                logger.info(f"Asesor eliminado: {eliminado.nombre} (ID: {asesor_id})")
                return eliminado
        raise AsesorNoEncontradoError(asesor_id)

    def obtener_nombres_asesores(self) -> list:
        """Retorna lista de nombres para usar en combos de selección."""
        return [f"{a.nombre} ({a.cedula})" for a in self._asesores]

    def obtener_mapa_asesores(self) -> dict:
        """Retorna mapeo display_name → Asesor para selección en combos."""
        return {
            f"{a.nombre} ({a.cedula})": a for a in self._asesores
        }
