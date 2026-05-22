"""Definición de la canasta fija de 30 productos (ICM-UADE).

EANs verificados contra el Maestro de Productos Interno (176.702 filas).
Cantidades mensuales calibradas para hogar tipo de 4 personas.
Total: 30 productos, 105 unidades mensuales.
"""
import pandas as pd

CANASTA_RAW: list[dict] = [
    # ── Lácteos (5) ──────────────────────────────────────────────────────────
    {"ean": 7790742363008, "nombre": "Leche entera 1L (Serenísima)",   "categoria": "Lácteos",  "cantidad": 20},
    {"ean": 7791337007628, "nombre": "Yogur 190g",                      "categoria": "Lácteos",  "cantidad":  8},
    {"ean": 7791337061361, "nombre": "Queso Casancrem 290g",            "categoria": "Lácteos",  "cantidad":  2},
    {"ean": 7793940052002, "nombre": "Manteca 100g",                    "categoria": "Lácteos",  "cantidad":  2},
    {"ean": 7791337007253, "nombre": "Cindor 1L",                       "categoria": "Lácteos",  "cantidad":  4},
    # ── Almacén (8) ──────────────────────────────────────────────────────────
    {"ean": 7790272001029, "nombre": "Aceite girasol 1,5L",             "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7790070433114, "nombre": "Arroz 500g",                      "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7790070320285, "nombre": "Fideos 500g (Favorita)",          "categoria": "Almacén",  "cantidad":  4},
    {"ean": 7792180140708, "nombre": "Harina leudante 1kg",             "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7792710000182, "nombre": "Yerba 500g",                      "categoria": "Almacén",  "cantidad":  2},
    {"ean": 7790550000157, "nombre": "Café 250g",                       "categoria": "Almacén",  "cantidad":  1},
    {"ean": 7790040143234, "nombre": "Chocolinas 250g",                 "categoria": "Almacén",  "cantidad":  4},
    {"ean": 7790072002080, "nombre": "Sal fina 500g (Celusal)",         "categoria": "Almacén",  "cantidad":  1},
    # ── Bebidas (5) ──────────────────────────────────────────────────────────
    {"ean": 7790895000232, "nombre": "Coca Cola lata 354ml",            "categoria": "Bebidas",  "cantidad":  8},
    {"ean": 7790895067570, "nombre": "Coca Sin Azúcar 2,25L",           "categoria": "Bebidas",  "cantidad":  4},
    {"ean": 7798062548716, "nombre": "Agua Levite 500ml",               "categoria": "Bebidas",  "cantidad":  8},
    {"ean": 7793147118860, "nombre": "Cerveza lata 473ml",              "categoria": "Bebidas",  "cantidad":  6},
    {"ean": 7798074864675, "nombre": "Vino Malbec 750ml",               "categoria": "Bebidas",  "cantidad":  2},
    # ── Limpieza (3) ─────────────────────────────────────────────────────────
    {"ean": 7790132098459, "nombre": "Lavandina 1L (Ayudín)",           "categoria": "Limpieza", "cantidad":  2},
    {"ean": 7791290794054, "nombre": "Detergente 300ml",                "categoria": "Limpieza", "cantidad":  2},
    {"ean": 7793253003500, "nombre": "Limpiador Poett 900ml",           "categoria": "Limpieza", "cantidad":  2},
    # ── Higiene (7) ──────────────────────────────────────────────────────────
    {"ean": 7791293047447, "nombre": "Shampoo 400ml",                   "categoria": "Higiene",  "cantidad":  1},
    {"ean": 7791293045948, "nombre": "Acondicionador 340ml",            "categoria": "Higiene",  "cantidad":  1},
    {"ean": 7791293051208, "nombre": "Jabón tocador 90g",               "categoria": "Higiene",  "cantidad":  4},
    {"ean": 7791293049557, "nombre": "Antitranspirante",                "categoria": "Higiene",  "cantidad":  2},
    {"ean": 7891024183083, "nombre": "Hilo dental",                     "categoria": "Higiene",  "cantidad":  1},
    {"ean": 7790770601899, "nombre": "Toallas femeninas x16",           "categoria": "Higiene",  "cantidad":  2},
    {"ean": 7790250015840, "nombre": "Papel higiénico",                 "categoria": "Higiene",  "cantidad":  2},
    # ── Snacks (2) ───────────────────────────────────────────────────────────
    {"ean": 7790580327415, "nombre": "Rocklets 40g",                    "categoria": "Snacks",   "cantidad":  2},
    {"ean": 7790580716707, "nombre": "Saladix 100g",                    "categoria": "Snacks",   "cantidad":  2},
]

# EANs de referencia para detección automática de factor de escala de precios
# Elegidos por ser baratos y estables (Sal, Fideos, Lavandina)
REFERENCE_EANS_FOR_SCALE: set[str] = {
    "7790072002080",  # Sal fina Celusal 500g
    "7790070320285",  # Fideos Favorita 500g
    "7790132098459",  # Lavandina Ayudín 1L
}

CATEGORIAS = ["Lácteos", "Almacén", "Bebidas", "Limpieza", "Higiene", "Snacks"]


def get_canasta_df() -> pd.DataFrame:
    """Retorna la canasta como DataFrame con columna ean_str normalizada (sin ceros a la izquierda)."""
    df = pd.DataFrame(CANASTA_RAW)
    df["ean_str"] = df["ean"].astype(str).str.lstrip("0")
    return df


# Lookups rápidos
CANASTA_BY_EAN: dict[str, dict] = {str(p["ean"]).lstrip("0"): p for p in CANASTA_RAW}
CANASTA_EANS:   set[str]        = set(CANASTA_BY_EAN.keys())
