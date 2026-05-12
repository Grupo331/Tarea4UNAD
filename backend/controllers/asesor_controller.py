# =============================================================================
# asesor_controller.py — Controlador de operaciones sobre Asesores
# =============================================================================
"""
Módulo de lógica de negocio para la gestión de Asesores del Sistema Software FJ.

Este controlador actúa como intermediario entre la interfaz de usuario y los 
modelos de datos. Implementa el ciclo de vida completo (CRUD) de los asesores 
en un repositorio en memoria, asegurando la integridad de los datos mediante 
validaciones de unicidad y el manejo robusto de excepciones para prevenir 
registros inconsistentes.
"""
# =============================================================================

from backend.models.asesor import Asesor
from backend.exceptions.excepciones import (
    ValidacionError, EntidadNoEncontradaError, OperacionError
)
from backend.utils.logger_config import obtener_logger

# Instancia global del logger para rastrear eventos y errores en este controlador
logger = obtener_logger("controllers.asesor")


class AsesorNoEncontradoError(EntidadNoEncontradaError):
    """
    Excepción lanzada cuando un asesor específico no puede ser localizado.
    
    Hereda de EntidadNoEncontradaError y proporciona un código de error
    estandarizado para facilitar su manejo en las capas superiores.
    """

    def __init__(self, identificador: str = ""):
        """
        Inicializa la excepción con un mensaje personalizado y el ID no hallado.
        
        Args:
            identificador (str): El ID o cédula que disparó la búsqueda fallida.
        """
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
        # _asesores: Lista privada que sirve como almacén volátil de objetos Asesor
        self._asesores: list = []

    @property
    def asesores(self) -> list:
        """
        Obtiene una copia segura de la lista de todos los asesores registrados.
        
        Returns:
            list[Asesor]: Copia de la lista interna de asesores para evitar
            modificaciones no autorizadas desde el exterior.
        """
        # Se utiliza .copy() para proteger el encapsulamiento de la lista interna
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
            nombre: Nombre completo del asesor.
            cedula: Documento de identidad único.
            especialidad: Área de experiencia del asesor. Por defecto es "".

        Returns:
            Asesor: La instancia del asesor recién creado y registrado.

        Raises:
            OperacionError: Si la cédula ya está registrada en el sistema.
            ValidacionError: Si los datos provistos no cumplen las reglas del modelo Asesor.
        """
        # Identificador de la operación para fines de registro en logs
        operacion = "crear_asesor"
        try:
            # LÓGICA DE UNICIDAD: Se eliminan espacios y se compara contra cada registro existente
            cedula_limpia = cedula.strip()
            for a in self._asesores:
                if a.cedula == cedula_limpia:
                    # Si hay coincidencia, se interrumpe el flujo con una excepción
                    raise OperacionError(
                        f"Ya existe un asesor con cédula {cedula_limpia}",
                        operacion
                    )

            # Se instancia el modelo (el cual lanza ValidacionError si los campos son incorrectos)
            asesor = Asesor(nombre, cedula, especialidad)
            # Se persiste el objeto en la lista en memoria
            self._asesores.append(asesor)
            return asesor

        except (ValidacionError, OperacionError):
            # Se re-lanzan excepciones de negocio para que sean manejadas por la UI
            raise
        except Exception as e:
            # Captura y registro de errores técnicos no previstos
            logger.error(f"Error inesperado al crear asesor: {e}")
            raise OperacionError(
                f"Error inesperado: {e}", operacion
            ) from e
        finally:
            # Registro mandatorio de la finalización del intento de operación
            logger.info(f"[FINALLY] Operación '{operacion}' finalizada")

    def buscar_por_id(self, asesor_id: str) -> Asesor:
        """
        Busca y retorna un asesor específico mediante su identificador único (UUID).

        Args:
            asesor_id: El ID interno generado para el asesor.

        Returns:
            Asesor: El objeto asesor correspondiente al ID.

        Raises:
            AsesorNoEncontradoError: Si no existe ningún asesor con el ID provisto.
        """
        # Búsqueda secuencial basada en el UUID del objeto
        for asesor in self._asesores:
            if asesor.id == asesor_id:
                return asesor
        # Si el bucle termina sin retorno, el recurso no existe
        raise AsesorNoEncontradoError(asesor_id)

    def buscar_por_cedula(self, cedula: str) -> Asesor:
        """
        Busca y retorna un asesor mediante su documento de identidad.

        Args:
            cedula: Cédula de identidad a buscar.

        Returns:
            Asesor: El objeto asesor correspondiente a la cédula.

        Raises:
            AsesorNoEncontradoError: Si la cédula no está registrada.
        """
        # Normalización de la cadena de búsqueda
        cedula = cedula.strip()
        for asesor in self._asesores:
            if asesor.cedula == cedula:
                return asesor
        # Excepción específica para fallos en búsqueda por documento
        raise AsesorNoEncontradoError(cedula)

    def buscar_por_nombre(self, nombre: str) -> list:
        """
        Realiza una búsqueda parcial y case-insensitive por el nombre de los asesores.

        Args:
            nombre: Subcadena de texto a buscar dentro de los nombres.

        Returns:
            list[Asesor]: Lista de asesores cuyos nombres coincidan total o parcialmente.
        """
        # Normalización a minúsculas para búsqueda flexible
        nombre_lower = nombre.lower()
        # Filtrado mediante comprensión de listas
        return [a for a in self._asesores if nombre_lower in a.nombre.lower()]

    def buscar_por_especialidad(self, especialidad: str) -> list:
        """
        Filtra los asesores según su área de especialidad de manera case-insensitive.

        Args:
            especialidad: Área temática a buscar.

        Returns:
            list[Asesor]: Lista de asesores que pertenecen a la especialidad indicada.
        """
        # Filtrado insensible a capitalización
        esp_lower = especialidad.lower()
        return [a for a in self._asesores if a.especialidad == esp_lower]

    def actualizar_asesor(self, asesor_id: str, **kwargs) -> Asesor:
        """
        Actualiza selectivamente los atributos de un asesor existente.

        Args:
            asesor_id: Identificador único del asesor a modificar.
            **kwargs: Diccionario de atributos a actualizar (e.g., nombre, especialidad).
                      Nota: La cédula no se debe actualizar por este medio.

        Returns:
            Asesor: El objeto asesor con sus atributos actualizados.

        Raises:
            AsesorNoEncontradoError: Si el asesor especificado no existe.
            ValidacionError: Si los nuevos valores no pasan las reglas de validación.
        """
        # Se garantiza la existencia del registro antes de intentar modificarlo
        asesor = self.buscar_por_id(asesor_id)

        try:
            # LÓGICA DE ACTUALIZACIÓN: Se validan y asignan campos opcionales desde kwargs
            if "nombre" in kwargs and kwargs["nombre"]:
                asesor.nombre = kwargs["nombre"]
            if "especialidad" in kwargs:
                asesor.especialidad = kwargs["especialidad"]
            logger.info(f"Asesor actualizado: {asesor.nombre} (ID: {asesor_id})")
        except ValidacionError:
            # Propagación de fallos detectados por el modelo (setters)
            raise
        except Exception as e:
            # Encadenamiento de excepción para errores de asignación inesperados
            raise ValidacionError(
                f"Error al actualizar asesor: {e}", ""
            ) from e

        return asesor

    def eliminar_asesor(self, asesor_id: str) -> Asesor:
        """
        Elimina un asesor del registro del sistema.

        Args:
            asesor_id: Identificador único del asesor a remover.

        Returns:
            Asesor: El objeto asesor que fue eliminado.

        Raises:
            AsesorNoEncontradoError: Si el asesor especificado no existe.
        """
        # Se utiliza enumerate para obtener el índice y realizar un pop eficiente
        for i, asesor in enumerate(self._asesores):
            if asesor.id == asesor_id:
                # Remoción física de la lista
                eliminado = self._asesores.pop(i)
                logger.info(f"Asesor eliminado: {eliminado.nombre} (ID: {asesor_id})")
                return eliminado
        # Error si el ID no corresponde a ningún elemento de la colección
        raise AsesorNoEncontradoError(asesor_id)

    def obtener_nombres_asesores(self) -> list:
        """
        Genera una lista de representación en texto de los asesores.
        
        Ideal para poblar componentes de interfaz gráfica como ComboBoxes.

        Returns:
            list[str]: Lista de cadenas en formato "Nombre (Cédula)".
        """
        # Formateo visual para facilitar la selección en ComboBoxes de la UI
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
        # Se genera un diccionario de búsqueda para recuperar el objeto 
        # original a partir de la selección de texto del usuario.
        return {
            f"{a.nombre} ({a.cedula})": a for a in self._asesores
        }
