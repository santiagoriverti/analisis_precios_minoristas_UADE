"""Carga de datos SEPA: descompresión de ZIPs y lectura de CSVs.

Soporta tres formatos de entrada:
  1. ZIP diario (AAAA-MM-DD.zip) con ZIPs internos por cadena (sepa_*.zip)
  2. ZIP semestral (AAAA-S.zip) con archivos .csv.gz por mes
  3. CSVs .csv.gz directos (archivos ya extraídos del ZIP semestral)
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

# ── Columnas CSV SEPA ──────────────────────────────────────────────────────
_DTYPES_COMERCIO = {
    "id_comercio":    "int32",
    "id_bandera":     "int32",
    "razon_social":   "category",
    "bandera_nombre": "category",
    "comercio_cuit":  "str",
}
_DTYPES_SUCURSAL = {
    "id_comercio":  "int32",
    "id_bandera":   "int32",
    "id_sucursal":  "int32",
    "sucursalNombre": "category",
    "sucursalTipo":   "category",
    "lat":  "float32",
    "lng":  "float32",
}
_DTYPES_PRODUCTO = {
    "id_comercio":  "int32",
    "id_bandera":   "int32",
    "id_sucursal":  "int32",
    "productos_ean": "str",
    "productos_descripcion": "category",
    "productos_marca": "category",
}


def _read_csv_from_bytes(data: bytes, filename: str = "") -> pd.DataFrame | None:
    """Lee un CSV SEPA con detección automática de encoding."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(
                io.BytesIO(data),
                sep="|",
                encoding=enc,
                dtype=str,
                on_bad_lines="skip",
                low_memory=False,
            )
            # Elimina líneas de metadata ("última actualización" en primera columna)
            first_col = df.columns[0]
            df = df[~df[first_col].astype(str).str.startswith("última", na=False)]
            df = df[~df[first_col].astype(str).str.startswith("Última", na=False)]
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
        # Detecta carpeta de fecha dentro del ZIP
        date_folders = {n.split("/")[0] for n in outer.namelist() if "/" in n}
        date_folder = next(
            (f for f in date_folders if re.match(r"\d{4}-\d{2}-\d{2}", f)), ""
        )
        inner_zips = [
            n for n in outer.namelist()
            if n.startswith(date_folder) and n.endswith(".zip") and "sepa_" in n
        ]
        log.info("ZIP diario: %d ZIPs internos detectados", len(inner_zips))

        for inner_name in inner_zips:
            inner_bytes = outer.read(inner_name)
            try:
                with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
                    for fname in inner.namelist():
                        data = inner.read(fname)
                        df = _read_csv_from_bytes(data, fname)
                        if df is None or df.empty:
                            continue
                        cols = {c.lower() for c in df.columns}
                        if "productos_ean" in cols:
                            producto_list.append(df)
                        elif "sucursalnombre" in cols or "lat" in cols:
                            sucursal_list.append(df)
                        elif "razon_social" in cols:
                            comercio_list.append(df)
            except Exception as e:
                log.warning("Error leyendo %s: %s", inner_name, e)

    result: dict[str, pd.DataFrame] = {}
    if comercio_list:
        result["comercio"] = pd.concat(comercio_list, ignore_index=True).drop_duplicates()
    if sucursal_list:
        result["sucursales"] = pd.concat(sucursal_list, ignore_index=True).drop_duplicates()
    if producto_list:
        result["productos"] = pd.concat(producto_list, ignore_index=True)

    gc.collect()
    log.info(
        "ZIP diario leído: %d productos, %d sucursales, %d comercios",
        len(result.get("productos", [])),
        len(result.get("sucursales", [])),
        len(result.get("comercio", [])),
    )
    return result


# ── Lectura de CSV.GZ semestrales ──────────────────────────────────────────

def iter_semester_csvgz(
    source: Path,
    ean_filter: set[str] | None = None,
) -> Iterator[pd.DataFrame]:
    """Itera sobre los archivos CSV.GZ de un semestre (ZIP o directorio).

    Yields DataFrames en formato largo (una fila por precio diario).
    ean_filter: si se pasa, filtra solo esos EANs (sin ceros a la izquierda).
    """
    source = Path(source)
    if source.suffix == ".zip":
        gz_files = _list_gz_in_zip(source)
        reader = lambda name: _read_gz_from_zip(source, name)
    elif source.is_dir():
        gz_files = sorted(source.glob("**/*.csv.gz"))
        reader = lambda p: open(p, "rb").read()  # type: ignore[assignment]
    else:
        raise ValueError(f"Fuente no reconocida: {source}")

    seen_hashes: set[int] = set()

    for gz_ref in gz_files:
        try:
            df = _read_csvgz_wide(gz_ref if source.is_dir() else reader(gz_ref), ean_filter)
            if df is None or df.empty:
                continue
            # Deduplica por hash simple de índice
            h = hash(str(gz_ref))
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            yield df
        except Exception as e:
            log.warning("Error en %s: %s", gz_ref, e)
        finally:
            gc.collect()


def _list_gz_in_zip(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path) as z:
        return [n for n in z.namelist() if n.endswith(".csv.gz")]


def _read_gz_from_zip(zip_path: Path, name: str) -> bytes:
    with zipfile.ZipFile(zip_path) as z:
        return z.read(name)


def _read_csvgz_wide(source: bytes | Path, ean_filter: set[str] | None) -> pd.DataFrame | None:
    """Lee un CSV.GZ en formato ancho (columnas precio_YYYYMMDD) y convierte a largo."""
    import gzip

    if isinstance(source, bytes):
        data = gzip.decompress(source)
    else:
        with gzip.open(source) as f:
            data = f.read()

    df = _read_csv_from_bytes(data)
    if df is None or df.empty:
        return None

    df.columns = [c.lower().strip() for c in df.columns]

    # Normalizar EAN
    if "id_producto" in df.columns:
        df["ean_norm"] = df["id_producto"].astype(str).str.lstrip("0")
    elif "productos_ean" in df.columns:
        df["ean_norm"] = df["productos_ean"].astype(str).str.lstrip("0")
    else:
        return None

    if ean_filter:
        df = df[df["ean_norm"].isin(ean_filter)]
    if df.empty:
        return None

    # Columnas de precio
    price_cols = [c for c in df.columns if re.match(r"precio_\d{8}$", c)]
    if not price_cols:
        return None

    id_cols = [c for c in df.columns if not re.match(r"precio_\d{8}$", c)]
    df_long = df.melt(id_vars=id_cols, value_vars=price_cols, var_name="fecha_col", value_name="precio_raw")
    df_long["fecha"] = pd.to_datetime(df_long["fecha_col"].str.replace("precio_", ""), format="%Y%m%d", errors="coerce")
    df_long = df_long.dropna(subset=["fecha"])
    df_long["precio_raw"] = pd.to_numeric(df_long["precio_raw"], errors="coerce")
    df_long = df_long.dropna(subset=["precio_raw"])
    df_long = df_long[df_long["precio_raw"] > 0]
    df_long = df_long.drop(columns=["fecha_col"])

    return df_long.reset_index(drop=True)


# ── Carga de maestros ──────────────────────────────────────────────────────

def load_master_products(path: Path | None = None) -> pd.DataFrame:
    """Carga el Maestro de Productos Interno desde Excel."""
    if path is None:
        path = MASTERS_DIR / MASTER_PRODUCTS_FILENAME
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Maestro de productos no encontrado: {path}")

    df = pd.read_excel(path, dtype=str)
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # Normaliza columna EAN
    ean_col = next((c for c in df.columns if "ean" in c), None)
    if ean_col:
        df["ean_norm"] = df[ean_col].astype(str).str.lstrip("0")
        df = df.rename(columns={ean_col: "ean_raw"})

    log.info("Maestro productos cargado: %d registros", len(df))
    return df


def load_master_branches(path: Path | None = None) -> pd.DataFrame:
    """Carga el maestro de sucursales desde Excel."""
    if path is None:
        path = MASTERS_DIR / MASTER_BRANCHES_FILENAME
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Maestro de sucursales no encontrado: {path}")

    df = pd.read_excel(path, dtype=str)
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # Normaliza coordenadas
    for col in ("lat", "lng", "latitud", "longitud"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normaliza IDs
    for col in ("id_comercio", "id_bandera", "id_sucursal"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int32")

    log.info("Maestro sucursales cargado: %d registros", len(df))
    return df
