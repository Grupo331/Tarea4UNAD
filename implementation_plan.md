# Sistema Integral de Gestión — Software FJ

## Objetivo

Sistema de escritorio en Python + Tkinter para gestionar clientes, servicios (salas, equipos, asesorías) y reservas, con arquitectura OOP rigurosa, excepciones personalizadas y logging.

---

## 1. Arquitectura de Carpetas

```
Grupo_331Fase4/
├── main.py                          # Punto de entrada
├── config.py                        # Constantes globales (tarifas, colores, etc.)
│
├── backend/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                  # EntidadBase (ABC)
│   │   ├── cliente.py               # Clase Cliente
│   │   ├── servicio.py              # ABC Servicio + 3 concretas
│   │   ├── reserva.py               # Clase Reserva + Enum EstadoReserva
│   │   └── catalogo.py              # Catálogos en memoria (tipos equipo, áreas asesoría)
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── cliente_controller.py
│   │   ├── servicio_controller.py
│   │   └── reserva_controller.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── excepciones.py           # Jerarquía de excepciones personalizadas
│   └── utils/
│       ├── __init__.py
│       ├── logger_config.py         # Configuración de logging
│       └── validadores.py           # Funciones de validación reutilizables
│
├── frontend/
│   ├── __init__.py
│   ├── app.py                       # Dashboard principal (sidebar + área central)
│   ├── estilos.py                   # Tema, colores corporativos, fuentes
│   ├── componentes/
│   │   ├── __init__.py
│   │   ├── sidebar.py               # Panel lateral de navegación
│   │   └── widgets.py               # Widgets reutilizables (tablas, formularios)
│   └── vistas/
│       ├── __init__.py
│       ├── cliente_vista.py         # CRUD de clientes
│       ├── servicio_vista.py        # Gestión de servicios y catálogos
│       ├── reserva_vista.py         # Gestión de reservas
│       └── log_vista.py             # Visor de logs en tiempo real
│
├── logs/                            # Directorio de archivos de log
│   └── (app.log se crea automáticamente)
│
└── simulacion.py                    # 10+ operaciones de demostración
```

**Principio clave:** Frontend importa Controllers → Controllers operan sobre Models. Frontend **nunca** accede a Models directamente.

---

## 2. Diseño de Clases (Modelo de Dominio)

### 2.1 Clase Abstracta Base

```
EntidadBase (ABC)
├── _id: str (UUID generado)
├── _fecha_creacion: datetime
├── @abstractmethod validar() -> bool
├── @abstractmethod to_dict() -> dict
├── __str__() -> str
```

### 2.2 Cliente

```
Cliente(EntidadBase)
├── _nombre: str
├── _cedula: str
├── _telefono: str
├── _email: str
├── Properties con @property y @setter (validación en setter)
├── validar() -> bool
├── to_dict() -> dict
```

**Validaciones:** cédula solo dígitos (8-12 chars), email con regex básico, teléfono solo dígitos (7-15 chars), nombre no vacío.

### 2.3 Jerarquía de Servicios

```
Servicio(EntidadBase, ABC)                    ← Clase abstracta
├── _nombre: str
├── _tarifa_hora: float
├── _tarifa_dia: float
├── @abstractmethod calcular_costo(duracion, unidad, **kwargs) -> float
├── @abstractmethod obtener_descripcion() -> str
├── @abstractmethod validar_disponibilidad(**kwargs) -> bool
│
├── ReservaSala(Servicio)
│   ├── _capacidad: int
│   ├── _tipo_sala: str              # "reunión", "capacitación", "coworking"
│   ├── _reservas_activas: list      # Para validar conflictos de horario
│   ├── calcular_costo(...)          # Polimorfismo
│   ├── obtener_descripcion()
│   └── validar_disponibilidad(fecha, hora_inicio, hora_fin)
│
├── AlquilerEquipo(Servicio)
│   ├── _tipo_equipo: str
│   ├── _stock_total: int            # 100 por defecto
│   ├── _stock_disponible: int
│   ├── calcular_costo(...)
│   ├── obtener_descripcion()
│   ├── validar_disponibilidad(cantidad)
│   ├── reservar_unidades(cantidad)
│   └── devolver_unidades(cantidad)
│
└── AsesoriaEspecializada(Servicio)
    ├── _area_tematica: str           # "legal", "contable", "técnica"
    ├── _asesor: str (opcional)
    ├── calcular_costo(...)
    ├── obtener_descripcion()
    └── validar_disponibilidad(fecha, hora)
```

### 2.4 Sobrecarga de Métodos (calcular_costo)

Python no tiene sobrecarga nativa. Usamos **parámetros opcionales con `**kwargs`**:

```python
def calcular_costo(self, duracion: float, unidad: str = "hora",
                   *, impuesto: float = 0.0, descuento: float = 0.0) -> float:
    """
    Variantes de uso (simula sobrecarga):
    1) calcular_costo(2, "hora")                         → base
    2) calcular_costo(1, "dia", impuesto=0.19)           → con IVA
    3) calcular_costo(3, "hora", impuesto=0.19, descuento=0.10) → con IVA y descuento
    """
    tarifa = self._tarifa_hora if unidad == "hora" else self._tarifa_dia
    subtotal = tarifa * duracion
    subtotal -= subtotal * descuento
    total = subtotal + (subtotal * impuesto)
    return round(total, 2)
```

Cada subclase **sobrescribe** este método agregando lógica propia (polimorfismo):

- `ReservaSala`: recargo por capacidad > 20 personas
- `AlquilerEquipo`: multiplicar por cantidad de unidades
- `AsesoriaEspecializada`: recargo por área "legal"

### 2.5 Reserva

```
EstadoReserva(Enum)
├── PENDIENTE
├── CONFIRMADA
├── EN_CURSO
├── COMPLETADA
├── CANCELADA
├── NO_ASISTIO

Reserva(EntidadBase)
├── _cliente: Cliente
├── _servicio: Servicio
├── _fecha_reserva: datetime
├── _duracion: float
├── _unidad_duracion: str            # "hora" o "dia"
├── _estado: EstadoReserva           # Inicia PENDIENTE
├── _costo_total: float
│
├── confirmar()                      # PENDIENTE → CONFIRMADA
├── iniciar()                        # CONFIRMADA → EN_CURSO
├── completar()                      # EN_CURSO → COMPLETADA
├── cancelar()                       # PENDIENTE|CONFIRMADA → CANCELADA
├── marcar_no_asistio()              # CONFIRMADA → NO_ASISTIO
├── procesar(**kwargs)               # Calcula costo vía servicio.calcular_costo()
├── validar() -> bool
├── to_dict() -> dict
```

**Transiciones válidas de estado:**

```
PENDIENTE ──→ CONFIRMADA ──→ EN_CURSO ──→ COMPLETADA
    │              │              
    └──→ CANCELADA └──→ CANCELADA
                   └──→ NO_ASISTIO
```

---

## 3. Jerarquía de Excepciones

```
SoftwareFJError (Exception base)
├── ValidacionError
│   ├── ClienteValidacionError
│   ├── ServicioValidacionError
│   └── ReservaValidacionError
├── DisponibilidadError
│   ├── SalaNoDisponibleError
│   ├── EquipoSinStockError
│   └── AsesorNoDisponibleError
├── TransicionEstadoError
└── EntidadNoEncontradaError
    ├── ClienteNoEncontradoError
    ├── ServicioNoEncontradoError
    └── ReservaNoEncontradaError
```

**Patrones de uso obligatorios:**

| Patrón | Dónde se usa |
|--------|-------------|
| `try/except` | Controllers: capturar errores de validación |
| `try/except/else` | Reserva.procesar(): si no hay error, confirmar |
| `try/except/finally` | Logging: siempre registrar la operación |
| `raise ... from ...` | Controller → re-lanzar con contexto cuando falla validación interna |

---

## 4. Sistema de Logging

- Librería estándar `logging` con `RotatingFileHandler`
- Archivo: `logs/app.log`, máx 5MB, 3 backups
- Formato: `[YYYY-MM-DD HH:MM:SS] [NIVEL] [módulo] mensaje`
- Niveles: `DEBUG` (dev), `INFO` (operaciones), `WARNING` (validaciones fallidas), `ERROR` (excepciones), `CRITICAL` (errores fatales)

**Eventos a registrar:** Crear/editar/eliminar cliente, crear/cancelar/completar reserva, errores de validación, conflictos de horario, cambios de stock.

---

## 5. Frontend Tkinter — Dashboard

```
┌──────────────────────────────────────────────────┐
│  ████  SOFTWARE FJ — Sistema de Gestión          │
├──────────┬───────────────────────────────────────┤
│          │                                       │
│ 👥 Clientes│     ÁREA CENTRAL DINÁMICA           │
│          │     (cambia según selección)          │
│ 🔧 Servicios│                                    │
│          │     ┌─────────────────────────┐       │
│ 📅 Reservas│   │  Tabla / Formulario     │       │
│          │     │  del módulo activo      │       │
│ 📋 Logs   │     │                         │       │
│          │     └─────────────────────────┘       │
│          │                                       │
├──────────┴───────────────────────────────────────┤
│  Barra de estado: usuario | fecha | registros    │
└──────────────────────────────────────────────────┘
```

- **Sidebar:** Frame con botones estilizados, resalta el activo
- **Área central:** Frame contenedor; se destruye/recrea el contenido al cambiar de módulo
- **Ventanas Toplevel:** Para formularios de crear/editar (no para navegación principal)
- **Tema:** `ttk.Style` con paleta corporativa (azul oscuro #1a237e, acento #00bcd4, fondo #f5f5f5)

---

## 6. Plan de 10+ Operaciones de Simulación

| # | Operación | Tipo | Qué demuestra |
|---|-----------|------|----------------|
| 1 | Crear cliente válido | ✅ Válida | Encapsulación, validación |
| 2 | Crear cliente con email inválido | ❌ Inválida | ClienteValidacionError |
| 3 | Reservar sala disponible por 2 horas | ✅ Válida | Polimorfismo calcular_costo |
| 4 | Reservar sala ya ocupada | ❌ Inválida | SalaNoDisponibleError, conflicto horario |
| 5 | Alquilar 5 laptops por 3 días con IVA | ✅ Válida | Sobrecarga (kwargs impuesto) |
| 6 | Alquilar más equipos que stock | ❌ Inválida | EquipoSinStockError |
| 7 | Crear asesoría legal por 1 hora + descuento | ✅ Válida | Sobrecarga (descuento + impuesto) |
| 8 | Confirmar y completar reserva | ✅ Válida | Flujo de estados completo |
| 9 | Cancelar reserva ya completada | ❌ Inválida | TransicionEstadoError |
| 10 | Buscar cliente inexistente | ❌ Inválida | ClienteNoEncontradoError |
| 11 | Crear reserva con cliente inválido | ❌ Inválida | raise...from... encadenamiento |
| 12 | Confirmar → Marcar No Asistió | ✅ Válida | Estado NO_ASISTIO |

---

## 7. Verificación

### Automatizada

- Ejecutar `simulacion.py` que corre las 12 operaciones y verifica resultados esperados
- Verificar que `logs/app.log` se genera correctamente

### Manual

- Lanzar `main.py`, navegar por todos los módulos del dashboard
- Crear cliente → crear reserva → confirmar → completar (flujo completo)
- Provocar errores y verificar que la app no se cae
