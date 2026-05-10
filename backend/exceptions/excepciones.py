# =============================================================================
# excepciones.py — Jerarquía de excepciones personalizadas de Software FJ
# =============================================================================
"""
Módulo de Excepciones Personalizadas para Software FJ.

Implementa una jerarquía organizada de errores que permite a la aplicación capturar 
fallos de forma granular (errores específicos de validación, de disponibilidad, etc.)
o general (usando la clase base SoftwareFJError).

Cada excepción personalizada está diseñada para incluir contexto útil y estructurado 
(códigos de error, IDs de entidades, variables de estado), lo cual facilita el 
manejo de errores en la interfaz gráfica y mejora la trazabilidad en los logs.
"""
# =============================================================================


class SoftwareFJError(Exception):
    """
    Excepción base raíz de toda la aplicación Software FJ.
    
    Todas las demás excepciones personalizadas del sistema deben heredar directa
    o indirectamente de esta clase. Esto permite capturar cualquier error 
    controlado por el negocio usando un único bloque `except SoftwareFJError`.

    Attributes:
        mensaje (str): Texto descriptivo y legible por humanos del error.
        codigo (str): Código de error estandarizado (e.g., "ERR_GENERAL") 
                      para uso en interfaces, APIs o sistemas de logs.
    """

    def __init__(self, mensaje: str = "Error en el sistema Software FJ", codigo: str = "ERR_GENERAL"):
        """
        Inicializa la excepción base con un mensaje y código.

        Args:
            mensaje (str, optional): Descripción del error. Por defecto "Error en el sistema Software FJ".
            codigo (str, optional): Código del error. Por defecto "ERR_GENERAL".
        """
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(self.mensaje)

    def __str__(self) -> str:
        """
        Representación en string de la excepción que incluye el código y el mensaje.
        
        Returns:
            str: Formato legible, ejemplo: "[ERR_GENERAL] Error en el sistema Software FJ".
        """
        return f"[{self.codigo}] {self.mensaje}"


# ─── Errores de Validación ───────────────────────────────────────────────────

class ValidacionError(SoftwareFJError):
    """
    Excepción base para cualquier fallo en la validación semántica o de formato de datos.

    Attributes:
        campo (str): El nombre del campo específico que falló la validación.
    """

    def __init__(self, mensaje: str = "Error de validación", campo: str = ""):
        """
        Inicializa el error de validación.

        Args:
            mensaje (str, optional): Descripción del fallo. Por defecto "Error de validación".
            campo (str, optional): Nombre del atributo o campo problemático.
        """
        self.campo = campo
        codigo = "ERR_VALIDACION"
        if campo:
            mensaje = f"{mensaje} (campo: {campo})"
        super().__init__(mensaje, codigo)


class ClienteValidacionError(ValidacionError):
    """Excepción específica para datos inválidos en el modelo Cliente."""

    def __init__(self, mensaje: str = "Error en datos del cliente", campo: str = ""):
        super().__init__(mensaje, campo)
        self.codigo = "ERR_CLIENTE_VALIDACION"


class ServicioValidacionError(ValidacionError):
    """Excepción específica para datos inválidos en cualquier modelo de Servicio."""

    def __init__(self, mensaje: str = "Error en datos del servicio", campo: str = ""):
        super().__init__(mensaje, campo)
        self.codigo = "ERR_SERVICIO_VALIDACION"


class ReservaValidacionError(ValidacionError):
    """Excepción específica para parámetros o fechas inválidas en una Reserva."""

    def __init__(self, mensaje: str = "Error en datos de la reserva", campo: str = ""):
        super().__init__(mensaje, campo)
        self.codigo = "ERR_RESERVA_VALIDACION"


# ─── Errores de Disponibilidad ───────────────────────────────────────────────

class DisponibilidadError(SoftwareFJError):
    """
    Excepción base lanzada cuando un recurso (sala, equipo o asesor) no está 
    disponible para ser reservado o utilizado.
    """

    def __init__(self, mensaje: str = "Recurso no disponible"):
        super().__init__(mensaje, "ERR_DISPONIBILIDAD")


class SalaNoDisponibleError(DisponibilidadError):
    """
    Excepción lanzada cuando la sala solicitada tiene cruce de horarios o 
    ya se encuentra reservada.

    Attributes:
        sala (str): El nombre o identificador de la sala solicitada.
        horario (str): El rango de horario problemático.
    """

    def __init__(self, sala: str = "", horario: str = ""):
        mensaje = f"La sala '{sala}' no está disponible"
        if horario:
            mensaje += f" en el horario {horario}"
        super().__init__(mensaje)
        self.codigo = "ERR_SALA_NO_DISPONIBLE"
        self.sala = sala
        self.horario = horario


class EquipoSinStockError(DisponibilidadError):
    """
    Excepción lanzada cuando se solicitan más unidades de un equipo de 
    las que se encuentran disponibles actualmente en stock.

    Attributes:
        tipo_equipo (str): Nombre de la categoría de equipo (e.g. 'Laptop').
        solicitado (int): Cantidad que se intentó reservar.
        disponible (int): Cantidad máxima real que podía reservarse.
    """

    def __init__(self, tipo_equipo: str = "", solicitado: int = 0, disponible: int = 0):
        mensaje = (
            f"Stock insuficiente de '{tipo_equipo}': "
            f"solicitado={solicitado}, disponible={disponible}"
        )
        super().__init__(mensaje)
        self.codigo = "ERR_EQUIPO_SIN_STOCK"
        self.tipo_equipo = tipo_equipo
        self.solicitado = solicitado
        self.disponible = disponible


class AsesorNoDisponibleError(DisponibilidadError):
    """
    Excepción lanzada cuando el profesional solicitado ya tiene una cita
    o no tiene disponibilidad en la fecha requerida.
    """

    def __init__(self, asesor: str = "", horario: str = ""):
        mensaje = f"El asesor '{asesor}' no está disponible"
        if horario:
            mensaje += f" en el horario {horario}"
        super().__init__(mensaje)
        self.codigo = "ERR_ASESOR_NO_DISPONIBLE"


# ─── Errores de Estado de Reserva ────────────────────────────────────────────

class TransicionEstadoError(SoftwareFJError):
    """
    Excepción lanzada cuando se intenta realizar un cambio de estado prohibido
    según la máquina de estados definida en la configuración global.
    
    Ejemplo: Intentar cambiar el estado de una reserva 'COMPLETADA' a 'EN_CURSO',
    lo cual no es un camino permitido.

    Attributes:
        estado_actual (str): Estado en el que se encuentra actualmente el objeto.
        estado_destino (str): Estado al que se intentó transicionar.
    """

    def __init__(self, estado_actual: str = "", estado_destino: str = ""):
        mensaje = (
            f"Transición de estado inválida: "
            f"'{estado_actual}' → '{estado_destino}' no está permitida"
        )
        super().__init__(mensaje, "ERR_TRANSICION_ESTADO")
        self.estado_actual = estado_actual
        self.estado_destino = estado_destino


# ─── Errores de Búsqueda ────────────────────────────────────────────────────

class EntidadNoEncontradaError(SoftwareFJError):
    """
    Excepción base para búsquedas fallidas.
    
    Se lanza cuando se realiza una consulta (típicamente por ID o identificador
    único) y el registro no existe en los catálogos en memoria.
    
    Attributes:
        entidad_id (str): Identificador que no fue hallado.
    """

    def __init__(self, mensaje: str = "Entidad no encontrada", entidad_id: str = ""):
        self.entidad_id = entidad_id
        if entidad_id:
            mensaje = f"{mensaje} (ID: {entidad_id})"
        super().__init__(mensaje, "ERR_NO_ENCONTRADO")


class ClienteNoEncontradoError(EntidadNoEncontradaError):
    """El cliente buscado (por cédula o ID) no existe en el sistema."""

    def __init__(self, identificador: str = ""):
        super().__init__("Cliente no encontrado", identificador)
        self.codigo = "ERR_CLIENTE_NO_ENCONTRADO"


class ServicioNoEncontradoError(EntidadNoEncontradaError):
    """El servicio (sala, equipo o asesoría) buscado no existe en el catálogo."""

    def __init__(self, identificador: str = ""):
        super().__init__("Servicio no encontrado", identificador)
        self.codigo = "ERR_SERVICIO_NO_ENCONTRADO"


class ReservaNoEncontradaError(EntidadNoEncontradaError):
    """La reserva buscada mediante ID no existe en el registro."""

    def __init__(self, identificador: str = ""):
        super().__init__("Reserva no encontrada", identificador)
        self.codigo = "ERR_RESERVA_NO_ENCONTRADA"


# ─── Errores de Operación ───────────────────────────────────────────────────

class OperacionError(SoftwareFJError):
    """
    Excepción genérica para errores durante el flujo de negocio.
    
    Usada comúnmente para capturar reglas de negocio violadas, como intentar 
    crear un registro con una clave única que ya existe (ej. cédula duplicada), 
    o errores inesperados que deben ser envueltos antes de llegar a la UI.

    Attributes:
        operacion (str): Nombre lógico de la operación que falló (e.g. 'crear_cliente').
    """

    def __init__(self, mensaje: str = "Error durante la operación", operacion: str = ""):
        self.operacion = operacion
        if operacion:
            mensaje = f"{mensaje} (operación: {operacion})"
        super().__init__(mensaje, "ERR_OPERACION")
