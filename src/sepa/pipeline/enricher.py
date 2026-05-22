"""Enriquecimiento de datos: join con maestros de productos y sucursales."""
from __future__ import annotations

import logging
import pandas as pd

from ..config.geo import normalize_provincia, ISO_TO_PROVINCIA, PROVINCIA_TO_REGION
from ..config.cadenas import get_cadena_name, is_excluida

log = logging.getLogger(__name__)


def enrich_with_products(df: pd.DataFrame, master_products: pd.DataFrame) -> pd.DataFrame:
    """Añade descripción, marca, rubro, categoría desde el maestro de productos."""
    if master_products is None or master_products.empty:
        return df

    cols_wanted = [c for c in ["ean_norm", "descripcion", "marca", "rubro", "categoria", "subcategoria", "proveedor"] if c in master_products.columns]
    mp = master_products[cols_wanted].drop_duplicates(subset=["ean_norm"])

    df = df.merge(mp, on="ean_norm", how="left", suffixes=("", "_master"))
    log.info("Enriquecimiento con productos: %d filas, match=%.1f%%",
             len(df), 100 * df["marca"].notna().mean() if "marca" in df.columns else 0)
    return df


def enrich_with_branches(df: pd.DataFrame, master_branches: pd.DataFrame) -> pd.DataFrame:
    """Añade provincia, región, coordenadas y nombre de cadena desde el maestro de sucursales."""
    if master_branches is None or master_branches.empty:
        return df

    mb = master_branches.copy()

    # Detecta columnas de coordenadas
    lat_col = next((c for c in mb.columns if c in ("lat", "latitud")), None)
    lon_col = next((c for c in mb.columns if c in ("lng", "longitud")), None)
    if lat_col and lat_col != "lat":
        mb = mb.rename(columns={lat_col: "lat"})
    if lon_col and lon_col != "lng":
        mb = mb.rename(columns={lon_col: "lng"})

    # Detecta columna de provincia
    prov_col = next((c for c in mb.columns if "provincia" in c.lower()), None)
    if prov_col:
        mb["provincia"] = mb[prov_col].apply(normalize_provincia)
    elif "id_provincia" in mb.columns:
        mb["provincia"] = mb["id_provincia"].map(ISO_TO_PROVINCIA)

    mb["region"] = mb["provincia"].map(PROVINCIA_TO_REGION)

    # Construye nombre de cadena
    if "id_comercio" in mb.columns and "id_bandera" in mb.columns:
        mb["cadena"] = mb.apply(
            lambda r: get_cadena_name(int(r["id_comercio"]) if pd.notna(r["id_comercio"]) else -1,
                                      int(r["id_bandera"]) if pd.notna(r["id_bandera"]) else -1),
            axis=1
        )

    key_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in mb.columns]
    cols_to_add = [c for c in ["provincia", "region", "cadena", "lat", "lng",
                                "sucursalnombre", "sucursaltipo", "localidad_nombre",
                                "barrio"] if c in mb.columns]
    mb_slim = mb[key_cols + cols_to_add].drop_duplicates(subset=key_cols)

    # Asegura tipos compatibles en columnas clave
    for col in key_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int32")
        mb_slim[col] = pd.to_numeric(mb_slim[col], errors="coerce").astype("Int32")

    df = df.merge(mb_slim, on=key_cols, how="left", suffixes=("", "_suc"))
    log.info("Enriquecimiento con sucursales: %d filas", len(df))
    return df


def filter_excluded_chains(df: pd.DataFrame, id_col: str = "id_comercio") -> pd.DataFrame:
    """Remueve cadenas no-supermercados (farmacias, e-commerce, etc.)."""
    if id_col not in df.columns:
        return df
    mask = df[id_col].apply(lambda x: not is_excluida(int(x)) if pd.notna(x) else True)
    removed = (~mask).sum()
    if removed > 0:
        log.info("Cadenas excluidas: %d filas removidas", removed)
    return df[mask].copy()
