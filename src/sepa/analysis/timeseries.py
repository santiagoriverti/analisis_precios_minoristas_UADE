"""Análisis de evolución temporal: índices, variaciones y comparativa IPC.

Consolida los resultados de múltiples semestres y los compara contra el IPC INDEC.
"""
from __future__ import annotations

import logging
from pathlib import Path
import pandas as pd
import numpy as np

from ..config.settings import MASTERS_DIR, IPC_FILENAME, VALID_FROM

log = logging.getLogger(__name__)


def consolidate_semesters(semester_files: list[Path]) -> dict[str, pd.DataFrame]:
    """Lee todos los Excel semestrales y consolida series nacionales, provinciales y regionales.

    Cada Excel tiene hojas: canasta_nacional_ponderada, canasta_mes_provincia, canasta_mes_region.
    Retorna un dict con claves 'nacional', 'provincia', 'region'.
    """
    nacional_parts, provincia_parts, region_parts = [], [], []

    for path in sorted(semester_files):
        try:
            xl = pd.ExcelFile(path)
            sheets = xl.sheet_names
            if "canasta_nacional_ponderada" in sheets:
                df = pd.read_excel(path, sheet_name="canasta_nacional_ponderada")
                df["origen"] = path.stem
                nacional_parts.append(df)
            if "canasta_mes_provincia" in sheets:
                df = pd.read_excel(path, sheet_name="canasta_mes_provincia")
                provincia_parts.append(df)
            if "canasta_mes_region" in sheets:
                df = pd.read_excel(path, sheet_name="canasta_mes_region")
                region_parts.append(df)
        except Exception as e:
            log.warning("Error leyendo %s: %s", path, e)

    def _concat_sort(parts: list[pd.DataFrame], sort_col: str) -> pd.DataFrame:
        if not parts:
            return pd.DataFrame()
        df = pd.concat(parts, ignore_index=True)
        if sort_col in df.columns:
            df = df.sort_values(sort_col).drop_duplicates(
                subset=[c for c in df.columns if c != "origen"], keep="last"
            )
        return df

    return {
        "nacional": _concat_sort(nacional_parts, "mes"),
        "provincia": _concat_sort(provincia_parts, "mes"),
        "region": _concat_sort(region_parts, "mes"),
    }


def build_national_index(df_nacional: pd.DataFrame,
                          base_month: str = VALID_FROM,
                          null_months: list[str] | None = None) -> pd.DataFrame:
    """Construye índice base 100 desde base_month.

    null_months: meses cuya variación se reemplaza por NaN (panel inestable).
    """
    df = df_nacional.copy()

    # Detecta columna de valor
    value_col = next((c for c in ["canasta_nacional", "canasta_ponderada", "valor"] if c in df.columns), None)
    if value_col is None:
        raise ValueError("No se encontró columna de valor en df_nacional")

    df["mes"] = df["mes"].astype(str)
    df = df[df["mes"] >= base_month].sort_values("mes").reset_index(drop=True)

    base_val = df.loc[df["mes"] == base_month, value_col].iloc[0]
    df["indice"] = df[value_col] / base_val * 100
    df["variacion_pct"] = df[value_col].pct_change() * 100

    if null_months:
        df.loc[df["mes"].isin(null_months), "variacion_pct"] = np.nan

    return df


def load_ipc(path: Path | None = None) -> pd.DataFrame:
    """Carga el IPC INDEC desde Excel."""
    if path is None:
        path = MASTERS_DIR / IPC_FILENAME
    if not Path(path).exists():
        raise FileNotFoundError(f"IPC no encontrado: {path}")

    df = pd.read_excel(path, dtype=str)
    df.columns = [c.lower().strip() for c in df.columns]

    # Detecta columna de fecha
    date_col = next((c for c in df.columns if "fecha" in c or "period" in c or "mes" in c), df.columns[0])
    df["mes"] = pd.to_datetime(df[date_col].str.replace(",", "."), errors="coerce").dt.to_period("M").astype(str)
    df = df.dropna(subset=["mes"])

    # Columnas numéricas
    for col in df.columns:
        if col not in (date_col, "mes"):
            df[col] = pd.to_numeric(df[col].str.replace(",", "."), errors="coerce")

    # Renombra columnas clave
    rename_map = {}
    for col in df.columns:
        if "general" in col and "nivel" in col:
            rename_map[col] = "ipc_general"
        elif "alimento" in col:
            rename_map[col] = "ipc_alimentos"
    df = df.rename(columns=rename_map)

    if "ipc_general" in df.columns:
        df["ipc_general_var"] = df["ipc_general"].pct_change() * 100
    if "ipc_alimentos" in df.columns:
        df["ipc_alimentos_var"] = df["ipc_alimentos"].pct_change() * 100

    log.info("IPC cargado: %d meses", len(df))
    return df


def build_comparative(df_nacional: pd.DataFrame, df_ipc: pd.DataFrame,
                       base_month: str = VALID_FROM) -> pd.DataFrame:
    """Construye tabla comparativa: índice canasta vs. índice IPC, y brechas."""
    idx = build_national_index(df_nacional, base_month=base_month)

    ipc = df_ipc[df_ipc["mes"] >= base_month].copy()
    if "ipc_general" in ipc.columns:
        base_ipc = ipc.loc[ipc["mes"] == base_month, "ipc_general"].iloc[0]
        ipc["indice_ipc"] = ipc["ipc_general"] / base_ipc * 100
    if "ipc_alimentos" in ipc.columns:
        base_ali = ipc.loc[ipc["mes"] == base_month, "ipc_alimentos"].iloc[0]
        ipc["indice_alimentos"] = ipc["ipc_alimentos"] / base_ali * 100

    result = idx.merge(ipc[["mes"] + [c for c in ["indice_ipc", "indice_alimentos", "ipc_general_var", "ipc_alimentos_var"] if c in ipc.columns]],
                       on="mes", how="left")

    if "indice_ipc" in result.columns:
        result["brecha_indice"] = result["indice"] - result["indice_ipc"]
    if "variacion_pct" in result.columns and "ipc_general_var" in result.columns:
        result["brecha_var_pp"] = result["variacion_pct"] - result["ipc_general_var"]

    return result
