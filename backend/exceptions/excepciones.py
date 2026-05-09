# =============================================================================
# excepciones.py — Jerarquía de excepciones personalizadas de Software FJ
# =============================================================================
# Implementa una jerarquía organizada que permite capturar errores de forma
# granular o general. Cada excepción incluye contexto útil para logging.
# =============================================================================


class SoftwareFJError(Exception):
    """Excepción base de toda la aplicación Software FJ.
    
    Todas las excepciones personalizadas heredan de esta clase,
    permitiendo capturar cualquier error del sistema con un solo except.
    """

    def __init__(self, mensaje: str = "Error en el sistema Software FJ", codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(self.mensaje)

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje}"


# ─── Errores de Validación ───────────────────────────────────────────────────

class ValidacionError(SoftwareFJError):
    """Error base para fallos de validación de datos."""

    def __init__(self, mensaje: str = "Error de validación", campo: str = ""):
        self.campo = campo
        codigo = "ERR_VALIDACION"
        if campo:
            mensaje = f"{mensaje} (campo: {campo})"
        super().__init__(mensaje, codigo)


class ClienteValidacionError(ValidacionError):
    """Error de validación específico para datos de clientes."""

    def __init__(self, mensaje: str = "Error en datos del cliente", campo: str = ""):
        super().__init__(mensaje, campo)
        self.codigo = "ERR_CLIENTE_VALIDACION"


class ServicioValidacionError(ValidacionError):
    """Error de validación específico para datos de servicios."""

    def __init__(self, mensaje: str = "Error en datos del servicio", campo: str = ""):
        super().__init__(mensaje, campo)
        self.codigo = "ERR_SERVICIO_VALIDACION"


class ReservaValidacionError(ValidacionError):
    """Error de validación específico para datos de reservas."""

    def __init__(self, mensaje: str = "Error en datos de la reserva", campo: str = ""):
        super().__init__(mensaje, campo)
        self.codigo = "ERR_RESERVA_VALIDACION"


# ─── Errores de Disponibilidad ───────────────────────────────────────────────

class DisponibilidadError(SoftwareFJError):
    """Error base cuando un recurso no está disponible."""

    def __init__(self, mensaje: str = "Recurso no disponible"):
        super().__init__(mensaje, "ERR_DISPONIBILIDAD")


class SalaNoDisponibleError(DisponibilidadError):
    """La sala solicitada ya está reservada en el horario indicado."""

    def __init__(self, sala: str = "", horario: str = ""):
        mensaje = f"La sala '{sala}' no está disponible"
        if horario:
            mensaje += f" en el horario {horario}"
        super().__init__(mensaje)
        self.codigo = "ERR_SALA_NO_DISPONIBLE"
        self.sala = sala
        self.horario = horario


class EquipoSinStockError(DisponibilidadError):
    """No hay suficiente stock del equipo solicitado."""

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
    """El asesor no está disponible en el horario solicitado."""

    def __init__(self, asesor: str = "", horario: str = ""):
        mensaje = f"El asesor '{asesor}' no está disponible"
        if horario:
            mensaje += f" en el horario {horario}"
        super().__init__(mensaje)
        self.codigo = "ERR_ASESOR_NO_DISPONIBLE"


# ─── Errores de Estado de Reserva ────────────────────────────────────────────

class TransicionEstadoError(SoftwareFJError):
    """Transición de estado inválida en una reserva.
    
    Ejemplo: intentar completar una reserva que está cancelada.
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
    """Error base cuando no se encuentra una entidad buscada."""

    def __init__(self, mensaje: str = "Entidad no encontrada", entidad_id: str = ""):
        self.entidad_id = entidad_id
        if entidad_id:
            mensaje = f"{mensaje} (ID: {entidad_id})"
        super().__init__(mensaje, "ERR_NO_ENCONTRADO")


class ClienteNoEncontradoError(EntidadNoEncontradaError):
    """El cliente buscado no existe en el sistema."""

    def __init__(self, identificador: str = ""):
        super().__init__("Cliente no encontrado", identificador)
        self.codigo = "ERR_CLIENTE_NO_ENCONTRADO"


class ServicioNoEncontradoError(EntidadNoEncontradaError):
    """El servicio buscado no existe en el sistema."""

    def __init__(self, identificador: str = ""):
        super().__init__("Servicio no encontrado", identificador)
        self.codigo = "ERR_SERVICIO_NO_ENCONTRADO"


class ReservaNoEncontradaError(EntidadNoEncontradaError):
    """La reserva buscada no existe en el sistema."""

    def __init__(self, identificador: str = ""):
        super().__init__("Reserva no encontrada", identificador)
        self.codigo = "ERR_RESERVA_NO_ENCONTRADA"


# ─── Errores de Operación ───────────────────────────────────────────────────

class OperacionError(SoftwareFJError):
    """Error genérico durante una operación del sistema."""

    def __init__(self, mensaje: str = "Error durante la operación", operacion: str = ""):
        self.operacion = operacion
        if operacion:
            mensaje = f"{mensaje} (operación: {operacion})"
        super().__init__(mensaje, "ERR_OPERACION")
