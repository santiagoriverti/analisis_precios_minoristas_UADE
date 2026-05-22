"""Rankings de cadenas por precio de canasta (nacional y por zona)."""
from __future__ import annotations

import logging
import pandas as pd

log = logging.getLogger(__name__)

# Regiones consideradas AMBA
AMBA_PROVINCIAS = {"Buenos Aires", "CABA"}


def chain_ranking(
    df_branch: pd.DataFrame,
    df_enriched: pd.DataFrame,
    mes: str | None = None,
    region_filter: set[str] | None = None,
) -> pd.DataFrame:
    """Ranking de cadenas por canasta promedio para un mes y zona dados.

    Parameters
    ----------
    df_branch   : output de build_branch_basket() — tiene canasta_total por sucursal
    df_enriched : DataFrame con columnas cadena, provincia (para join)
    mes         : 'YYYY-MM'; si None usa el último mes
    region_filter : set de nombres de provincia para filtrar; None = nacional
    """
    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_enriched.columns]
    suc_info = df_enriched[branch_cols + ["cadena", "provincia"]].drop_duplicates(subset=branch_cols)

    df = df_branch.merge(suc_info, on=branch_cols, how="left")
    df = df.dropna(subset=["cadena"])

    if mes is None:
        mes = df["mes"].max()
    df = df[df["mes"] == mes]

    if region_filter:
        df = df[df["provincia"].isin(region_filter)]

    result = (
        df.groupby("cadena")
        .agg(
            canasta_promedio=("canasta_total", "mean"),
            n_sucursales=("canasta_total", "count"),
        )
        .reset_index()
        .sort_values("canasta_promedio")
    )
    result["ranking"] = range(1, len(result) + 1)

    national_avg = result["canasta_promedio"].mean()
    result["vs_promedio_pct"] = (result["canasta_promedio"] / national_avg - 1) * 100

    label = "AMBA" if region_filter == AMBA_PROVINCIAS else "Nacional"
    log.info("Ranking %s (%s): %d cadenas", label, mes, len(result))
    return result


def national_ranking(df_branch: pd.DataFrame, df_enriched: pd.DataFrame, mes: str | None = None) -> pd.DataFrame:
    return chain_ranking(df_branch, df_enriched, mes=mes, region_filter=None)


def amba_ranking(df_branch: pd.DataFrame, df_enriched: pd.DataFrame, mes: str | None = None) -> pd.DataFrame:
    return chain_ranking(df_branch, df_enriched, mes=mes, region_filter=AMBA_PROVINCIAS)


def chain_time_series(df_branch: pd.DataFrame, df_enriched: pd.DataFrame) -> pd.DataFrame:
    """Canasta promedio mensual por cadena (serie temporal)."""
    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_enriched.columns]
    suc_info = df_enriched[branch_cols + ["cadena"]].drop_duplicates(subset=branch_cols)
    df = df_branch.merge(suc_info, on=branch_cols, how="left").dropna(subset=["cadena"])

    return (
        df.groupby(["cadena", "mes"])["canasta_total"]
        .mean()
        .reset_index()
        .rename(columns={"canasta_total": "canasta_promedio"})
        .sort_values(["cadena", "mes"])
    )
