---
name: barrios-caba
description: Análisis de precios de canasta ICM-UADE por barrio de CABA. Clasifica sucursales en los 48 barrios usando bounding boxes de coordenadas WGS84. Genera ranking de barrios, detecta patrón norte/centro vs. sur/oeste, identifica falsos positivos por nombre de calle (ej. "Av. Belgrano" en Boedo).
---

# Barrios CABA — ICM-UADE

Análisis de precios minoristas a nivel de barrio en la Ciudad Autónoma de Buenos Aires.

## Metodología de clasificación

La clasificación usa **coordenadas GPS**, no nombres de calles ni barrio declarado por la sucursal.
Esto evita falsos positivos como sucursales en "Av. Belgrano" que físicamente están en Boedo o Monserrat.

Los bounding boxes de los 48 barrios están en `src/sepa/config/geo.py:BARRIOS_CABA_BBOX`.
Formato: `(lat_min, lat_max, lon_min, lon_max)`.

## Filtros previos necesarios

Antes de calcular el ranking de barrios, verificar que se aplicaron:
1. Exclusión de sucursales tipo **Web** (`sucursales_tipo != 'Web'`)
2. Exclusión de sucursales con CABA declarada pero coordenadas fuera del bounding box CABA:
   - lat: [-34.71, -34.53]
   - lon: [-58.53, -58.34]

## Resultados de referencia — Abril 2026

- **668 sucursales** asignadas a barrio (77% de 869 totales en CABA)
- **Dispersión total CABA: 2,40%** (mucho menor que nacional 12.1%)
- **Patrón**: norte/centro más caro vs. sur/oeste más barato

### Top 5 más caros
| Barrio | Canasta | vs. CABA |
|--------|---------|---------|
| San Nicolás | $327.321 | +0,90% |
| Belgrano | $326.332 | +0,60% |
| Recoleta | $325.399 | +0,31% |
| Villa del Parque | $324.978 | +0,18% |
| Caballito | $324.846 | +0,14% |

### Top 5 más baratos
| Barrio | Canasta | vs. CABA |
|--------|---------|---------|
| Villa Soldati | $319.641 | -1,47% |
| La Paternal | $320.163 | -1,30% |
| Villa Real | $320.462 | -1,21% |
| Villa Lugano | $320.636 | -1,16% |
| Vélez Sársfield | $321.217 | -0,98% |

## Caso especial: Belgrano

"Belgrano" buscado por nombre de sucursal da 33 resultados pero incluye 5 falsos positivos
(Carrefour Express en "Av. Belgrano" ubicados en Boedo/Monserrat).
Usando clasificación por coordenadas: **28-30 sucursales reales** en el barrio Belgrano.

## Uso en código

```python
from sepa.analysis.basket import barrio_ranking_caba
from sepa.config.geo import assign_barrio_caba

# Asignar barrio a una coordenada
barrio = assign_barrio_caba(-34.575, -58.450)  # → "Belgrano"

# Ranking completo
df_ranking = barrio_ranking_caba(df_branch, df_enriched, mes="2026-04")
print(df_ranking[["ranking", "barrio_caba", "canasta_barrio", "vs_promedio_caba_pct", "n_sucursales"]])
```

## Mejoras futuras

- GeoJSON con polígonos exactos de los 48 barrios (más preciso que bounding boxes)
- Cruzamiento con datos socioeconómicos Censo 2022 por barrio
- Evolución temporal del ranking por barrio
