# Checklist para mañana — ICM-UADE

> Última actualización: 2026-05-22 (sesión 2)

## ✅ Estado actual del repositorio

- **`MAPA_MES_COMPLETO.ipynb` funciona end-to-end en Colab** ✓
  - Autentica a Drive, descarga `2026.zip` (1.38 GB), extrae los CSV.GZ del mes, carga maestros desde `Archivos_de_apoyo.zip`
  - Genera mapa interactivo, ranking de cadenas, ranking provincial, ranking barrios CABA
  - Optimizado para memoria: loader lee en chunks, DataFrames grandes liberados con `del`
- Drive tiene ZIPs anuales: `2018.zip` ... `2026.zip` + `Archivos_de_apoyo.zip` (con maestros)
- `drive_manifest.json` rediseñado para ZIPs (no IDs individuales) — pendiente poblar con IDs reales
- Paper LaTeX en `overleaf/` con figuras de abril 2026
- **Todo pusheado y vigente en GitHub**

---

## 🔴 Prioridad 1 — Mejorar el Colab (cosas pendientes de la sesión de hoy)

El usuario dijo "se ejecutó bien pero hay cosas para mejorar". Preguntar al inicio de la sesión qué mejoras específicas quiere, pero los candidatos más probables son:

- **El mapa no se visualiza dentro de Colab** (solo se genera el HTML) — Folium dentro de IFrame a veces no renderiza en Colab moderno
- **Los rankings de cadenas** pueden necesitar ajuste de formato o filtro de cadenas con pocas sucursales
- **El mapa estático de provincia** (coropleta PNG) no se genera — `make_province_choropleth` requiere `ar.json` en `data/masters/` que no existe en Colab
- **Los outputs descargados** pueden necesitar nombres más claros o más archivos (ej. Excel con todos los datos)
- **Cobertura mayorista**: el ZIP contiene también archivos `MMAAAA_pais_mayoristaNOMBRE.csv.gz` que el notebook ignora (¿usarlos?)

---

## 🟡 Prioridad 2 — Poblar el manifest (desbloquea Colab sin auth)

El manifest nuevo usa IDs de ZIPs (no de CSV.GZ individuales). Cuando el Colab corre con auth, al final imprime los IDs encontrados. Copiar esos IDs a `data/drive_manifest.json`:

```json
"zips": {
  "2026.zip": {"id": "ID_QUE_IMPRIMIO_COLAB", "meses": ["2026-01","2026-02","2026-03","2026-04"]},
  ...
}
```

Luego `git add data/drive_manifest.json && git commit -m "manifest: poblar IDs de ZIPs" && git push`.
Una vez hecho, el Colab no pedirá login de Google.

---

## 🟡 Prioridad 3 — Serie temporal completa (todos los meses)

El `MAPA_MES_COMPLETO.ipynb` procesa un mes a la vez. Para la serie histórica (ICM-UADE mes a mes desde 2023) hay que:
1. Procesar cada semestre/año por separado con `analisis_SEPA_evolucion`-style code
2. Consolidar todos los outputs con `consolidacion_analisis_SEPA`-style code
3. Generar los gráficos de índices (`grafico_indices_desde_mar24.png`, `grafico_variaciones_desde_mar24.png`)

Estos gráficos son necesarios para actualizar el paper LaTeX.

---

## 🟢 Prioridad 4 — Activar GitHub Pages (publicar el mapa online)

1. Ir a: https://github.com/santiagoriverti/analisis_precios_minoristas_UADE/settings/pages
2. En "Source" → elegir **"GitHub Actions"**
3. El mapa se publica en: `https://santiagoriverti.github.io/analisis_precios_minoristas_UADE/`

---

## 🟢 Prioridad 5 — Correr el mapa de mayo 2026

Cuando salgan los datos del Ministerio:
- En Colab cambiar `MES = '2026-05'` en la celda de configuración
- El notebook buscará `2026.zip` o `2026B.zip` (si el Ministerio publica semestre B)

---

## 🟢 Prioridad 6 — Corregir el paper LaTeX

Ver `overleaf/README.md` para la lista de correcciones pendientes.
Las 4 críticas son:
- Unificar período en Metodología → "marzo 2024 → abril 2026"
- Base 100 en gráficos → "marzo de 2024" (no 2023)
- Verificar variación interanual 25,7%
- Dispersión provincial → 12,1%

---

## Estructura de datos en Drive (confirmada)

| Archivo | Contenido |
|---------|-----------|
| `2026.zip` | `012026_pais_parte[12]COMPLETO.csv.gz` ... `042026_pais_parte[12]COMPLETO.csv.gz` + archivos mayoristas |
| `2025.zip` | Meses 01–12 de 2025 |
| `2024.zip` | Meses 01–12 de 2024 |
| `2023.zip` | Meses de 2023 |
| `2021A.zip` | Meses 01–06 de 2021 |
| `2021B.zip` | Meses 07–12 de 2021 |
| `Archivos_de_apoyo.zip` | `Maestro de Productos Interno.xlsx` + `maestro_sucursales_completo.xlsx` |

---

## Arranque rápido de cada sesión

```
1. Abrir el proyecto clonado: C:\Users\santi\OneDrive\Escritorio\Repositorios\analisis_precios_minoristas_UADE
2. Leer este archivo: PARA_MANANA.md
3. Colab link: https://colab.research.google.com/github/santiagoriverti/analisis_precios_minoristas_UADE/blob/main/notebooks/MAPA_MES_COMPLETO.ipynb
```

---

## Links útiles

| Recurso | URL |
|---------|-----|
| Repositorio | https://github.com/santiagoriverti/analisis_precios_minoristas_UADE |
| Colab (mapa) | https://colab.research.google.com/github/santiagoriverti/analisis_precios_minoristas_UADE/blob/main/notebooks/MAPA_MES_COMPLETO.ipynb |
| GitHub Actions | https://github.com/santiagoriverti/analisis_precios_minoristas_UADE/actions |
| GitHub Pages | https://santiagoriverti.github.io/analisis_precios_minoristas_UADE/ (activar primero) |
| Drive SEPA 2024+ | https://drive.google.com/drive/folders/1GNs9SrZ4BIoBsviBVWYYqRcsj4dwPF-I |
| Drive SEPA histórico | https://drive.google.com/drive/folders/13GONeBs5lQCSUdBioHYk-8GhfDtIyliD |
