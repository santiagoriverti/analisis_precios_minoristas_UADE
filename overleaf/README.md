# Informe de prensa ICM-UADE — LaTeX

Plantilla del informe mensual de prensa del **Índice de Canasta de Mercado UADE (ICM-UADE)**.  
Desarrollado por **INECO — Instituto de Economía, Universidad Argentina de la Empresa**.

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `main.tex.txt` | Documento LaTeX principal (renombrar a `main.tex` en Overleaf) |
| `bibliografia.bib.txt` | Bibliografía en formato BibTeX (renombrar a `bibliografia.bib`) |
| `figuras/` | Imágenes y gráficos generados por el pipeline Python |

## Cómo usar en Overleaf

1. Ir a [overleaf.com](https://overleaf.com) → Nuevo proyecto → Subir archivos
2. Subir `main.tex.txt` **renombrándolo** a `main.tex`
3. Subir `bibliografia.bib.txt` **renombrándolo** a `bibliografia.bib`
4. Subir toda la carpeta `figuras/` con las imágenes
5. Compilar con pdfLaTeX

> Las figuras se referencia automáticamente desde `figuras/` (configurado en `\graphicspath{{figuras/}}`).

## Figuras disponibles

| Archivo | Descripción |
|---------|-------------|
| `ranking_cadenas_nacional_042026.png` | Ranking de cadenas nacional — abril 2026 |
| `ranking_cadenas_amba_042026.png` | Ranking de cadenas AMBA — abril 2026 |
| `grafico_indices_desde_mar24.png` | Índices ICM-UADE vs. IPC INDEC desde marzo 2024 |
| `grafico_variaciones_desde_mar24.png` | Variaciones mensuales desde marzo 2024 |
| `mapa_canasta_2026-04.png` | Mapa coroplético provincial — abril 2026 |
| `cobertura_cadena.png` | Cobertura de productos por cadena |
| `cobertura_provincia.png` | Cobertura de productos por provincia |
| `matriz_intensidad.png` | Heatmap cadena × provincia (intensidad) |
| `matriz_presencia.png` | Mapa de presencia cadena × provincia |
| `logo_ineco.jpg` | Logo INECO para la portada |

## Generar figuras actualizadas

Las figuras se generan automáticamente con el pipeline Python.
Para actualizarlas con datos de un nuevo mes, correr el notebook `05_consolidacion_ipc.ipynb`
o el notebook Colab principal:

```
https://colab.research.google.com/github/santiagoriverti/analisis_precios_minoristas_UADE/blob/main/notebooks/MAPA_MES_COMPLETO.ipynb
```

Los outputs de los gráficos se guardan en `products/` y pueden copiarse a `overleaf/figuras/`.

## Correcciones pendientes al informe (identificadas en la memoria del chat original)

### 🔴 Críticas
1. Inconsistencia período Metodología — unificar a "marzo 2024 → abril 2026"
2. "base 100 en marzo de 2023" en Comparación con IPC → cambiar a "marzo de 2024"
3. Verificar variación interanual 25,7% (puede estar desactualizada)
4. Dispersión provincial "12,5%" → corregir a **12,1%** (o el valor actual)

### 🟡 Medias
5. Reordenar: primero Ranking barrios CABA, después caso Belgrano
6. Unificar "Norte Grande" vs. "NEA y NOA"
7. "ordenados de menor a mayor" → "mayor a menor" en intro tabla barrios

### 🟢 Menores
8. Unificar grafías: **ChangoMas** (no "Changomás"), **DIA** (no "Dia")
9. "estrategias comerciales agresivas" → "de descuento" (más neutral)
10. Label en gráficos: **"ICM-UADE"** (no "Canasta SEPA-UADE")
