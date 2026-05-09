# =============================================================================
# base.py — Clase abstracta base para todas las entidades del sistema
# =============================================================================
# EntidadBase define el contrato mínimo que toda entidad del dominio debe
# cumplir: un ID único, fecha de creación, validación y serialización.
# =============================================================================

import uuid
from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """Clase abstracta base para todas las entidades del dominio.

    Define la estructura mínima obligatoria que deben implementar todas
    las entidades: identificador único, timestamp de creación, y métodos
    abstractos de validación y serialización.

    Attributes:
        _id (str): Identificador único generado con UUID4.
        _fecha_creacion (datetime): Momento de creación de la entidad.
    """

    def __init__(self):
        """Inicializa la entidad con un ID único y fecha de creación."""
        self._id: str = str(uuid.uuid4())[:8]  # ID corto para legibilidad
        self._fecha_creacion: datetime = datetime.now()

    # ─── Properties ──────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        """Identificador único de la entidad (solo lectura)."""
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha y hora de creación de la entidad (solo lectura)."""
        return self._fecha_creacion

    # ─── Métodos abstractos ──────────────────────────────────────────────

    @abstractmethod
    def validar(self) -> bool:
        """Valida que todos los datos de la entidad sean correctos.

        Cada subclase define sus propias reglas de validación.

        Returns:
            True si la entidad es válida.

        Raises:
            ValidacionError: Si algún dato no cumple las reglas.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Convierte la entidad a un diccionario para serialización.

        Returns:
            Diccionario con todos los atributos de la entidad.
        """
        pass

    # ─── Métodos comunes ─────────────────────────────────────────────────

    def __str__(self) -> str:
        """Representación legible de la entidad."""
        return f"{self.__class__.__name__}(id={self._id})"

    def __repr__(self) -> str:
        """Representación técnica de la entidad."""
        return f"<{self.__class__.__name__} id={self._id} creado={self._fecha_creacion:%Y-%m-%d %H:%M}>"

    def __eq__(self, other) -> bool:
        """Dos entidades son iguales si tienen el mismo ID."""
        if not isinstance(other, EntidadBase):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash basado en el ID para uso en sets y dicts."""
        return hash(self._id)
