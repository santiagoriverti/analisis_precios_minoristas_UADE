"""Mapeos geográficos: ISO → provincia, región, GeoJSON."""

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

# Normalizaciones de nombres de provincia que aparecen en los datos
PROVINCIA_ALIASES: dict[str, str] = {
    "Provincia de Buenos Aires": "Buenos Aires",
    "Buenos Aires (Conurbano)":  "Buenos Aires",
    "Ciudad de Buenos Aires":    "CABA",
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "Tierra del Fuego",
}

# GeoJSON property name que corresponde a la provincia
GEOJSON_NAME_PROPERTY = "name"

# Equivalencias GeoJSON → nombre canónico
GEOJSON_ALIASES: dict[str, str] = {
    "Ciudad de Buenos Aires": "CABA",
}


def normalize_provincia(name: str) -> str:
    """Retorna el nombre canónico de la provincia."""
    if not name:
        return ""
    name = str(name).strip()
    return PROVINCIA_ALIASES.get(name, name)
