# =============================================================================
# cliente.py — Modelo de Cliente con encapsulación y validación
# =============================================================================
"""
Módulo que define el modelo de negocio Cliente.

Implementa la clase Cliente con properties que validan datos en cada setter,
garantizando que un cliente siempre tenga datos consistentes a lo largo 
del ciclo de vida de la aplicación.
"""
# =============================================================================

from backend.models.base import EntidadBase
from backend.exceptions.excepciones import ClienteValidacionError
from backend.utils.validadores import validar_no_vacio, validar_cedula, validar_email, validar_telefono
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("models.cliente")


class Cliente(EntidadBase):
    """Representa un cliente del sistema Software FJ.

    Encapsula los datos personales del cliente con validación estricta
    en cada setter. Hereda de EntidadBase para obtener ID y timestamp.

    Attributes:
        _nombre (str): Nombre completo del cliente.
        _cedula (str): Documento de identidad (8-12 dígitos).
        _telefono (str): Número de teléfono (7-15 dígitos).
        _email (str): Dirección de correo electrónico.
    """

    def __init__(self, nombre: str, cedula: str, telefono: str, email: str):
        """Inicializa un nuevo cliente con validación inmediata.

        Args:
            nombre: Nombre completo del cliente.
            cedula: Documento de identidad.
            telefono: Número de teléfono.
            email: Correo electrónico.

        Raises:
            ClienteValidacionError: Si algún dato no es válido.
        """
        super().__init__()
        # Asignar vía properties para activar validaciones
        self.nombre = nombre
        self.cedula = cedula
        self.telefono = telefono
        self.email = email
        logger.info(f"Cliente creado: {self._nombre} (Cédula: {self._cedula}, ID: {self._id})")

    # ─── Properties con validación en setter ─────────────────────────────

    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        try:
            self._nombre = validar_no_vacio(valor, "nombre")
        except Exception as e:
            raise ClienteValidacionError(str(e), "nombre") from e

    @property
    def cedula(self) -> str:
        """Documento de identidad del cliente (solo lectura después de creación)."""
        return self._cedula

    @cedula.setter
    def cedula(self, valor: str) -> None:
        try:
            self._cedula = validar_cedula(valor)
        except Exception as e:
            raise ClienteValidacionError(str(e), "cédula") from e

    @property
    def telefono(self) -> str:
        """Número de teléfono del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        try:
            self._telefono = validar_telefono(valor)
        except Exception as e:
            raise ClienteValidacionError(str(e), "teléfono") from e

    @property
    def email(self) -> str:
        """Correo electrónico del cliente."""
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        try:
            self._email = validar_email(valor)
        except Exception as e:
            raise ClienteValidacionError(str(e), "email") from e

    # ─── Métodos abstractos implementados ────────────────────────────────

    def validar(self) -> bool:
        """Valida todos los campos del cliente.

        Returns:
            True si todos los datos son válidos.

        Raises:
            ClienteValidacionError: Si algún campo no cumple las reglas.
        """
        try:
            validar_no_vacio(self._nombre, "nombre")
            validar_cedula(self._cedula)
            validar_telefono(self._telefono)
            validar_email(self._email)
        except Exception as e:
            raise ClienteValidacionError(f"Validación fallida: {e}", "") from e
        return True

    def to_dict(self) -> dict:
        """Serializa el cliente a diccionario.

        Returns:
            Diccionario con todos los atributos del cliente.
        """
        return {
            "id": self._id,
            "nombre": self._nombre,
            "cedula": self._cedula,
            "telefono": self._telefono,
            "email": self._email,
            "fecha_creacion": self._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self) -> str:
        return f"Cliente: {self._nombre} (Cédula: {self._cedula})"
