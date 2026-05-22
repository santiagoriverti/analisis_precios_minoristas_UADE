"""Agregación de precios: canasta por sucursal, provincia, región y nación.

Implementa:
- Precio mensual promedio por (EAN, sucursal)
- Canasta completa con imputación de productos faltantes (vectorizado)
- Ponderación poblacional para agregación nacional
"""
from __future__ import annotations

import logging
import pandas as pd
import numpy as np

from ..config.canasta import CANASTA_RAW, get_canasta_df
from ..config.settings import (
    MIN_BASKET_PRODUCTS, TOTAL_BASKET_PRODUCTS,
    POPULATION_WEIGHTS, TOTAL_POPULATION,
)

log = logging.getLogger(__name__)


def compute_monthly_avg(
    df: pd.DataFrame,
    ean_col: str = "ean_norm",
    price_col: str = "precio",
    date_col: str = "fecha",
) -> pd.DataFrame:
    """Calcula precio promedio mensual por (EAN, sucursal).

    Input:  df largo con una fila por precio diario.
    Output: df con columna 'mes' (YYYY-MM) y 'precio_mes'.
    """
    df = df.copy()
    df["mes"] = df[date_col].dt.to_period("M").astype(str)

    group_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal", ean_col, "mes"]
                  if c in df.columns]
    result = (
        df.groupby(group_cols, observed=True)[price_col]
        .mean()
        .reset_index()
        .rename(columns={price_col: "precio_mes"})
    )
    log.info("Precios mensuales: %d filas, %d meses", len(result),
             result["mes"].nunique() if "mes" in result.columns else 0)
    return result


def build_branch_basket(
    df_monthly: pd.DataFrame,
    impute_with_national: bool = True,
    min_own_products: int = MIN_BASKET_PRODUCTS,
) -> pd.DataFrame:
    """Construye la canasta mensual por sucursal (operaciones vectorizadas).

    Para cada (sucursal, mes):
    - Usa precios propios para los productos que la sucursal reporta
    - Imputa el promedio nacional para los productos faltantes
    - Excluye sucursales con menos de min_own_products productos propios

    Retorna columnas:
      id_comercio, id_bandera, id_sucursal, mes, canasta_total,
      n_productos_propios, n_productos_imputados
    """
    canasta_df = get_canasta_df()
    canasta_eans = set(canasta_df["ean_str"].tolist())
    qty_map = canasta_df.set_index("ean_str")["cantidad"].to_dict()

    # Filtrar solo productos de la canasta
    df_c = df_monthly[df_monthly["ean_norm"].isin(canasta_eans)].copy()
    if df_c.empty:
        log.warning("No hay precios para productos de la canasta")
        return pd.DataFrame()

    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_c.columns]
    all_group = branch_cols + ["mes"]

    # Cantidad mensual de cada EAN
    df_c["cantidad"] = df_c["ean_norm"].map(qty_map)
    df_c["subtotal"] = df_c["precio_mes"] * df_c["cantidad"]

    # ── Promedio nacional por (ean, mes) para imputación ─────────────────────
    nat_avg = (
        df_c.groupby(["ean_norm", "mes"], observed=True)["precio_mes"]
        .mean()
        .reset_index(name="precio_nacional")
    )
    nat_avg["cantidad"] = nat_avg["ean_norm"].map(qty_map)
    nat_avg["subtotal_nacional"] = nat_avg["precio_nacional"] * nat_avg["cantidad"]

    # Total canasta a precios nacionales (los 30 productos) por mes
    canasta_nat_total = (
        nat_avg.groupby("mes", observed=True)["subtotal_nacional"]
        .sum()
        .reset_index(name="canasta_nacional_total")
    )

    # ── Subtotales propios y count de productos por sucursal+mes ─────────────
    own_agg = (
        df_c.groupby(all_group + ["ean_norm"], observed=True)["precio_mes"]
        .mean()
        .reset_index(name="precio_propio")
    )
    own_agg["cantidad"] = own_agg["ean_norm"].map(qty_map)
    own_agg["subtotal_propio"] = own_agg["precio_propio"] * own_agg["cantidad"]

    # Subtotal nacional de los productos que la sucursal SÍ tiene
    own_agg = own_agg.merge(
        nat_avg[["ean_norm", "mes", "subtotal_nacional"]],
        on=["ean_norm", "mes"], how="left"
    )

    # Agregar por (sucursal, mes)
    result = (
        own_agg.groupby(all_group, observed=True)
        .agg(
            subtotal_propio=("subtotal_propio", "sum"),
            subtotal_nacional_de_propios=("subtotal_nacional", "sum"),
            n_productos_propios=("ean_norm", "nunique"),
        )
        .reset_index()
    )

    # Filtrar sucursales con cobertura mínima
    result = result[result["n_productos_propios"] >= min_own_products].copy()

    if result.empty:
        log.warning("Ninguna sucursal supera el mínimo de %d productos propios", min_own_products)
        return pd.DataFrame()

    # ── Canasta total = propios a precio propio + faltantes a precio nacional ─
    result = result.merge(canasta_nat_total, on="mes", how="left")

    if impute_with_national:
        # canasta_total = subtotal_propio + (canasta_total_nacional - nacional_de_propios)
        result["canasta_total"] = (
            result["subtotal_propio"]
            + (result["canasta_nacional_total"] - result["subtotal_nacional_de_propios"])
        )
    else:
        result["canasta_total"] = result["subtotal_propio"]

    result["n_productos_imputados"] = TOTAL_BASKET_PRODUCTS - result["n_productos_propios"]

    # Limpiar columnas intermedias
    result = result.drop(columns=["subtotal_propio", "subtotal_nacional_de_propios",
                                   "canasta_nacional_total"], errors="ignore")

    log.info("Canasta por sucursal: %d filas, %d meses", len(result),
             result["mes"].nunique() if "mes" in result.columns else 0)
    return result


def aggregate_by_province(
    df_branch: pd.DataFrame,
    df_enriched: pd.DataFrame,
) -> pd.DataFrame:
    """Agrega la canasta promedio de sucursales por provincia y mes."""
    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"]
                   if c in df_enriched.columns]
    extra_cols = [c for c in ["provincia", "region"] if c in df_enriched.columns]
    suc_prov = (
        df_enriched[branch_cols + extra_cols]
        .drop_duplicates(subset=branch_cols)
    )
    df = df_branch.merge(suc_prov, on=branch_cols, how="left")

    group_cols = [c for c in ["provincia", "region", "mes"] if c in df.columns]
    result = (
        df.groupby(group_cols, observed=True)["canasta_total"]
        .mean()
        .reset_index()
        .rename(columns={"canasta_total": "canasta_provincia"})
    )
    return result


def aggregate_by_region(df_province: pd.DataFrame) -> pd.DataFrame:
    """Agrega la canasta promedio de provincias por región y mes."""
    if "region" not in df_province.columns:
        return pd.DataFrame()
    return (
        df_province.groupby(["region", "mes"], observed=True)["canasta_provincia"]
        .mean()
        .reset_index()
        .rename(columns={"canasta_provincia": "canasta_region"})
    )


def aggregate_national_weighted(df_province: pd.DataFrame) -> pd.DataFrame:
    """Canasta nacional ponderada por población (Censo INDEC 2022)."""
    df = df_province.copy()
    df["peso"] = df["provincia"].map(POPULATION_WEIGHTS).fillna(0) / TOTAL_POPULATION
    df["canasta_ponderada"] = df["canasta_provincia"] * df["peso"]

    result = (
        df.groupby("mes", observed=True)["canasta_ponderada"]
        .sum()
        .reset_index()
        .rename(columns={"canasta_ponderada": "canasta_nacional"})
        .sort_values("mes")
    )
    result["variacion_pct"] = result["canasta_nacional"].pct_change() * 100
    return result
