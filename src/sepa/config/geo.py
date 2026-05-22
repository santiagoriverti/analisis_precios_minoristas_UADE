"""Mapeos geográficos: ISO → provincia, región, normalización de nombres, barrios CABA."""

ISO_TO_PROVINCIA: dict[str, str] = {
    "AR-B": "Buenos Aires",
    "AR-C": "CABA",
    "AR-K": "Catamarca",
    "AR-H": "Chaco",
    "AR-U": "Chubut",
    "AR-X": "Córdoba",
    "AR-W": "Corrientes",
    "AR-E": "Entre Ríos",
    "AR-P": "Formosa",
    "AR-Y": "Jujuy",
    "AR-L": "La Pampa",
    "AR-F": "La Rioja",
    "AR-M": "Mendoza",
    "AR-N": "Misiones",
    "AR-Q": "Neuquén",
    "AR-R": "Río Negro",
    "AR-A": "Salta",
    "AR-J": "San Juan",
    "AR-D": "San Luis",
    "AR-Z": "Santa Cruz",
    "AR-S": "Santa Fe",
    "AR-G": "Santiago del Estero",
    "AR-V": "Tierra del Fuego",
    "AR-T": "Tucumán",
}

PROVINCIA_TO_REGION: dict[str, str] = {
    "Buenos Aires":        "AMBA/Pampeana",
    "CABA":                "AMBA/Pampeana",
    "Córdoba":             "AMBA/Pampeana",
    "Santa Fe":            "AMBA/Pampeana",
    "Entre Ríos":          "AMBA/Pampeana",
    "La Pampa":            "AMBA/Pampeana",
    "Jujuy":               "NOA",
    "Salta":               "NOA",
    "Tucumán":             "NOA",
    "Catamarca":           "NOA",
    "La Rioja":            "NOA",
    "Santiago del Estero": "NOA",
    "Chaco":               "NEA",
    "Corrientes":          "NEA",
    "Formosa":             "NEA",
    "Misiones":            "NEA",
    "Mendoza":             "Cuyo",
    "San Juan":            "Cuyo",
    "San Luis":            "Cuyo",
    "Neuquén":             "Patagonia",
    "Río Negro":           "Patagonia",
    "Chubut":              "Patagonia",
    "Santa Cruz":          "Patagonia",
    "Tierra del Fuego":    "Patagonia",
}

REGIONES = ["AMBA/Pampeana", "NOA", "NEA", "Cuyo", "Patagonia"]

# Normalización completa de nombres de provincia (incluyendo variantes del SEPA)
PROVINCIA_ALIASES: dict[str, str] = {
    "Provincia de Buenos Aires":       "Buenos Aires",
    "Buenos Aires (Conurbano)":        "Buenos Aires",
    "Ciudad de Buenos Aires":          "CABA",
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "Tierra del Fuego",
    "Tierra del fuego":                "Tierra del Fuego",
    "Santiago Del Estero":             "Santiago del Estero",
    "La rioja":                        "La Rioja",
    "San luis":                        "San Luis",
    "La pampa":                        "La Pampa",
    "Santa cruz":                      "Santa Cruz",
    "San juan":                        "San Juan",
    "Entre Rios":                      "Entre Ríos",
    "Cordoba":                         "Córdoba",
    "Rio Negro":                       "Río Negro",
    "Neuquen":                         "Neuquén",
    "Tucuman":                         "Tucumán",
}

# GeoJSON property name → nombre canónico de provincia
GEOJSON_NAME_PROPERTY = "name"
GEOJSON_ALIASES: dict[str, str] = {
    "Ciudad de Buenos Aires": "CABA",
}

# ── Bounding boxes de los 48 barrios de CABA ─────────────────────────────────
# Formato: (lat_min, lat_max, lon_min, lon_max) en WGS84
# Clasificación por coordenadas (no por nombres de calles)
# 668 de 869 sucursales CABA asignadas con este sistema (77%)
BARRIOS_CABA_BBOX: dict[str, tuple[float, float, float, float]] = {
    "Agronomía":           (-34.604, -34.587, -58.498, -58.476),
    "Almagro":             (-34.622, -34.598, -58.435, -58.405),
    "Balvanera":           (-34.617, -34.598, -58.418, -58.388),
    "Barracas":            (-34.661, -34.628, -58.395, -58.366),
    "Belgrano":            (-34.575, -34.547, -58.471, -58.434),
    "Boedo":               (-34.638, -34.620, -58.426, -58.408),
    "Caballito":           (-34.628, -34.602, -58.460, -58.421),
    "Chacarita":           (-34.595, -34.575, -58.470, -58.443),
    "Coghlan":             (-34.572, -34.555, -58.485, -58.469),
    "Colegiales":          (-34.580, -34.563, -58.460, -58.439),
    "Constitución":        (-34.631, -34.620, -58.395, -58.378),
    "Flores":              (-34.642, -34.615, -58.480, -58.435),
    "Floresta":            (-34.633, -34.615, -58.500, -58.479),
    "La Boca":             (-34.643, -34.620, -58.371, -58.350),
    "La Paternal":         (-34.605, -34.585, -58.475, -58.456),
    "Liniers":             (-34.652, -34.628, -58.534, -58.506),
    "Mataderos":           (-34.665, -34.641, -58.522, -58.488),
    "Monte Castro":        (-34.628, -34.610, -58.520, -58.500),
    "Monserrat":           (-34.625, -34.605, -58.391, -58.371),
    "Nueva Pompeya":       (-34.658, -34.638, -58.418, -58.396),
    "Núñez":               (-34.553, -34.532, -58.475, -58.443),
    "Palermo":             (-34.595, -34.560, -58.435, -58.398),
    "Parque Avellaneda":   (-34.660, -34.638, -58.495, -58.470),
    "Parque Chacabuco":    (-34.645, -34.625, -58.448, -58.422),
    "Parque Chas":         (-34.591, -34.578, -58.487, -58.475),
    "Parque Patricios":    (-34.652, -34.628, -58.418, -58.395),
    "Puerto Madero":       (-34.625, -34.587, -58.371, -58.349),
    "Recoleta":            (-34.598, -34.575, -58.405, -58.378),
    "Retiro":              (-34.595, -34.578, -58.388, -58.365),
    "Saavedra":            (-34.560, -34.540, -58.495, -58.467),
    "San Cristóbal":       (-34.625, -34.612, -58.408, -58.391),
    "San Nicolás":         (-34.610, -34.595, -58.395, -58.371),
    "San Telmo":           (-34.625, -34.610, -58.378, -58.365),
    "Vélez Sársfield":     (-34.642, -34.624, -58.510, -58.493),
    "Versalles":           (-34.640, -34.621, -58.525, -58.508),
    "Villa Crespo":        (-34.605, -34.585, -58.452, -58.428),
    "Villa del Parque":    (-34.615, -34.595, -58.498, -58.472),
    "Villa Devoto":        (-34.612, -34.585, -58.518, -58.490),
    "Villa General Mitre": (-34.615, -34.600, -58.475, -58.458),
    "Villa Lugano":        (-34.690, -34.660, -58.475, -58.435),
    "Villa Luro":          (-34.645, -34.628, -58.510, -58.491),
    "Villa Ortúzar":       (-34.590, -34.575, -58.475, -58.456),
    "Villa Pueyrredón":    (-34.585, -34.565, -58.510, -58.485),
    "Villa Real":          (-34.628, -34.615, -58.530, -58.512),
    "Villa Riachuelo":     (-34.695, -34.680, -58.470, -58.450),
    "Villa Santa Rita":    (-34.622, -34.605, -58.488, -58.470),
    "Villa Soldati":       (-34.682, -34.655, -58.460, -58.420),
    "Villa Urquiza":       (-34.590, -34.565, -58.495, -58.470),
}

# Bounding box de CABA completa para filtrar sucursales mal clasificadas
CABA_LAT_MIN, CABA_LAT_MAX = -34.71, -34.53
CABA_LON_MIN, CABA_LON_MAX = -58.53, -58.34


def normalize_provincia(name: str) -> str:
    """Retorna el nombre canónico de la provincia, o el original si no hay alias."""
    if not name:
        return ""
    name = str(name).strip()
    return PROVINCIA_ALIASES.get(name, name)


def assign_barrio_caba(lat: float, lon: float) -> str | None:
    """Asigna un barrio de CABA a una coordenada. Retorna None si no cae en ningún barrio."""
    for barrio, (lat_min, lat_max, lon_min, lon_max) in BARRIOS_CABA_BBOX.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return barrio
    return None


def is_caba_valid_coords(lat: float, lon: float) -> bool:
    """Verifica que las coordenadas estén dentro del bounding box de CABA."""
    return (CABA_LAT_MIN <= lat <= CABA_LAT_MAX) and (CABA_LON_MIN <= lon <= CABA_LON_MAX)
