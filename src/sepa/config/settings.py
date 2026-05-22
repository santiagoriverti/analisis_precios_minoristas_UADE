"""Global settings — auto-detects Google Colab vs. local execution."""
import os
from pathlib import Path

IS_COLAB = "COLAB_RELEASE_TAG" in os.environ or os.path.exists("/content")

if IS_COLAB:
    PROJECT_ROOT = Path("/content/analisis_precios_minoristas_UADE")
else:
    # src/sepa/config/settings.py → project root is 3 levels up
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
MASTERS_DIR = DATA_DIR / "masters"
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = DATA_DIR / "output"
PRODUCTS_DIR = PROJECT_ROOT / "products"
MEMORY_DIR = PROJECT_ROOT / "memory"
MEMORY_DB = MEMORY_DIR / "state.db"

# ── Maestros (nombres por defecto, configurables) ──────────────────────────
MASTER_PRODUCTS_FILENAME = "Maestro de Productos Interno.xlsx"
MASTER_BRANCHES_FILENAME = "maestro_sucursales_completo.xlsx"
IPC_FILENAME = "IPC.xlsx"

# ── Filtros de calidad ──────────────────────────────────────────────────────
MIN_VALID_PRICE = 5.0          # precios menores son placeholders
MIN_BASKET_PRODUCTS = 20       # mínimo de productos propios para incluir una sucursal
TOTAL_BASKET_PRODUCTS = 30

# ── Coordenadas válidas Argentina ───────────────────────────────────────────
LAT_MIN, LAT_MAX = -55.0, -22.0
LON_MIN, LON_MAX = -73.0, -53.0

# ── Semestres disponibles ───────────────────────────────────────────────────
SEMESTERS = [
    "2022A", "2022B",
    "2023A", "2023B",
    "2024A", "2024B",
    "2025A", "2025B",
    "2026A",
]

# Primer mes con cobertura estable de SEPA
VALID_FROM = "2023-05"

# ── Pesos poblacionales (Censo 2022) ────────────────────────────────────────
POPULATION_WEIGHTS = {
    "Buenos Aires":        17_569_053,
    "CABA":                 3_075_646,
    "Catamarca":              429_301,
    "Chaco":                1_204_541,
    "Chubut":                 618_994,
    "Córdoba":              3_978_984,
    "Corrientes":           1_120_801,
    "Entre Ríos":           1_385_961,
    "Formosa":                606_041,
    "Jujuy":                  795_988,
    "La Pampa":               365_571,
    "La Rioja":               393_531,
    "Mendoza":              2_014_533,
    "Misiones":             1_273_739,
    "Neuquén":                664_057,
    "Río Negro":              747_610,
    "Salta":                1_441_988,
    "San Juan":               781_217,
    "San Luis":               508_328,
    "Santa Cruz":             333_473,
    "Santa Fe":             3_536_418,
    "Santiago del Estero":    978_313,
    "Tierra del Fuego":       173_432,
    "Tucumán":              1_694_656,
}
TOTAL_POPULATION = sum(POPULATION_WEIGHTS.values())
