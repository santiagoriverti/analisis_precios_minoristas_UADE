"""Definición de herramientas (tool_use) disponibles para el agente Claude.

Cada función tool_* implementa la lógica; el dict TOOLS_SCHEMA define los esquemas
para pasarle a la API de Anthropic.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..config.settings import OUTPUT_DIR, PRODUCTS_DIR, MASTERS_DIR, CACHE_DIR

log = logging.getLogger(__name__)


# ── Schemas para la API ───────────────────────────────────────────────────

TOOLS_SCHEMA = [
    {
        "name": "run_daily_analysis",
        "description": (
            "Procesa un archivo ZIP diario del SEPA y genera: tabla de productos únicos, "
            "canasta por provincia, coropleta por provincia y Excel de resultados."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "zip_path": {"type": "string", "description": "Ruta al ZIP diario (AAAA-MM-DD.zip)"},
                "output_label": {"type": "string", "description": "Etiqueta para los archivos de salida (e.g. '2026-04-26')"},
            },
            "required": ["zip_path"],
        },
    },
    {
        "name": "run_semester_analysis",
        "description": (
            "Procesa todos los CSV.GZ de un semestre del SEPA y genera la serie temporal "
            "de canasta por sucursal, provincia, región y nacional ponderada."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "semester": {"type": "string", "description": "Código de semestre: '2025A', '2025B', etc."},
                "source_path": {"type": "string", "description": "Ruta al ZIP semestral o directorio con CSV.GZ"},
            },
            "required": ["semester"],
        },
    },
    {
        "name": "run_consolidation",
        "description": (
            "Consolida todos los semestres procesados en una serie temporal única, "
            "calcula índices y variaciones, compara contra IPC INDEC y genera gráficos."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "from_month": {"type": "string", "description": "Mes de inicio (YYYY-MM). Default: 2023-05"},
            },
            "required": [],
        },
    },
    {
        "name": "generate_branch_map",
        "description": "Genera el mapa Folium interactivo por sucursal para un mes dado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mes": {"type": "string", "description": "Mes a visualizar (YYYY-MM). Si omitido, usa el último disponible."},
            },
            "required": [],
        },
    },
    {
        "name": "generate_chain_rankings",
        "description": "Genera ranking de cadenas nacional y AMBA con gráficos PNG.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mes": {"type": "string", "description": "Mes a rankear (YYYY-MM)."},
            },
            "required": [],
        },
    },
    {
        "name": "list_available_data",
        "description": "Lista los datos disponibles: ZIPs de entrada, semestres procesados y artefactos generados.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_analysis_summary",
        "description": "Retorna un resumen estadístico del último análisis disponible (canasta promedio, variación, n sucursales).",
        "input_schema": {
            "type": "object",
            "properties": {
                "mes": {"type": "string", "description": "Mes (YYYY-MM). Omitir para el último disponible."},
            },
            "required": [],
        },
    },
]


# ── Implementaciones ───────────────────────────────────────────────────────

def tool_list_available_data() -> dict[str, Any]:
    """Lista archivos de entrada y resultados disponibles."""
    from ..config.settings import INPUT_DIR

    def _list_dir(d: Path, pattern: str) -> list[str]:
        if not d.exists():
            return []
        return sorted(str(p.name) for p in d.glob(pattern))

    return {
        "zips_diarios": _list_dir(INPUT_DIR / "diarios", "*.zip"),
        "zips_semestrales": _list_dir(INPUT_DIR / "semestrales", "*.zip"),
        "masters": _list_dir(MASTERS_DIR, "*.xlsx"),
        "excels_output": _list_dir(OUTPUT_DIR, "*.xlsx"),
        "parquets_cache": _list_dir(CACHE_DIR, "*.parquet"),
        "products": _list_dir(PRODUCTS_DIR, "*"),
    }


def tool_get_analysis_summary(mes: str | None = None) -> dict[str, Any]:
    """Retorna estadísticas del último análisis de canasta disponible."""
    parquets = sorted(CACHE_DIR.glob("canasta_branch_*.parquet")) if CACHE_DIR.exists() else []
    if not parquets:
        return {"error": "No hay datos procesados en cache. Correr primero un análisis semestral o diario."}

    from ..viz.exports import load_parquet
    df = load_parquet(parquets[-1])

    if mes and "mes" in df.columns:
        df = df[df["mes"] == mes]
    elif "mes" in df.columns:
        mes = df["mes"].max()
        df = df[df["mes"] == mes]

    if df.empty:
        return {"error": f"Sin datos para mes={mes}"}

    return {
        "mes": mes,
        "n_sucursales": int(len(df)),
        "canasta_promedio": round(float(df["canasta_total"].mean()), 0),
        "canasta_minimo": round(float(df["canasta_total"].min()), 0),
        "canasta_maximo": round(float(df["canasta_total"].max()), 0),
        "canasta_mediana": round(float(df["canasta_total"].median()), 0),
        "cv_pct": round(float(df["canasta_total"].std() / df["canasta_total"].mean() * 100), 2),
    }


def dispatch_tool(tool_name: str, tool_input: dict) -> Any:
    """Despacha la llamada a la función correspondiente al tool."""
    if tool_name == "list_available_data":
        return tool_list_available_data()
    elif tool_name == "get_analysis_summary":
        return tool_get_analysis_summary(tool_input.get("mes"))
    elif tool_name == "run_daily_analysis":
        from .orchestrator import _run_daily
        return _run_daily(tool_input["zip_path"], tool_input.get("output_label"))
    elif tool_name == "run_semester_analysis":
        from .orchestrator import _run_semester
        return _run_semester(tool_input["semester"], tool_input.get("source_path"))
    elif tool_name == "run_consolidation":
        from .orchestrator import _run_consolidation
        return _run_consolidation(tool_input.get("from_month"))
    elif tool_name == "generate_branch_map":
        from .orchestrator import _generate_map
        return _generate_map(tool_input.get("mes"))
    elif tool_name == "generate_chain_rankings":
        from .orchestrator import _generate_rankings
        return _generate_rankings(tool_input.get("mes"))
    else:
        return {"error": f"Tool desconocida: {tool_name}"}
