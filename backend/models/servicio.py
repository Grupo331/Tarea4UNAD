# =============================================================================
# servicio.py — Jerarquía de servicios con polimorfismo y sobrecarga
# =============================================================================
# Servicio (ABC) → ReservaSala, AlquilerEquipo, AsesoriaEspecializada
# Cada subclase sobrescribe calcular_costo() con lógica propia (polimorfismo)
# y acepta parámetros opcionales para simular sobrecarga de métodos.
# =============================================================================

from abc import abstractmethod
from backend.models.base import EntidadBase
from backend.exceptions.excepciones import (
    ServicioValidacionError, SalaNoDisponibleError,
    EquipoSinStockError, AsesorNoDisponibleError
)
from backend.utils.validadores import validar_no_vacio, validar_numero_positivo, validar_opcion
from backend.utils.logger_config import obtener_logger

logger = obtener_logger("models.servicio")


# =============================================================================
# Clase Abstracta: Servicio
# =============================================================================

class Servicio(EntidadBase):
    """Clase abstracta base para todos los servicios de Software FJ.

    Define el contrato que deben cumplir todos los servicios:
    - calcular_costo(): con soporte para impuestos y descuentos (sobrecarga)
    - obtener_descripcion(): descripción legible del servicio
    - validar_disponibilidad(): verificar si el servicio está disponible

    El método calcular_costo() acepta parámetros opcionales (impuesto, descuento)
    para simular sobrecarga de métodos en Python de forma idiomática.

    Attributes:
        _nombre (str): Nombre del servicio.
        _tarifa_hora (float): Costo por hora en COP.
        _tarifa_dia (float): Costo por día en COP.
    """

    def __init__(self, nombre: str, tarifa_hora: float, tarifa_dia: float):
        super().__init__()
        self._nombre = validar_no_vacio(nombre, "nombre del servicio")
        self._tarifa_hora = validar_numero_positivo(tarifa_hora, "tarifa por hora")
        self._tarifa_dia = validar_numero_positivo(tarifa_dia, "tarifa por día")

    # ─── Properties ──────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def tarifa_dia(self) -> float:
        return self._tarifa_dia

    # ─── Método con "sobrecarga" via kwargs ──────────────────────────────

    @abstractmethod
    def calcular_costo(self, duracion: float, unidad: str = "hora",
                       *, impuesto: float = 0.0, descuento: float = 0.0,
                       **kwargs) -> float:
        """Calcula el costo del servicio según duración y parámetros opcionales.

        Simula sobrecarga de métodos en Python mediante parámetros opcionales:
        - Variante 1: calcular_costo(2, "hora")                → costo base
        - Variante 2: calcular_costo(1, "dia", impuesto=0.19)  → con IVA
        - Variante 3: calcular_costo(3, "hora", impuesto=0.19, descuento=0.10) → IVA + descuento

        Args:
            duracion: Cantidad de horas o días.
            unidad: "hora" o "dia".
            impuesto: Porcentaje de impuesto (ej: 0.19 para 19%).
            descuento: Porcentaje de descuento (ej: 0.10 para 10%).
            **kwargs: Parámetros adicionales específicos de cada subclase.

        Returns:
            Costo total calculado en COP.

        Raises:
            ServicioValidacionError: Si los parámetros son inválidos.
        """
        pass

    @abstractmethod
    def obtener_descripcion(self) -> str:
        """Retorna una descripción legible del servicio."""
        pass

    @abstractmethod
    def validar_disponibilidad(self, **kwargs) -> bool:
        """Verifica si el servicio está disponible según los parámetros dados.

        Returns:
            True si está disponible.

        Raises:
            DisponibilidadError: Si no está disponible.
        """
        pass

    # ─── Método protegido de cálculo base ────────────────────────────────

    def _calcular_costo_base(self, duracion: float, unidad: str,
                             impuesto: float, descuento: float) -> float:
        """Cálculo base compartido: tarifa × duración - descuento + impuesto.

        Args:
            duracion: Cantidad de horas o días.
            unidad: "hora" o "dia".
            impuesto: Porcentaje de impuesto.
            descuento: Porcentaje de descuento.

        Returns:
            Subtotal después de aplicar descuento e impuesto.
        """
        duracion = validar_numero_positivo(duracion, "duración")
        unidad = validar_opcion(unidad, ["hora", "dia"], "unidad de tiempo")

        tarifa = self._tarifa_hora if unidad == "hora" else self._tarifa_dia
        subtotal = tarifa * duracion

        # Aplicar descuento primero, luego impuesto
        if descuento > 0:
            subtotal -= subtotal * descuento
        if impuesto > 0:
            subtotal += subtotal * impuesto

        return round(subtotal, 2)

    # ─── Implementaciones de EntidadBase ─────────────────────────────────

    def validar(self) -> bool:
        validar_no_vacio(self._nombre, "nombre")
        validar_numero_positivo(self._tarifa_hora, "tarifa hora")
        validar_numero_positivo(self._tarifa_dia, "tarifa día")
        return True

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "tipo": self.__class__.__name__,
            "nombre": self._nombre,
            "tarifa_hora": self._tarifa_hora,
            "tarifa_dia": self._tarifa_dia,
            "fecha_creacion": self._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self._nombre}"


# =============================================================================
# Servicio Concreto 1: Reserva de Sala
# =============================================================================

class ReservaSala(Servicio):
    """Servicio de reserva de salas con validación de conflictos de horario.

    Tipos: reunión, capacitación, coworking.
    Polimorfismo: recargo del 20% si la capacidad supera 20 personas.

    Attributes:
        _capacidad (int): Capacidad máxima de la sala en personas.
        _tipo_sala (str): Tipo de sala (reunión, capacitación, coworking).
        _reservas_horario (list): Lista de tuplas (fecha, hora_inicio, hora_fin)
            para validación de conflictos.
    """

    TIPOS_SALA = ["reunión", "capacitación", "coworking"]

    def __init__(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                 capacidad: int, tipo_sala: str):
        super().__init__(nombre, tarifa_hora, tarifa_dia)
        self._capacidad = int(capacidad)
        self._tipo_sala = validar_opcion(tipo_sala, self.TIPOS_SALA, "tipo de sala")
        self._reservas_horario: list = []  # [(fecha_str, hora_inicio, hora_fin), ...]
        logger.info(f"Sala creada: {nombre} (Tipo: {tipo_sala}, Capacidad: {capacidad})")

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def tipo_sala(self) -> str:
        return self._tipo_sala

    @property
    def reservas_horario(self) -> list:
        return self._reservas_horario.copy()

    def calcular_costo(self, duracion: float, unidad: str = "hora",
                       *, impuesto: float = 0.0, descuento: float = 0.0,
                       **kwargs) -> float:
        """Calcula el costo de la reserva de sala.

        Polimorfismo: aplica recargo del 20% si la capacidad > 20 personas.

        Args:
            duracion: Horas o días de la reserva.
            unidad: "hora" o "dia".
            impuesto: Porcentaje de impuesto.
            descuento: Porcentaje de descuento.

        Returns:
            Costo total en COP.
        """
        costo = self._calcular_costo_base(duracion, unidad, impuesto, descuento)

        # Recargo por sala grande (> 20 personas)
        if self._capacidad > 20:
            recargo = costo * 0.20
            costo += recargo
            logger.debug(f"Recargo por capacidad alta (+20%): +${recargo:,.0f}")

        logger.info(f"Costo calculado para sala '{self._nombre}': ${costo:,.0f}")
        return round(costo, 2)

    def obtener_descripcion(self) -> str:
        return (
            f"Sala de {self._tipo_sala} '{self._nombre}' — "
            f"Capacidad: {self._capacidad} personas — "
            f"Tarifa: ${self._tarifa_hora:,.0f}/hora | ${self._tarifa_dia:,.0f}/día"
        )

    def validar_disponibilidad(self, **kwargs) -> bool:
        """Valida que la sala no tenga conflicto de horario.

        Args:
            **kwargs: Debe incluir 'fecha', 'hora_inicio', 'hora_fin' como strings.

        Returns:
            True si está disponible.

        Raises:
            SalaNoDisponibleError: Si hay conflicto de horario.
            ServicioValidacionError: Si faltan datos requeridos.
        """
        fecha = kwargs.get("fecha", "")
        hora_inicio = kwargs.get("hora_inicio", "")
        hora_fin = kwargs.get("hora_fin", "")

        if not all([fecha, hora_inicio, hora_fin]):
            raise ServicioValidacionError(
                "Se requiere fecha, hora_inicio y hora_fin para validar disponibilidad"
            )

        # Verificar conflictos con reservas existentes
        for reserva_fecha, reserva_inicio, reserva_fin in self._reservas_horario:
            if reserva_fecha == fecha:
                # Hay conflicto si los rangos se solapan
                if hora_inicio < reserva_fin and hora_fin > reserva_inicio:
                    horario = f"{fecha} {hora_inicio}-{hora_fin}"
                    raise SalaNoDisponibleError(self._nombre, horario)

        return True

    def registrar_reserva_horario(self, fecha: str, hora_inicio: str, hora_fin: str) -> None:
        """Registra un horario como ocupado tras confirmar una reserva."""
        self._reservas_horario.append((fecha, hora_inicio, hora_fin))
        logger.info(f"Horario registrado en sala '{self._nombre}': {fecha} {hora_inicio}-{hora_fin}")

    def liberar_reserva_horario(self, fecha: str, hora_inicio: str, hora_fin: str) -> None:
        """Libera un horario previamente reservado (cancelación)."""
        tupla = (fecha, hora_inicio, hora_fin)
        if tupla in self._reservas_horario:
            self._reservas_horario.remove(tupla)
            logger.info(f"Horario liberado en sala '{self._nombre}': {fecha} {hora_inicio}-{hora_fin}")

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update({
            "capacidad": self._capacidad,
            "tipo_sala": self._tipo_sala,
            "reservas_activas": len(self._reservas_horario),
        })
        return datos


# =============================================================================
# Servicio Concreto 2: Alquiler de Equipo
# =============================================================================

class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos con control de stock.

    Tipos iniciales: laptop, proyector, impresora (extensible).
    Polimorfismo: el costo se multiplica por la cantidad de unidades.

    Attributes:
        _tipo_equipo (str): Tipo del equipo.
        _stock_total (int): Stock total disponible.
        _stock_disponible (int): Unidades actualmente disponibles.
    """

    def __init__(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                 tipo_equipo: str, stock_total: int = 100):
        # Equipos no se cobran por hora, pero mantenemos la interfaz uniforme
        super().__init__(nombre, tarifa_hora, tarifa_dia)
        self._tipo_equipo = validar_no_vacio(tipo_equipo, "tipo de equipo")
        self._stock_total = int(stock_total)
        self._stock_disponible = self._stock_total
        logger.info(f"Equipo creado: {nombre} (Tipo: {tipo_equipo}, Stock: {stock_total})")

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def stock_total(self) -> int:
        return self._stock_total

    @property
    def stock_disponible(self) -> int:
        return self._stock_disponible

    def calcular_costo(self, duracion: float, unidad: str = "dia",
                       *, impuesto: float = 0.0, descuento: float = 0.0,
                       cantidad: int = 1, **kwargs) -> float:
        """Calcula el costo del alquiler multiplicado por cantidad de unidades.

        Polimorfismo: extiende el cálculo base multiplicando por unidades.

        Args:
            duracion: Días de alquiler.
            unidad: "hora" o "dia" (equipos normalmente por día).
            impuesto: Porcentaje de impuesto.
            descuento: Porcentaje de descuento.
            cantidad: Número de unidades a alquilar.

        Returns:
            Costo total en COP.
        """
        cantidad = max(1, int(cantidad))
        costo_unitario = self._calcular_costo_base(duracion, unidad, impuesto, descuento)
        costo_total = costo_unitario * cantidad

        logger.info(
            f"Costo calculado para equipo '{self._nombre}': "
            f"{cantidad} uds × ${costo_unitario:,.0f} = ${costo_total:,.0f}"
        )
        return round(costo_total, 2)

    def obtener_descripcion(self) -> str:
        return (
            f"Equipo '{self._nombre}' ({self._tipo_equipo}) — "
            f"Stock: {self._stock_disponible}/{self._stock_total} — "
            f"Tarifa: ${self._tarifa_dia:,.0f}/día"
        )

    def validar_disponibilidad(self, **kwargs) -> bool:
        """Verifica que haya stock suficiente.

        Args:
            **kwargs: Debe incluir 'cantidad' (int).

        Returns:
            True si hay stock suficiente.

        Raises:
            EquipoSinStockError: Si no hay unidades suficientes.
        """
        cantidad = kwargs.get("cantidad", 1)
        cantidad = max(1, int(cantidad))

        if cantidad > self._stock_disponible:
            raise EquipoSinStockError(
                self._tipo_equipo, cantidad, self._stock_disponible
            )
        return True

    def reservar_unidades(self, cantidad: int) -> None:
        """Reduce el stock disponible al confirmar un alquiler.

        Args:
            cantidad: Número de unidades a reservar.

        Raises:
            EquipoSinStockError: Si no hay suficiente stock.
        """
        self.validar_disponibilidad(cantidad=cantidad)
        self._stock_disponible -= cantidad
        logger.info(
            f"Stock actualizado '{self._nombre}': "
            f"-{cantidad} → {self._stock_disponible} disponibles"
        )

    def devolver_unidades(self, cantidad: int) -> None:
        """Incrementa el stock al devolver equipos o cancelar."""
        self._stock_disponible = min(
            self._stock_disponible + cantidad,
            self._stock_total
        )
        logger.info(
            f"Equipos devueltos '{self._nombre}': "
            f"+{cantidad} → {self._stock_disponible} disponibles"
        )

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update({
            "tipo_equipo": self._tipo_equipo,
            "stock_total": self._stock_total,
            "stock_disponible": self._stock_disponible,
        })
        return datos


# =============================================================================
# Servicio Concreto 3: Asesoría Especializada
# =============================================================================

class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada por área temática.

    Áreas: legal, contable, técnica (extensible).
    Polimorfismo: recargo del 15% para asesorías legales.
    Soporta asignación de objetos Asesor vinculados por especialidad.

    Attributes:
        _area_tematica (str): Área de la asesoría.
        _asesor_obj: Objeto Asesor asignado (puede ser None).
        _horarios_ocupados (list): Horarios ya reservados.
    """

    AREAS_TEMATICAS = ["legal", "contable", "técnica"]

    def __init__(self, nombre: str, tarifa_hora: float, tarifa_dia: float,
                 area_tematica: str, asesor=None):
        super().__init__(nombre, tarifa_hora, tarifa_dia)
        self._area_tematica = validar_opcion(area_tematica, self.AREAS_TEMATICAS, "área temática")
        self._asesor_obj = None  # Objeto Asesor o None
        if asesor is not None:
            self.asignar_asesor(asesor)
        self._horarios_ocupados: list = []
        logger.info(
            f"Asesoría creada: {nombre} (Área: {area_tematica}, Asesor: {self.asesor_nombre})"
        )

    @property
    def area_tematica(self) -> str:
        return self._area_tematica

    @property
    def asesor_obj(self):
        """Objeto Asesor asignado (puede ser None)."""
        return self._asesor_obj

    @property
    def asesor_nombre(self) -> str:
        """Nombre del asesor asignado o 'Sin asignar'."""
        if self._asesor_obj is not None:
            return self._asesor_obj.nombre
        return "Sin asignar"

    @property
    def asesor(self) -> str:
        """Nombre del asesor (compatibilidad con código existente)."""
        return self.asesor_nombre

    def asignar_asesor(self, asesor) -> None:
        """Asigna un asesor a esta asesoría, validando la especialidad.

        El asesor debe tener la misma especialidad que el área temática
        de la asesoría, o no tener especialidad definida.

        Args:
            asesor: Objeto Asesor a asignar.

        Raises:
            ServicioValidacionError: Si la especialidad no coincide.
        """
        # Importación local para evitar dependencia circular
        from backend.models.asesor import Asesor

        if not isinstance(asesor, Asesor):
            raise ServicioValidacionError(
                "Se requiere un objeto Asesor válido", "asesor"
            )

        # Validar que la especialidad coincida (si el asesor tiene una)
        if asesor.especialidad and asesor.especialidad != self._area_tematica:
            raise ServicioValidacionError(
                f"El asesor '{asesor.nombre}' tiene especialidad '{asesor.especialidad}' "
                f"pero esta asesoría es de área '{self._area_tematica}'. "
                f"Solo se pueden asignar asesores con la misma especialidad.",
                "asesor"
            )

        self._asesor_obj = asesor
        logger.info(
            f"Asesor '{asesor.nombre}' asignado a asesoría '{self._nombre}'"
        )

    def remover_asesor(self) -> None:
        """Remueve el asesor asignado a esta asesoría."""
        nombre_anterior = self.asesor_nombre
        self._asesor_obj = None
        logger.info(
            f"Asesor '{nombre_anterior}' removido de asesoría '{self._nombre}'"
        )

    def calcular_costo(self, duracion: float, unidad: str = "hora",
                       *, impuesto: float = 0.0, descuento: float = 0.0,
                       **kwargs) -> float:
        """Calcula el costo de la asesoría.

        Polimorfismo: recargo del 15% para asesorías legales.

        Args:
            duracion: Horas o días de asesoría.
            unidad: "hora" o "dia".
            impuesto: Porcentaje de impuesto.
            descuento: Porcentaje de descuento.

        Returns:
            Costo total en COP.
        """
        costo = self._calcular_costo_base(duracion, unidad, impuesto, descuento)

        # Recargo por asesoría legal (+15%)
        if self._area_tematica == "legal":
            recargo = costo * 0.15
            costo += recargo
            logger.debug(f"Recargo asesoría legal (+15%): +${recargo:,.0f}")

        logger.info(f"Costo calculado para asesoría '{self._nombre}': ${costo:,.0f}")
        return round(costo, 2)

    def obtener_descripcion(self) -> str:
        return (
            f"Asesoría {self._area_tematica} '{self._nombre}' — "
            f"Asesor: {self.asesor_nombre} — "
            f"Tarifa: ${self._tarifa_hora:,.0f}/hora | ${self._tarifa_dia:,.0f}/día"
        )

    def validar_disponibilidad(self, **kwargs) -> bool:
        """Verifica que el horario de asesoría esté libre.

        Args:
            **kwargs: Debe incluir 'fecha' y 'hora'.

        Returns:
            True si está disponible.

        Raises:
            AsesorNoDisponibleError: Si el horario ya está ocupado.
        """
        fecha = kwargs.get("fecha", "")
        hora = kwargs.get("hora", "")

        if not fecha or not hora:
            return True  # Sin datos de horario, se asume disponible

        for ocupado_fecha, ocupado_hora in self._horarios_ocupados:
            if ocupado_fecha == fecha and ocupado_hora == hora:
                raise AsesorNoDisponibleError(self.asesor_nombre, f"{fecha} {hora}")

        return True

    def registrar_horario(self, fecha: str, hora: str) -> None:
        """Registra un horario como ocupado."""
        self._horarios_ocupados.append((fecha, hora))

    def liberar_horario(self, fecha: str, hora: str) -> None:
        """Libera un horario ocupado."""
        tupla = (fecha, hora)
        if tupla in self._horarios_ocupados:
            self._horarios_ocupados.remove(tupla)

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update({
            "area_tematica": self._area_tematica,
            "asesor": self.asesor_nombre,
            "asesor_id": self._asesor_obj.id if self._asesor_obj else None,
            "asesor_cedula": self._asesor_obj.cedula if self._asesor_obj else None,
            "horarios_ocupados": len(self._horarios_ocupados),
        })
        return datos
