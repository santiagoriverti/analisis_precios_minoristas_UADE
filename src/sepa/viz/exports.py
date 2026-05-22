"""Exportación de resultados a Excel, Parquet y formatos de texto."""
from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

log = logging.getLogger(__name__)


def save_excel(sheets: dict[str, pd.DataFrame], output_path: Path, author: str = "ICM-UADE") -> Path:
    """Guarda múltiples DataFrames en un Excel con formato básico.

    sheets: dict nombre_hoja → DataFrame
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            if df is None or df.empty:
                continue
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

            # Ajusta ancho de columnas
            ws = writer.sheets[sheet_name[:31]]
            for col_cells in ws.columns:
                max_len = max(
                    (len(str(cell.value)) for cell in col_cells if cell.value is not None),
                    default=10
                )
                ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 2, 40)

    log.info("Excel guardado: %s (%d hojas)", output_path, len(sheets))
    return output_path


def save_parquet(df: pd.DataFrame, output_path: Path) -> Path:
    """Guarda DataFrame como Parquet con compresión snappy."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convierte categorías a string (compatibilidad parquet)
    df_out = df.copy()
    for col in df_out.select_dtypes(["category"]).columns:
        df_out[col] = df_out[col].astype(str)

    df_out.to_parquet(output_path, compression="snappy", index=False)
    mb = output_path.stat().st_size / 1_048_576
    log.info("Parquet guardado: %s (%.1f MB)", output_path, mb)
    return output_path


def load_parquet(path: Path) -> pd.DataFrame:
    """Carga un Parquet; lanza FileNotFoundError si no existe."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Parquet no encontrado: {path}")
    return pd.read_parquet(path)


def save_semester_excel(
    semester: str,
    df_cobertura: pd.DataFrame,
    df_diaria: pd.DataFrame | None,
    df_provincia: pd.DataFrame,
    df_region: pd.DataFrame | None,
    df_nacional: pd.DataFrame,
    df_pesos: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Guarda el Excel estándar de un semestre (7 hojas)."""
    from ..config.canasta import get_canasta_df
    canasta_df = get_canasta_df()[["ean_str", "nombre", "categoria", "cantidad"]]
    canasta_df = canasta_df.rename(columns={"ean_str": "ean_norm"})

    sheets = {
        "cobertura_temporal":       df_cobertura,
        "canasta_definicion":       canasta_df,
        "serie_diaria_nacional":    df_diaria,
        "canasta_mes_provincia":    df_provincia,
        "canasta_mes_region":       df_region,
        "canasta_nacional_ponderada": df_nacional,
        "pesos_poblacionales":      df_pesos,
    }
    out = Path(output_dir) / f"canasta_{semester}_serie.xlsx"
    return save_excel(sheets, out)


def save_consolidated_excel(
    df_nacional: pd.DataFrame,
    df_provincia: pd.DataFrame,
    df_region: pd.DataFrame,
    df_ipc: pd.DataFrame,
    df_comparativa: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Guarda el Excel consolidado multi-semestral."""
    metodologia = pd.DataFrame([{
        "campo": "Período válido",          "valor": "Mayo 2023 – presente"},
        {"campo": "Base índice",             "valor": "Mayo 2023 = 100"},
        {"campo": "Productos",               "valor": "30 EANs fijos"},
        {"campo": "Ponderación nacional",    "valor": "Pesos poblacionales Censo 2022"},
        {"campo": "Fuente precios",          "valor": "SEPA — datos.produccion.gob.ar"},
        {"campo": "Generado",                "valor": datetime.now().strftime("%Y-%m-%d %H:%M")},
    ])
    sheets = {
        "nacional_valida":    df_nacional,
        "por_provincia":      df_provincia,
        "por_region":         df_region,
        "ipc_indec":          df_ipc,
        "comparativa_sepa_ipc": df_comparativa,
        "metodologia":        metodologia,
    }
    return save_excel(sheets, output_path)
