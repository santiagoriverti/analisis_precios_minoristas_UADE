---
name: statistical-analyst
description: Análisis estadístico especializado para el ICM-UADE: construcción de índices de precios, cálculo de variaciones, análisis de dispersión, comparativas IPC y significancia estadística de diferencias entre cadenas/provincias.
---

# Statistical Analyst — ICM-UADE / Precios Minoristas

Análisis estadístico riguroso para el Índice de Canasta de Mercado UADE.

## Índices de precios

### Construcción del índice base 100

```python
# Índice de Laspeyres con cantidades fijas (metodología ICM-UADE)
# Base: mayo 2023 = 100

def build_laspeyres_index(df_nacional: pd.DataFrame, base_month: str = '2023-05') -> pd.DataFrame:
    """
    Laspeyres: usa cantidades fijas del período base.
    Apropiado para la canasta ICM-UADE porque las cantidades son fijas por definición.
    """
    value_col = 'canasta_nacional'
    base_val = df_nacional.loc[df_nacional['mes'] == base_month, value_col].iloc[0]
    df = df_nacional.copy()
    df['indice'] = df[value_col] / base_val * 100
    df['variacion_pct'] = df[value_col].pct_change() * 100
    df['variacion_anual_pct'] = df[value_col].pct_change(12) * 100
    return df
```

### Análisis de dispersión de precios

```python
# Coeficiente de variación entre sucursales — mide competencia de precios
def price_dispersion(df_branch: pd.DataFrame, mes: str) -> dict:
    data = df_branch[df_branch['mes'] == mes]['canasta_total']
    return {
        'cv': data.std() / data.mean(),           # Variación relativa
        'p10_p90_ratio': data.quantile(0.9) / data.quantile(0.1),  # Brecha extremos
        'gini': _gini(data.values),               # Desigualdad de precios
        'n': len(data)
    }

# Interpretación:
# CV < 0.05 → mercado muy competitivo (AMBA típicamente 0.054)
# CV > 0.15 → alta dispersión (nacional ~0.121)
# p90/p10 > 1.5 → diferencia significativa entre cadenas caras y baratas
```

## Comparativa con IPC INDEC

### Brecha estadística (test t de diferencia de medias)

```python
from scipy import stats

def test_divergence(canasta_var: pd.Series, ipc_var: pd.Series) -> dict:
    """Test si la canasta SEPA crece significativamente más que el IPC."""
    # Alinear por fecha
    diff = canasta_var - ipc_var
    t_stat, p_value = stats.ttest_1samp(diff.dropna(), 0)
    return {
        'diferencia_media_pp': diff.mean(),
        't_statistic': t_stat,
        'p_value': p_value,
        'significativo': p_value < 0.05
    }
```

### Correlación canasta-IPC

```python
# Alta correlación → misma tendencia, diferente nivel
# Baja correlación → canasta captura shocks distintos al IPC
correlation = canasta_series.corr(ipc_series)  # Esperado: 0.85-0.95
```

## Rankings y significancia entre cadenas

```python
# Kruskal-Wallis: diferencias entre cadenas son estadísticamente significativas?
from scipy.stats import kruskal

grupos = [group['canasta_total'].values for _, group in df_branch.groupby('cadena')]
stat, p = kruskal(*grupos)
print(f"Diferencias entre cadenas: {'significativas' if p < 0.05 else 'NO significativas'} (p={p:.4f})")

# Post-hoc: Mann-Whitney para pares de cadenas
from scipy.stats import mannwhitneyu
# Usar corrección Bonferroni para comparaciones múltiples
```

## Análisis de tendencia y estacionalidad

```python
# Descomposición STL para detectar estacionalidad en la canasta
from statsmodels.tsa.seasonal import STL

stl = STL(canasta_series, period=12)
result = stl.fit()
# result.trend → tendencia subyacente
# result.seasonal → patrón estacional (¿hay efecto diciembre/enero?)
# result.resid → residuos (anomalías)
```

## Métricas clave para el informe ICM-UADE

| Métrica | Fórmula | Interpretación |
|---------|---------|---------------|
| Acumulado (base 100) | (valor_actual / valor_base - 1) × 100 | Inflación total del período |
| Variación mensual | (valor_t / valor_t-1 - 1) × 100 | Inflación del mes |
| Variación interanual | (valor_t / valor_t-12 - 1) × 100 | Inflación de los últimos 12 meses |
| Brecha vs IPC (pp) | variacion_canasta - variacion_ipc | Diferencia en puntos porcentuales |
| CV entre sucursales | σ / μ × 100 | % de dispersión de precios |
| Brecha p10-p90 | precio_p90 / precio_p10 - 1 | Diferencia entre sucursal más cara y más barata |

## Consideraciones metodológicas

1. **No comparar variaciones antes de julio 2023** — el panel SEPA estaba en consolidación
2. **Usar medianas para precios de referencia** — más robustas a outliers que medias
3. **Ponderación poblacional obligatoria** para el índice nacional (Censo 2022)
4. **Imputación solo por provincia**, nunca usar promedio de otra cadena como sustituto
5. **Factor de escala** debe verificarse en cada nuevo dataset — no asumir el del período anterior
