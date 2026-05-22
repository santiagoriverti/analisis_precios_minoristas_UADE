"""Análisis de la canasta: cobertura, rankings y comparativas provinciales."""
from __future__ import annotations

import logging
import pandas as pd
import numpy as np

from ..config.canasta import get_canasta_df, CANASTA_RAW

log = logging.getLogger(__name__)


def basket_by_province(df_province: pd.DataFrame, last_month: str | None = None) -> pd.DataFrame:
    """Retorna el valor de canasta por provincia para un mes dado.

    df_province: output de aggregator.aggregate_by_province()
    last_month:  'YYYY-MM'; si None usa el último mes disponible.
    """
    if last_month is None:
        last_month = df_province["mes"].max()

    df = df_province[df_province["mes"] == last_month].copy()
    national_avg = df["canasta_provincia"].mean()

    df["vs_promedio_pct"] = (df["canasta_provincia"] / national_avg - 1) * 100
    df = df.sort_values("canasta_provincia")
    df["ranking"] = range(1, len(df) + 1)
    log.info("Canasta por provincia: mes=%s, n=%d, promedio=%.0f", last_month, len(df), national_avg)
    return df


def product_coverage_summary(df_products: pd.DataFrame, ean_col: str = "ean_norm") -> pd.DataFrame:
    """Métricas de cobertura del universo de productos SEPA.

    df_products debe tener columnas: ean_norm, n_sucursales, n_cadenas, n_provincias,
    precio_promedio, precio_cv (o calcula las que puede).
    """
    canasta = get_canasta_df()
    canasta_eans = set(canasta["ean_str"].tolist())

    df = df_products.copy()
    df["en_canasta"] = df[ean_col].isin(canasta_eans)

    summary = {
        "total_productos":    len(df),
        "en_canasta":         df["en_canasta"].sum(),
        "alta_cobertura":     (df.get("n_provincias", pd.Series(dtype=int)) >= 20).sum() if "n_provincias" in df.columns else None,
        "promedio_cadenas":   df.get("n_cadenas", pd.Series(dtype=float)).mean() if "n_cadenas" in df.columns else None,
    }
    return pd.Series(summary)


def canasta_composition_table() -> pd.DataFrame:
    """Tabla de composición de la canasta con pesos por categoría."""
    df = get_canasta_df()
    return df[["ean_str", "nombre", "categoria", "cantidad"]].copy()


def compute_price_dispersion(df_branch: pd.DataFrame) -> pd.DataFrame:
    """Calcula dispersión de precios de canasta entre sucursales.

    Retorna estadísticas: p5, p25, p50, p75, p95, cv.
    """
    grp = df_branch.groupby("mes")["canasta_total"]
    result = grp.agg(
        p5=lambda x: x.quantile(0.05),
        p25=lambda x: x.quantile(0.25),
        p50="median",
        p75=lambda x: x.quantile(0.75),
        p95=lambda x: x.quantile(0.95),
        mean="mean",
        std="std",
    ).reset_index()
    result["cv"] = result["std"] / result["mean"]
    return result
