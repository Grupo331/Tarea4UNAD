# =============================================================================
# reserva.py — Modelo de Reserva con máquina de estados
# =============================================================================
# Integra Cliente + Servicio con control de transiciones de estado,
# cálculo de costos polimórfico y registro de eventos.
# =============================================================================

from enum import Enum
from datetime import datetime
from backend.models.base import EntidadBase
from backend.models.cliente import Cliente
from backend.models.servicio import Servicio
from backend.exceptions.excepciones import (
    ReservaValidacionError, TransicionEstadoError, ValidacionError
)
from backend.utils.validadores import validar_numero_positivo, validar_opcion, validar_fecha
from backend.utils.logger_config import obtener_logger
from config import TRANSICIONES_ESTADO

logger = obtener_logger("models.reserva")


class EstadoReserva(Enum):
    """Estados posibles de una reserva con transiciones definidas."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    EN_CURSO = "En Curso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    NO_ASISTIO = "No Asistió"


class Reserva(EntidadBase):
    """Representa una reserva que integra un cliente con un servicio.

    Implementa una máquina de estados para controlar el ciclo de vida
    de la reserva (Pendiente → Confirmada → En Curso → Completada).

    Demuestra:
    - Composición: contiene objetos Cliente y Servicio
    - Delegación: delega el cálculo de costos al servicio (polimorfismo)
    - try/except/else: en procesar(), si el cálculo es exitoso se confirma
    - try/except/finally: siempre registra la operación en el log

    Attributes:
        _cliente (Cliente): Cliente que realiza la reserva.
        _servicio (Servicio): Servicio reservado.
        _fecha_reserva (datetime): Fecha/hora del servicio reservado.
        _duracion (float): Duración del servicio.
        _unidad_duracion (str): "hora" o "dia".
        _estado (EstadoReserva): Estado actual de la reserva.
        _costo_total (float): Costo calculado del servicio.
    """

    def __init__(self, cliente: Cliente, servicio: Servicio,
                 fecha_reserva: str, duracion: float,
                 unidad_duracion: str = "hora"):
        """Crea una nueva reserva en estado PENDIENTE.

        Args:
            cliente: Cliente que solicita el servicio.
            servicio: Servicio a reservar.
            fecha_reserva: Fecha del servicio (formato "YYYY-MM-DD").
            duracion: Duración (horas o días).
            unidad_duracion: "hora" o "dia".

        Raises:
            ReservaValidacionError: Si los datos son inválidos.
        """
        super().__init__()

        # Validar tipos
        if not isinstance(cliente, Cliente):
            raise ReservaValidacionError("Se requiere un objeto Cliente válido", "cliente")
        if not isinstance(servicio, Servicio):
            raise ReservaValidacionError("Se requiere un objeto Servicio válido", "servicio")

        self._cliente = cliente
        self._servicio = servicio
        self._fecha_reserva_str = validar_fecha(fecha_reserva, "fecha de reserva")
        self._duracion = validar_numero_positivo(duracion, "duración")
        self._unidad_duracion = validar_opcion(unidad_duracion, ["hora", "dia"], "unidad de duración")
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total: float = 0.0
        self._fecha_estado_cambio: datetime = datetime.now()

        logger.info(
            f"Reserva creada [{self._id}]: Cliente={cliente.nombre}, "
            f"Servicio={servicio.nombre}, Duración={duracion} {unidad_duracion}(s)"
        )

    # ─── Properties ──────────────────────────────────────────────────────

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def fecha_reserva(self) -> str:
        return self._fecha_reserva_str

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def unidad_duracion(self) -> str:
        return self._unidad_duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    # ─── Transiciones de estado ──────────────────────────────────────────

    def _cambiar_estado(self, nuevo_estado: EstadoReserva) -> None:
        """Cambia el estado validando la transición.

        Args:
            nuevo_estado: Estado destino.

        Raises:
            TransicionEstadoError: Si la transición no es válida.
        """
        estado_actual = self._estado.name
        estado_destino = nuevo_estado.name

        permitidos = TRANSICIONES_ESTADO.get(estado_actual, [])
        if estado_destino not in permitidos:
            raise TransicionEstadoError(
                self._estado.value, nuevo_estado.value
            )

        estado_anterior = self._estado
        self._estado = nuevo_estado
        self._fecha_estado_cambio = datetime.now()
        logger.info(
            f"Reserva [{self._id}]: Estado cambiado "
            f"'{estado_anterior.value}' → '{nuevo_estado.value}'"
        )

    def confirmar(self) -> None:
        """Cambia estado de PENDIENTE a CONFIRMADA."""
        self._cambiar_estado(EstadoReserva.CONFIRMADA)

    def iniciar(self) -> None:
        """Cambia estado de CONFIRMADA a EN_CURSO."""
        self._cambiar_estado(EstadoReserva.EN_CURSO)

    def completar(self) -> None:
        """Cambia estado de EN_CURSO a COMPLETADA."""
        self._cambiar_estado(EstadoReserva.COMPLETADA)

    def cancelar(self) -> None:
        """Cambia estado a CANCELADA (desde PENDIENTE o CONFIRMADA)."""
        self._cambiar_estado(EstadoReserva.CANCELADA)

    def marcar_no_asistio(self) -> None:
        """Cambia estado de CONFIRMADA a NO_ASISTIO."""
        self._cambiar_estado(EstadoReserva.NO_ASISTIO)

    # ─── Procesamiento de la reserva ─────────────────────────────────────

    def procesar(self, *, impuesto: float = 0.0, descuento: float = 0.0,
                 **kwargs) -> float:
        """Calcula el costo y confirma la reserva si es exitoso.

        Demuestra el patrón try/except/else/finally:
        - try: intenta calcular el costo vía polimorfismo
        - except: captura errores de cálculo
        - else: si no hubo error, confirma la reserva
        - finally: siempre registra la operación en el log

        Args:
            impuesto: Porcentaje de impuesto.
            descuento: Porcentaje de descuento.
            **kwargs: Parámetros adicionales para el servicio.

        Returns:
            El costo total calculado.

        Raises:
            ReservaValidacionError: Si el cálculo falla.
        """
        operacion_exitosa = False
        try:
            # Delegar cálculo al servicio (POLIMORFISMO)
            self._costo_total = self._servicio.calcular_costo(
                self._duracion, self._unidad_duracion,
                impuesto=impuesto, descuento=descuento,
                **kwargs
            )
        except Exception as e:
            # Encadenamiento de excepciones (raise ... from ...)
            logger.error(f"Error al procesar reserva [{self._id}]: {e}")
            raise ReservaValidacionError(
                f"Error al calcular el costo: {e}", "costo"
            ) from e
        else:
            # Solo se ejecuta si no hubo excepción
            if self._estado == EstadoReserva.PENDIENTE:
                self.confirmar()
            operacion_exitosa = True
            logger.info(
                f"Reserva [{self._id}] procesada exitosamente. "
                f"Costo: ${self._costo_total:,.0f}"
            )
        finally:
            # Siempre se ejecuta, haya o no error
            estado_log = "ÉXITO" if operacion_exitosa else "FALLO"
            logger.info(
                f"[FINALLY] Operación procesar reserva [{self._id}]: {estado_log}"
            )

        return self._costo_total

    # ─── Implementaciones de EntidadBase ─────────────────────────────────

    def validar(self) -> bool:
        """Valida la reserva completa incluyendo cliente y servicio.

        Raises:
            ReservaValidacionError: Si algún dato es inválido.
        """
        try:
            self._cliente.validar()
            self._servicio.validar()
            validar_numero_positivo(self._duracion, "duración")
        except ValidacionError as e:
            raise ReservaValidacionError(
                f"Validación de reserva fallida: {e}", ""
            ) from e
        return True

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "cliente": self._cliente.to_dict(),
            "servicio": self._servicio.to_dict(),
            "fecha_reserva": self._fecha_reserva_str,
            "duracion": self._duracion,
            "unidad_duracion": self._unidad_duracion,
            "estado": self._estado.value,
            "costo_total": self._costo_total,
            "fecha_creacion": self._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_estado_cambio": self._fecha_estado_cambio.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self) -> str:
        return (
            f"Reserva [{self._id}] — {self._cliente.nombre} → "
            f"{self._servicio.nombre} | {self._estado.value} | "
            f"${self._costo_total:,.0f}"
        )
