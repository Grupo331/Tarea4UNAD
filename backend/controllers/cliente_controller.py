# =============================================================================
# cliente_controller.py — Controlador de operaciones sobre Clientes
# =============================================================================
"""
Módulo controlador para la gestión de Clientes.

Este módulo actúa como intermediario entre la capa de interfaz gráfica y la capa 
de datos (el modelo Cliente). Su responsabilidad es mantener el estado de los 
clientes en memoria, además de encapsular y exponer todas las operaciones del 
ciclo de vida (CRUD), garantizando la validación y evitando registros duplicados.
"""
# =============================================================================

from backend.models.cliente import Cliente
from backend.exceptions.excepciones import (
    ClienteValidacionError, ClienteNoEncontradoError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("controllers.cliente")


class ClienteController:
    """
    Controlador central para la gestión de operaciones CRUD sobre clientes.

    Mantiene el estado de la colección de clientes en memoria y expone una API
    para crear, buscar, actualizar y eliminar registros de clientes de forma segura,
    ejecutando las respectivas validaciones de negocio en cada paso.

    Attributes:
        _clientes (list[Cliente]): Almacenamiento interno de la lista de clientes registrados.
    """

    def __init__(self):
        """Inicializa el controlador con una lista vacía de clientes."""
        self._clientes: list = []

    @property
    def clientes(self) -> list:
        """
        Obtiene una copia segura de la lista de todos los clientes registrados.

        Returns:
            list[Cliente]: Copia de la lista interna de clientes para evitar
            modificaciones no autorizadas en el arreglo original.
        """
        return self._clientes.copy()

    @property
    def total_clientes(self) -> int:
        """
        Calcula el número total de clientes registrados en el sistema.

        Returns:
            int: Cantidad de clientes actualmente en memoria.
        """
        return len(self._clientes)

    def crear_cliente(self, nombre: str, cedula: str,
                      telefono: str, email: str) -> Cliente:
        """
        Crea y registra un nuevo cliente aplicando reglas de validación.

        Verifica que no exista un cliente con la misma cédula en el sistema antes
        de crear el objeto. Este método incluye un bloque try/except/finally 
        para asegurar el registro de intentos en los logs en todo momento.

        Args:
            nombre (str): Nombre completo del cliente.
            cedula (str): Documento de identidad (debe ser único).
            telefono (str): Número de teléfono de contacto.
            email (str): Dirección de correo electrónico válida.

        Returns:
            Cliente: La instancia del cliente recién creado.

        Raises:
            OperacionError: Si ya existe un cliente registrado con la cédula provista.
            ClienteValidacionError: Si alguno de los datos proporcionados es inválido
            según las reglas del modelo.
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
        """
        Busca y retorna un cliente específico mediante su identificador interno (UUID).

        Args:
            cliente_id (str): ID interno único generado por el sistema.

        Returns:
            Cliente: El objeto cliente correspondiente al ID.

        Raises:
            ClienteNoEncontradoError: Si no existe ningún cliente con ese ID.
        """
        for cliente in self._clientes:
            if cliente.id == cliente_id:
                return cliente
        raise ClienteNoEncontradoError(cliente_id)

    def buscar_por_cedula(self, cedula: str) -> Cliente:
        """
        Busca un cliente exacto utilizando su documento de identidad.

        Args:
            cedula (str): Número de documento de identidad a buscar.

        Returns:
            Cliente: El objeto cliente correspondiente a la cédula.

        Raises:
            ClienteNoEncontradoError: Si la cédula no está registrada en el sistema.
        """
        cedula = cedula.strip()
        for cliente in self._clientes:
            if cliente.cedula == cedula:
                return cliente
        raise ClienteNoEncontradoError(cedula)

    def buscar_por_nombre(self, nombre: str) -> list:
        """
        Realiza una búsqueda parcial en los nombres de los clientes.
        
        La búsqueda no distingue entre mayúsculas y minúsculas (case-insensitive).

        Args:
            nombre (str): Subcadena de texto a buscar.

        Returns:
            list[Cliente]: Lista de clientes que contienen la subcadena en su nombre.
        """
        nombre_lower = nombre.lower()
        return [c for c in self._clientes if nombre_lower in c.nombre.lower()]

    def actualizar_cliente(self, cliente_id: str, **kwargs) -> Cliente:
        """
        Modifica los atributos permitidos de un cliente ya existente.

        Args:
            cliente_id (str): Identificador único del cliente a actualizar.
            **kwargs: Diccionario con los campos a modificar (nombre, telefono, email).
                      (La cédula no debe actualizarse por este medio).

        Returns:
            Cliente: El objeto cliente ya actualizado.

        Raises:
            ClienteNoEncontradoError: Si el ID del cliente no existe.
            ClienteValidacionError: Si alguno de los nuevos valores introducidos 
            incumple las reglas de validación del modelo.
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
        """
        Remueve un cliente permanentemente del registro en memoria del sistema.

        Args:
            cliente_id (str): Identificador único del cliente a eliminar.

        Returns:
            Cliente: El objeto cliente que fue eliminado de la memoria.

        Raises:
            ClienteNoEncontradoError: Si no se encuentra un cliente con ese ID.
        """
        for i, cliente in enumerate(self._clientes):
            if cliente.id == cliente_id:
                eliminado = self._clientes.pop(i)
                logger.info(f"Cliente eliminado: {eliminado.nombre} (ID: {cliente_id})")
                return eliminado
        raise ClienteNoEncontradoError(cliente_id)
