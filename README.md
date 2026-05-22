# ICM-UADE — Análisis de Precios Minoristas SEPA

> **INECO · Instituto de Economía · Universidad Argentina de la Empresa**

Sistema unificado de análisis de precios minoristas argentinos basado en datos del **SEPA** (Sistema Electrónico de Publicidad de Precios Argentinos). Construye el **ICM-UADE** (Índice de Canasta de Mercado): 30 productos de consumo masivo valuados mensualmente por sucursal, provincia, región y país.

---

## ¿Qué genera este sistema?

| Output | Descripción |
|--------|-------------|
| 🗺️ **Mapa interactivo** | Precio de canasta por sucursal, coloreado verde→rojo, con popup de 30 productos |
| 📊 **Ranking de cadenas** | Nacional y AMBA por precio promedio de canasta |
| 🏙️ **Canasta por provincia** | 24 provincias rankeadas con % vs. promedio nacional |
| 📈 **Serie temporal** | ICM-UADE mensual desde mayo 2023 con índice base 100 |
| 📉 **Comparativa IPC** | Canasta vs. IPC INDEC General y Alimentos, brecha acumulada |

---

## Instalación

### Requisitos

- Python 3.10 o superior
- pip

### Clonar e instalar

```bash
git clone https://github.com/santiagoriverti/analisis_precios_minoristas_UADE.git
cd analisis_precios_minoristas_UADE
pip install -r requirements.txt
```

Para desarrollo (incluye Jupyter):

```bash
pip install -e ".[dev]"
```

### Variables de entorno (solo para el agente de IA)

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Linux / Mac / Google Colab
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Datos requeridos

### Archivos maestros

Colocar en `data/masters/`:

| Archivo | Descripción | Cómo obtenerlo |
|---------|-------------|----------------|
| `Maestro de Productos Interno.xlsx` | ~176K productos con EAN, marca, rubro, categoría, proveedor | Provisto por INECO |
| `maestro_sucursales_completo.xlsx` | ~3.6K sucursales con coordenadas (lat/lng), provincia, región | Provisto por INECO |
| `IPC.xlsx` | IPC INDEC mensual por división (desde 2017) | [INDEC](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31) |
| `ar.json` | GeoJSON de polígonos de provincias argentinas (opcional, para coropleta) | [datos.gob.ar](https://datos.gob.ar) |

### Datos SEPA

Fuente oficial: [datos.produccion.gob.ar/dataset/sepa-precios](https://datos.produccion.gob.ar/dataset/sepa-precios)

#### Para análisis mensual / mapa de sucursales:

Colocar en `data/input/semestrales/` el ZIP de cada semestre:

```
data/input/semestrales/
├── 2022A.zip
├── 2022B.zip
├── 2023A.zip
├── 2023B.zip
├── 2024A.zip
├── 2024B.zip
├── 2025A.zip
├── 2025B.zip
└── 2026A.zip
```

El nombre del archivo determina el código de semestre que usa el sistema (`AAAA` + `A`/`B`).

#### Para análisis de un día específico:

Colocar en `data/input/diarios/`:

```
data/input/diarios/
└── 2026-04-26.zip
```

---

## Uso — Notebooks (recomendado)

Abrir Jupyter:

```bash
jupyter lab notebooks/
```

| # | Notebook | ¿Qué hace? | Input principal |
|---|----------|-----------|-----------------|
| 01 | `01_universo_productos.ipynb` | Identifica todos los EANs únicos del SEPA, cobertura por cadena y provincia | ZIP diario |
| 02 | `02_canasta_diaria.ipynb` | Calcula la canasta ICM-UADE por provincia y genera la coropleta | ZIP diario + maestros |
| 03 | `03_mapa_sucursales.ipynb` | Mapa Folium interactivo + rankings de cadenas nacional y AMBA | ZIP semestral + maestros |
| 04 | `04_evolucion_semestral.ipynb` | Serie temporal mensual de un semestre (provincia / región / nación) | ZIP semestral + maestros |
| 05 | `05_consolidacion_ipc.ipynb` | Consolida todos los semestres, construye índice y compara contra IPC INDEC | Outputs del notebook 04 + IPC.xlsx |

### Uso en Google Colab

Los notebooks detectan automáticamente si están corriendo en Colab. Solo asegurarse de que el proyecto esté disponible en `/content/analisis_precios_minoristas_UADE`:

```python
# En la primera celda de Colab:
!git clone https://github.com/santiagoriverti/analisis_precios_minoristas_UADE.git /content/analisis_precios_minoristas_UADE
!pip install -r /content/analisis_precios_minoristas_UADE/requirements.txt

# Luego subir los archivos maestros y ZIPs a /content/analisis_precios_minoristas_UADE/data/
```

---

## Uso — Scripts CLI

### Procesar un semestre

```bash
# Procesar el semestre 2026A (busca data/input/semestrales/2026A.zip)
python scripts/procesar_semestral.py 2026A

# Procesar todos los ZIPs disponibles
python scripts/procesar_semestral.py --todos

# Ver estado actual
python scripts/procesar_semestral.py
```

### Consolidar series y comparar con IPC

```bash
# Consolida todos los semestres procesados y genera gráficos
python scripts/consolidar_series.py

# Desde un mes específico
python scripts/consolidar_series.py --desde 2024-01
```

### Agente de IA interactivo

```bash
# Modo chat interactivo
python scripts/agente_interactivo.py

# Modo no interactivo (una sola tarea)
python scripts/agente_interactivo.py --tarea "Procesá el semestre 2026A y generá el mapa"
```

---

## Agente de IA multi-agente

El sistema incluye un **orquestador multi-agente** (`src/sepa/agents/orchestrator.py`) basado en la API de Anthropic:

### Características

- **Modelo**: Claude claude-sonnet-4-6 con **prompt caching** (reduce costos en sesiones largas)
- **Tool use**: El agente puede ejecutar 7 herramientas especializadas
- **Memoria persistente**: SQLite en `memory/state.db` — recuerda qué períodos ya fueron procesados
- **Lenguaje natural**: Responde en español con contexto metodológico del ICM-UADE

### Herramientas disponibles

| Tool | Descripción |
|------|-------------|
| `run_daily_analysis` | Procesa un ZIP diario del SEPA |
| `run_semester_analysis` | Procesa un semestre completo |
| `run_consolidation` | Consolida todos los semestres + IPC |
| `generate_branch_map` | Genera mapa Folium interactivo |
| `generate_chain_rankings` | Rankings nacional y AMBA con PNGs |
| `list_available_data` | Lista datos disponibles y resultados |
| `get_analysis_summary` | Estadísticas del último análisis |

### Ejemplo de uso

```python
from sepa.agents.orchestrator import SEPAOrchestrator

agent = SEPAOrchestrator()

# Ejecutar análisis completo
result = agent.chat("Procesá el semestre 2026A, generá el mapa y el ranking de cadenas")
print(result)

# Consultar estado
result = agent.chat("¿Qué semestres ya están procesados?")
print(result)
```

### Uso desde Python en un notebook

```python
import sys
sys.path.insert(0, 'src')

from sepa.agents.orchestrator import SEPAOrchestrator

agent = SEPAOrchestrator()
print(agent.chat("¿Cuál fue la cadena más barata en AMBA en abril 2026?"))
```

---

## Uso programático del paquete

```python
import sys
sys.path.insert(0, 'src')

# Cargar datos
from sepa.pipeline.loader import iter_semester_csvgz, load_master_branches
from sepa.pipeline.cleaner import clean_prices
from sepa.pipeline.enricher import enrich_with_branches, filter_excluded_chains
from sepa.pipeline.aggregator import compute_monthly_avg, build_branch_basket, aggregate_national_weighted

# Configuración
from sepa.config.canasta import CANASTA_EANS

# Procesar semestre
frames = []
for chunk in iter_semester_csvgz('data/input/semestrales/2026A.zip', ean_filter=CANASTA_EANS):
    chunk = filter_excluded_chains(chunk)
    chunk = clean_prices(chunk, auto_scale=True)
    frames.append(chunk)

import pandas as pd
df = pd.concat(frames)

# Calcular canasta por sucursal
df_monthly = compute_monthly_avg(df)
df_branch  = build_branch_basket(df_monthly)

# Agregar a nivel nacional
from sepa.pipeline.aggregator import aggregate_by_province
mb = load_master_branches()
df_enriched = enrich_with_branches(df, mb)
df_prov = aggregate_by_province(df_branch, df_enriched)
df_nat  = aggregate_national_weighted(df_prov)
print(df_nat)

# Generar mapa
from sepa.viz.maps import make_branch_map
make_branch_map(df_branch, df_enriched, 'products/mapa_2026-04.html', mes='2026-04')

# Rankings
from sepa.analysis.chains import national_ranking, amba_ranking
rank_nac  = national_ranking(df_branch, df_enriched, mes='2026-04')
rank_amba = amba_ranking(df_branch, df_enriched, mes='2026-04')

# Comparativa IPC
from sepa.analysis.timeseries import load_ipc, build_comparative
df_ipc  = load_ipc('data/masters/IPC.xlsx')
df_comp = build_comparative(df_nat, df_ipc, base_month='2023-05')

# Gráficos
from sepa.viz.charts import plot_index_series, plot_chain_ranking
plot_index_series(df_comp, 'products/indices.png')
plot_chain_ranking(rank_nac, 'products/ranking_nacional.png')
```

---

## Arquitectura del código

```
analisis_precios_minoristas_UADE/
│
├── src/sepa/                        ← Paquete Python principal
│   ├── config/
│   │   ├── settings.py              ← Rutas, parámetros globales, pesos poblacionales
│   │   ├── canasta.py               ← 30 EANs con cantidades mensuales y categorías
│   │   ├── geo.py                   ← Mapeos ISO → provincia → región
│   │   └── cadenas.py               ← IDs de cadenas SEPA → nombre comercial
│   │
│   ├── pipeline/
│   │   ├── loader.py                ← Descompresión de ZIPs, lectura de CSVs, maestros
│   │   ├── cleaner.py               ← Detección automática de escala de precios, filtros
│   │   ├── enricher.py              ← Join con maestros de productos y sucursales
│   │   └── aggregator.py            ← Canasta por sucursal, imputación, ponderación
│   │
│   ├── analysis/
│   │   ├── basket.py                ← Cobertura, composición, dispersión de la canasta
│   │   ├── chains.py                ← Rankings nacional y AMBA, series por cadena
│   │   └── timeseries.py            ← Consolidación multi-semestre, índices, IPC
│   │
│   ├── viz/
│   │   ├── maps.py                  ← Mapa Folium por sucursal + coropleta provincial
│   │   ├── charts.py                ← Rankings, series temporales, variaciones
│   │   └── exports.py               ← Excel multi-hoja, Parquet, consolidado
│   │
│   └── agents/
│       ├── memory.py                ← SQLite: historial de runs, artefactos, KV store
│       ├── tools.py                 ← Definición de tools para la API de Anthropic
│       └── orchestrator.py          ← Orquestador multi-agente (Claude claude-sonnet-4-6)
│
├── notebooks/
│   ├── 01_universo_productos.ipynb  ← Explorar todos los productos del SEPA
│   ├── 02_canasta_diaria.ipynb      ← Canasta por provincia (datos de un día)
│   ├── 03_mapa_sucursales.ipynb     ← Mapa interactivo + rankings
│   ├── 04_evolucion_semestral.ipynb ← Serie temporal de un semestre
│   └── 05_consolidacion_ipc.ipynb   ← Consolidación multi-año + IPC INDEC
│
├── scripts/
│   ├── procesar_semestral.py        ← CLI: procesar uno o todos los semestres
│   ├── consolidar_series.py         ← CLI: consolidar + IPC + gráficos
│   └── agente_interactivo.py        ← CLI: chat con el agente de IA
│
├── data/
│   ├── input/diarios/               ← ZIPs diarios del SEPA (gitignoreados)
│   ├── input/semestrales/           ← ZIPs semestrales del SEPA (gitignoreados)
│   ├── masters/                     ← Archivos de referencia (gitignoreados)
│   ├── cache/                       ← Parquets intermedios (gitignoreados)
│   └── output/                      ← Excels generados (gitignoreados)
│
├── products/                        ← Outputs publicables (HTML, PNG)
├── memory/                          ← state.db — memoria persistente del agente
│
├── CLAUDE.md                        ← Instrucciones para Claude Code (AI assistant)
├── README.md
├── requirements.txt
└── pyproject.toml
```

---

## Canasta de 30 productos (ICM-UADE)

Calibrada para hogar de 4 personas. Cantidades mensuales fijas:

| Categoría | Productos | EAN ejemplo |
|-----------|-----------|-------------|
| **Lácteos (5)** | Leche entera 1L ×20, Yogur 190g ×8, Queso Casancrem 290g ×2, Manteca 100g ×2, Cindor 1L ×4 | 7790742363008 |
| **Almacén (8)** | Aceite girasol 1.5L ×2, Arroz 500g ×2, Fideos 500g ×4, Harina leudante 1kg ×2, Yerba 500g ×2, Café 250g ×1, Chocolinas 250g ×4, Sal fina 500g ×1 | 7794000012000 |
| **Bebidas (5)** | Coca Cola lata 354ml ×8, Coca Sin Azúcar 2.25L ×4, Agua Levite 500ml ×8, Cerveza lata 473ml ×6, Vino Malbec 750ml ×2 | 7790895004837 |
| **Limpieza (3)** | Lavandina 1L ×2, Detergente 300ml ×2, Limpiador Poett 900ml ×2 | 7790230512009 |
| **Higiene (7)** | Shampoo 400ml ×1, Acondicionador 340ml ×1, Jabón tocador 90g ×4, Antitranspirante ×2, Hilo dental ×1, Toallas femeninas x16 ×2, Papel higiénico ×2 | 7791293020063 |
| **Snacks (2)** | Rocklets 40g ×2, Saladix 100g ×2 | 7790580413405 |

Los EANs exactos están en [`src/sepa/config/canasta.py`](src/sepa/config/canasta.py).

---

## Metodología

### Período válido

La serie temporal del ICM-UADE es confiable **desde mayo de 2023**. Antes de ese mes, la cobertura del SEPA era heterogénea y muchos productos de la canasta aparecían en una sola cadena o no reportaban datos.

- Los meses de mayo y junio de 2023 tienen variaciones marcadas como `NaN` (panel aún en consolidación).
- El primer mes con variación comparable es **julio de 2023**.

### Ponderación nacional

La canasta nacional ponderada usa **pesos poblacionales del Censo 2022** (45.9 millones de personas, 24 provincias). La fórmula es:

```
Canasta_Nacional(mes) = Σ [ Canasta_Provincia(prov, mes) × Peso(prov) ]
```

Donde `Peso(prov) = Población(prov) / Población_Total`.

### Imputación de productos faltantes

Si una sucursal no reporta precio para un producto de la canasta, se imputa el **promedio nacional de ese producto en ese mes**. Solo se incluyen sucursales con al menos **20 de 30 productos propios** (sin imputar).

### Detección automática de escala de precios

Algunas versiones del SEPA reportan precios con decimales implícitos (e.g., `17890` en lugar de `$178.90`). El sistema detecta automáticamente el factor correcto examinando las medianas de 3 productos de referencia (Sal, Fideos, Lavandina):

| Mediana observada | Factor | Interpretación |
|------------------|--------|---------------|
| $30 – $10.000 | ÷1 | Precios ya en pesos |
| $3.000 – $1.000.000 | ÷100 | Centavos → pesos |
| > $1.000.000 | ÷10.000 | Decimales implícitos |

### Cadenas incluidas

| ID Comercio | Cadena(s) |
|-------------|----------|
| 2 | La Anónima |
| 9 | Vea / Disco / Jumbo (Cencosud) |
| 10 | Carrefour / Carrefour Market / Carrefour Express |
| 11 | ChangoMas / Mi ChangoMas / Hiper ChangoMas |
| 12 | Coto |
| 13 | Cooperativa Obrera |
| 15 | DIA |
| 16 | Hipermercado Libertad |
| 20 | LAR |
| 21 | Toledo |
| 47 | Pasamonte |

**Excluidas**: Mercado Libre (4), FULL (19), Easy (2013), Farmacity (3001), Simplicity (3002).

---

## Hallazgos principales (mayo 2023 – abril 2026)

| Métrica | Valor |
|---------|-------|
| **Acumulado ICM-UADE** | **+946%** |
| **IPC INDEC General acumulado** | +586% |
| **Brecha** | +360 puntos de índice |
| Sucursales analizadas (abr. 2026) | 2.371 |
| Cadenas relevadas | 16 |
| Provincia más barata (abr. 2026) | **Córdoba** (−4.0% vs. promedio) |
| Provincia más cara (abr. 2026) | **Santa Cruz** (+8.4% vs. promedio) |
| Dispersión precios AMBA | 5.4% |
| Dispersión precios nacional | 12.1% |

*La canasta de bienes de góndola (30 productos de consumo masivo) aumentó ~1.6× más rápido que el IPC general, que incluye servicios regulados (educación, transporte, vivienda).*

---

## Dependencias

```
pandas>=2.0.0        # DataFrames
numpy>=1.24.0        # Operaciones numéricas
openpyxl>=3.1.0      # Lectura/escritura Excel
pyarrow>=12.0.0      # Parquet (cache eficiente)
matplotlib>=3.7.0    # Gráficos
folium>=0.14.0       # Mapas interactivos Leaflet
branca>=0.6.0        # Colormaps para Folium
anthropic>=0.40.0    # API de Claude (agente multi-herramienta)
jupyter>=1.0.0       # Notebooks (opcional)
```

---

## Contribución

Este es un proyecto institucional de INECO/UADE. Para reportar problemas o sugerir mejoras, abrir un issue en este repositorio.

---

## Fuentes de datos

- **SEPA**: [datos.produccion.gob.ar/dataset/sepa-precios](https://datos.produccion.gob.ar/dataset/sepa-precios)
- **IPC INDEC**: [indec.gob.ar](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31)
- **Censo 2022**: [indec.gob.ar](https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165)

---

*Desarrollado por INECO — Instituto de Economía, Universidad Argentina de la Empresa*
