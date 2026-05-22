"""Global settings — auto-detects Google Colab vs. local execution."""
import os
from pathlib import Path

IS_COLAB = "COLAB_RELEASE_TAG" in os.environ or os.path.exists("/content")

if IS_COLAB:
    PROJECT_ROOT = Path("/content/analisis_precios_minoristas_UADE")
else:
    # src/sepa/config/settings.py → raíz del proyecto es 3 niveles arriba
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR     = PROJECT_ROOT / "data"
INPUT_DIR    = DATA_DIR / "input"
MASTERS_DIR  = DATA_DIR / "masters"
CACHE_DIR    = DATA_DIR / "cache"
OUTPUT_DIR   = DATA_DIR / "output"
PRODUCTS_DIR = PROJECT_ROOT / "products"
MEMORY_DIR   = PROJECT_ROOT / "memory"
MEMORY_DB    = MEMORY_DIR / "state.db"

# ── Nombres de archivos maestros ───────────────────────────────────────────
MASTER_PRODUCTS_FILENAME = "Maestro de Productos Interno.xlsx"
MASTER_BRANCHES_FILENAME = "maestro_sucursales_completo.xlsx"
IPC_FILENAME             = "IPC.xlsx"
GEOJSON_FILENAME         = "ar.json"

# ── Filtros de calidad ─────────────────────────────────────────────────────
MIN_VALID_PRICE    = 5.0   # precios menores se consideran placeholders
MIN_BASKET_PRODUCTS = 20   # mínimo de productos propios para incluir sucursal
TOTAL_BASKET_PRODUCTS = 30

# ── Filtros de sucursales ──────────────────────────────────────────────────
EXCLUIR_TIPO_WEB = True    # excluir sucursales de tipo "Web" (sin ubicación física)

# ── Coordenadas válidas Argentina ──────────────────────────────────────────
LAT_MIN, LAT_MAX = -55.0, -22.0
LON_MIN, LON_MAX = -73.0, -53.0

# ── Período válido de análisis ─────────────────────────────────────────────
# Antes de mayo 2023 la cobertura SEPA era heterogénea (muchos EANs ausentes)
VALID_FROM = "2023-05"
# Variaciones de estos meses se anulan (panel SEPA en consolidación)
NULL_VARIATION_MONTHS = ["2023-05", "2023-06"]

# ── Semestres disponibles (para procesamiento automático) ──────────────────
SEMESTERS = [
    "2022A", "2022B",
    "2023A", "2023B",
    "2024A", "2024B",
    "2025A", "2025B",
    "2026A",
]

# ── Ponderación nacional — Censo INDEC 2022 ────────────────────────────────
# Total: 45.892.285 habitantes
POPULATION_WEIGHTS: dict[str, int] = {
    "Buenos Aires":        17_523_996,
    "Córdoba":              3_840_905,
    "Santa Fe":             3_544_908,
    "CABA":                 3_121_707,
    "Mendoza":              2_043_540,
    "Tucumán":              1_731_820,
    "Salta":                1_441_351,
    "Entre Ríos":           1_425_578,
    "Misiones":             1_278_873,
    "Corrientes":           1_212_696,
    "Chaco":                1_129_606,
    "Santiago del Estero":  1_060_906,
    "San Juan":               822_853,
    "Jujuy":                  811_611,
    "Río Negro":              750_768,
    "Neuquén":                710_814,
    "Formosa":                607_419,
    "Chubut":                 592_621,
    "San Luis":               542_069,
    "Catamarca":              429_562,
    "La Rioja":               383_865,
    "La Pampa":               361_859,
    "Santa Cruz":             337_226,
    "Tierra del Fuego":       185_732,
}
TOTAL_POPULATION = sum(POPULATION_WEIGHTS.values())  # 45_892_285
