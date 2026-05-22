"""Definición de la canasta fija de 30 productos (ICM-UADE).

Cada producto tiene:
  ean      → código EAN-13 (int)
  nombre   → nombre descriptivo
  categoria → grupo (Lácteos, Almacén, Bebidas, Limpieza, Higiene, Snacks)
  cantidad → unidades mensuales para hogar de 4 personas
"""
import pandas as pd

CANASTA_RAW: list[dict] = [
    # ── Lácteos ──────────────────────────────────────────────────────────────
    {"ean": 7790742363008, "nombre": "Leche entera 1L",       "categoria": "Lácteos",  "cantidad": 20},
    {"ean": 7790580503002, "nombre": "Yogur 190g",             "categoria": "Lácteos",  "cantidad":  8},
    {"ean": 7790900029305, "nombre": "Queso Casancrem 290g",   "categoria": "Lácteos",  "cantidad":  2},
    {"ean": 7790040738000, "nombre": "Manteca 100g",           "categoria": "Lácteos",  "cantidad":  2},
    {"ean": 7790742362001, "nombre": "Cindor 1L",              "categoria": "Lácteos",  "cantidad":  4},
    # ── Almacén ──────────────────────────────────────────────────────────────
    {"ean": 7794000012000, "nombre": "Aceite girasol 1.5L",   "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7790895000785, "nombre": "Arroz 500g",             "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7792260000101, "nombre": "Fideos 500g",            "categoria": "Almacén",  "cantidad":  4},
    {"ean": 7790895000044, "nombre": "Harina leudante 1kg",   "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7790940012106, "nombre": "Yerba 500g",             "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7790580018018, "nombre": "Café 250g",              "categoria": "Almacén",  "cantidad":  1},
    {"ean": 7790040067000, "nombre": "Chocolinas 250g",        "categoria": "Almacén",  "cantidad":  4},
    {"ean": 7790380000057, "nombre": "Sal fina 500g",          "categoria": "Almacén",  "cantidad":  1},
    # ── Bebidas ──────────────────────────────────────────────────────────────
    {"ean": 7790895004837, "nombre": "Coca Cola lata 354ml",  "categoria": "Bebidas",  "cantidad":  8},
    {"ean": 7790895104277, "nombre": "Coca Sin Azúcar 2.25L", "categoria": "Bebidas",  "cantidad":  4},
    {"ean": 7798108640055, "nombre": "Agua Levite 500ml",     "categoria": "Bebidas",  "cantidad":  8},
    {"ean": 7790269000012, "nombre": "Cerveza lata 473ml",    "categoria": "Bebidas",  "cantidad":  6},
    {"ean": 7798034980083, "nombre": "Vino Malbec 750ml",     "categoria": "Bebidas",  "cantidad":  2},
    # ── Limpieza ─────────────────────────────────────────────────────────────
    {"ean": 7790230512009, "nombre": "Lavandina 1L",           "categoria": "Limpieza", "cantidad":  2},
    {"ean": 7791290047006, "nombre": "Detergente 300ml",       "categoria": "Limpieza", "cantidad":  2},
    {"ean": 7790940016050, "nombre": "Limpiador Poett 900ml", "categoria": "Limpieza", "cantidad":  2},
    # ── Higiene ──────────────────────────────────────────────────────────────
    {"ean": 7791293020063, "nombre": "Shampoo 400ml",          "categoria": "Higiene",  "cantidad":  1},
    {"ean": 7791293020070, "nombre": "Acondicionador 340ml",  "categoria": "Higiene",  "cantidad":  1},
    {"ean": 7702006209025, "nombre": "Jabón tocador 90g",      "categoria": "Higiene",  "cantidad":  4},
    {"ean": 7509546038000, "nombre": "Antitranspirante",       "categoria": "Higiene",  "cantidad":  2},
    {"ean": 7702006092003, "nombre": "Hilo dental",            "categoria": "Higiene",  "cantidad":  1},
    {"ean": 7702006212001, "nombre": "Toallas femeninas x16", "categoria": "Higiene",  "cantidad":  2},
    {"ean": 7702006088006, "nombre": "Papel higiénico",        "categoria": "Higiene",  "cantidad":  2},
    # ── Snacks ───────────────────────────────────────────────────────────────
    {"ean": 7790580413405, "nombre": "Rocklets 40g",           "categoria": "Snacks",   "cantidad":  2},
    {"ean": 7790040575001, "nombre": "Saladix 100g",           "categoria": "Snacks",   "cantidad":  2},
]

def get_canasta_df() -> pd.DataFrame:
    """Retorna la canasta como DataFrame con columna ean_str normalizada."""
    df = pd.DataFrame(CANASTA_RAW)
    df["ean_str"] = df["ean"].astype(str).str.lstrip("0")
    return df

# Lookup rápido: ean_str → dict del producto
CANASTA_BY_EAN: dict[str, dict] = {
    str(p["ean"]).lstrip("0"): p for p in CANASTA_RAW
}

CANASTA_EANS: set[str] = set(CANASTA_BY_EAN.keys())

# Productos de referencia para detección de escala de precios
REFERENCE_EANS_FOR_SCALE = {
    str(7790380000057).lstrip("0"),  # Sal
    str(7792260000101).lstrip("0"),  # Fideos
    str(7790230512009).lstrip("0"),  # Lavandina
}

CATEGORIAS = ["Lácteos", "Almacén", "Bebidas", "Limpieza", "Higiene", "Snacks"]
