# ICM-UADE — Análisis de Precios Minoristas SEPA

**INECO · Universidad Argentina de la Empresa**

Sistema unificado de análisis de precios minoristas argentinos basado en datos del SEPA (Sistema Electrónico de Publicidad de Precios Argentinos).

## ¿Qué genera este sistema?

| Output | Descripción |
|--------|-------------|
| **Mapa interactivo** | Precio de canasta por sucursal, coloreado verde→rojo, con popup detallado de 30 productos |
| **Ranking de cadenas** | Nacional y AMBA, por precio promedio de canasta |
| **Canasta por provincia** | Los 24 distritos rankeados con % vs. promedio nacional |
| **Serie temporal** | ICM-UADE mensual desde mayo 2023, con índice base 100 |
| **Comparativa IPC** | Canasta vs. IPC INDEC General y Alimentos, brecha acumulada |

## Instalación

```bash
git clone https://github.com/santiagoriverti/analisis_precios_minoristas_UADE
cd analisis_precios_minoristas_UADE
pip install -r requirements.txt
```

## Datos requeridos

Poner en `data/masters/`:
- `Maestro de Productos Interno.xlsx`
- `maestro_sucursales_completo.xlsx`
- `IPC.xlsx`

Poner en `data/input/semestrales/`:
- `2026A.zip`, `2025B.zip`, etc. (ZIPs del SEPA por semestre)

Fuente: https://datos.produccion.gob.ar/dataset/sepa-precios

## Uso rápido

### Notebooks (recomendado para análisis exploratorio)

```bash
jupyter lab notebooks/
```

| Notebook | Propósito |
|----------|-----------|
| `01_universo_productos.ipynb` | Explorar todos los productos del SEPA |
| `02_canasta_diaria.ipynb` | Canasta por provincia (datos de un día) |
| `03_mapa_sucursales.ipynb` | Mapa interactivo + rankings de cadenas |
| `04_evolucion_semestral.ipynb` | Serie temporal de un semestre |
| `05_consolidacion_ipc.ipynb` | Consolidación multi-año + IPC |

### Scripts CLI

```bash
# Procesar un semestre
python scripts/procesar_semestral.py 2026A

# Procesar todos los semestres disponibles
python scripts/procesar_semestral.py --todos

# Consolidar y generar comparativa IPC
python scripts/consolidar_series.py
```

### Agente de IA interactivo

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/agente_interactivo.py
```

El agente puede ejecutar análisis completos respondiendo a lenguaje natural:
- *"Procesá el semestre 2026A y generá el mapa"*
- *"¿Qué cadena fue la más barata en AMBA en abril 2026?"*
- *"Generá el ranking nacional con gráfico"*

## Canasta de 30 productos (ICM-UADE)

Calibrada para hogar de 4 personas, categorías:
**Lácteos** (5) · **Almacén** (8) · **Bebidas** (5) · **Limpieza** (3) · **Higiene** (7) · **Snacks** (2)

## Hallazgos principales (mayo 2023 – abril 2026)

| Métrica | Valor |
|---------|-------|
| Acumulado canasta ICM-UADE | **+946%** |
| Acumulado IPC INDEC General | +586% |
| Brecha | +360 puntos índice |
| Sucursales analizadas (abr. 2026) | 2.371 |
| Provincia más barata (abr. 2026) | Córdoba (-4.0% vs. promedio) |
| Provincia más cara (abr. 2026) | Santa Cruz (+8.4% vs. promedio) |

## Arquitectura del código

```
src/sepa/
├── config/     canasta.py · geo.py · cadenas.py · settings.py
├── pipeline/   loader.py · cleaner.py · enricher.py · aggregator.py
├── analysis/   basket.py · chains.py · timeseries.py
├── viz/        maps.py · charts.py · exports.py
└── agents/     memory.py · tools.py · orchestrator.py
```

El sistema detecta automáticamente si corre en **Google Colab** o localmente,
y ajusta las rutas de datos en consecuencia.

## Metodología

- **Período válido**: mayo 2023 en adelante (cobertura SEPA estable)
- **Ponderación**: Censo 2022 (45.9M personas, 24 provincias)
- **Imputación**: si una sucursal no tiene un producto → precio nacional promedio
- **Escala de precios**: detección automática (algunos períodos reportan en centavos)
- **Cadenas incluidas**: Carrefour, DIA, Coto, Cencosud, ChangoMas, Cooperativa Obrera, La Anónima, Toledo, LAR, Libertad, Pasamonte

---

*Desarrollado por INECO — Instituto de Economía, UADE*
