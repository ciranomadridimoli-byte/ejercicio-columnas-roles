
# Informe de columnas de la Encuesta Permanente de Hogares según el rol solicitado.

# 1-
COLUMNAS = {
    "PONDERA":    {"tipo": "int", "completitud": 100.0},
    "ESTADO":     {"tipo": "int", "completitud": 98.5},
    "CAT_OCUP":   {"tipo": "int", "completitud": 61.2},
    "EDAD":       {"tipo": "int", "completitud": 99.9},
    "REGION":     {"tipo": "int", "completitud": 100.0},
    "AGLOMERADO": {"tipo": "int", "completitud": 100.0},
    "MAS_500":    {"tipo": "str", "completitud": 100.0},
    "ANO4":       {"tipo": "int", "completitud": 100.0},
    "TRIMESTRE":  {"tipo": "int", "completitud": 100.0},
    "ITF":        {"tipo": "int", "completitud": 72.4},
    "GDECCFR":    {"tipo": "int", "completitud": 55.0},
}

# ---------------------------------------------------------------------------
# 2) Definicion de los roles: columnas de interés, criterio de orden (nombre / completitud), 
# la forma de ordenar ("A": ascendente, "B": descendente) y, opcionalmente, 
# un porcentaje mínimo ("minimo") de completitud exigido.
# ---------------------------------------------------------------------------


ROLES = {
    "docente": {
        "columnas": ["EDAD", "ESTADO", "CAT_OCUP", "REGION", "ANO4"],
        "criterio": "nombre",
        "orden": "A",
    },
    "investigador": {
        "columnas": ["PONDERA", "ITF", "GDECCFR", "EDAD", "AGLOMERADO", "TRIMESTRE"],
        "criterio": "completitud",
        "orden": "B",
        "minimo": 60,
    },
    "analista": {
        "columnas": ["ESTADO", "CAT_OCUP", "ITF", "MAS_500", "ANO4", "TRIMESTRE"],
        "criterio": "completitud",
        "orden": "A",
        "minimo": 50,
    },
}

CRITERIOS_VALIDOS = ("nombre", "completitud")
ORDENES_VALIDOS = ("A", "B")

# Valores por defecto cuando no se especifica un rol
CRITERIO_DEFAULT = "completitud"
ORDEN_DEFAULT = "B"

# Diccionario de funciones de orden: agregar un criterio nuevo es sumar una
# entrada acá, sin tocar el resto del código. Esto en caso que alguna de las modificaciones
# pida sumar un nuevo criterio para ordenar (para cambiar lo menos posible el codigo)
FUNCIONES_DE_ORDEN = {
    "nombre": lambda nombre, columnas: nombre,
    "completitud": lambda nombre, columnas: columnas[nombre]["completitud"],
}


# 3) Programa que informa según el rol solicitado


def construir_filtro_completitud(config):

# Tambien pienso en las posibles modificaciones, en caso que en vez de un porcentaje minimo de 
# completitud, se pida un maximo (se cambia 'minimo' a 'maximo' en la clave)

    """Devuelve una función que indica si una completitud cumple el rango del rol.

    Soporta 'minimo', 'maximo', ambos a la vez, o ninguno (sin restricción).
    Así, si un rol necesita un techo en vez de un piso, alcanza con cambiar
    la clave en ROLES (de 'minimo' a 'maximo') sin tocar esta función.

    Uso de config como argumento: diccionario de configuración del rol.
    """
    minimo = config.get("minimo")
    maximo = config.get("maximo")

    def cumple(completitud):
        if minimo is not None and completitud < minimo:
            return False
        if maximo is not None and completitud > maximo:
            return False
        return True

    return cumple


def filtrar_por_completitud(columnas, nombres, config):
    """Usa filter() para quedarse solo con las columnas que cumplen el rango del rol.

    Argumentos:
        columnas: diccionario con los datos de cada columna.
        nombres: lista de nombres de columnas a filtrar.
        config: diccionario de configuración del rol (con 'minimo' y/o 'maximo').
    """
    cumple = construir_filtro_completitud(config)
# filtro los nombres de las columnas, usando su porcentaje de completitud con la
# funcion "cumple" creada anteriormente y los convierte en una lista. Uso "lambda"
# para crear una funcion anonima rapidamente.
    return list(filter(lambda nombre: cumple(columnas[nombre]["completitud"]), nombres))


def clave_de_orden(criterio, columnas):
    """Devuelve la función clave a usar en sorted() según el criterio.

    Si el criterio no está en FUNCIONES_DE_ORDEN, se usa el criterio por defecto.

    Argumentos:
        criterio: nombre del criterio (por ejemplo, "nombre" o "completitud").
        columnas: diccionario con los datos de cada columna.
    """
# sorted() requiere saber que valor debe usar para ordenar cada elemento.

    funcion = FUNCIONES_DE_ORDEN.get(criterio, FUNCIONES_DE_ORDEN[CRITERIO_DEFAULT])
    return lambda nombre: funcion(nombre, columnas)


def obtener_config_rol(rol, roles=ROLES):
    """Devuelve la configuración (criterio, orden, columnas, mínimo) para un rol.

    Si rol es None, devuelve la configuración por defecto (todas las columnas,
    ordenadas por completitud en forma descendente).
    Si el rol no existe, devuelve None.
    """
    if rol is None:
        return {
            "columnas": list(COLUMNAS.keys()),
            "criterio": CRITERIO_DEFAULT,
            "orden": ORDEN_DEFAULT,
            "minimo": None,
        }
    return roles.get(rol)


def generar_informe(rol=None, columnas=COLUMNAS, roles=ROLES):
    """Genera la lista de nombres de columnas a mostrar, filtrada y ordenada.

    Argumentos:
        rol: nombre del rol solicitado, o None para informar todas las columnas.
        columnas: diccionario con los datos de cada columna.
        roles: diccionario con la configuración de cada rol.

    Devuelve una lista vacía si el rol no existe.
    """
    config = obtener_config_rol(rol, roles)
    if config is None:
        print(f"El rol '{rol}' no existe. Roles disponibles: {list(roles.keys())}")
        return []

    criterio = config.get("criterio", CRITERIO_DEFAULT)
    if criterio not in CRITERIOS_VALIDOS:
        print(f"Criterio '{criterio}' no reconocido. Se usa '{CRITERIO_DEFAULT}' por defecto.")
        criterio = CRITERIO_DEFAULT

    orden = config.get("orden", ORDEN_DEFAULT)
    if orden not in ORDENES_VALIDOS:
        print(f"Orden '{orden}' no reconocido. Se usa '{ORDEN_DEFAULT}' por defecto.")
        orden = ORDEN_DEFAULT

    nombres_interes = config["columnas"]

    nombres_filtrados = filtrar_por_completitud(columnas, nombres_interes, config)
    descendente = (orden == "B")
    return sorted(nombres_filtrados, key=clave_de_orden(criterio, columnas), reverse=descendente)


def imprimir_informe(rol=None, columnas=COLUMNAS, roles=ROLES):
    """Imprime por pantalla el informe de columnas para el rol indicado."""
    nombres = generar_informe(rol, columnas, roles)

    print(f"\nInforme - rol: {rol if rol else 'sin rol (todas las columnas)'}")
    print(f"{'Columna':<12}{'Tipo':<6}{'Completitud':>12}")

    # Se imprime alineado a la izquierda o derecha ocupando determinado espacio.

    # Uso de map() para armar cada línea del informe a partir de cada elemento de "nombres".
    filas = list(map(
        lambda n: f"{n:<12}{columnas[n]['tipo']:<6}{columnas[n]['completitud']:>11.1f}%",
        nombres,
    ))

    if not filas:
        print("(ninguna columna cumple los criterios)")
        return

    for fila in filas:
        print(fila)
# Los imprime uno abajo del otro.

def main():
    """Muestra los roles disponibles, pide uno por teclado (Enter = sin rol)
    y muestra el informe correspondiente."""
    print("Roles disponibles:")
    for nombre_rol in ROLES:
        print("-", nombre_rol)

    rol = input("Rol (Enter para todas): ")
    rol = rol.strip()
    imprimir_informe(rol if rol else None)

# Uso strip para eliminar posibles espacios al principio y final

if __name__ == "__main__":
    main()
