# =============================================================================
# validadores.py — Funciones de validación reutilizables
# =============================================================================
# Centraliza validaciones comunes (email, cédula, teléfono, etc.)
# para evitar duplicación entre modelos y controladores.
# =============================================================================

import re
from backend.exceptions.excepciones import ValidacionError


def validar_no_vacio(valor: str, nombre_campo: str) -> str:
    """Valida que un string no esté vacío ni sea solo espacios.
    
    Args:
        valor: El valor a validar.
        nombre_campo: Nombre del campo para el mensaje de error.
    
    Returns:
        El valor limpio (sin espacios al inicio/final).
    
    Raises:
        ValidacionError: Si el valor está vacío.
    """
    if not valor or not valor.strip():
        raise ValidacionError(f"El campo '{nombre_campo}' no puede estar vacío", nombre_campo)
    return valor.strip()


def validar_cedula(cedula: str) -> str:
    """Valida que la cédula contenga solo dígitos (8 a 12 caracteres).
    
    Args:
        cedula: Número de cédula a validar.
    
    Returns:
        La cédula limpia.
    
    Raises:
        ValidacionError: Si la cédula no cumple el formato.
    """
    cedula = cedula.strip()
    if not cedula:
        raise ValidacionError("La cédula no puede estar vacía", "cédula")
    if not cedula.isdigit():
        raise ValidacionError("La cédula debe contener solo dígitos", "cédula")
    if not (8 <= len(cedula) <= 12):
        raise ValidacionError("La cédula debe tener entre 8 y 12 dígitos", "cédula")
    return cedula


def validar_email(email: str) -> str:
    """Valida formato básico de email usando expresión regular.
    
    Args:
        email: Dirección de email a validar.
    
    Returns:
        El email en minúsculas y limpio.
    
    Raises:
        ValidacionError: Si el email no tiene un formato válido.
    """
    email = email.strip().lower()
    if not email:
        raise ValidacionError("El email no puede estar vacío", "email")
    # Regex básico pero funcional para validación de email
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron, email):
        raise ValidacionError(f"El email '{email}' no tiene un formato válido", "email")
    return email


def validar_telefono(telefono: str) -> str:
    """Valida que el teléfono contenga solo dígitos (7 a 15 caracteres).
    
    Args:
        telefono: Número de teléfono a validar.
    
    Returns:
        El teléfono limpio.
    
    Raises:
        ValidacionError: Si el teléfono no cumple el formato.
    """
    telefono = telefono.strip()
    if not telefono:
        raise ValidacionError("El teléfono no puede estar vacío", "teléfono")
    if not telefono.isdigit():
        raise ValidacionError("El teléfono debe contener solo dígitos", "teléfono")
    if not (7 <= len(telefono) <= 15):
        raise ValidacionError("El teléfono debe tener entre 7 y 15 dígitos", "teléfono")
    return telefono


def validar_numero_positivo(valor, nombre_campo: str) -> float:
    """Valida que un valor sea numérico y mayor que cero.
    
    Args:
        valor: El valor a validar (puede ser str, int o float).
        nombre_campo: Nombre del campo para el mensaje de error.
    
    Returns:
        El valor como float.
    
    Raises:
        ValidacionError: Si el valor no es un número positivo.
    """
    try:
        numero = float(valor)
    except (ValueError, TypeError):
        raise ValidacionError(
            f"El campo '{nombre_campo}' debe ser un número válido", nombre_campo
        )
    if numero <= 0:
        raise ValidacionError(
            f"El campo '{nombre_campo}' debe ser mayor que cero", nombre_campo
        )
    return numero


def validar_entero_positivo(valor, nombre_campo: str) -> int:
    """Valida que un valor sea un entero positivo.
    
    Args:
        valor: El valor a validar.
        nombre_campo: Nombre del campo para el mensaje de error.
    
    Returns:
        El valor como int.
    
    Raises:
        ValidacionError: Si el valor no es un entero positivo.
    """
    try:
        numero = int(valor)
    except (ValueError, TypeError):
        raise ValidacionError(
            f"El campo '{nombre_campo}' debe ser un número entero", nombre_campo
        )
    if numero <= 0:
        raise ValidacionError(
            f"El campo '{nombre_campo}' debe ser mayor que cero", nombre_campo
        )
    return numero


def validar_opcion(valor: str, opciones_validas: list, nombre_campo: str) -> str:
    """Valida que un valor esté dentro de un conjunto de opciones válidas.
    
    Args:
        valor: El valor a validar.
        opciones_validas: Lista de opciones permitidas.
        nombre_campo: Nombre del campo para el mensaje de error.
    
    Returns:
        El valor en minúsculas.
    
    Raises:
        ValidacionError: Si el valor no está entre las opciones válidas.
    """
    valor = valor.strip().lower()
    opciones_lower = [o.lower() for o in opciones_validas]
    if valor not in opciones_lower:
        opciones_str = ", ".join(f"'{o}'" for o in opciones_validas)
        raise ValidacionError(
            f"El campo '{nombre_campo}' debe ser una de las opciones: {opciones_str}",
            nombre_campo
        )
    return valor


def validar_fecha(fecha: str, nombre_campo: str = "fecha") -> str:
    """Valida que una fecha tenga el formato AAAA-MM-DD y no sea anterior a hoy.
    
    Args:
        fecha: La fecha a validar.
        nombre_campo: Nombre del campo para el mensaje de error.
    
    Returns:
        La fecha validada como string.
    
    Raises:
        ValidacionError: Si el formato es incorrecto o la fecha es pasada.
    """
    import datetime
    
    fecha = fecha.strip()
    if not fecha:
        raise ValidacionError(f"El campo '{nombre_campo}' no puede estar vacío", nombre_campo)
        
    try:
        # Validar formato
        fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise ValidacionError(
            f"El campo '{nombre_campo}' debe tener el formato AAAA-MM-DD", 
            nombre_campo
        )
        
    # Validar que no sea anterior a hoy
    hoy = datetime.date.today()
    if fecha_obj < hoy:
        raise ValidacionError(
            f"La {nombre_campo} no puede ser anterior a la fecha actual ({hoy.strftime('%Y-%m-%d')})",
            nombre_campo
        )
        
    # Validar que el año no sea mayor al actual
    if fecha_obj.year > hoy.year:
        raise ValidacionError(
            f"La {nombre_campo} no puede tener un año mayor al actual ({hoy.year})",
            nombre_campo
        )
        
    return fecha
