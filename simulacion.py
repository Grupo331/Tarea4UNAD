# =============================================================================
# simulacion.py — 12 operaciones de simulación (válidas e inválidas)
# =============================================================================
"""
Este módulo actúa como una suite de pruebas de integración y demostración funcional.

Su propósito es validar el comportamiento del motor lógico del sistema (Backend)
sin necesidad de interactuar con la interfaz gráfica. Permite verificar la 
integridad de las reglas de negocio, la correcta propagación de excepciones 
personalizadas, el cálculo polimórfico de tarifas y el flujo de estados de 
las reservas, asegurando que el sistema sea robusto ante datos correctos y erróneos.
"""
# =============================================================================
# Demuestra el funcionamiento completo del sistema sin interfaz gráfica:
# - Creación de clientes y servicios
# - Reservas exitosas y fallidas
# - Polimorfismo en cálculo de costos
# - Sobrecarga de métodos (kwargs)
# - Excepciones personalizadas y encadenamiento
# - Transiciones de estado válidas e inválidas
# - Logging de todas las operaciones
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.logger_config import configurar_logging, obtener_logger
from backend.controllers.cliente_controller import ClienteController
from backend.controllers.servicio_controller import ServicioController
from backend.controllers.reserva_controller import ReservaController
from backend.models.catalogo import CatalogoServicios
from backend.exceptions.excepciones import (
    ClienteValidacionError, EquipoSinStockError, SalaNoDisponibleError,
    TransicionEstadoError, ClienteNoEncontradoError, OperacionError,
    ReservaValidacionError
)

# Inicializar el sistema de logging para capturar la trazabilidad de la simulación
configurar_logging()
logger = obtener_logger("simulacion")


def separador(titulo: str) -> None:
    """
    Genera un separador visual estandarizado en la consola.
    
    Args:
        titulo (str): Texto que se mostrará centrado en el separador.
    """
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


def operacion(numero: int, descripcion: str, tipo: str) -> None:
    """
    Imprime el encabezado de una prueba específica y lo registra en los logs.
    
    Args:
        numero (int): Índice correlativo de la operación.
        descripcion (str): Resumen de lo que se intenta probar.
        tipo (str): Categoría de la prueba ('valida' o 'invalida').
    """
    emoji = "✅" if tipo == "valida" else "❌"
    print(f"\n--- Operación {numero}: {emoji} {descripcion} ({tipo.upper()}) ---")
    logger.info(f"SIMULACIÓN - Operación {numero}: {descripcion}")


def ejecutar_simulacion():
    """
    Orquesta la ejecución de las 12 pruebas lógicas definidas en el plan de implementación.
    
    La función inicializa los controladores necesarios y ejecuta secuencialmente 
    casos de uso que cubren el CRUD de clientes, gestión de inventario, 
    conflictos de disponibilidad y la máquina de estados de las reservas.
    """

    # ─── Inicialización ──────────────────────────────────────────────
    # Se instancian los controladores que gestionan la lógica de negocio en memoria.
    separador("INICIALIZACIÓN DEL SISTEMA")
    
    # El catálogo precarga los servicios definidos en la configuración
    catalogo = CatalogoServicios()
    
    # Inyección de dependencias en los controladores
    cliente_ctrl = ClienteController()
    servicio_ctrl = ServicioController(catalogo)
    reserva_ctrl = ReservaController()
    
    print(f"Catálogo cargado: {servicio_ctrl.obtener_resumen()}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 1: Crear cliente válido ✅
    # Demuestra: Encapsulación, validación en properties
    # ═══════════════════════════════════════════════════════════════════
    operacion(1, "Crear cliente válido", "valida")
    try:
        # Se intenta crear un cliente con todos los campos correctos.
        # El controlador valida internamente mediante @property.setters.
        cliente1 = cliente_ctrl.crear_cliente(
            "Juan Carlos Pérez", "12345678", "3001234567", "juan@email.com"
        )
        print(f"  → {cliente1}")
        print(f"  → ID: {cliente1.id}, Creado: {cliente1.fecha_creacion}")
    except Exception as e:
        print(f"  → ERROR: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 2: Crear cliente con email inválido ❌
    # Demuestra: ClienteValidacionError, raise...from (encadenamiento)
    # ═══════════════════════════════════════════════════════════════════
    operacion(2, "Crear cliente con email inválido", "invalida")
    try:
        # El sistema de validación debe detectar que el email no cumple con el Regex 
        # y lanzar una excepción controlada.
        cliente_malo = cliente_ctrl.crear_cliente(
            "María López", "87654321", "3009876543", "email-invalido"
        )
    except ClienteValidacionError as e:
        print(f"  → Excepción capturada: {e}")
        print(f"  → Tipo: {type(e).__name__}, Código: {e.codigo}")
        if e.__cause__:
            # Demuestra el uso de 'raise ... from' para rastrear el error original
            print(f"  → Causa original (encadenamiento): {e.__cause__}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 3: Reservar sala disponible por 2 horas ✅
    # Demuestra: Polimorfismo en calcular_costo(), calcular_costo(2, "hora")
    # ═══════════════════════════════════════════════════════════════════
    operacion(3, "Reservar sala disponible por 2 horas (costo base)", "valida")
    try:
        salas = servicio_ctrl.obtener_salas()
        sala_reunion = salas[0]  # Sala Reunión A
        print(f"  → Servicio: {sala_reunion.obtener_descripcion()}")

        # Uso de argumentos posicionales para la configuración básica de la reserva
        reserva1 = reserva_ctrl.crear_reserva(
            cliente1, sala_reunion, "2026-05-10", 2, "hora",
            hora_inicio="09:00", hora_fin="11:00"
        )
        print(f"  → {reserva1}")
        print(f"  → Costo (sin impuestos): ${reserva1.costo_total:,.0f}")
    except Exception as e:
        print(f"  → ERROR: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 4: Reservar la misma sala en horario ocupado ❌
    # Demuestra: SalaNoDisponibleError, validación de conflictos
    # ═══════════════════════════════════════════════════════════════════
    operacion(4, "Reservar sala ya ocupada (conflicto de horario)", "invalida")
    try:
        # Crear otro cliente para esta reserva
        cliente2 = cliente_ctrl.crear_cliente(
            "Ana García", "11223344", "3112233445", "ana@email.com"
        )
        # Intentar reservar la misma sala en horario solapado
        reserva_conflicto = reserva_ctrl.crear_reserva(
            cliente2, sala_reunion, "2026-05-10", 1, "hora",
            hora_inicio="10:00", hora_fin="11:00"
        )
    except SalaNoDisponibleError as e:
        print(f"  → Excepción capturada: {e}")
        print(f"  → Sala: {e.sala}, Horario: {e.horario}")
        # Se valida que no se haya creado una reserva fantasma

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 5: Alquilar 5 laptops por 3 días con IVA ✅
    # Demuestra: Sobrecarga con kwargs (impuesto=0.19, cantidad=5)
    # ═══════════════════════════════════════════════════════════════════
    operacion(5, "Alquilar 5 laptops por 3 días con IVA (sobrecarga)", "valida")
    try:
        equipos = servicio_ctrl.obtener_equipos()
        laptop = equipos[0]  # Laptop
        print(f"  → Servicio: {laptop.obtener_descripcion()}")
        print(f"  → Stock antes: {laptop.stock_disponible}")
        
        # Se pasan argumentos de palabra clave (kwargs) para el cálculo de impuestos y stock
        reserva2 = reserva_ctrl.crear_reserva(
            cliente1, laptop, "2026-05-12", 3, "dia",
            impuesto=0.19, cantidad=5
        )
        print(f"  → {reserva2}")
        print(f"  → Costo (3 días × 5 uds + IVA 19%): ${reserva2.costo_total:,.0f}")
        print(f"  → Stock después: {laptop.stock_disponible}")
    except Exception as e:
        print(f"  → ERROR: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 6: Alquilar más equipos que stock disponible ❌
    # Demuestra: EquipoSinStockError
    # ═══════════════════════════════════════════════════════════════════
    operacion(6, "Alquilar más equipos que stock disponible", "invalida")
    try:
        # Se solicita una cantidad astronómica (200) para forzar el error de 
        # disponibilidad de inventario físico.
        reserva_sin_stock = reserva_ctrl.crear_reserva(
            cliente2, laptop, "2026-05-15", 1, "dia",
            cantidad=200  # Más que el stock disponible
        )
    except EquipoSinStockError as e:
        print(f"  → Excepción capturada: {e}")
        print(f"  → Tipo equipo: {e.tipo_equipo}")
        print(f"  → Solicitado: {e.solicitado}, Disponible: {e.disponible}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 7: Asesoría legal 1 hora + descuento + IVA ✅
    # Demuestra: Sobrecarga completa (impuesto + descuento), recargo legal
    # ═══════════════════════════════════════════════════════════════════
    operacion(7, "Asesoría legal 1 hora con descuento 10% + IVA (sobrecarga completa)", "valida")
    try:
        asesorias = servicio_ctrl.obtener_asesorias()
        asesoria_legal = asesorias[0]  # Asesoría Legal
        print(f"  → Servicio: {asesoria_legal.obtener_descripcion()}")

        # Esta prueba combina lógica de impuestos, descuentos y un recargo 
        # interno del 15% aplicado por la clase AsesoriaEspecializada.
        reserva3 = reserva_ctrl.crear_reserva(
            cliente2, asesoria_legal, "2026-05-14", 1, "hora",
            impuesto=0.19, descuento=0.10,
            hora_inicio="14:00"
        )
        print(f"  → {reserva3}")
        print(f"  → Costo (1hr legal + desc 10% + IVA 19% + recargo 15%): ${reserva3.costo_total:,.0f}")
    except Exception as e:
        print(f"  → ERROR: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 8: Confirmar → Iniciar → Completar reserva ✅
    # Demuestra: Flujo completo de estados
    # ═══════════════════════════════════════════════════════════════════
    operacion(8, "Flujo completo de estados: Confirmada → En Curso → Completada", "valida")
    try:
        print(f"  → Estado actual: {reserva1.estado.value}")
        
        # La reserva ya está CONFIRMADA por el proceso de creación
        reserva_ctrl.iniciar_reserva(reserva1.id)
        print(f"  → Después de iniciar: {reserva1.estado.value}")
        reserva_ctrl.completar_reserva(reserva1.id)
        print(f"  → Después de completar: {reserva1.estado.value}")
    except Exception as e:
        print(f"  → ERROR: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 9: Cancelar reserva ya completada ❌
    # Demuestra: TransicionEstadoError
    # ═══════════════════════════════════════════════════════════════════
    operacion(9, "Cancelar reserva ya completada (transición inválida)", "invalida")
    try:
        # Un estado 'COMPLETADA' es final; intentar cancelarla debe violar la máquina de estados.
        reserva_ctrl.cancelar_reserva(reserva1.id)
    except TransicionEstadoError as e:
        print(f"  → Excepción capturada: {e}")
        print(f"  → Estado actual: {e.estado_actual}, Destino: {e.estado_destino}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 10: Buscar cliente inexistente ❌
    # Demuestra: ClienteNoEncontradoError
    # ═══════════════════════════════════════════════════════════════════
    operacion(10, "Buscar cliente inexistente", "invalida")
    try:
        # Prueba de manejo de errores en operaciones de búsqueda por identificador único.
        cliente_fantasma = cliente_ctrl.buscar_por_cedula("99999999")
    except ClienteNoEncontradoError as e:
        print(f"  → Excepción capturada: {e}")
        print(f"  → Código: {e.codigo}, ID buscado: {e.entidad_id}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 11: Crear reserva con cliente inválido ❌
    # Demuestra: raise...from... (encadenamiento de excepciones)
    # ═══════════════════════════════════════════════════════════════════
    operacion(11, "Crear reserva con objeto cliente inválido (encadenamiento)", "invalida")
    try:
        # Se envía un tipo de dato erróneo para disparar el encadenamiento de excepciones.
        reserva_mala = reserva_ctrl.crear_reserva(
            "no_soy_un_cliente", sala_reunion, "2026-05-20", 1, "hora",
            hora_inicio="15:00", hora_fin="16:00"
        )
    except (ReservaValidacionError, OperacionError) as e:
        print(f"  → Excepción capturada: {e}")
        print(f"  → Tipo: {type(e).__name__}")
        if e.__cause__:
            print(f"  → Causa encadenada (__cause__): {e.__cause__}")

    # ═══════════════════════════════════════════════════════════════════
    # OPERACIÓN 12: Confirmar → Marcar No Asistió ✅
    # Demuestra: Estado NO_ASISTIO
    # ═══════════════════════════════════════════════════════════════════
    operacion(12, "Reserva → Confirmar → Marcar No Asistió", "valida")
    try:
        # Crear nueva reserva para esta demo
        salas = servicio_ctrl.obtener_salas()
        sala_cap = salas[1]  # Sala Capacitación A

        reserva4 = reserva_ctrl.crear_reserva(
            cliente2, sala_cap, "2026-05-18", 1, "dia",
            hora_inicio="08:00", hora_fin="17:00"
        )
        print(f"  → Estado inicial: {reserva4.estado.value}")
        
        # Ya está confirmada por el proceso
        # Esta operación debe liberar los recursos bloqueados.
        reserva_ctrl.marcar_no_asistio(reserva4.id)
        print(f"  → Estado final: {reserva4.estado.value}")
    except Exception as e:
        print(f"  → ERROR: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════════════════════════
    # Muestra un reporte consolidado del estado de la memoria tras las operaciones.
    separador("RESUMEN FINAL DE LA SIMULACIÓN")

    print(f"\n📊 Clientes registrados: {cliente_ctrl.total_clientes}")
    for c in cliente_ctrl.clientes:
        print(f"   • {c}")

    print(f"\n🔧 Servicios en catálogo: {servicio_ctrl.obtener_resumen()}")

    print(f"\n📅 Reservas totales: {reserva_ctrl.total_reservas}")
    resumen = reserva_ctrl.obtener_resumen()
    for key, value in resumen.items():
        if key != "total":
            print(f"   • {key}: {value}")

    print(f"\n✅ Simulación completada exitosamente.")
    print(f"📋 Revise el archivo logs/app.log para ver todos los eventos registrados.\n")


if __name__ == "__main__":
    ejecutar_simulacion()
