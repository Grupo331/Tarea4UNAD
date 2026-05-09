# =============================================================================
# reserva_controller.py — Controlador de operaciones sobre Reservas
# =============================================================================
# Orquesta la creación, procesamiento y gestión de reservas integrando
# clientes, servicios, validaciones de disponibilidad y transiciones de estado.
# =============================================================================

from backend.models.reserva import Reserva, EstadoReserva
from backend.models.cliente import Cliente
from backend.models.servicio import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from backend.exceptions.excepciones import (
    ReservaValidacionError, ReservaNoEncontradaError,
    TransicionEstadoError, DisponibilidadError, OperacionError
)
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("controllers.reserva")


class ReservaController:
    """Controlador que orquesta las operaciones sobre reservas.

    Gestiona el ciclo de vida completo: creación → validación de
    disponibilidad → procesamiento de costos → transiciones de estado.

    Attributes:
        _reservas (list[Reserva]): Lista de todas las reservas.
    """

    def __init__(self):
        self._reservas: list = []

    @property
    def reservas(self) -> list:
        return self._reservas.copy()

    @property
    def total_reservas(self) -> int:
        return len(self._reservas)

    def crear_reserva(self, cliente: Cliente, servicio: Servicio,
                      fecha_reserva: str, duracion: float,
                      unidad_duracion: str = "hora",
                      *, impuesto: float = 0.0, descuento: float = 0.0,
                      **kwargs) -> Reserva:
        """Crea, valida disponibilidad, calcula costo y confirma la reserva.

        Flujo completo:
        1. Crear la reserva (estado PENDIENTE)
        2. Validar disponibilidad del servicio
        3. Procesar (calcular costo + confirmar)
        4. Registrar ocupación del recurso

        Demuestra try/except/else con encadenamiento:
        - try: crear y procesar la reserva
        - except: captura errores de disponibilidad o validación
        - else: solo si todo fue exitoso, registrar ocupación

        Args:
            cliente: Cliente que reserva.
            servicio: Servicio a reservar.
            fecha_reserva: Fecha (formato "YYYY-MM-DD").
            duracion: Duración del servicio.
            unidad_duracion: "hora" o "dia".
            impuesto: Porcentaje de impuesto.
            descuento: Porcentaje de descuento.
            **kwargs: Parámetros adicionales (hora_inicio, hora_fin, cantidad, etc.)

        Returns:
            La reserva creada y confirmada.

        Raises:
            ReservaValidacionError: Si los datos son inválidos.
            DisponibilidadError: Si el servicio no está disponible.
        """
        reserva = None
        try:
            # 1. Crear reserva
            reserva = Reserva(cliente, servicio, fecha_reserva, duracion, unidad_duracion)

            # 2. Validar disponibilidad según tipo de servicio
            params_disponibilidad = {"fecha": fecha_reserva}
            params_disponibilidad.update(kwargs)
            servicio.validar_disponibilidad(**params_disponibilidad)

            # 3. Procesar (calcular costo + confirmar)
            reserva.procesar(impuesto=impuesto, descuento=descuento, **kwargs)

        except (ReservaValidacionError, DisponibilidadError, TransicionEstadoError):
            logger.warning(f"Reserva fallida: {type(reserva).__name__ if reserva else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear reserva: {e}")
            raise OperacionError(
                f"Error inesperado al crear reserva: {e}", "crear_reserva"
            ) from e
        else:
            # 4. Solo si todo fue exitoso, registrar ocupación del recurso
            self._registrar_ocupacion(servicio, fecha_reserva, **kwargs)
            self._reservas.append(reserva)
            logger.info(
                f"Reserva completada [{reserva.id}]: "
                f"{cliente.nombre} → {servicio.nombre} = ${reserva.costo_total:,.0f}"
            )

        return reserva

    def _registrar_ocupacion(self, servicio: Servicio, fecha: str, **kwargs) -> None:
        """Registra la ocupación del recurso tras confirmar la reserva."""
        if isinstance(servicio, ReservaSala):
            hora_inicio = kwargs.get("hora_inicio", "")
            hora_fin = kwargs.get("hora_fin", "")
            if hora_inicio and hora_fin:
                servicio.registrar_reserva_horario(fecha, hora_inicio, hora_fin)

        elif isinstance(servicio, AlquilerEquipo):
            cantidad = kwargs.get("cantidad", 1)
            servicio.reservar_unidades(cantidad)

        elif isinstance(servicio, AsesoriaEspecializada):
            hora = kwargs.get("hora", kwargs.get("hora_inicio", ""))
            if hora:
                servicio.registrar_horario(fecha, hora)

    def _liberar_ocupacion(self, reserva: Reserva) -> None:
        """Libera la ocupación del recurso al cancelar una reserva."""
        servicio = reserva.servicio
        if isinstance(servicio, ReservaSala):
            # Intentar liberar horarios asociados
            for fecha, inicio, fin in servicio.reservas_horario:
                if fecha == reserva.fecha_reserva:
                    servicio.liberar_reserva_horario(fecha, inicio, fin)
                    break
        elif isinstance(servicio, AlquilerEquipo):
            servicio.devolver_unidades(1)  # Simplificado

    # ─── Transiciones de estado ──────────────────────────────────────────

    def confirmar_reserva(self, reserva_id: str) -> Reserva:
        """Confirma una reserva pendiente."""
        reserva = self.buscar_por_id(reserva_id)
        reserva.confirmar()
        return reserva

    def iniciar_reserva(self, reserva_id: str) -> Reserva:
        """Marca una reserva confirmada como en curso."""
        reserva = self.buscar_por_id(reserva_id)
        reserva.iniciar()
        return reserva

    def completar_reserva(self, reserva_id: str) -> Reserva:
        """Marca una reserva en curso como completada."""
        reserva = self.buscar_por_id(reserva_id)
        reserva.completar()
        return reserva

    def cancelar_reserva(self, reserva_id: str) -> Reserva:
        """Cancela una reserva y libera el recurso.

        Demuestra try/except/finally:
        - try: cambiar estado a CANCELADA
        - except: si falla la transición
        - finally: siempre intentar liberar el recurso
        """
        reserva = self.buscar_por_id(reserva_id)
        recurso_liberado = False
        try:
            reserva.cancelar()
        except TransicionEstadoError:
            raise
        finally:
            # Siempre intentar liberar el recurso (incluso si falla la transición)
            try:
                self._liberar_ocupacion(reserva)
                recurso_liberado = True
            except Exception as e:
                logger.warning(f"No se pudo liberar recurso de reserva [{reserva_id}]: {e}")
            logger.info(
                f"[FINALLY] Cancelación [{reserva_id}]: recurso_liberado={recurso_liberado}"
            )
        return reserva

    def marcar_no_asistio(self, reserva_id: str) -> Reserva:
        """Marca una reserva confirmada como No Asistió."""
        reserva = self.buscar_por_id(reserva_id)
        reserva.marcar_no_asistio()
        self._liberar_ocupacion(reserva)
        return reserva

    # ─── Búsqueda ────────────────────────────────────────────────────────

    def buscar_por_id(self, reserva_id: str) -> Reserva:
        """Busca una reserva por su ID.

        Raises:
            ReservaNoEncontradaError: Si no se encuentra.
        """
        for reserva in self._reservas:
            if reserva.id == reserva_id:
                return reserva
        raise ReservaNoEncontradaError(reserva_id)

    def buscar_por_cliente(self, cliente_id: str) -> list:
        """Retorna todas las reservas de un cliente."""
        return [r for r in self._reservas if r.cliente.id == cliente_id]

    def buscar_por_estado(self, estado: EstadoReserva) -> list:
        """Retorna todas las reservas con un estado específico."""
        return [r for r in self._reservas if r.estado == estado]

    def buscar_por_fecha(self, fecha: str) -> list:
        """Retorna todas las reservas de una fecha específica."""
        return [r for r in self._reservas if r.fecha_reserva == fecha]

    # ─── Estadísticas ────────────────────────────────────────────────────

    def obtener_resumen(self) -> dict:
        """Resumen de reservas para el dashboard."""
        resumen = {"total": len(self._reservas)}
        for estado in EstadoReserva:
            resumen[estado.value.lower()] = len(
                [r for r in self._reservas if r.estado == estado]
            )
        resumen["ingresos_totales"] = sum(
            r.costo_total for r in self._reservas
            if r.estado in (EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO,
                            EstadoReserva.COMPLETADA)
        )
        return resumen
