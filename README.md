# Software FJ - Sistema Integral de Gestión

## Descripción
Software FJ es un sistema de escritorio desarrollado en Python con Tkinter para gestionar clientes, servicios (salas, equipos, asesorías), asesores y reservas. Implementa una arquitectura rigurosa Orientada a Objetos, manejo de excepciones personalizadas, listas internas para gestión de datos en memoria y un sistema de logging para trazabilidad, cumpliendo estrictamente con los lineamientos del proyecto (sin uso de bases de datos).

## Requisitos Mínimos
- **Sistema Operativo:** Windows, macOS o Linux.
- **Python:** Versión 3.8 o superior instalada en el sistema.
- **Librerías:** No se requieren librerías de terceros (`pip install` no es necesario). El sistema utiliza exclusivamente bibliotecas de la Standard Library de Python (`tkinter`, `logging`, `os`, `sys`, `datetime`).

## Ejecución de la Aplicación

Para iniciar la aplicación gráfica, abre una terminal o línea de comandos, navega hasta el directorio raíz del proyecto y ejecuta el archivo principal:
```bash
python main.py
```

Para ejecutar el script de simulación automática (que prueba los diferentes flujos, validaciones y registro de excepciones en consola y logs):
```bash
python simulacion.py
```

## Arquitectura y Componentes del Sistema

El proyecto sigue una arquitectura de capas bien definida:

1. **Modelos (`backend/models/`)**: 
   - Clases de dominio que incluyen `Cliente`, `Reserva`, `Servicio` (junto con sus subclases `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`), `Asesor` y la clase abstracta `EntidadBase`.
   - Estas clases contienen toda la lógica de negocio, encapsulamiento estricto y validación de datos a través de *properties*.
2. **Controladores (`backend/controllers/`)**: 
   - Actúan como intermediarios (CRUD) entre las vistas y los modelos. 
   - Gestionan las listas en memoria de clientes, servicios, asesores y reservas.
3. **Excepciones (`backend/exceptions/`)**: 
   - Jerarquía de errores personalizados (`excepciones.py`) como `ValidacionError`, `DisponibilidadError`, o `TransicionEstadoError`. Garantizan un manejo estructurado de errores.
4. **Utilidades (`backend/utils/`)**: 
   - Configuraciones globales que incluyen validadores estandarizados y la configuración de logs mediante `RotatingFileHandler` en `logger_config.py`.
5. **Vistas (`frontend/`)**: 
   - Componentes de interfaz gráfica de usuario creados con `tkinter` y `ttk`. 
   - Incluye la ventana principal (`app.py`), estilos corporativos (`estilos.py`) y los módulos visuales específicos para cada sección (Clientes, Servicios, Asesores, Reservas y Logs).
6. **Configuración (`config.py`)**: 
   - Archivo centralizado con variables globales, tarifas de los servicios, colores de la interfaz y fuentes para la GUI.

## Instrucciones de Uso

Al iniciar la aplicación mediante `main.py`, accederás al **Dashboard Principal** con un resumen ejecutivo de métricas. Utiliza el **Panel Lateral (Sidebar)** izquierdo para navegar entre los distintos módulos:

- **👥 Clientes**: Permite registrar nuevos clientes. El sistema valida estrictamente que su documento de identidad sea único y que su correo electrónico y teléfono posean formatos correctos. Permite también la actualización y eliminación.
- **👨‍💼 Asesores**: Sección para dar de alta, buscar y gestionar el personal especializado (asesores legales, contables o técnicos) requeridos para prestar los servicios de asesoría.
- **🔧 Servicios**: Un catálogo visual donde se administran y consultan los servicios que ofrece la empresa: Salas (con diferentes capacidades y cálculos de tarifas), Equipos (con control dinámico de stock disponible), y Asesorías Especializadas (vinculadas a los asesores registrados).
- **📅 Reservas**: El módulo principal de transacciones. Aquí puedes crear reservas vinculando un cliente a un servicio. El sistema validará la disponibilidad antes de confirmar. También puedes gestionar el ciclo de vida de cada reserva modificando sus estados lógicos (Pendiente -> Confirmada -> En Curso -> Completada, o Cancelada/No Asistió).
- **📋 Logs**: Un visor integrado en la aplicación que permite auditar en tiempo real el registro de eventos y errores que ocurren en la sesión, leyendo directamente del archivo `logs/app.log`.

### Flujo Recomendado de Uso (Paso a Paso)

Debido a que el sistema inicia en blanco en cada ejecución (en memoria volátil), te recomendamos seguir este orden lógico para probar todas las funcionalidades correctamente sin encontrarte con listas vacías:

1. **Paso 1 - Crear Asesores (`👨‍💼 Asesores`)**: Ve al módulo de asesores y crea al menos un profesional. Esto es necesario si vas a ofrecer servicios de Asesoría Especializada.
2. **Paso 2 - Registrar Clientes (`👥 Clientes`)**: Crea los perfiles de los clientes que utilizarán el sistema. Si intentas hacer una reserva sin clientes, el sistema te lo impedirá.
3. **Paso 3 - Configurar Servicios (`🔧 Servicios`)**: Aunque el catálogo trae algunos servicios por defecto, aquí puedes asignar el Asesor que creaste en el *Paso 1* a una "Asesoría Especializada", o registrar nuevos Equipos y Salas.
4. **Paso 4 - Crear y Procesar Reservas (`📅 Reservas`)**: Ahora que tienes clientes y servicios disponibles, ve al módulo de reservas. Selecciona un cliente, un servicio y crea la reserva.
5. **Paso 5 - Gestionar Estados (`📅 Reservas`)**: Finalmente, usa los botones de acción para cambiar el estado de la reserva (ej: de *Pendiente* a *Confirmada* y luego a *Completada*).
6. **Paso 6 - Revisar Auditoría (`📋 Logs`)**: Al finalizar, puedes ir al módulo de logs para observar todo el rastro de las creaciones, cálculos y transiciones de estado que acabas de realizar.

> **⚠️ Nota Importante sobre la Persistencia:** Este proyecto está diseñado para funcionar de manera volátil en memoria como parte del requerimiento académico de diseño estructurado. Los datos creados (clientes, asesores, reservas) se reiniciarán al cerrar la aplicación. **Solo los eventos y excepciones documentados por el sistema de Logs permanecerán guardados en disco** dentro de la carpeta `logs/`.
