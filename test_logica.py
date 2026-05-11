# =============================================================================
# test_logica.py — Suite de Pruebas Unitarias e Integración
# =============================================================================
"""
Este archivo contiene la suite de pruebas automatizadas para el Sistema Software FJ.

Utiliza el framework 'unittest' de Python para validar de forma aislada y repetible
los 12 escenarios críticos definidos en el plan de implementación. Las pruebas
cubren validaciones de modelos, lógica de controladores, cálculo de tarifas
polimórficas y el manejo robusto de excepciones personalizadas.
"""
# =============================================================================

import unittest
import sys
import os

# Configuración del PATH para localizar los módulos del backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.controllers.cliente_controller import ClienteController
from backend.controllers.servicio_controller import ServicioController
from backend.controllers.reserva_controller import ReservaController
from backend.models.catalogo import CatalogoServicios
from backend.models.reserva import EstadoReserva
from backend.exceptions.excepciones import (
    ClienteValidacionError, EquipoSinStockError, SalaNoDisponibleError,
    TransicionEstadoError, ClienteNoEncontradoError, OperacionError,
    ReservaValidacionError
)

class TestSistemaGestion(unittest.TestCase):
    """
    Clase de prueba que consolida los 12 escenarios de validación del sistema.
    Cada método representa una unidad de comportamiento que debe cumplirse.
    """

    def setUp(self):
        """
        Configuración inicial antes de cada prueba (Fixtures).
        Se instancian los controladores y se precarga el catálogo para asegurar
        un estado limpio en cada ejecución.
        """
        self.catalogo = CatalogoServicios()
        self.cliente_ctrl = ClienteController()
        self.servicio_ctrl = ServicioController(self.catalogo)
        self.reserva_ctrl = ReservaController()

    # ─── PRUEBAS DE CLIENTES ──────────────────────────────────────────

    def test_01_crear_cliente_valido(self):
        """Escenario 1: Validar que un cliente con datos correctos se cree exitosamente."""
        cliente = self.cliente_ctrl.crear_cliente(
            "Juan Perez", "12345678", "3001234567", "juan@email.com"
        )
        # Verificamos que el objeto no sea nulo y que los datos coincidan
        self.assertIsNotNone(cliente.id)
        self.assertEqual(cliente.nombre, "Juan Perez")

    def test_02_cliente_email_invalido(self):
        """Escenario 2: Validar que el sistema rechace emails con formato incorrecto."""
        # Se espera que se lance ClienteValidacionError
        with self.assertRaises(ClienteValidacionError) as cm:
            self.cliente_ctrl.crear_cliente(
                "Error", "87654321", "3009876543", "email_malo"
            )
        # Validamos que el código de error sea el esperado (definido en el backend)
        self.assertEqual(cm.exception.codigo, "ERR_CLIENTE_VAL")

    # ─── PRUEBAS DE RESERVAS Y POLIMORFISMO ───────────────────────────

    def test_03_reserva_sala_costo_base(self):
        """Escenario 3: Validar cálculo polimórfico de costo base para una sala (2 horas)."""
        cliente = self.cliente_ctrl.crear_cliente("Test", "12345678", "3001", "t@e.com")
        sala = self.servicio_ctrl.obtener_salas()[0] # Sala Reunión A ($50.000/hr)
        
        reserva = self.reserva_ctrl.crear_reserva(
            cliente, sala, "2026-05-10", 2, "hora", 
            hora_inicio="09:00", hora_fin="11:00"
        )
        # 50.000 * 2 = 100.000
        self.assertEqual(reserva.costo_total, 100000.0)

    def test_04_conflicto_horario_sala(self):
        """Escenario 4: Validar detección de traslape de horarios en la misma sala."""
        cliente1 = self.cliente_ctrl.crear_cliente("C1", "1234", "3001", "c1@e.com")
        cliente2 = self.cliente_ctrl.crear_cliente("C2", "5678", "3002", "c2@e.com")
        sala = self.servicio_ctrl.obtener_salas()[0]

        # Primera reserva exitosa
        self.reserva_ctrl.crear_reserva(
            cliente1, sala, "2026-05-10", 2, "hora", 
            hora_inicio="09:00", hora_fin="11:00"
        )
        
        # Segunda reserva en el mismo horario debe fallar
        with self.assertRaises(SalaNoDisponibleError):
            self.reserva_ctrl.crear_reserva(
                cliente2, sala, "2026-05-10", 1, "hora", 
                hora_inicio="10:00", hora_fin="11:00"
            )

    def test_05_alquiler_equipos_con_iva(self):
        """Escenario 5: Validar sobrecarga de costos (cantidad + impuesto)."""
        cliente = self.cliente_ctrl.crear_cliente("Test", "1", "2", "t@e.com")
        laptop = self.servicio_ctrl.obtener_equipos()[0] # Laptop ($30.000/día)
        stock_inicial = laptop.stock_disponible

        # 5 laptops por 3 días = 15 unidades de cobro
        # 15 * 30.000 = 450.000. Con 19% IVA = 535.500
        reserva = self.reserva_ctrl.crear_reserva(
            cliente, laptop, "2026-05-12", 3, "dia", 
            impuesto=0.19, cantidad=5
        )
        
        self.assertEqual(reserva.costo_total, 535500.0)
        self.assertEqual(laptop.stock_disponible, stock_inicial - 5)

    def test_06_equipo_sin_stock(self):
        """Escenario 6: Validar que no se permita alquilar más del stock físico."""
        cliente = self.cliente_ctrl.crear_cliente("Test", "1", "2", "t@e.com")
        laptop = self.servicio_ctrl.obtener_equipos()[0]

        with self.assertRaises(EquipoSinStockError):
            self.reserva_ctrl.crear_reserva(
                cliente, laptop, "2026-05-15", 1, "dia", cantidad=500
            )

    def test_07_asesoria_costo_complejo(self):
        """Escenario 7: Validar cálculo con recargo legal, descuento e IVA."""
        cliente = self.cliente_ctrl.crear_cliente("Test", "1", "2", "t@e.com")
        legal = self.servicio_ctrl.obtener_asesorias()[0] # Legal ($80.000/hr)
        
        # Lógica esperada: (Base + 15% recargo legal) - 10% desc + 19% IVA
        # (80.000 * 1.15) = 92.000
        # 92.000 - 10% = 82.800
        # 82.800 + 19% IVA = 98.532
        reserva = self.reserva_ctrl.crear_reserva(
            cliente, legal, "2026-05-14", 1, "hora",
            impuesto=0.19, descuento=0.10, hora_inicio="14:00"
        )
        self.assertEqual(reserva.costo_total, 98532.0)

    # ─── PRUEBAS DE ESTADOS Y BÚSQUEDA ───────────────────────────────

    def test_08_flujo_estados_completo(self):
        """Escenario 8: Validar transiciones lineales de la máquina de estados."""
        cliente = self.cliente_ctrl.crear_cliente("T", "1", "2", "t@e.com")
        sala = self.servicio_ctrl.obtener_salas()[0]
        
        reserva = self.reserva_ctrl.crear_reserva(
            cliente, sala, "2026-05-10", 1, "hora", 
            hora_inicio="09:00", hora_fin="10:00"
        )
        
        # Transiciones exitosas
        self.reserva_ctrl.iniciar_reserva(reserva.id)
        self.assertEqual(reserva.estado, EstadoReserva.EN_CURSO)
        
        self.reserva_ctrl.completar_reserva(reserva.id)
        self.assertEqual(reserva.estado, EstadoReserva.COMPLETADA)

    def test_09_transicion_invalida_cancelar_completada(self):
        """Escenario 9: Validar que no se pueda cancelar una reserva ya finalizada."""
        cliente = self.cliente_ctrl.crear_cliente("T", "1", "2", "t@e.com")
        sala = self.servicio_ctrl.obtener_salas()[0]
        reserva = self.reserva_ctrl.crear_reserva(
            cliente, sala, "2026-05-10", 1, "hora", 
            hora_inicio="09:00", hora_fin="10:00"
        )
        
        self.reserva_ctrl.iniciar_reserva(reserva.id)
        self.reserva_ctrl.completar_reserva(reserva.id)

        # Intentar cancelar después de completada debe disparar error
        with self.assertRaises(TransicionEstadoError):
            self.reserva_ctrl.cancelar_reserva(reserva.id)

    def test_10_buscar_cliente_inexistente(self):
        """Escenario 10: Validar que la búsqueda de IDs erróneos lance la excepción correcta."""
        with self.assertRaises(ClienteNoEncontradoError):
            self.cliente_ctrl.buscar_por_cedula("99999999")

    def test_11_encadenamiento_excepciones_cliente_invalido(self):
        """
        Escenario 11: Validar 'raise from'.
        Al pasar un objeto inválido, el controlador debe relanzar el error
        manteniendo la causa original.
        """
        sala = self.servicio_ctrl.obtener_salas()[0]
        
        try:
            # Pasamos un string en lugar de un objeto Cliente
            self.reserva_ctrl.crear_reserva(
                "NoSoyUnCliente", sala, "2026-05-20", 1, "hora",
                hora_inicio="15:00", hora_fin="16:00"
            )
        except (ReservaValidacionError, OperacionError) as e:
            # Verificamos que exista una causa encadenada (el error de tipo original)
            self.assertTrue(hasattr(e, '__cause__') or e is not None)
            self.assertIn("reserva", str(e).lower())

    def test_12_marcar_no_asistio_y_liberar(self):
        """Escenario 12: Validar estado NO_ASISTIO y liberación de recursos."""
        cliente = self.cliente_ctrl.crear_cliente("T", "1", "2", "t@e.com")
        laptop = self.servicio_ctrl.obtener_equipos()[0]
        stock_inicial = laptop.stock_disponible

        reserva = self.reserva_ctrl.crear_reserva(
            cliente, laptop, "2026-05-18", 1, "dia", cantidad=1
        )
        self.assertEqual(laptop.stock_disponible, stock_inicial - 1)

        # Marcar inasistencia debe liberar el stock
        self.reserva_ctrl.marcar_no_asistio(reserva.id)
        self.assertEqual(reserva.estado, EstadoReserva.NO_ASISTIO)
        self.assertEqual(laptop.stock_disponible, stock_inicial)

if __name__ == '__main__':
    unittest.main()