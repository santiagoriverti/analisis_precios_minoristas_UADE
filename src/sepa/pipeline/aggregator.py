"""Agregación de precios: canasta por sucursal, provincia, región y nación.

Implementa:
- Precio mensual promedio por (EAN, sucursal)
- Canasta completa con imputación de productos faltantes
- Peso poblacional para agregación nacional
"""
from __future__ import annotations

import logging
import pandas as pd
import numpy as np

from ..config.canasta import CANASTA_RAW, get_canasta_df
from ..config.settings import MIN_BASKET_PRODUCTS, TOTAL_BASKET_PRODUCTS, POPULATION_WEIGHTS, TOTAL_POPULATION

log = logging.getLogger(__name__)


def compute_monthly_avg(df: pd.DataFrame,
                        ean_col: str = "ean_norm",
                        price_col: str = "precio",
                        date_col: str = "fecha") -> pd.DataFrame:
    """Calcula precio promedio mensual por (EAN, sucursal).

    Input: df largo con una fila por precio diario.
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
    return result


def build_branch_basket(
    df_monthly: pd.DataFrame,
    impute_with_national: bool = True,
    min_own_products: int = MIN_BASKET_PRODUCTS,
) -> pd.DataFrame:
    """Construye la canasta por sucursal para cada mes.

    Para cada (sucursal, mes):
    - Calcula precio mensual promedio de cada producto de la canasta
    - Si la sucursal no tiene un producto → imputa con el promedio nacional de ese mes
    - Filtra sucursales con menos de min_own_products productos propios
    - Retorna el total de canasta por sucursal + metadata

    Columnas en el output:
      id_comercio, id_bandera, id_sucursal, mes, canasta_total,
      n_productos_propios, n_productos_imputados
    """
    canasta_df = get_canasta_df()
    canasta_eans = set(canasta_df["ean_str"].tolist())

    # Filtrar solo productos de la canasta
    df_c = df_monthly[df_monthly["ean_norm"].isin(canasta_eans)].copy()
    if df_c.empty:
        log.warning("No hay precios para productos de la canasta")
        return pd.DataFrame()

    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_c.columns]

    # Promedio nacional por (ean, mes) para imputación
    national_avg = (
        df_c.groupby(["ean_norm", "mes"], observed=True)["precio_mes"]
        .mean()
        .reset_index()
        .rename(columns={"precio_mes": "precio_nacional"})
    )

    # Merge canasta × sucursales × meses: producto cartesiano
    meses = df_c["mes"].unique()
    sucursales = df_c[branch_cols].drop_duplicates()

    # Construir tabla completa: todas las combinaciones sucursal × ean × mes
    canasta_long = canasta_df[["ean_str", "nombre", "categoria", "cantidad"]].rename(columns={"ean_str": "ean_norm"})

    records = []
    for mes in meses:
        df_mes = df_c[df_c["mes"] == mes]
        nat_mes = national_avg[national_avg["mes"] == mes].set_index("ean_norm")["precio_nacional"]

        for _, suc_row in sucursales.iterrows():
            suc_mask = True
            for col in branch_cols:
                suc_mask = suc_mask & (df_mes[col] == suc_row[col])
            df_suc = df_mes[suc_mask]

            propios = df_suc.set_index("ean_norm")["precio_mes"].to_dict()
            total = 0.0
            n_propios = 0
            n_imputados = 0

            for _, prod in canasta_long.iterrows():
                ean = prod["ean_norm"]
                qty = prod["cantidad"]
                if ean in propios:
                    precio = propios[ean]
                    n_propios += 1
                elif impute_with_national and ean in nat_mes.index:
                    precio = nat_mes[ean]
                    n_imputados += 1
                else:
                    precio = np.nan
                total += (precio * qty) if pd.notna(precio) else 0

            if n_propios >= min_own_products:
                row = {col: suc_row[col] for col in branch_cols}
                row.update({"mes": mes, "canasta_total": total,
                             "n_productos_propios": n_propios,
                             "n_productos_imputados": n_imputados})
                records.append(row)

    result = pd.DataFrame(records)
    log.info("Canasta por sucursal: %d filas (%d meses)", len(result), len(meses))
    return result


def aggregate_by_province(df_branch: pd.DataFrame, df_enriched: pd.DataFrame) -> pd.DataFrame:
    """Agrega la canasta de sucursales por provincia y mes."""
    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_enriched.columns]
    suc_prov = df_enriched[branch_cols + ["provincia", "region"]].drop_duplicates(subset=branch_cols)

    df = df_branch.merge(suc_prov, on=branch_cols, how="left")
    result = (
        df.groupby(["provincia", "mes"], observed=True)["canasta_total"]
        .mean()
        .reset_index()
        .rename(columns={"canasta_total": "canasta_provincia"})
    )
    return result


def aggregate_national_weighted(df_province: pd.DataFrame) -> pd.DataFrame:
    """Canasta nacional ponderada por población (Censo 2022)."""
    total_pop = TOTAL_POPULATION
    df = df_province.copy()
    df["peso"] = df["provincia"].map(POPULATION_WEIGHTS).fillna(0) / total_pop
    df["canasta_ponderada"] = df["canasta_provincia"] * df["peso"]

    result = (
        df.groupby("mes")["canasta_ponderada"]
        .sum()
        .reset_index()
        .rename(columns={"canasta_ponderada": "canasta_nacional"})
        .sort_values("mes")
    )

    # Variación mensual
    result["variacion_pct"] = result["canasta_nacional"].pct_change() * 100
    return result
