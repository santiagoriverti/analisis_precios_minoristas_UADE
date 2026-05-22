# ICM-UADE — Análisis de Precios Minoristas SEPA

## Skills instalados en este proyecto

### Memoria (Self-Improving Agent)

| Comando | Skill | Cuándo usar |
|---------|-------|-------------|
| `/si:remember` | `si-remember` | Guardar decisiones, convenciones, gotchas del SEPA entre sesiones |
| `/si:review` | `si-review` | Auditar y limpiar la memoria del proyecto |
| `/si:promote` | `si-promote` | Promover patrones repetidos a reglas permanentes en CLAUDE.md |
| `/si:extract` | `si-extract` | Extraer un patrón como skill reutilizable en otros proyectos |

La memoria del proyecto vive en `.claude/MEMORY.md`. Se carga automáticamente al iniciar cada sesión.

### Análisis de datos

| Skill | Cuándo se activa | Fuente |
|-------|-----------------|--------|
| `data-quality-auditor` | Al cargar datos SEPA nuevos o antes de publicar resultados | alirezarezvani/claude-skills |
| `statistical-analyst` | Al calcular índices, variaciones, comparativas IPC | alirezarezvani/claude-skills |
| `senior-data-scientist` | Al diseñar análisis estadísticos, experimentos, modelos | alirezarezvani/claude-skills |
| `senior-data-engineer` | Al optimizar el pipeline, diseñar esquemas, mejorar ETL | alirezarezvani/claude-skills |

Los skills están en `.claude/skills/`. Sus SKILL.md se cargan automáticamente.

---

## ¿Qué es este proyecto?

Sistema de análisis de precios minoristas argentinos usando datos del **SEPA** (Sistema Electrónico de Publicidad de Precios Argentinos). Desarrollado por **INECO — Universidad Argentina de la Empresa**.

Construye el **ICM-UADE** (Índice de Canasta de Mercado): canasta fija de 30 productos de consumo masivo, valuada mensualmente por sucursal, provincia, región y a nivel nacional (ponderada por Censo 2022).

## Estructura del proyecto

```
src/sepa/
├── config/     → canasta.py (30 EANs + cantidades), geo.py, cadenas.py, settings.py
├── pipeline/   → loader.py, cleaner.py, enricher.py, aggregator.py
├── analysis/   → basket.py, chains.py, timeseries.py
├── viz/        → maps.py (Folium), charts.py (matplotlib), exports.py (Excel/Parquet)
└── agents/     → memory.py (SQLite), tools.py, orchestrator.py (Anthropic API)

notebooks/      → 5 notebooks ordenados por flujo de trabajo
scripts/        → CLI runners
data/           → input/, masters/, cache/, output/ (gitignoreados)
products/       → outputs publicables (HTMLs, PNGs)
memory/         → state.db (SQLite con historial de runs)
```

## Flujos de trabajo (en orden)

### 1. Análisis de universo de productos (notebook 01)
```python
# Input: data/input/diarios/AAAA-MM-DD.zip
# Output: data/output/productos_unicos_AAAA-MM-DD.xlsx
```

### 2. Canasta diaria por provincia (notebook 02)
```python
# Input: ZIP diario + maestros
# Output: Excel + coropleta PNG
```

### 3. Mapa interactivo + rankings (notebook 03)
```python
# Input: ZIP semestral o CSV.GZ + maestros
# Output: products/mapa_canasta_YYYYMM.html + ranking PNGs
```

### 4. Serie temporal semestral (notebook 04 / CLI)
```python
# CLI: python scripts/procesar_semestral.py 2026A
# Output: data/output/canasta_2026A_serie.xlsx
```

### 5. Consolidación + IPC (notebook 05 / CLI)
```python
# CLI: python scripts/consolidar_series.py
# Output: data/output/canasta_SEPA_consolidado.xlsx + graficos en products/
```

### 6. Agente interactivo (multi-agente)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/agente_interactivo.py
# O directamente:
python scripts/agente_interactivo.py --tarea "Generá el mapa del mes 2026-04"
```

## Datos de entrada necesarios

Colocar en `data/masters/`:
- `Maestro de Productos Interno.xlsx` — 176K productos con EANs y metadatos
- `maestro_sucursales_completo.xlsx` — 3.6K sucursales con coordenadas
- `IPC.xlsx` — IPC INDEC mensual (para comparativa)
- `ar.json` — GeoJSON de provincias argentinas (para coropleta)

Colocar en `data/input/`:
- `diarios/AAAA-MM-DD.zip` — ZIP diario del SEPA
- `semestrales/AAAA-S.zip` — ZIP semestral (ej: `2026A.zip`, `2025B.zip`)

## Canasta de 30 productos

La canasta está definida en `src/sepa/config/canasta.py` con EANs exactos:

| Categoría | Productos | Ejemplo |
|-----------|-----------|---------|
| Lácteos (5) | 20L leche, yogur, queso... | Leche SanCor 1L × 20 |
| Almacén (8) | Aceite, arroz, fideos... | Yerba Taragüi 500g × 2 |
| Bebidas (5) | Coca Cola, agua, cerveza... | Coca Cola lata × 8 |
| Limpieza (3) | Lavandina, detergente... | Lavandina Ayudín × 2 |
| Higiene (7) | Shampoo, jabón... | Papel higiénico × 2 |
| Snacks (2) | Rocklets, Saladix | Rocklets 40g × 2 |

## Decisiones técnicas importantes

- **Escala de precios**: Se detecta automáticamente (algunas versiones de SEPA reportan en centavos). Ver `pipeline/cleaner.py:detect_price_scale()`.
- **Período válido**: Desde mayo 2023 (cobertura SEPA estable). Los meses previos existen pero no son comparables.
- **Imputación**: Si una sucursal no tiene un producto, se imputa el promedio nacional. Solo se incluyen sucursales con ≥20/30 productos propios.
- **Cadenas excluidas**: FULL (19), Easy (2013), Mercado Libre (4), Farmacity (3001), Simplicity (3002).
- **Ponderación nacional**: Censo 2022, 24 provincias. Ver `config/settings.py:POPULATION_WEIGHTS`.
- **Cache**: Los resultados intermedios se guardan como Parquet en `data/cache/`. El historial de runs en `memory/state.db` (SQLite).

## Instalación

```bash
pip install -e ".[dev]"
# o
pip install -r requirements.txt
```

## Multi-agente

El orquestador en `agents/orchestrator.py` usa Claude via Anthropic SDK con:
- **Prompt caching** para reducir costos en sesiones largas
- **Tool use** para despachar análisis a módulos especializados
- **Memoria persistente** en SQLite para recordar qué períodos ya fueron procesados

Variables de entorno requeridas:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

## Fuentes de datos

- SEPA: https://datos.produccion.gob.ar/dataset/sepa-precios
- IPC INDEC: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31
- Censo 2022: https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165
