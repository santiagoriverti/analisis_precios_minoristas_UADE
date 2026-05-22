"""Orquestador multi-agente: coordina el análisis usando la API de Anthropic.

Arquitectura:
  - SEPAOrchestrator es el punto de entrada principal (CLI o notebook)
  - Usa Claude claude-sonnet-4-6 como modelo base con prompt caching
  - Los agentes especializados se invocan via tool_use
  - El estado se persiste en SQLite via MemoryManager

Uso:
    from sepa.agents.orchestrator import SEPAOrchestrator
    agent = SEPAOrchestrator()
    result = agent.chat("Procesá el ZIP diario del 2026-05-01 y generá el mapa")
"""
from __future__ import annotations

import gc
import json
import logging
import uuid
from pathlib import Path
from typing import Any

from .memory import MemoryManager
from .tools import TOOLS_SCHEMA, dispatch_tool
from ..config.settings import (
    INPUT_DIR, OUTPUT_DIR, PRODUCTS_DIR, CACHE_DIR, MASTERS_DIR, VALID_FROM
)

log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Sos el asistente de análisis de precios del ICM-UADE (Índice de Canasta de Mercado — Universidad Argentina de la Empresa), desarrollado por INECO.

Tu rol es ayudar a procesar datos del SEPA (Sistema Electrónico de Publicidad de Precios Argentinos) y generar análisis de precios minoristas para Argentina.

Capacidades disponibles (via tools):
1. Procesar ZIPs diarios del SEPA → productos únicos + canasta por provincia
2. Procesar semestres completos → series temporales de canasta
3. Consolidar series multi-año y comparar contra IPC INDEC
4. Generar mapas interactivos por sucursal
5. Rankings de cadenas (nacional y AMBA)
6. Listar datos disponibles y estado de procesamiento

Contexto metodológico:
- La canasta tiene 30 productos fijos con cantidades mensuales calibradas para hogar de 4 personas
- Se excluyen farmacias, estaciones de servicio y e-commerce
- Los precios se validan detectando el factor de escala automáticamente
- Para la serie válida: desde mayo 2023 (cobertura estable del SEPA)
- Ponderación nacional: Censo 2022

Respondé en español, con precisión técnica y orientado a resultados concretos.
Si el usuario pide un análisis, ejecutá la tool correspondiente y comunicá los resultados.
"""


class SEPAOrchestrator:
    """Orquestador principal del sistema ICM-UADE."""

    def __init__(self, db_path: Path | None = None):
        try:
            import anthropic
            self.client = anthropic.Anthropic()
        except ImportError:
            raise ImportError("Instalar anthropic: pip install anthropic")

        self.memory = MemoryManager(db_path)
        self.session_id = str(uuid.uuid4())[:8]
        self.messages: list[dict] = []
        log.info("SEPAOrchestrator iniciado — sesión: %s", self.session_id)

    def chat(self, user_message: str, max_turns: int = 10) -> str:
        """Envía un mensaje al agente y retorna la respuesta final.

        Soporta múltiples rondas de tool_use automáticamente.
        """
        import anthropic

        self.messages.append({"role": "user", "content": user_message})

        for turn in range(max_turns):
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},  # prompt caching
                    }
                ],
                tools=TOOLS_SCHEMA,
                messages=self.messages,
            )

            # Añade respuesta del asistente al historial
            self.messages.append({"role": "assistant", "content": response.content})

            # Si terminó sin tool_use → retornar texto
            if response.stop_reason == "end_turn":
                text = _extract_text(response.content)
                self._persist_session(user_message)
                return text

            # Procesar tool_use
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        log.info("Tool call: %s(%s)", block.name, json.dumps(block.input)[:120])
                        try:
                            result = dispatch_tool(block.name, block.input)
                            result_text = json.dumps(result, ensure_ascii=False, default=str)
                        except Exception as e:
                            result_text = json.dumps({"error": str(e)})
                            log.error("Error en tool %s: %s", block.name, e)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })

                self.messages.append({"role": "user", "content": tool_results})
                continue

            break

        self._persist_session(user_message)
        return "Análisis completado."

    def _persist_session(self, task: str):
        self.memory.save_session(self.session_id, task, self.messages[-20:])  # últimos 20 mensajes

    def reset(self):
        """Reinicia el historial de conversación."""
        self.messages = []
        self.session_id = str(uuid.uuid4())[:8]


# ── Implementaciones de tools de alto nivel ───────────────────────────────

def _run_daily(zip_path: str, output_label: str | None = None) -> dict:
    """Procesa un ZIP diario completo."""
    from ..pipeline.loader import read_daily_zip, load_master_products, load_master_branches
    from ..pipeline.cleaner import clean_prices, normalize_ean_column
    from ..pipeline.enricher import enrich_with_products, enrich_with_branches, filter_excluded_chains

    p = Path(zip_path)
    if not p.exists():
        return {"error": f"Archivo no encontrado: {zip_path}"}

    label = output_label or p.stem
    mem = MemoryManager()
    run_id = mem.start_run("daily", period=label)

    try:
        raw = read_daily_zip(p)
        if "productos" not in raw:
            mem.fail_run(run_id, "Sin productos en el ZIP")
            return {"error": "ZIP sin datos de productos"}

        df = raw["productos"]
        df = normalize_ean_column(df, "productos_ean")
        df = filter_excluded_chains(df)

        # Enriquece con maestros si están disponibles
        try:
            mp = load_master_products()
            df = enrich_with_products(df, mp)
        except FileNotFoundError:
            pass
        try:
            mb = load_master_branches()
            df = enrich_with_branches(df, mb)
        except FileNotFoundError:
            pass

        n_unique = df["ean_norm"].nunique()
        n_branches = df[["id_comercio", "id_bandera", "id_sucursal"]].drop_duplicates().__len__() if all(c in df.columns for c in ["id_comercio", "id_bandera", "id_sucursal"]) else "N/D"

        mem.complete_run(run_id)
        return {
            "status": "ok",
            "label": label,
            "n_productos_unicos": n_unique,
            "n_sucursales": n_branches,
            "nota": "Maestros no disponibles — enriquecimiento limitado" if "marca" not in df.columns else "Procesamiento completo",
        }
    except Exception as e:
        mem.fail_run(run_id, str(e))
        return {"error": str(e)}


def _run_semester(semester: str, source_path: str | None = None) -> dict:
    """Procesa un semestre del SEPA."""
    from ..pipeline.loader import iter_semester_csvgz, load_master_products, load_master_branches
    from ..pipeline.cleaner import clean_prices
    from ..pipeline.enricher import enrich_with_branches, filter_excluded_chains
    from ..pipeline.aggregator import compute_monthly_avg, build_branch_basket, aggregate_by_province, aggregate_national_weighted
    from ..viz.exports import save_parquet, save_semester_excel
    import pandas as pd

    if source_path is None:
        candidates = list((INPUT_DIR / "semestrales").glob(f"*{semester}*.zip"))
        if not candidates:
            return {"error": f"No se encontró ZIP para semestre {semester} en {INPUT_DIR / 'semestrales'}"}
        source_path = str(candidates[0])

    mem = MemoryManager()
    run_id = mem.start_run("semester", period=semester)

    try:
        from ..config.canasta import CANASTA_EANS
        frames = []
        for df_chunk in iter_semester_csvgz(Path(source_path), ean_filter=CANASTA_EANS):
            df_chunk = filter_excluded_chains(df_chunk)
            df_chunk = clean_prices(df_chunk, auto_scale=True)
            frames.append(df_chunk)
            gc.collect()

        if not frames:
            mem.fail_run(run_id, "Sin datos")
            return {"error": "No se encontraron datos en la fuente"}

        df_long = pd.concat(frames, ignore_index=True)
        del frames; gc.collect()

        try:
            mb = load_master_branches()
            df_enriched = enrich_with_branches(df_long, mb)
        except FileNotFoundError:
            df_enriched = df_long

        df_monthly = compute_monthly_avg(df_enriched)
        df_branch = build_branch_basket(df_monthly)

        cache_path = CACHE_DIR / f"canasta_branch_{semester}.parquet"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        save_parquet(df_branch, cache_path)
        mem.register_artifact(run_id, "parquet", cache_path, period=semester, description="Canasta por sucursal")

        df_prov = aggregate_by_province(df_branch, df_enriched) if "provincia" in df_enriched.columns else pd.DataFrame()
        df_nat = aggregate_national_weighted(df_prov) if not df_prov.empty else pd.DataFrame()

        excel_path = OUTPUT_DIR / f"canasta_{semester}_serie.xlsx"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        save_semester_excel(
            semester=semester,
            df_cobertura=pd.DataFrame(),
            df_diaria=None,
            df_provincia=df_prov,
            df_region=None,
            df_nacional=df_nat,
            df_pesos=pd.DataFrame(list({"provincia": k, "peso": v} for k, v in __import__("sepa.config.settings", fromlist=["POPULATION_WEIGHTS"]).POPULATION_WEIGHTS.items())),
            output_dir=OUTPUT_DIR,
        )
        mem.register_artifact(run_id, "excel", excel_path, period=semester)
        mem.complete_run(run_id, str(excel_path))

        return {
            "status": "ok",
            "semester": semester,
            "n_sucursales": len(df_branch),
            "meses": sorted(df_branch["mes"].unique().tolist()) if "mes" in df_branch.columns else [],
            "output": str(excel_path),
        }
    except Exception as e:
        mem.fail_run(run_id, str(e))
        log.exception("Error en semestre %s", semester)
        return {"error": str(e)}


def _run_consolidation(from_month: str | None = None) -> dict:
    """Consolida todos los semestres y genera comparativa IPC."""
    from ..analysis.timeseries import consolidate_semesters, build_comparative, load_ipc
    from ..viz.exports import save_consolidated_excel
    from ..viz.charts import plot_index_series, plot_monthly_variations
    import pandas as pd

    excel_files = sorted(OUTPUT_DIR.glob("canasta_*_serie.xlsx")) if OUTPUT_DIR.exists() else []
    if not excel_files:
        return {"error": "No hay archivos de semestres en output/. Procesar semestres primero."}

    from_month = from_month or VALID_FROM
    mem = MemoryManager()
    run_id = mem.start_run("consolidation")

    try:
        series = consolidate_semesters(excel_files)
        df_nat = series["nacional"]
        df_prov = series["provincia"]
        df_reg = series["region"]

        try:
            df_ipc = load_ipc()
            df_comp = build_comparative(df_nat, df_ipc, base_month=from_month)
        except FileNotFoundError:
            df_ipc = pd.DataFrame()
            df_comp = pd.DataFrame()

        out_excel = OUTPUT_DIR / "canasta_SEPA_consolidado.xlsx"
        save_consolidated_excel(df_nat, df_prov, df_reg, df_ipc, df_comp, out_excel)

        PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
        chart_paths = []
        if not df_comp.empty:
            p = plot_index_series(df_comp, PRODUCTS_DIR / "indices_consolidado.png", from_month=from_month)
            p2 = plot_monthly_variations(df_comp, PRODUCTS_DIR / "variaciones_consolidado.png", from_month=from_month)
            chart_paths = [str(p), str(p2)]

        mem.complete_run(run_id, str(out_excel))
        return {
            "status": "ok",
            "semestres_procesados": len(excel_files),
            "meses_validos": len(df_nat[df_nat["mes"] >= from_month]) if not df_nat.empty else 0,
            "output_excel": str(out_excel),
            "graficos": chart_paths,
        }
    except Exception as e:
        mem.fail_run(run_id, str(e))
        return {"error": str(e)}


def _generate_map(mes: str | None = None) -> dict:
    """Genera el mapa interactivo por sucursal."""
    from ..viz.maps import make_branch_map
    from ..viz.exports import load_parquet
    import pandas as pd

    parquets = sorted(CACHE_DIR.glob("canasta_branch_*.parquet")) if CACHE_DIR.exists() else []
    if not parquets:
        return {"error": "No hay datos de sucursales en cache. Procesar un semestre primero."}

    try:
        frames = [load_parquet(p) for p in parquets]
        df_branch = pd.concat(frames, ignore_index=True)
        if mes:
            df_branch = df_branch[df_branch["mes"] == mes]
        if df_branch.empty:
            return {"error": f"Sin datos para mes={mes}"}
        mes = df_branch["mes"].max()

        from ..pipeline.loader import load_master_branches
        from ..pipeline.enricher import enrich_with_branches
        df_meta = load_master_branches()
        branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_branch.columns]
        df_enriched = enrich_with_branches(df_branch[branch_cols].drop_duplicates(), df_meta)

        out = PRODUCTS_DIR / f"mapa_sucursales_{mes.replace('-', '')}.html"
        PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
        make_branch_map(df_branch, df_enriched, out, mes=mes)
        return {"status": "ok", "mes": mes, "output": str(out), "n_sucursales": len(df_branch)}
    except Exception as e:
        return {"error": str(e)}


def _generate_rankings(mes: str | None = None) -> dict:
    """Genera los rankings de cadenas."""
    from ..viz.exports import load_parquet
    from ..analysis.chains import national_ranking, amba_ranking
    from ..viz.charts import plot_chain_ranking
    from ..pipeline.loader import load_master_branches
    from ..pipeline.enricher import enrich_with_branches
    import pandas as pd

    parquets = sorted(CACHE_DIR.glob("canasta_branch_*.parquet")) if CACHE_DIR.exists() else []
    if not parquets:
        return {"error": "Sin datos en cache."}

    try:
        frames = [load_parquet(p) for p in parquets]
        df_branch = pd.concat(frames, ignore_index=True)
        if mes:
            df_branch = df_branch[df_branch["mes"] == mes]
        mes = df_branch["mes"].max()
        df_branch = df_branch[df_branch["mes"] == mes]

        mb = load_master_branches()
        branch_cols = [c for c in ["id_comercio", "id_bandera", "id_sucursal"] if c in df_branch.columns]
        df_enriched = enrich_with_branches(df_branch[branch_cols].drop_duplicates(), mb)

        rank_nac = national_ranking(df_branch, df_enriched, mes=mes)
        rank_amba = amba_ranking(df_branch, df_enriched, mes=mes)

        PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
        p1 = plot_chain_ranking(rank_nac, PRODUCTS_DIR / f"ranking_nacional_{mes.replace('-','')}.png",
                                 title=f"Ranking Nacional — {mes}")
        p2 = plot_chain_ranking(rank_amba, PRODUCTS_DIR / f"ranking_amba_{mes.replace('-','')}.png",
                                 title=f"Ranking AMBA — {mes}")
        return {
            "status": "ok", "mes": mes,
            "ranking_nacional": str(p1),
            "ranking_amba": str(p2),
            "n_cadenas_nacional": len(rank_nac),
            "n_cadenas_amba": len(rank_amba),
        }
    except Exception as e:
        return {"error": str(e)}
