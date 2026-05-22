---
name: informe-mensual
description: Genera el informe de prensa mensual del ICM-UADE con todos los resultados: valor de canasta, variación, comparativa IPC, ranking provincial, ranking de cadenas nacional y AMBA, ranking de barrios CABA, análisis de costa atlántica. Produce tablas LaTeX listas para el documento académico.
---

# Informe Mensual ICM-UADE — Generador

Produce el informe de prensa mensual del Índice de Canasta de Mercado UADE.

## Estructura del informe

### 1. Valor de la canasta
- ICM-UADE nacional ponderado (Censo 2022)
- Variación mensual %
- Variación interanual % (vs. mismo mes año anterior)
- Comparativa: ICM-UADE vs. IPC INDEC General vs. IPC Alimentos

### 2. Cobertura del relevamiento
- N° de sucursales analizadas
- N° de provincias
- N° de localidades
- N° de cadenas

### 3. Ranking provincial
- 24 provincias ordenadas de menor a mayor canasta
- % vs. promedio nacional
- Tabla LaTeX lista para pegar

### 4. Ranking de cadenas — Nacional
- Ordenado de más cara a más barata
- Filtro: mínimo 10 sucursales (usar `MIN_SUCURSALES_RANKING`)
- Incluye: nombre, canasta promedio, n° sucursales, % vs. promedio

### 5. Ranking de cadenas — AMBA
- Solo Buenos Aires + CABA
- Misma estructura que nacional

### 6. Ranking de barrios CABA (48 barrios)
- Clasificación por coordenadas GPS (no por nombre de calle)
- Top 10 más caros y top 10 más baratos
- Dispersión total CABA

### 7. Casos especiales (mencionar si aplica)
- Costa Atlántica (66 sucursales)
- Belgrano real (coordenadas) vs. Belgrano por nombre
- Ciudades grandes con suficiente muestra

## Convenciones de escritura

- **Español argentino**: voseo natural
- **Tipografía numérica argentina**: punto como separador de miles, coma para decimales
  - ✅ $322.566 (+3,01%)
  - ❌ $322,566 (+3.01%)
- **Nombres de cadenas**: DIA (no "Dia"), ChangoMas (no "Changomás"), Carrefour (no "carrefour")
- **Label correcto**: "ICM-UADE" (no "Canasta SEPA-UADE" ni "canasta SEPA")
- **Período de índices**: base = marzo 2024 = 100 (para gráficos recientes)
- **Período válido**: desde mayo 2023. Las variaciones de mayo y junio 2023 no son comparables.

## Checklist antes de publicar

- [ ] Verificar variación interanual (parece baja si da < 20% en 2026)
- [ ] Confirmar dispersión provincial (debería ser ~12-13%)
- [ ] Verificar que "más cara → más barata" en tabla de cadenas (no al revés)
- [ ] Belgrano en CABA: usar coordenadas, no nombre de sucursal
- [ ] DPI de gráficos: 300 (no 600 — 4x más livianos)
- [ ] Label en gráficos: "ICM-UADE" en la leyenda
- [ ] Unificar terminología: "Norte Grande" = NOA + NEA

## Template de tabla LaTeX provincial

```latex
\\begin{table}[h]
\\centering
\\caption{ICM-UADE por provincia — {MES} (en pesos corrientes)}
\\label{tab:canasta_provincias}
\\begin{tabular}{llrr}
\\toprule
Rank & Provincia & Canasta & vs. promedio \\\\
\\midrule
{FILAS}
\\bottomrule
\\end{tabular}
\\end{table}
```

## Código para generar el informe completo

```python
from sepa.analysis import basket_by_province, national_ranking, amba_ranking, barrio_ranking_caba
from sepa.analysis import build_comparative
from sepa.viz.charts import plot_chain_ranking, plot_province_ranking, plot_index_series, plot_monthly_variations

# Cargar datos del mes
mes = "2026-04"

# 1. Canasta por provincia
df_prov_rank = basket_by_province(df_province, mes)
print(df_prov_rank[["ranking", "provincia", "canasta_provincia", "vs_promedio_pct"]])

# 2. Rankings cadenas
rank_nac  = national_ranking(df_branch, df_enriched, mes=mes)
rank_amba = amba_ranking(df_branch, df_enriched, mes=mes)

# 3. Barrios CABA
rank_barrios = barrio_ranking_caba(df_branch, df_enriched, mes=mes)

# 4. Gráficos
plot_chain_ranking(rank_nac, f"products/ranking_cadenas_nacional_{mes}.png", title=f"Ranking Nacional — {mes}")
plot_province_ranking(df_province, f"products/ranking_provincias_{mes}.png", mes=mes)
```
