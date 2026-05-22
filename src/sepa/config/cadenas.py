"""Mapeo de IDs de cadenas SEPA → nombre comercial.

Clave: (id_comercio, id_bandera)  o  solo id_comercio cuando es unívoco.
El campo 'excluir' marca cadenas no-supermercados (farmacias, estaciones, e-commerce).
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
    # ChangoMas / Dorinka
    (11, 1): "ChangoMas",
    (11, 2): "Mi ChangoMas",
    (11, 3): "Hiper ChangoMas",
    # Otros supermercados
    (12, 1): "Coto",
    (13, 1): "Cooperativa Obrera",
    (15, 1): "DIA",
    (16, 1): "Hipermercado Libertad",
    (20, 1): "LAR",
    (21, 1): "Toledo",
    (47, 1): "Pasamonte",
    (2,  1): "La Anónima",
}

# id_comercio → nombre cuando la cadena tiene un solo banner
CADENA_BY_COMERCIO: dict[int, str] = {
    2:  "La Anónima",
    9:  "Cencosud",
    10: "Carrefour",
    11: "ChangoMas",
    12: "Coto",
    13: "Cooperativa Obrera",
    15: "DIA",
    16: "Hipermercado Libertad",
    20: "LAR",
    21: "Toledo",
    47: "Pasamonte",
}

# Cadenas a excluir del análisis (no supermercados)
CADENAS_EXCLUIDAS_IDS: set[int] = {
    4,     # Mercado Libre
    19,    # FULL
    2013,  # Easy (materiales)
    3001,  # Farmacity
    3002,  # Simplicity
}

# Bandera de "no relevante" para análisis de canasta
BANDERAS_NO_RELEVANTES: set[tuple[int, int]] = set()


def get_cadena_name(id_comercio: int, id_bandera: int) -> str | None:
    """Retorna el nombre comercial de la cadena o None si no se reconoce."""
    name = CADENA_BY_BANNER.get((id_comercio, id_bandera))
    if name is None:
        name = CADENA_BY_COMERCIO.get(id_comercio)
    return name


def is_excluida(id_comercio: int) -> bool:
    return id_comercio in CADENAS_EXCLUIDAS_IDS
