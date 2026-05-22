"""Análisis de la canasta: cobertura, rankings provinciales y dispersión."""
from __future__ import annotations

import logging
import pandas as pd
import numpy as np

from ..config.canasta import get_canasta_df

log = logging.getLogger(__name__)


def basket_by_province(df_province: pd.DataFrame, last_month: str | None = None) -> pd.DataFrame:
    """Retorna el valor de canasta por provincia para un mes dado con ranking.

    df_province: output de aggregate_by_province() — tiene columna 'canasta_provincia'
    last_month:  'YYYY-MM'; si None usa el último mes disponible.
    """
    if last_month is None:
        last_month = df_province["mes"].max()

    df = df_province[df_province["mes"] == last_month].copy()
    if df.empty:
        log.warning("Sin datos para mes=%s", last_month)
        return df

    national_avg = df["canasta_provincia"].mean()
    df["vs_promedio_pct"] = (df["canasta_provincia"] / national_avg - 1) * 100
    df = df.sort_values("canasta_provincia").reset_index(drop=True)
    df["ranking"] = range(1, len(df) + 1)

    log.info("Canasta por provincia: mes=%s, n=%d, promedio=%.0f",
             last_month, len(df), national_avg)
    return df


def product_coverage_summary(df_products: pd.DataFrame, ean_col: str = "ean_norm") -> pd.Series:
    """Métricas de cobertura del universo de productos SEPA."""
    canasta = get_canasta_df()
    canasta_eans = set(canasta["ean_str"].tolist())

    df = df_products.copy()
    df["en_canasta"] = df[ean_col].isin(canasta_eans)

    summary = {
        "total_productos": len(df),
        "en_canasta":      int(df["en_canasta"].sum()),
        "alta_cobertura":  int((df["n_provincias"] >= 20).sum()) if "n_provincias" in df.columns else None,
        "promedio_cadenas": float(df["n_cadenas"].mean()) if "n_cadenas" in df.columns else None,
    }
    return pd.Series(summary)


def canasta_composition_table() -> pd.DataFrame:
    """Tabla de composición de la canasta con EANs, cantidades y categorías."""
    return get_canasta_df()[["ean_str", "nombre", "categoria", "cantidad"]].copy()


def compute_price_dispersion(df_branch: pd.DataFrame, mes_col: str = "mes") -> pd.DataFrame:
    """Dispersión de precios de canasta entre sucursales por mes.

    Métricas: p5, p25, p50, p75, p95, mean, std, cv (coef. de variación).
    """
    grp = df_branch.groupby(mes_col, observed=True)["canasta_total"]
    result = grp.agg(
        p5=lambda x: x.quantile(0.05),
        p25=lambda x: x.quantile(0.25),
        p50="median",
        p75=lambda x: x.quantile(0.75),
        p95=lambda x: x.quantile(0.95),
        mean="mean",
        std="std",
        n="count",
    ).reset_index()
    result["cv"] = result["std"] / result["mean"]
    result["brecha_p10_p90"] = grp.quantile(0.9).values / grp.quantile(0.1).values - 1
    return result


def barrio_ranking_caba(df_branch: pd.DataFrame, df_enriched: pd.DataFrame,
                        mes: str | None = None) -> pd.DataFrame:
    """Ranking de precios de canasta por barrio de CABA.

    Requiere que df_enriched tenga columna 'barrio_caba' (asignada en enricher).
    Filtra a sucursales en CABA con barrio asignado y mínimo 2 sucursales por barrio.
    """
    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"]
                   if c in df_enriched.columns]
    if "barrio_caba" not in df_enriched.columns or "provincia" not in df_enriched.columns:
        log.warning("barrio_caba o provincia no disponibles en df_enriched")
        return pd.DataFrame()

    suc_caba = (
        df_enriched[df_enriched["provincia"] == "CABA"][branch_cols + ["barrio_caba"]]
        .dropna(subset=["barrio_caba"])
        .drop_duplicates(subset=branch_cols)
    )

    if mes is None:
        mes = df_branch["mes"].max()
    df = df_branch[df_branch["mes"] == mes].merge(suc_caba, on=branch_cols, how="inner")
    if df.empty:
        return pd.DataFrame()

    result = (
        df.groupby("barrio_caba")["canasta_total"]
        .agg(canasta_barrio="mean", n_sucursales="count")
        .reset_index()
    )
    result = result[result["n_sucursales"] >= 2]  # mínimo 2 sucursales por barrio

    caba_avg = result["canasta_barrio"].mean()
    result["vs_promedio_caba_pct"] = (result["canasta_barrio"] / caba_avg - 1) * 100
    result = result.sort_values("canasta_barrio", ascending=False).reset_index(drop=True)
    result["ranking"] = range(1, len(result) + 1)

    log.info("Ranking barrios CABA: %d barrios, mes=%s", len(result), mes)
    return result
