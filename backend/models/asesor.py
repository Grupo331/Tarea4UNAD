# =============================================================================
# asesor.py — Modelo de Asesor con encapsulación y validación
# =============================================================================
# Representa un asesor que puede ser asignado a asesorías especializadas.
# Incluye fecha de creación y de última modificación.
# =============================================================================

from datetime import datetime
from backend.models.base import EntidadBase
from backend.exceptions.excepciones import ValidacionError
from backend.utils.validadores import validar_no_vacio, validar_cedula
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("models.asesor")


class Asesor(EntidadBase):
    """Representa un asesor del sistema Software FJ.

    Puede ser asignado a una o más asesorías especializadas.
    Registra fecha de creación y fecha de última modificación.

    Attributes:
        _nombre (str): Nombre completo del asesor.
        _cedula (str): Documento de identidad (8-12 dígitos).
        _especialidad (str): Área de especialidad (legal, contable, técnica).
        _fecha_modificacion (datetime): Última vez que se modificaron sus datos.
    """

    ESPECIALIDADES = ["legal", "contable", "técnica"]

    def __init__(self, nombre: str, cedula: str, especialidad: str = ""):
        """Inicializa un nuevo asesor con validación inmediata.

        Args:
            nombre: Nombre completo del asesor.
            cedula: Documento de identidad.
            especialidad: Área de especialidad (opcional).

        Raises:
            ValidacionError: Si algún dato no es válido.
        """
        super().__init__()
        # Asignar vía properties para activar validaciones
        self.nombre = nombre
        self.cedula = cedula
        self._especialidad = especialidad.strip().lower() if especialidad else ""
        self._fecha_modificacion: datetime = self._fecha_creacion
        logger.info(
            f"Asesor creado: {self._nombre} (Cédula: {self._cedula}, ID: {self._id})"
        )

    # ─── Properties con validación en setter ─────────────────────────────

    @property
    def nombre(self) -> str:
        """Nombre completo del asesor."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        try:
            self._nombre = validar_no_vacio(valor, "nombre")
        except Exception as e:
            raise ValidacionError(f"Error en nombre del asesor: {e}", "nombre") from e
        self._actualizar_fecha_modificacion()

    @property
    def cedula(self) -> str:
        """Documento de identidad del asesor."""
        return self._cedula

    @cedula.setter
    def cedula(self, valor: str) -> None:
        try:
            self._cedula = validar_cedula(valor)
        except Exception as e:
            raise ValidacionError(f"Error en cédula del asesor: {e}", "cédula") from e
        self._actualizar_fecha_modificacion()

    @property
    def especialidad(self) -> str:
        """Área de especialidad del asesor."""
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor: str) -> None:
        self._especialidad = valor.strip().lower() if valor else ""
        self._actualizar_fecha_modificacion()

    @property
    def fecha_modificacion(self) -> datetime:
        """Fecha y hora de la última modificación (solo lectura)."""
        return self._fecha_modificacion

    # ─── Métodos privados ────────────────────────────────────────────────

    def _actualizar_fecha_modificacion(self) -> None:
        """Actualiza la fecha de modificación al momento actual."""
        # Solo actualizar si el atributo ya existe (evitar durante __init__)
        if hasattr(self, '_fecha_modificacion'):
            self._fecha_modificacion = datetime.now()

    # ─── Métodos abstractos implementados ────────────────────────────────

    def validar(self) -> bool:
        """Valida todos los campos del asesor.

        Returns:
            True si todos los datos son válidos.

        Raises:
            ValidacionError: Si algún campo no cumple las reglas.
        """
        try:
            validar_no_vacio(self._nombre, "nombre")
            validar_cedula(self._cedula)
        except Exception as e:
            raise ValidacionError(f"Validación de asesor fallida: {e}", "") from e
        return True

    def to_dict(self) -> dict:
        """Serializa el asesor a diccionario.

        Returns:
            Diccionario con todos los atributos del asesor.
        """
        return {
            "id": self._id,
            "nombre": self._nombre,
            "cedula": self._cedula,
            "especialidad": self._especialidad,
            "fecha_creacion": self._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_modificacion": self._fecha_modificacion.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self) -> str:
        esp = f" [{self._especialidad}]" if self._especialidad else ""
        return f"Asesor: {self._nombre} (Cédula: {self._cedula}){esp}"
