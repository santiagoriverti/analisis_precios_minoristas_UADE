# ICM-UADE — Análisis de Precios Minoristas SEPA

**INECO · Instituto de Economía · Universidad Argentina de la Empresa**  
**Autor**: Santiago Riverti — sriverti@uade.edu.ar

Sistema de análisis de precios minoristas argentinos basado en datos del **SEPA** (Sistema Electrónico de Publicidad de Precios Argentinos, Ministerio de Economía). Construye el **ICM-UADE** (Índice de Canasta de Mercado): 30 productos de consumo masivo valuados mensualmente por sucursal, provincia, región, barrio de CABA y país.

---

## ¿Qué genera este sistema?

| Análisis | Output |
|----------|--------|
| 🗺️ **Mapa interactivo** | HTML Folium — precio de canasta por sucursal, coloreado verde→rojo, popup con detalle de 30 productos |
| 📊 **Ranking de cadenas** | PNG — Nacional y AMBA, por precio promedio de canasta |
| 🏙️ **Ranking de barrios CABA** | 48 barrios clasificados por coordenadas GPS (no por nombre de calle) |
| 🏛️ **Canasta por provincia** | 24 provincias rankeadas con % vs. promedio nacional |
| 📈 **Serie temporal** | ICM-UADE mensual desde mayo 2023 con índice base 100 |
| 📉 **Comparativa IPC** | ICM-UADE vs. IPC INDEC General y Alimentos, brecha acumulada |
| 📄 **Tabla LaTeX** | Lista para pegar en el informe académico |

---

## Instalación

```bash
git clone https://github.com/santiagoriverti/analisis_precios_minoristas_UADE.git
cd analisis_precios_minoristas_UADE
pip install -r requirements.txt
```

En Google Colab:
```python
!git clone https://github.com/santiagoriverti/analisis_precios_minoristas_UADE.git /content/analisis_precios_minoristas_UADE
!pip install -r /content/analisis_precios_minoristas_UADE/requirements.txt
```

---

## Datos necesarios

### Archivos maestros — colocar en `data/masters/`

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `Maestro de Productos Interno.xlsx` | 176.702 productos con EAN, marca, rubro, categoría | ~21 MB |
| `maestro_sucursales_completo.xlsx` | 3.611 sucursales con coordenadas GPS, provincia, región | ~480 KB |
| `IPC.xlsx` | IPC INDEC mensual por división (desde 2017) | ~25 KB |
| `ar.json` | GeoJSON de 24 provincias argentinas (simplemaps.com) | ~1 MB |

### Datos SEPA

**Fuente oficial**: [datos.produccion.gob.ar/dataset/sepa-precios](https://datos.produccion.gob.ar/dataset/sepa-precios)

**Archivos históricos**:
- 2018-2023: [Google Drive](https://drive.google.com/drive/folders/13GONeBs5lQCSUdBioHYk-8GhfDtIyliD)
- 2024-2026: [Google Drive](https://drive.google.com/drive/folders/1GNs9SrZ4BIoBsviBVWYYqRcsj4dwPF-I)

#### Para análisis de evolución semestral

Colocar en `data/input/semestrales/` con nombre `AAAAS.zip` (A=primer semestre, B=segundo):

```
data/input/semestrales/
├── 2022A.zip    ← enero-junio 2022
├── 2022B.zip    ← julio-diciembre 2022
├── 2023A.zip
├── 2023B.zip
├── 2024A.zip
├── 2024B.zip
├── 2025A.zip
├── 2025B.zip
└── 2026A.zip    ← enero-junio 2026
```

#### Para análisis mensual / mapa de sucursales

Colocar en `data/input/semestrales/` o un directorio aparte los archivos mensuales:

```
MMAAAA_pais_parte1COMPLETO.csv.gz
MMAAAA_pais_parte2COMPLETO.csv.gz
```

Ejemplo: `042026_pais_parte1COMPLETO.csv.gz` = abril 2026.

---

## Flujo de trabajo

### Notebooks (recomendado para análisis)

```bash
jupyter lab notebooks/
```

| Notebook | ¿Qué hace? | Input |
|----------|-----------|-------|
| `01_universo_productos.ipynb` | Identifica todos los EANs únicos del SEPA con cobertura por cadena y provincia | ZIP diario |
| `02_canasta_diaria.ipynb` | Canasta ICM-UADE por provincia + coropleta PNG | ZIP diario + maestros |
| `03_mapa_sucursales.ipynb` | Mapa Folium interactivo + rankings de cadenas + barrios CABA | ZIP semestral + maestros |
| `04_evolucion_semestral.ipynb` | Serie temporal mensual de un semestre por provincia/región/nación | ZIP semestral + maestros |
| `05_consolidacion_ipc.ipynb` | Consolida todos los semestres + índice + comparativa IPC + gráficos | Outputs notebook 04 + IPC.xlsx |

### Scripts CLI

```bash
# Procesar un semestre (busca data/input/semestrales/2026A.zip)
python scripts/procesar_semestral.py 2026A

# Procesar todos los ZIPs disponibles de una vez
python scripts/procesar_semestral.py --todos

# Consolidar y generar comparativa IPC + gráficos
python scripts/consolidar_series.py

# Agente de IA interactivo (requiere ANTHROPIC_API_KEY)
python scripts/agente_interactivo.py
```

### Agente de IA

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Linux / Mac / Colab
export ANTHROPIC_API_KEY="sk-ant-..."

python scripts/agente_interactivo.py
```

El agente responde en lenguaje natural en español argentino:
- *"Procesá el semestre 2026A y generá el mapa"*
- *"¿Cuánto vale la canasta en abril 2026? ¿Qué cadena fue la más barata?"*
- *"Generá el ranking de barrios de CABA"*
- *"Consolidá todos los semestres y comparalos con el IPC"*

---

## Canasta de 30 productos (ICM-UADE)

Calibrada para hogar tipo de 4 personas — **105 unidades mensuales en total**.

| Categoría | Productos | Ejemplo | EAN |
|-----------|-----------|---------|-----|
| **Lácteos** (5) | Leche ×20, Yogur ×8, Queso ×2, Manteca ×2, Cindor ×4 | Serenísima 1L | 7790742363008 |
| **Almacén** (8) | Aceite ×2, Arroz ×2, Fideos ×4, Harina ×2, Yerba ×2, Café ×1, Chocolinas ×4, Sal ×1 | Fideos Favorita 500g | 7790070320285 |
| **Bebidas** (5) | Coca Cola lata ×8, Coca Sin Azúcar ×4, Agua Levite ×8, Cerveza ×6, Vino ×2 | | 7790895000232 |
| **Limpieza** (3) | Lavandina ×2, Detergente ×2, Limpiador Poett ×2 | Ayudín 1L | 7790132098459 |
| **Higiene** (7) | Shampoo ×1, Acondicionador ×1, Jabón ×4, Desodorante ×2, Hilo dental ×1, Toallas ×2, Papel higiénico ×2 | | — |
| **Snacks** (2) | Rocklets ×2, Saladix ×2 | | 7790580327415 |

Lista completa con EANs verificados en [`src/sepa/config/canasta.py`](src/sepa/config/canasta.py).

---

## Metodología

### Período válido

La serie histórica del ICM-UADE es confiable **desde mayo de 2023**. Antes, la cobertura SEPA era insuficiente.
Las variaciones de mayo y junio 2023 se anulan (panel en consolidación). El primer mes comparable es **julio 2023**.

### Detección automática de escala de precios

El SEPA varía el factor de escala entre períodos. Se detecta automáticamente con la mediana de Sal + Fideos + Lavandina:

| Mediana observada | Factor divisor | Ejemplo |
|-------------------|---------------|---------|
| $30 – $5.000 | ÷1 | Precios ya en pesos |
| $3.000 – $500.000 | ÷100 | Centavos → pesos |
| > $500.000 | ÷10.000 | Decimales implícitos |

### Imputación de productos faltantes

Si una sucursal no reporta un producto → se imputa el promedio nacional de ese producto y mes.
Solo se incluyen sucursales con **al menos 20 de 30 productos propios** (sin imputar).

### Ponderación nacional

Usa **pesos poblacionales del Censo INDEC 2022** (45.892.285 personas, 24 provincias).

### Filtros de calidad

- Cadenas excluidas: FULL/YPF (19), Mercado Libre (2013), Easy (3001), ID 4
- Sucursales excluidas: tipo "Web" (sin ubicación física)
- CABA mal clasificadas: coordenadas fuera del bounding box lat[-34.71,-34.53] lon[-58.53,-58.34]

### Barrios CABA

Los 48 barrios se clasifican por **coordenadas GPS** (bounding boxes), no por nombre de sucursal.
Esto evita falsos positivos como sucursales en "Av. Belgrano" que físicamente están en Boedo.

---

## Cadenas incluidas (14 representativas)

| ID | Cadena(s) |
|----|---------|
| 9 | Vea / Disco / Jumbo (Cencosud) |
| 10 | Carrefour / Carrefour Market / Carrefour Express |
| 11 | ChangoMas / Hiper ChangoMas / Mi ChangoMas (ex Walmart) |
| 12 | Coto |
| 13 | Cooperativa Obrera |
| 15 | DIA |
| 16 | Hipermercado Libertad / Mini Libertad |
| 2 | La Anónima |
| 20 | LAR |
| 21 | Toledo |
| 47 | Pasamonte |

---

## Resultados — Abril 2026 (último período procesado)

| Métrica | Valor |
|---------|-------|
| **ICM-UADE nacional ponderado** | **$322.566** |
| Variación mensual | +3,01% |
| Sucursales analizadas | 2.369 |
| Cadenas | 14 |
| Provincias | 24 |
| Localidades | 477 |
| Cadena más barata (nacional) | Hipermercado Libertad ($298.914) |
| Cadena más cara (nacional) | La Anónima ($335.213) |
| Dispersión nacional | 12,1% |
| Dispersión AMBA | 5,4% |
| Barrio más barato CABA | Villa Soldati ($319.641, −1,47%) |
| Barrio más caro CABA | San Nicolás ($327.321, +0,90%) |

---

## Arquitectura del código

```
src/sepa/
├── config/
│   ├── settings.py     — rutas, parámetros, pesos poblacionales Censo 2022
│   ├── canasta.py      — 30 EANs verificados con cantidades mensuales
│   ├── geo.py          — ISO→provincia, normalización, 48 barrios CABA (bounding boxes)
│   └── cadenas.py      — IDs SEPA → nombres comerciales, cadenas excluidas
├── pipeline/
│   ├── loader.py       — ZIPs (diario/semestral), CSV.GZ, auto-detección separador
│   ├── cleaner.py      — detección factor de escala, filtros de precio, dedup
│   ├── enricher.py     — join con maestros, filtros Web/CABA, barrios CABA
│   └── aggregator.py   — canasta por sucursal (vectorizado), provincia, región, nación
├── analysis/
│   ├── basket.py       — ranking provincial, barrios CABA, dispersión
│   ├── chains.py       — rankings nacional y AMBA
│   └── timeseries.py   — consolidación multi-semestre, índices, comparativa IPC
├── viz/
│   ├── maps.py         — mapa Folium por sucursal, coropleta por provincia
│   ├── charts.py       — rankings, series temporales, variaciones mensuales
│   └── exports.py      — Excel multi-hoja, Parquet, consolidado
└── agents/
    ├── memory.py       — SQLite: historial de runs, artefactos, KV store
    ├── tools.py        — definición de tools para la API de Anthropic
    └── orchestrator.py — agente multi-herramienta (Claude claude-sonnet-4-6 + prompt caching)

.claude/
├── MEMORY.md           — memoria del proyecto (cargada en cada sesión)
├── settings.json       — permisos y registro de skills
└── skills/
    ├── si-remember/    — /si:remember — guardar decisiones entre sesiones
    ├── si-review/      — /si:review   — auditar memoria
    ├── si-promote/     — /si:promote  — promover patrones a reglas permanentes
    ├── si-extract/     — /si:extract  — extraer skills reutilizables
    ├── barrios-caba/   — análisis de barrios CABA por coordenadas
    ├── informe-mensual/ — generador del informe de prensa ICM-UADE
    ├── data-quality-auditor/    — validación de datos SEPA
    ├── statistical-analyst/     — índices, dispersión, tests estadísticos
    ├── senior-data-scientist/   — análisis estadístico avanzado
    └── senior-data-engineer/    — optimización de pipeline y ETL
```

---

## Dependencias

```
pandas>=2.0.0       numpy>=1.24.0
openpyxl>=3.1.0     pyarrow>=12.0.0
matplotlib>=3.7.0   folium>=0.14.0    branca>=0.6.0
anthropic>=0.40.0   jupyter>=1.0.0
```

---

## Fuentes de datos

| Fuente | URL |
|--------|-----|
| SEPA (portal oficial) | [datos.produccion.gob.ar/dataset/sepa-precios](https://datos.produccion.gob.ar/dataset/sepa-precios) |
| SEPA histórico 2018-2023 | [Google Drive](https://drive.google.com/drive/folders/13GONeBs5lQCSUdBioHYk-8GhfDtIyliD) |
| SEPA 2024-2026 | [Google Drive](https://drive.google.com/drive/folders/1GNs9SrZ4BIoBsviBVWYYqRcsj4dwPF-I) |
| IPC INDEC | [indec.gob.ar](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31) |
| Censo 2022 | [indec.gob.ar](https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165) |
| GeoJSON provincias | [simplemaps.com](https://simplemaps.com/gis/country/ar) |
| Marco normativo SEPA | Resolución 12/2016, ex Secretaría de Comercio |

---

*Desarrollado por INECO — Instituto de Economía, Universidad Argentina de la Empresa (UADE)*
