"""Mapeo de IDs de cadenas SEPA → nombre comercial.

Verificado contra datos de abril 2026 (14 cadenas representativas).
Los IDs se manejan como enteros internamente; la conversión desde string
se hace en enricher.py antes de llamar a estas funciones.

Nota: DORINKA SRL = ChangoMas (Grupo De Narváez, ex-Walmart Argentina).
"""

# (id_comercio, id_bandera) → nombre_cadena
CADENA_BY_BANNER: dict[tuple[int, int], str] = {
    # Cencosud
    (9, 1):  "Vea",
    (9, 2):  "Disco",
    (9, 3):  "Jumbo",
    # Carrefour
    (10, 1): "Carrefour",
    (10, 2): "Carrefour Market",
    (10, 3): "Carrefour Express",
    # ChangoMas / DORINKA SRL (ex-Walmart Argentina)
    (11, 2): "ChangoMas",
    (11, 4): "Hiper ChangoMas",
    (11, 5): "Mi ChangoMas",
    # Hipermercado Libertad (Grupo Casino)
    (16, 1): "Hipermercado Libertad",
    (16, 2): "Mini Libertad",
}

# id_comercio → nombre cuando la cadena tiene un solo banner relevante
CADENA_BY_COMERCIO: dict[int, str] = {
    2:  "La Anónima",
    3:  "Cadena 3",
    5:  "Hipermercado Misiones",
    8:  "Cadena 8 (Córdoba)",
    12: "Coto",
    13: "Cooperativa Obrera",
    15: "DIA",
    20: "LAR",
    21: "Toledo",
    23: "Cadena 23",
    47: "Pasamonte",
}

# Cadenas a excluir del análisis (no supermercados de consumo masivo)
# 19  = FULL / YPF (estaciones de servicio)
# 2013 = Mercado Libre (e-commerce, sin sucursal física)
# 3001 = Easy (ferretería / hogar)
# 4   = sucursal única no representativa
CADENAS_EXCLUIDAS_IDS: set[int] = {4, 19, 2013, 3001}

# Mínimo de sucursales para aparecer en rankings
MIN_SUCURSALES_RANKING = 10


def get_cadena_name(id_comercio: int, id_bandera: int) -> str | None:
    """Retorna el nombre comercial de la cadena o None si no se reconoce."""
    name = CADENA_BY_BANNER.get((id_comercio, id_bandera))
    if name is None:
        name = CADENA_BY_COMERCIO.get(id_comercio)
    return name


def is_excluida(id_comercio: int) -> bool:
    """Retorna True si la cadena debe excluirse del análisis."""
    return id_comercio in CADENAS_EXCLUIDAS_IDS
