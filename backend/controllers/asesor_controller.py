# =============================================================================
# asesor_controller.py — Controlador de operaciones sobre Asesores
# =============================================================================
"""
Módulo controlador para la gestión de Asesores.

Este módulo define la clase AsesorController, la cual es responsable de la 
gestión del ciclo de vida (CRUD) de los objetos Asesor en memoria. Implementa 
lógica de negocio como la validación de unicidad (por cédula), múltiples 
criterios de búsqueda y el manejo de excepciones personalizadas.
"""
# =============================================================================

from backend.models.asesor import Asesor
from backend.exceptions.excepciones import (
    ValidacionError, EntidadNoEncontradaError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("controllers.asesor")


class AsesorNoEncontradoError(EntidadNoEncontradaError):
    """
    Excepción lanzada cuando un asesor específico no puede ser localizado.
    
    Hereda de EntidadNoEncontradaError y proporciona un código de error
    estandarizado para facilitar su manejo en las capas superiores.
    """

    def __init__(self, identificador: str = ""):
        super().__init__("Asesor no encontrado", identificador)
        self.codigo = "ERR_ASESOR_NO_ENCONTRADO"


class AsesorController:
    """
    Controlador central para la gestión de operaciones CRUD sobre asesores.

    Mantiene el estado de la colección de asesores en memoria y encapsula toda
    la lógica de negocio relacionada con la creación, recuperación, actualización
    y eliminación de estos registros.

    Attributes:
        _asesores (list[Asesor]): Almacenamiento interno de la lista de asesores.
    """

    def __init__(self):
        """Inicializa el controlador con una lista vacía de asesores."""
        self._asesores: list = []

    @property
    def asesores(self) -> list:
        """
        Obtiene una copia segura de la lista de todos los asesores registrados.
        
        Returns:
            list[Asesor]: Copia de la lista interna de asesores para evitar
            modificaciones no autorizadas desde el exterior.
        """
        return self._asesores.copy()

    @property
    def total_asesores(self) -> int:
        """
        Obtiene el número total de asesores registrados.
        
        Returns:
            int: Cantidad de elementos en la lista de asesores.
        """
        return len(self._asesores)

    def crear_asesor(self, nombre: str, cedula: str,
                     especialidad: str = "") -> Asesor:
        """
        Crea y registra un nuevo asesor con validación completa.

        Verifica que no exista un asesor previamente registrado con la misma cédula
        antes de instanciar y almacenar el nuevo registro.

        Args:
            nombre (str): Nombre completo del asesor.
            cedula (str): Documento de identidad único.
            especialidad (str, optional): Área de experiencia del asesor. Por defecto es "".

        Returns:
            Asesor: La instancia del asesor recién creado y registrado.

        Raises:
            OperacionError: Si la cédula ya está registrada en el sistema.
            ValidacionError: Si los datos provistos no cumplen las reglas del modelo Asesor.
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
        """
        Busca y retorna un asesor específico mediante su identificador único (UUID).

        Args:
            asesor_id (str): El ID interno generado para el asesor.

        Returns:
            Asesor: El objeto asesor correspondiente al ID.

        Raises:
            AsesorNoEncontradoError: Si no existe ningún asesor con el ID provisto.
        """
        for asesor in self._asesores:
            if asesor.id == asesor_id:
                return asesor
        raise AsesorNoEncontradoError(asesor_id)

    def buscar_por_cedula(self, cedula: str) -> Asesor:
        """
        Busca y retorna un asesor mediante su documento de identidad.

        Args:
            cedula (str): Cédula de identidad a buscar.

        Returns:
            Asesor: El objeto asesor correspondiente a la cédula.

        Raises:
            AsesorNoEncontradoError: Si la cédula no está registrada.
        """
        cedula = cedula.strip()
        for asesor in self._asesores:
            if asesor.cedula == cedula:
                return asesor
        raise AsesorNoEncontradoError(cedula)

    def buscar_por_nombre(self, nombre: str) -> list:
        """
        Realiza una búsqueda parcial y case-insensitive por el nombre de los asesores.

        Args:
            nombre (str): Subcadena de texto a buscar dentro de los nombres.

        Returns:
            list[Asesor]: Lista de asesores cuyos nombres coincidan total o parcialmente.
        """
        nombre_lower = nombre.lower()
        return [a for a in self._asesores if nombre_lower in a.nombre.lower()]

    def buscar_por_especialidad(self, especialidad: str) -> list:
        """
        Filtra los asesores según su área de especialidad de manera case-insensitive.

        Args:
            especialidad (str): Área temática a buscar.

        Returns:
            list[Asesor]: Lista de asesores que pertenecen a la especialidad indicada.
        """
        esp_lower = especialidad.lower()
        return [a for a in self._asesores if a.especialidad == esp_lower]

    def actualizar_asesor(self, asesor_id: str, **kwargs) -> Asesor:
        """
        Actualiza selectivamente los atributos de un asesor existente.

        Args:
            asesor_id (str): Identificador único del asesor a modificar.
            **kwargs: Diccionario de atributos a actualizar (e.g., nombre, especialidad).
                      Nota: La cédula no se debe actualizar por este medio.

        Returns:
            Asesor: El objeto asesor con sus atributos actualizados.

        Raises:
            AsesorNoEncontradoError: Si el asesor especificado no existe.
            ValidacionError: Si los nuevos valores no pasan las reglas de validación.
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
        """
        Elimina un asesor del registro del sistema.

        Args:
            asesor_id (str): Identificador único del asesor a remover.

        Returns:
            Asesor: El objeto asesor que fue eliminado.

        Raises:
            AsesorNoEncontradoError: Si el asesor especificado no existe.
        """
        for i, asesor in enumerate(self._asesores):
            if asesor.id == asesor_id:
                eliminado = self._asesores.pop(i)
                logger.info(f"Asesor eliminado: {eliminado.nombre} (ID: {asesor_id})")
                return eliminado
        raise AsesorNoEncontradoError(asesor_id)

    def obtener_nombres_asesores(self) -> list:
        """
        Genera una lista de representación en texto de los asesores.
        
        Ideal para poblar componentes de interfaz gráfica como ComboBoxes.

        Returns:
            list[str]: Lista de cadenas en formato "Nombre (Cédula)".
        """
        return [f"{a.nombre} ({a.cedula})" for a in self._asesores]

    def obtener_mapa_asesores(self) -> dict:
        """
        Genera un diccionario que relaciona la representación visual de un asesor
        con su objeto correspondiente.

        Esto facilita la recuperación del objeto Asesor a partir de la selección
        del usuario en la interfaz gráfica.

        Returns:
            dict[str, Asesor]: Mapeo donde la clave es "Nombre (Cédula)" 
            y el valor es la instancia Asesor.
        """
        return {
            f"{a.nombre} ({a.cedula})": a for a in self._asesores
        }
