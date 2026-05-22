"""Limpieza de datos de precios SEPA.

Responsabilidades:
- Detección automática del factor de escala de precios
- Filtrado de precios inválidos
- Deduplicación
- Validación de coordenadas
"""
from __future__ import annotations

import logging
import numpy as np
import pandas as pd

from ..config.settings import MIN_VALID_PRICE, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX
from ..config.canasta import REFERENCE_EANS_FOR_SCALE

log = logging.getLogger(__name__)

# Rangos de precio esperado por unidad para detectar el factor de escala
# (mediana de la sal en ARS reales según el período)
_SCALE_RANGES = {
    1:     (30,    10_000),    # precios ya en pesos
    100:   (3_000, 1_000_000), # centavos → pesos (÷100)
    10_000:(100_000, 1e10),    # decimales implícitos (÷10000)
}


def detect_price_scale(df: pd.DataFrame, ean_col: str = "ean_norm", price_col: str = "precio_raw") -> int:
    """Detecta el factor divisor necesario para convertir precios a pesos reales.

    Examina medianas de EANs de referencia (Sal, Fideos, Lavandina) y compara
    contra rangos esperados para cada factor de escala posible.

    Retorna 1, 100 o 10_000.
    """
    ref = df[df[ean_col].isin(REFERENCE_EANS_FOR_SCALE)][price_col].dropna()
    if ref.empty:
        log.warning("Sin EANs de referencia para detección de escala — asumiendo factor=1")
        return 1

    median = ref.median()
    log.info("Mediana de precios de referencia: %.2f", median)

    for factor, (lo, hi) in _SCALE_RANGES.items():
        if lo <= median <= hi:
            log.info("Factor de escala detectado: %d", factor)
            return factor

    log.warning("Mediana fuera de rangos conocidos (%.2f) — asumiendo factor=1", median)
    return 1


def apply_price_scale(df: pd.DataFrame, factor: int, price_col: str = "precio_raw") -> pd.DataFrame:
    """Divide los precios por el factor y filtra valores inválidos."""
    df = df.copy()
    df["precio"] = df[price_col] / factor
    df = df[df["precio"] >= MIN_VALID_PRICE].copy()
    return df


def clean_prices(
    df: pd.DataFrame,
    ean_col: str = "ean_norm",
    price_col: str = "precio_raw",
    auto_scale: bool = True,
) -> pd.DataFrame:
    """Pipeline completo de limpieza de precios.

    1. Convierte precio_raw a numérico
    2. Detecta y aplica factor de escala
    3. Filtra precios < MIN_VALID_PRICE
    4. Elimina duplicados
    """
    df = df.copy()
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[price_col])
    df = df[df[price_col] > 0]

    if auto_scale:
        factor = detect_price_scale(df, ean_col=ean_col, price_col=price_col)
    else:
        factor = 1

    df = apply_price_scale(df, factor, price_col=price_col)

    # Deduplicación por clave natural
    key_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal", ean_col, "fecha"] if c in df.columns]
    if key_cols:
        before = len(df)
        df = df.drop_duplicates(subset=key_cols, keep="last")
        log.info("Deduplicación: %d → %d filas", before, len(df))

    log.info("Precios limpios: %d filas, factor=%d", len(df), factor)
    return df


def filter_valid_coordinates(df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lng") -> pd.DataFrame:
    """Filtra filas con coordenadas dentro del territorio argentino."""
    if lat_col not in df.columns or lon_col not in df.columns:
        return df
    mask = (
        df[lat_col].between(LAT_MIN, LAT_MAX) &
        df[lon_col].between(LON_MIN, LON_MAX)
    )
    dropped = (~mask).sum()
    if dropped > 0:
        log.info("Coordenadas inválidas removidas: %d filas", dropped)
    return df[mask].copy()


def normalize_ean_column(df: pd.DataFrame, ean_col: str) -> pd.DataFrame:
    """Normaliza EANs removiendo ceros a la izquierda."""
    df = df.copy()
    df["ean_norm"] = df[ean_col].astype(str).str.strip().str.lstrip("0")
    return df
