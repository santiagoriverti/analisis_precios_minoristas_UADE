"""Carga de datos SEPA: descompresión de ZIPs y lectura de CSVs.

Soporta tres formatos de entrada:
  1. ZIP diario (AAAA-MM-DD.zip) con ZIPs internos por cadena (sepa_*.zip)
  2. ZIP semestral (AAAA-S.zip) con archivos .csv.gz por mes
  3. CSVs .csv.gz directos (archivos mensuales ya extraídos: MMAAAA_pais_parteN_COMPLETO.csv.gz)

Nota sobre separadores:
  Los archivos internos de los ZIPs diarios usan | (pipe).
  Los archivos .csv.gz mensuales (pais_parte*) usan , (coma).
  El loader detecta automáticamente el separador correcto.
"""
from __future__ import annotations

import gc
import io
import logging
import re
import zipfile
from pathlib import Path
from typing import Iterator

import pandas as pd

from ..config.settings import MASTERS_DIR, MASTER_PRODUCTS_FILENAME, MASTER_BRANCHES_FILENAME

log = logging.getLogger(__name__)


def _detect_separator(data: bytes, encoding: str = "utf-8") -> str:
    """Detecta si el CSV usa coma o pipe como separador."""
    try:
        sample = data[:4096].decode(encoding, errors="replace")
        first_line = sample.split("\n")[0]
        pipe_count  = first_line.count("|")
        comma_count = first_line.count(",")
        return "|" if pipe_count > comma_count else ","
    except Exception:
        return ","


def _read_csv_from_bytes(data: bytes, filename: str = "") -> pd.DataFrame | None:
    """Lee un CSV SEPA con detección automática de encoding y separador."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            sep = _detect_separator(data, enc)
            df = pd.read_csv(
                io.BytesIO(data),
                sep=sep,
                encoding=enc,
                dtype=str,
                on_bad_lines="skip",
                low_memory=False,
            )
            # Eliminar líneas de metadata ("última actualización")
            first_col = df.columns[0]
            mask = df[first_col].astype(str).str.lower().str.startswith("última", na=False)
            df = df[~mask]
            if df.empty or len(df.columns) < 3:
                continue
            return df
        except Exception:
            continue
    log.warning("No se pudo leer: %s", filename)
    return None


# ── Lectura de ZIP diario ──────────────────────────────────────────────────

def read_daily_zip(zip_path: Path) -> dict[str, pd.DataFrame]:
    """Lee un ZIP diario SEPA y retorna {'comercio': df, 'sucursales': df, 'productos': df}."""
    zip_path = Path(zip_path)
    comercio_list, sucursal_list, producto_list = [], [], []

    with zipfile.ZipFile(zip_path) as outer:
        date_folders = {n.split("/")[0] for n in outer.namelist() if "/" in n}
        date_folder  = next(
            (f for f in date_folders if re.match(r"\d{4}-\d{2}-\d{2}", f)), ""
        )
        inner_zips = [
            n for n in outer.namelist()
            if n.endswith(".zip") and "sepa_" in n.lower()
        ]
        log.info("ZIP diario %s: %d ZIPs internos", zip_path.name, len(inner_zips))

        for inner_name in inner_zips:
            inner_bytes = outer.read(inner_name)
            try:
                with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
                    for fname in inner.namelist():
                        if not fname.endswith(".csv"):
                            continue
                        data = inner.read(fname)
                        df   = _read_csv_from_bytes(data, fname)
                        if df is None or df.empty:
                            continue
                        cols_lower = {c.lower() for c in df.columns}
                        if any("productos_ean" in c or "id_producto" in c for c in cols_lower):
                            producto_list.append(df)
                        elif any("lat" in c or "sucursalnombre" in c for c in cols_lower):
                            sucursal_list.append(df)
                        elif "razon_social" in cols_lower or "bandera_nombre" in cols_lower:
                            comercio_list.append(df)
            except Exception as e:
                log.warning("Error leyendo %s: %s", inner_name, e)

    result: dict[str, pd.DataFrame] = {}
    if comercio_list:
        result["comercio"]   = pd.concat(comercio_list,  ignore_index=True).drop_duplicates()
    if sucursal_list:
        result["sucursales"] = pd.concat(sucursal_list,  ignore_index=True).drop_duplicates()
    if producto_list:
        result["productos"]  = pd.concat(producto_list,  ignore_index=True)

    gc.collect()
    log.info("Leído: %d productos, %d sucursales, %d comercios",
             len(result.get("productos", [])),
             len(result.get("sucursales", [])),
             len(result.get("comercio",   [])))
    return result


# ── Lectura de CSV.GZ semestrales / mensuales ──────────────────────────────

def iter_semester_csvgz(
    source: Path,
    ean_filter: set[str] | None = None,
) -> Iterator[pd.DataFrame]:
    """Itera sobre archivos CSV.GZ de un semestre (ZIP o directorio).

    Yields DataFrames en formato largo (una fila por precio diario).
    ean_filter: si se pasa, filtra solo esos EANs (normalizados, sin ceros).
    """
    source = Path(source)
    if source.suffix == ".zip":
        with zipfile.ZipFile(source) as z:
            gz_names = sorted(n for n in z.namelist() if n.endswith(".csv.gz"))
        log.info("ZIP semestral %s: %d archivos CSV.GZ", source.name, len(gz_names))
        for gz_name in gz_names:
            with zipfile.ZipFile(source) as z:
                gz_bytes = z.read(gz_name)
            df = _read_csvgz_wide(gz_bytes, ean_filter, label=gz_name)
            if df is not None and not df.empty:
                yield df
            gc.collect()
    elif source.is_dir():
        gz_files = sorted(source.glob("**/*.csv.gz"))
        log.info("Directorio %s: %d archivos CSV.GZ", source.name, len(gz_files))
        for gz_path in gz_files:
            with open(gz_path, "rb") as f:
                gz_bytes = f.read()
            df = _read_csvgz_wide(gz_bytes, ean_filter, label=gz_path.name)
            if df is not None and not df.empty:
                yield df
            gc.collect()
    else:
        # Archivo .csv.gz individual
        with open(source, "rb") as f:
            gz_bytes = f.read()
        df = _read_csvgz_wide(gz_bytes, ean_filter, label=source.name)
        if df is not None and not df.empty:
            yield df


def _read_csvgz_wide(gz_bytes: bytes, ean_filter: set[str] | None,
                     label: str = "") -> pd.DataFrame | None:
    """Lee un CSV.GZ en formato ancho (columnas precio_YYYYMMDD) y convierte a largo.

    Usa lectura por chunks para evitar materializar el CSV completo (~1.5 GB) en memoria.
    Con ean_filter, los chunks descartados se liberan inmediatamente.
    Solo se conservan las columnas esenciales (branch IDs + ean_norm + precios).
    """
    _ESSENTIAL = {"id_comercio", "id_bandera", "id_sucursal"}
    _CHUNKSIZE  = 100_000

    chunks_filtrados: list[pd.DataFrame] = []
    ean_col: str | None = None

    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            reader = pd.read_csv(
                io.BytesIO(gz_bytes),
                compression="gzip",
                sep=None,                 # auto-detecta , vs |
                engine="python",
                dtype=str,
                on_bad_lines="skip",
                encoding=enc,
                chunksize=_CHUNKSIZE,
            )
            for chunk in reader:
                chunk.columns = [c.lower().strip() for c in chunk.columns]

                # Eliminar filas de metadata ("última actualización …")
                first_col = chunk.columns[0]
                mask_meta = chunk[first_col].astype(str).str.lower().str.startswith("última", na=False)
                if mask_meta.any():
                    chunk = chunk[~mask_meta]
                if chunk.empty:
                    continue

                # Detectar columna EAN en el primer chunk no vacío
                if ean_col is None:
                    ean_col = next(
                        (c for c in chunk.columns if "id_producto" in c or "productos_ean" in c),
                        None,
                    )
                    if ean_col is None:
                        log.warning("Sin columna EAN en %s (columnas: %s)", label, list(chunk.columns)[:8])
                        break

                chunk["ean_norm"] = chunk[ean_col].astype(str).str.strip().str.lstrip("0")

                if ean_filter:
                    chunk = chunk[chunk["ean_norm"].isin(ean_filter)]
                if chunk.empty:
                    continue

                # Conservar solo columnas esenciales + precios  → reduce ancho de ~15 a ~5 cols
                price_cols = [c for c in chunk.columns if re.match(r"precio_\d{8}$", c)]
                essential  = [c for c in chunk.columns if c in _ESSENTIAL or c == "ean_norm"]
                if not essential or not price_cols:
                    continue

                chunks_filtrados.append(chunk[essential + price_cols].copy())

            break  # encoding funcionó
        except UnicodeDecodeError:
            ean_col = None
            chunks_filtrados = []
            continue
        except Exception as e:
            log.warning("Error leyendo %s con encoding %s: %s", label, enc, e)
            ean_col = None
            chunks_filtrados = []
            continue

    if not chunks_filtrados:
        log.warning("Sin datos de canasta en %s", label)
        return None

    df = pd.concat(chunks_filtrados, ignore_index=True)
    del chunks_filtrados
    gc.collect()

    price_cols = [c for c in df.columns if re.match(r"precio_\d{8}$", c)]
    id_cols    = [c for c in df.columns if not re.match(r"precio_\d{8}$", c)]

    df_long = df.melt(
        id_vars=id_cols,
        value_vars=price_cols,
        var_name="fecha_col",
        value_name="precio_raw",
    )
    del df
    gc.collect()

    df_long["fecha"] = pd.to_datetime(
        df_long["fecha_col"].str.replace("precio_", ""), format="%Y%m%d", errors="coerce"
    )
    df_long = df_long.dropna(subset=["fecha"])
    df_long["precio_raw"] = pd.to_numeric(df_long["precio_raw"], errors="coerce")
    df_long = df_long.dropna(subset=["precio_raw"])
    df_long = df_long[df_long["precio_raw"] > 0]
    df_long = df_long.drop(columns=["fecha_col"])

    log.info("Leído %s: %d filas, %d EANs únicos", label, len(df_long),
             df_long["ean_norm"].nunique())
    return df_long.reset_index(drop=True)


# ── Carga de maestros ──────────────────────────────────────────────────────

def load_master_products(path: Path | None = None) -> pd.DataFrame:
    """Carga el Maestro de Productos Interno desde Excel (176.702 productos)."""
    if path is None:
        path = MASTERS_DIR / MASTER_PRODUCTS_FILENAME
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Maestro de productos no encontrado: {path}")

    df = pd.read_excel(path, dtype=str)
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    ean_col = next((c for c in df.columns if "ean" in c or "id_producto" in c), None)
    if ean_col:
        df["ean_norm"] = df[ean_col].astype(str).str.strip().str.lstrip("0")
        if ean_col != "ean_norm":
            df = df.rename(columns={ean_col: "ean_raw"})

    log.info("Maestro productos: %d registros", len(df))
    return df


def load_master_branches(path: Path | None = None) -> pd.DataFrame:
    """Carga el maestro de sucursales desde Excel (3.611 sucursales con coordenadas)."""
    if path is None:
        path = MASTERS_DIR / MASTER_BRANCHES_FILENAME
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Maestro de sucursales no encontrado: {path}")

    df = pd.read_excel(path, dtype=str)
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # Coordenadas a float
    for col in ("lat", "lng", "latitud", "longitud", "sucursales_latitud", "sucursales_longitud"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # IDs a Int32
    for col in ("id_comercio", "id_bandera", "id_sucursal"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int32")

    log.info("Maestro sucursales: %d registros", len(df))
    return df
