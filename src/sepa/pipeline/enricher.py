"""Enriquecimiento de datos: join con maestros de productos y sucursales.

También aplica filtros de calidad:
- Elimina sucursales de tipo "Web"
- Elimina sucursales mal clasificadas como CABA por coordenadas
- Asigna barrio de CABA a sucursales en CABA
"""
from __future__ import annotations

import logging
import pandas as pd

from ..config.geo import (
    normalize_provincia, ISO_TO_PROVINCIA, PROVINCIA_TO_REGION,
    assign_barrio_caba, is_caba_valid_coords,
)
from ..config.cadenas import get_cadena_name, is_excluida
from ..config.settings import EXCLUIR_TIPO_WEB

log = logging.getLogger(__name__)


def enrich_with_products(df: pd.DataFrame, master_products: pd.DataFrame) -> pd.DataFrame:
    """Añade descripción, marca, rubro, categoría desde el maestro de productos."""
    if master_products is None or master_products.empty:
        return df

    cols_wanted = [c for c in ["ean_norm", "descripcion", "marca", "rubro",
                                "categoria", "subcategoria", "proveedor"]
                   if c in master_products.columns]
    mp = master_products[cols_wanted].drop_duplicates(subset=["ean_norm"])
    df = df.merge(mp, on="ean_norm", how="left", suffixes=("", "_master"))

    match_pct = 100 * df["marca"].notna().mean() if "marca" in df.columns else 0
    log.info("Enriquecimiento con productos: %d filas, match=%.1f%%", len(df), match_pct)
    return df


def enrich_with_branches(df: pd.DataFrame, master_branches: pd.DataFrame) -> pd.DataFrame:
    """Añade provincia, región, coordenadas, barrio CABA y nombre de cadena.

    También aplica filtros:
    - Sucursales tipo "Web" (sin ubicación física)
    - Sucursales con CABA en provincia pero coordenadas fuera del bounding box de CABA
    """
    if master_branches is None or master_branches.empty:
        return df

    mb = master_branches.copy()

    # Normalizar columnas de coordenadas
    lat_col = next((c for c in mb.columns if c in ("lat", "latitud", "sucursales_latitud")), None)
    lon_col = next((c for c in mb.columns if c in ("lng", "longitud", "sucursales_longitud")), None)
    if lat_col and lat_col != "lat":
        mb = mb.rename(columns={lat_col: "lat"})
    if lon_col and lon_col != "lng":
        mb = mb.rename(columns={lon_col: "lng"})

    # Normalizar provincia
    prov_col = next((c for c in mb.columns if "provincia" in c.lower()), None)
    if prov_col:
        mb["provincia"] = mb[prov_col].apply(normalize_provincia)
    elif "id_provincia" in mb.columns:
        mb["provincia"] = mb["id_provincia"].map(ISO_TO_PROVINCIA)

    mb["region"] = mb.get("provincia", pd.Series(dtype=str)).map(PROVINCIA_TO_REGION)

    # Tipo de sucursal
    tipo_col = next((c for c in mb.columns if "tipo" in c.lower()), None)
    if tipo_col and tipo_col != "sucursales_tipo":
        mb = mb.rename(columns={tipo_col: "sucursales_tipo"})

    # Nombre de cadena
    if "id_comercio" in mb.columns and "id_bandera" in mb.columns:
        mb["cadena"] = mb.apply(
            lambda r: get_cadena_name(
                int(r["id_comercio"]) if pd.notna(r["id_comercio"]) else -1,
                int(r["id_bandera"]) if pd.notna(r["id_bandera"]) else -1,
            ),
            axis=1,
        )

    # Asignar barrio CABA por coordenadas
    if "lat" in mb.columns and "lng" in mb.columns and "provincia" in mb.columns:
        mask_caba = mb["provincia"] == "CABA"
        mb.loc[mask_caba, "barrio_caba"] = mb[mask_caba].apply(
            lambda r: assign_barrio_caba(r["lat"], r["lng"])
            if pd.notna(r["lat"]) and pd.notna(r["lng"]) else None,
            axis=1,
        )

    # ── Filtros de calidad de sucursales ─────────────────────────────────────

    # 1) Eliminar sucursales tipo Web
    if EXCLUIR_TIPO_WEB and "sucursales_tipo" in mb.columns:
        n_before = len(mb)
        mb = mb[mb["sucursales_tipo"].str.lower().ne("web")]
        log.info("Sucursales Web eliminadas: %d", n_before - len(mb))

    # 2) Eliminar sucursales mal clasificadas como CABA (coordenadas fuera del bounding box)
    if "lat" in mb.columns and "lng" in mb.columns and "provincia" in mb.columns:
        mask_caba_mal = (
            (mb["provincia"] == "CABA") &
            mb["lat"].notna() & mb["lng"].notna() &
            ~mb.apply(lambda r: is_caba_valid_coords(r["lat"], r["lng"]), axis=1)
        )
        n_bad = mask_caba_mal.sum()
        if n_bad > 0:
            log.info("Sucursales mal clasificadas como CABA eliminadas: %d", n_bad)
            mb = mb[~mask_caba_mal]

    # ── Join con el DataFrame principal ──────────────────────────────────────
    key_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in mb.columns]
    cols_to_add = [c for c in ["provincia", "region", "cadena", "lat", "lng",
                                "sucursales_tipo", "sucursales_nombre", "localidad_nombre",
                                "barrio", "barrio_caba"]
                   if c in mb.columns]

    mb_slim = mb[key_cols + cols_to_add].drop_duplicates(subset=key_cols)

    # Tipos compatibles en claves
    for col in key_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int32")
        if col in mb_slim.columns:
            mb_slim[col] = pd.to_numeric(mb_slim[col], errors="coerce").astype("Int32")

    df = df.merge(mb_slim, on=key_cols, how="left", suffixes=("", "_suc"))
    log.info("Enriquecimiento con sucursales: %d filas", len(df))
    return df


def filter_excluded_chains(df: pd.DataFrame, id_col: str = "id_comercio") -> pd.DataFrame:
    """Remueve cadenas no-supermercados (YPF, e-commerce, ferreterías)."""
    if id_col not in df.columns:
        return df
    mask = df[id_col].apply(
        lambda x: not is_excluida(int(x)) if pd.notna(x) else True
    )
    removed = (~mask).sum()
    if removed > 0:
        log.info("Cadenas excluidas removidas: %d filas", removed)
    return df[mask].copy()
