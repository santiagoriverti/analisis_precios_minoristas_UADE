"""Mapas interactivos (Folium) y coropletas (matplotlib/GeoJSON).

Exports principales:
  - make_branch_map()   → Mapa interactivo por sucursal (como mapa_precios_argentina_abril2026)
  - make_province_choropleth() → Mapa coroplético por provincia
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

try:
    import folium
    from folium import plugins
    from branca.colormap import LinearColormap
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    log.warning("folium no instalado — mapas interactivos no disponibles")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import Normalize, TwoSlopeNorm
    from matplotlib.cm import ScalarMappable
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ── Mapa interactivo por sucursal ──────────────────────────────────────────

def make_branch_map(
    df_branch: pd.DataFrame,
    df_enriched: pd.DataFrame,
    output_path: Path,
    mes: str | None = None,
    title: str = "ICM-UADE por Sucursal",
) -> Path:
    """Genera el mapa Folium interactivo con una marca por sucursal.

    df_branch   : build_branch_basket() output — tiene canasta_total
    df_enriched : DataFrame con lat, lng, cadena, provincia, sucursalnombre, etc.
    output_path : ruta donde guardar el HTML
    mes         : 'YYYY-MM'; si None usa el último mes
    """
    if not HAS_FOLIUM:
        raise ImportError("Instalar folium: pip install folium branca")

    branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_enriched.columns]
    suc_info = df_enriched[branch_cols + [c for c in ["lat", "lng", "cadena", "provincia", "region",
                                                        "sucursalnombre", "localidad_nombre", "barrio"]
                                           if c in df_enriched.columns]].drop_duplicates(subset=branch_cols)

    if mes is None:
        mes = df_branch["mes"].max()
    df = df_branch[df_branch["mes"] == mes].merge(suc_info, on=branch_cols, how="left")
    df = df.dropna(subset=["lat", "lng", "canasta_total"])
    df = df[df["lat"].between(-55, -22) & df["lng"].between(-73, -53)]

    n_stores = len(df)
    national_avg = df["canasta_total"].mean()

    # Escala de colores
    p5 = df["canasta_total"].quantile(0.05)
    p95 = df["canasta_total"].quantile(0.95)
    colormap = LinearColormap(
        colors=["#2ecc71", "#f1c40f", "#e74c3c"],
        vmin=p5, vmax=p95,
        caption="Canasta mensual (ARS)",
    )

    m = folium.Map(location=[-38, -63.5], zoom_start=5, tiles="CartoDB positron")

    # Panel de resumen
    summary_html = f"""
    <div style="position:fixed;top:10px;left:50px;z-index:1000;background:white;
                padding:10px 16px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.3);
                font-family:Arial;font-size:13px;max-width:260px">
      <b style="font-size:15px">{title}</b><br>
      <span style="color:#666">{mes}</span><br>
      <hr style="margin:6px 0">
      🏪 {n_stores:,} sucursales<br>
      💰 Promedio: ${national_avg:,.0f}<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(summary_html))

    # Marcadores
    for _, row in df.iterrows():
        val = row["canasta_total"]
        color = colormap(min(max(val, p5), p95))
        cadena = row.get("cadena", "Desconocida") or "Desconocida"
        prov = row.get("provincia", "") or ""
        nombre_suc = row.get("sucursalnombre", "") or ""
        localidad = row.get("localidad_nombre", "") or ""

        tooltip = f"<b>{cadena}</b><br>{nombre_suc}<br>{localidad}, {prov}<br>${val:,.0f}"
        popup_html = _build_popup(row)

        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=0.5,
            tooltip=folium.Tooltip(tooltip, sticky=True),
            popup=folium.Popup(popup_html, max_width=420),
        ).add_to(m)

    colormap.add_to(m)

    # Nota Islas Malvinas
    folium.Marker(
        location=[-51.7, -59.0],
        icon=folium.DivIcon(html='<div style="font-size:9px;color:#555;white-space:nowrap">Islas Malvinas<br>(Arg.)</div>'),
    ).add_to(m)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output_path))
    log.info("Mapa guardado: %s (%d sucursales)", output_path, n_stores)
    return output_path


def _build_popup(row: pd.Series) -> str:
    """Construye el HTML del popup para una sucursal."""
    cadena = row.get("cadena", "") or ""
    prov = row.get("provincia", "") or ""
    region = row.get("region", "") or ""
    nombre = row.get("sucursalnombre", "") or ""
    localidad = row.get("localidad_nombre", "") or ""
    total = row.get("canasta_total", 0)
    n_propios = row.get("n_productos_propios", "—")
    n_imput = row.get("n_productos_imputados", "—")

    return f"""
    <div style="font-family:Arial;font-size:12px;width:380px">
      <h4 style="margin:0 0 6px;color:#2c3e50">{cadena} — {nombre}</h4>
      <p style="margin:2px 0;color:#555">{localidad}, {prov} ({region})</p>
      <hr style="margin:8px 0">
      <p><b>Canasta mensual:</b> <span style="font-size:15px;color:#27ae60">${total:,.0f}</span></p>
      <p style="color:#666;font-size:11px">
        Productos propios: {n_propios}/30
        &nbsp;|&nbsp; Imputados: {n_imput}
      </p>
    </div>
    """


# ── Coropleta por provincia ────────────────────────────────────────────────

def make_province_choropleth(
    df_province: pd.DataFrame,
    geojson_path: Path,
    output_path: Path,
    mes: str | None = None,
    value_col: str = "canasta_provincia",
    title: str = "Canasta ICM-UADE por Provincia",
) -> Path:
    """Genera mapa coroplético de Argentina por provincia con matplotlib."""
    if not HAS_MPL:
        raise ImportError("Instalar matplotlib")

    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib.cm import RdYlGn

    geojson_path = Path(geojson_path)
    if not geojson_path.exists():
        raise FileNotFoundError(f"GeoJSON no encontrado: {geojson_path}")

    with open(geojson_path, encoding="utf-8") as f:
        geo = json.load(f)

    if mes is None:
        mes = df_province["mes"].max()
    df = df_province[df_province["mes"] == mes].copy()

    prov_vals = df.set_index("provincia")[value_col].to_dict()
    national_avg = df[value_col].mean()

    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    norm = TwoSlopeNorm(vmin=df[value_col].min(), vcenter=national_avg, vmax=df[value_col].max())

    from matplotlib.patches import Polygon as MplPolygon
    from matplotlib.collections import PatchCollection

    for feature in geo["features"]:
        prov_name = feature["properties"].get("name", "")
        val = prov_vals.get(prov_name)
        color = RdYlGn(1 - norm(val)) if val is not None else "#cccccc"

        geom = feature["geometry"]
        patches = _geom_to_patches(geom)
        for patch in patches:
            patch.set_facecolor(color)
            patch.set_edgecolor("white")
            patch.set_linewidth(0.5)
            ax.add_patch(patch)

        if val is not None and patches:
            centroid = _geom_centroid(geom)
            if centroid:
                pct = (val / national_avg - 1) * 100
                sign = "+" if pct >= 0 else ""
                ax.annotate(
                    f"{prov_name}\n${val/1000:.0f}k\n{sign}{pct:.1f}%",
                    xy=centroid, ha="center", va="center",
                    fontsize=6.5, color="#222",
                )

    ax.set_xlim(-73, -53)
    ax.set_ylim(-55, -22)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{title}\n{mes}", fontsize=14, fontweight="bold", pad=12)

    sm = ScalarMappable(cmap=lambda x: RdYlGn(1 - x), norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Canasta mensual (ARS)", fontsize=9)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info("Coropleta guardada: %s", output_path)
    return output_path


def _geom_to_patches(geom: dict) -> list[Any]:
    from matplotlib.patches import Polygon as MplPolygon
    patches = []
    gtype = geom["type"]
    coords_list = geom["coordinates"]
    if gtype == "Polygon":
        coords_list = [coords_list]
    for polygon in coords_list:
        ring = polygon[0]
        arr = np.array(ring)
        if arr.shape[1] >= 2:
            patches.append(MplPolygon(arr[:, :2], closed=True))
    return patches


def _geom_centroid(geom: dict) -> tuple[float, float] | None:
    try:
        gtype = geom["type"]
        coords = geom["coordinates"]
        if gtype == "Polygon":
            ring = np.array(coords[0])
        elif gtype == "MultiPolygon":
            ring = np.array(max(coords, key=lambda p: len(p[0]))[0])
        else:
            return None
        return float(ring[:, 0].mean()), float(ring[:, 1].mean())
    except Exception:
        return None
