# =============================================================================
# cliente_controller.py — Controlador de operaciones sobre Clientes
# =============================================================================
# Media entre la interfaz gráfica y el modelo Cliente.
# Gestiona la lista de clientes en memoria y expone operaciones CRUD.
# =============================================================================

from backend.models.cliente import Cliente
from backend.exceptions.excepciones import (
    ClienteValidacionError, ClienteNoEncontradoError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("controllers.cliente")


class ClienteController:
    """Controlador que gestiona las operaciones CRUD sobre clientes.

    Mantiene una lista en memoria de todos los clientes registrados
    y proporciona métodos para crear, buscar, actualizar y eliminar.

    Attributes:
        _clientes (list[Cliente]): Lista de clientes registrados.
    """

    def __init__(self):
        self._clientes: list = []

    @property
    def clientes(self) -> list:
        """Lista de todos los clientes (copia para seguridad)."""
        return self._clientes.copy()

    @property
    def total_clientes(self) -> int:
        return len(self._clientes)

    def crear_cliente(self, nombre: str, cedula: str,
                      telefono: str, email: str) -> Cliente:
        """Crea un nuevo cliente con validación completa.

        Demuestra try/except/finally: siempre registra el intento.

        Args:
            nombre: Nombre completo.
            cedula: Documento de identidad.
            telefono: Número de teléfono.
            email: Correo electrónico.

        Returns:
            El cliente creado.

        Raises:
            ClienteValidacionError: Si los datos son inválidos.
            OperacionError: Si la cédula ya está registrada.
        """
        operacion = "crear_cliente"
        try:
            # Verificar que la cédula no esté duplicada
            cedula_limpia = cedula.strip()
            for c in self._clientes:
                if c.cedula == cedula_limpia:
                    raise OperacionError(
                        f"Ya existe un cliente con cédula {cedula_limpia}",
                        operacion
                    )

            cliente = Cliente(nombre, cedula, telefono, email)
            self._clientes.append(cliente)
            return cliente

        except (ClienteValidacionError, OperacionError):
            raise  # Re-lanzar excepciones conocidas tal cual
        except Exception as e:
            logger.error(f"Error inesperado al crear cliente: {e}")
            raise OperacionError(
                f"Error inesperado: {e}", operacion
            ) from e
        finally:
            logger.info(f"[FINALLY] Operación '{operacion}' finalizada")

    def buscar_por_id(self, cliente_id: str) -> Cliente:
        """Busca un cliente por su ID.

        Args:
            cliente_id: ID del cliente.

        Returns:
            El cliente encontrado.

        Raises:
            ClienteNoEncontradoError: Si no se encuentra.
        """
        for cliente in self._clientes:
            if cliente.id == cliente_id:
                return cliente
        raise ClienteNoEncontradoError(cliente_id)

    def buscar_por_cedula(self, cedula: str) -> Cliente:
        """Busca un cliente por su cédula.

        Args:
            cedula: Número de cédula.

        Returns:
            El cliente encontrado.

        Raises:
            ClienteNoEncontradoError: Si no se encuentra.
        """
        cedula = cedula.strip()
        for cliente in self._clientes:
            if cliente.cedula == cedula:
                return cliente
        raise ClienteNoEncontradoError(cedula)

    def buscar_por_nombre(self, nombre: str) -> list:
        """Busca clientes cuyo nombre contenga el texto dado.

        Args:
            nombre: Texto a buscar (búsqueda parcial, case-insensitive).

        Returns:
            Lista de clientes que coinciden.
        """
        nombre_lower = nombre.lower()
        return [c for c in self._clientes if nombre_lower in c.nombre.lower()]

    def actualizar_cliente(self, cliente_id: str, **kwargs) -> Cliente:
        """Actualiza los datos de un cliente existente.

        Args:
            cliente_id: ID del cliente a actualizar.
            **kwargs: Campos a actualizar (nombre, telefono, email).

        Returns:
            El cliente actualizado.

        Raises:
            ClienteNoEncontradoError: Si no se encuentra.
            ClienteValidacionError: Si los nuevos datos son inválidos.
        """
        cliente = self.buscar_por_id(cliente_id)

        try:
            if "nombre" in kwargs:
                cliente.nombre = kwargs["nombre"]
            if "telefono" in kwargs:
                cliente.telefono = kwargs["telefono"]
            if "email" in kwargs:
                cliente.email = kwargs["email"]
            logger.info(f"Cliente actualizado: {cliente.nombre} (ID: {cliente_id})")
        except ClienteValidacionError:
            raise
        except Exception as e:
            raise ClienteValidacionError(
                f"Error al actualizar: {e}", ""
            ) from e

        return cliente

    def eliminar_cliente(self, cliente_id: str) -> Cliente:
        """Elimina un cliente del sistema.

        Args:
            cliente_id: ID del cliente a eliminar.

        Returns:
            El cliente eliminado.

        Raises:
            ClienteNoEncontradoError: Si no se encuentra.
        """
        for i, cliente in enumerate(self._clientes):
            if cliente.id == cliente_id:
                eliminado = self._clientes.pop(i)
                logger.info(f"Cliente eliminado: {eliminado.nombre} (ID: {cliente_id})")
                return eliminado
        raise ClienteNoEncontradoError(cliente_id)
