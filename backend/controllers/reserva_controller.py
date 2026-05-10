# =============================================================================
# reserva_controller.py — Controlador de operaciones sobre Reservas
# =============================================================================
"""
Módulo controlador para la gestión del ciclo de vida de Reservas.

Este módulo orquesta la creación, procesamiento, validación y gestión de las reservas
en el sistema. Actúa como integrador entre los modelos Cliente, Servicio y Reserva,
asegurando que las reglas de negocio, como la disponibilidad de recursos y las
transiciones de estado (ej: PENDIENTE -> CONFIRMADA -> EN_CURSO), se cumplan
estrictamente.
"""
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
    """
    Controlador que orquesta las operaciones integrales sobre reservas.

    Gestiona el ciclo de vida completo de cada reserva, desde su creación inicial,
    pasando por la validación de disponibilidad del servicio asociado, el procesamiento
    de costos (impuestos, descuentos) y todas las subsecuentes transiciones de estado.
    Mantiene un registro en memoria de todas las reservas activas e históricas.

    Attributes:
        _reservas (list[Reserva]): Almacenamiento interno de todas las reservas gestionadas.
    """

    def __init__(self):
        """Inicializa el controlador con un historial vacío de reservas."""
        self._reservas: list = []

    @property
    def reservas(self) -> list:
        """
        Obtiene una copia segura de la lista completa de reservas.

        Returns:
            list[Reserva]: Copia superficial de la lista interna de reservas.
        """
        return self._reservas.copy()

    @property
    def total_reservas(self) -> int:
        """
        Calcula la cantidad total de reservas registradas en el controlador.

        Returns:
            int: Número de reservas en el historial.
        """
        return len(self._reservas)

    def crear_reserva(self, cliente: Cliente, servicio: Servicio,
                      fecha_reserva: str, duracion: float,
                      unidad_duracion: str = "hora",
                      *, impuesto: float = 0.0, descuento: float = 0.0,
                      **kwargs) -> Reserva:
        """
        Crea, valida disponibilidad, calcula el costo y confirma una nueva reserva.

        Este método orquesta un flujo complejo de 4 pasos principales:
        1. Instancia la reserva en estado inicial (PENDIENTE).
        2. Verifica que el servicio seleccionado tenga disponibilidad en la fecha requerida.
        3. Procesa los cálculos financieros aplicando impuestos y descuentos.
        4. Si todo es exitoso, registra la ocupación efectiva del recurso y almacena la reserva.

        Se utiliza un bloque `try/except/else` para asegurar que el recurso sólo
        se ocupe si todo el proceso lógico previo fue exitoso.

        Args:
            cliente (Cliente): El objeto del cliente que solicita la reserva.
            servicio (Servicio): El objeto del servicio (Sala, Equipo, Asesoría) a reservar.
            fecha_reserva (str): Fecha de la reserva en formato "YYYY-MM-DD".
            duracion (float): Magnitud de la duración solicitada.
            unidad_duracion (str, optional): Unidad de tiempo ("hora" o "dia"). Por defecto "hora".
            impuesto (float, optional): Porcentaje impositivo a aplicar (ej. 0.19 para 19%). Por defecto 0.0.
            descuento (float, optional): Porcentaje de descuento (ej. 0.10 para 10%). Por defecto 0.0.
            **kwargs: Argumentos adicionales específicos para cada tipo de servicio 
                      (ej: `hora_inicio`, `hora_fin`, `cantidad`).

        Returns:
            Reserva: El objeto de la reserva completamente procesado y almacenado.

        Raises:
            ReservaValidacionError: Si algún dato provisto es inválido semánticamente.
            DisponibilidadError: Si el recurso/servicio no está disponible en esa fecha/hora.
            OperacionError: Si ocurre un fallo inesperado durante la orquestación.
            TransicionEstadoError: Si hay un error interno al intentar cambiar de estado.
        """
        reserva = None
        try:
            # 1. Crear reserva en memoria (PENDIENTE)
            reserva = Reserva(cliente, servicio, fecha_reserva, duracion, unidad_duracion)

            # 2. Validar disponibilidad dinámica según tipo de servicio
            params_disponibilidad = {"fecha": fecha_reserva}
            params_disponibilidad.update(kwargs)
            servicio.validar_disponibilidad(**params_disponibilidad)

            # 3. Procesar cálculos y transiciones de negocio
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
            # 4. Bloque else: Solo se ejecuta si NO hubo excepciones en el try.
            # Aquí garantizamos que la ocupación se registre en el servicio respectivo.
            self._registrar_ocupacion(servicio, fecha_reserva, **kwargs)
            self._reservas.append(reserva)
            logger.info(
                f"Reserva completada [{reserva.id}]: "
                f"{cliente.nombre} → {servicio.nombre} = ${reserva.costo_total:,.0f}"
            )

        return reserva

    def _registrar_ocupacion(self, servicio: Servicio, fecha: str, **kwargs) -> None:
        """
        Registra la ocupación de un recurso en el servicio correspondiente tras una reserva exitosa.

        Despacha la lógica de ocupación utilizando polimorfismo o verificación de tipos (isinstance)
        para invocar los métodos concretos de cada subclase de Servicio.

        Args:
            servicio (Servicio): Instancia del servicio reservado.
            fecha (str): Fecha en la que ocurre la ocupación.
            **kwargs: Parámetros adicionales (hora_inicio, hora_fin, cantidad, hora) requeridos
                      dependiendo de la naturaleza del servicio.
        """
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
        """
        Libera la disponibilidad de un recurso previamente ocupado.

        Se llama típicamente cuando una reserva es cancelada o el cliente no asiste.

        Args:
            reserva (Reserva): El objeto de reserva cuya ocupación se desea revertir.
        """
        servicio = reserva.servicio
        if isinstance(servicio, ReservaSala):
            # Intentar liberar los horarios exactos asociados a esta reserva
            for fecha, inicio, fin in servicio.reservas_horario:
                if fecha == reserva.fecha_reserva:
                    servicio.liberar_reserva_horario(fecha, inicio, fin)
                    break
        elif isinstance(servicio, AlquilerEquipo):
            servicio.devolver_unidades(1)  # Simplificado para fines de demostración

    # ─── Transiciones de estado ──────────────────────────────────────────

    def confirmar_reserva(self, reserva_id: str) -> Reserva:
        """
        Intenta confirmar una reserva que está en estado PENDIENTE.

        Args:
            reserva_id (str): ID de la reserva.

        Returns:
            Reserva: Objeto modificado.

        Raises:
            ReservaNoEncontradaError: Si la reserva no existe.
            TransicionEstadoError: Si el estado actual de la reserva no permite confirmar.
        """
        reserva = self.buscar_por_id(reserva_id)
        reserva.confirmar()
        return reserva

    def iniciar_reserva(self, reserva_id: str) -> Reserva:
        """
        Marca que la prestación del servicio asociado a una reserva ha comenzado.

        Args:
            reserva_id (str): ID de la reserva.

        Returns:
            Reserva: Objeto modificado a estado EN_CURSO.
        """
        reserva = self.buscar_por_id(reserva_id)
        reserva.iniciar()
        return reserva

    def completar_reserva(self, reserva_id: str) -> Reserva:
        """
        Marca la prestación del servicio como finalizada exitosamente.

        Args:
            reserva_id (str): ID de la reserva.

        Returns:
            Reserva: Objeto modificado a estado COMPLETADA.
        """
        reserva = self.buscar_por_id(reserva_id)
        reserva.completar()
        return reserva

    def cancelar_reserva(self, reserva_id: str) -> Reserva:
        """
        Cancela de manera definitiva una reserva y libera el recurso bloqueado.

        Usa un bloque `try/except/finally` para asegurar que, independientemente 
        del resultado de la transición de estado del objeto `Reserva`, se haga un 
        esfuerzo de limpieza y liberación de recursos subyacentes.

        Args:
            reserva_id (str): Identificador único de la reserva.

        Returns:
            Reserva: La reserva en estado CANCELADA.

        Raises:
            ReservaNoEncontradaError: Si la reserva no existe.
            TransicionEstadoError: Si la reserva ya estaba completada o en un estado irreversible.
        """
        reserva = self.buscar_por_id(reserva_id)
        recurso_liberado = False
        try:
            reserva.cancelar()
        except TransicionEstadoError:
            raise
        finally:
            # Este bloque asegura que siempre intentaremos liberar el recurso 
            # (aún si la transición lógica falla).
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
        """
        Registra que el cliente no se presentó a disfrutar del servicio.

        A nivel lógico, libera también el recurso para que pueda ser aprovechado.

        Args:
            reserva_id (str): ID de la reserva.

        Returns:
            Reserva: Reserva actualizada.
        """
        reserva = self.buscar_por_id(reserva_id)
        reserva.marcar_no_asistio()
        self._liberar_ocupacion(reserva)
        return reserva

    # ─── Búsqueda ────────────────────────────────────────────────────────

    def buscar_por_id(self, reserva_id: str) -> Reserva:
        """
        Busca y retorna una reserva por su identificador único (UUID).

        Args:
            reserva_id (str): ID interno de la reserva.

        Returns:
            Reserva: El objeto de reserva encontrado.

        Raises:
            ReservaNoEncontradaError: Si el identificador no existe en el registro.
        """
        for reserva in self._reservas:
            if reserva.id == reserva_id:
                return reserva
        raise ReservaNoEncontradaError(reserva_id)

    def buscar_por_cliente(self, cliente_id: str) -> list:
        """
        Encuentra todas las reservas asociadas a un cliente específico.

        Args:
            cliente_id (str): UUID del cliente en cuestión.

        Returns:
            list[Reserva]: Lista de reservas solicitadas por ese cliente.
        """
        return [r for r in self._reservas if r.cliente.id == cliente_id]

    def buscar_por_estado(self, estado: EstadoReserva) -> list:
        """
        Filtra las reservas según su estado actual.

        Args:
            estado (EstadoReserva): Miembro del enum de estados.

        Returns:
            list[Reserva]: Colección de reservas que se encuentran en el estado provisto.
        """
        return [r for r in self._reservas if r.estado == estado]

    def buscar_por_fecha(self, fecha: str) -> list:
        """
        Obtiene el subconjunto de reservas programadas para un día en particular.

        Args:
            fecha (str): Fecha a consultar (formato YYYY-MM-DD).

        Returns:
            list[Reserva]: Reservas correspondientes a esa fecha.
        """
        return [r for r in self._reservas if r.fecha_reserva == fecha]

    # ─── Estadísticas ────────────────────────────────────────────────────

    def obtener_resumen(self) -> dict:
        """
        Genera un reporte resumido de métricas y estadísticas sobre las reservas.

        Calcula totales por estado, así como la sumatoria de ingresos (excluyendo
        las reservas canceladas o no asistidas).

        Returns:
            dict: Diccionario que contiene las métricas (ej. total, confirmada, ingresos_totales).
        """
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
