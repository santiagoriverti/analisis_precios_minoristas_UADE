# Memoria del proyecto — ICM-UADE / analisis_precios_minoristas_UADE

Auto-memoria del proyecto. Las primeras 200 líneas se cargan en cada sesión.
Usar `/si:remember` para agregar, `/si:review` para auditar, `/si:promote` para promover a reglas permanentes.

---

## Identidad del proyecto

- **Institución**: INECO — Instituto de Economía, Universidad Argentina de la Empresa (UADE)
- **Autor**: Santiago Riverti (sriverti@uade.edu.ar)
- **Producto**: ICM-UADE (Índice de Canasta de Mercado) — informe mensual de prensa
- **GitHub**: github.com/santiagoriverti/analisis_precios_minoristas_UADE
- **Idioma de comunicación**: español argentino rioplatense (voseo)
- **Tipografía numérica**: punto = miles, coma = decimales ($322.566, +3,01%)

## Convenciones de código

- IDs (id_comercio, id_bandera, id_sucursal) siempre como string en los CSVs del SEPA → convertir a Int32 en enricher
- EANs: siempre normalizar con `.str.lstrip('0')` antes de cualquier join
- Separador CSV: PIPE `|` en ZIPs diarios, COMA `,` en .csv.gz mensuales — el loader detecta automáticamente
- Encoding: UTF-8 primera opción, latin-1 como fallback
- Período válido: desde `2023-05` (cobertura SEPA estable)
- Variaciones de `2023-05` y `2023-06` se anulan (`NULL_VARIATION_MONTHS`)

## Canasta — 30 EANs verificados

Los EANs correctos están en `src/sepa/config/canasta.py`. Los principales:
- Sal Celusal 500g: 7790072002080 (referencia para detección de escala)
- Fideos Favorita 500g: 7790070320285 (referencia)
- Lavandina Ayudín 1L: 7790132098459 (referencia)
- Leche Serenísima 1L: 7790742363008
- Coca Cola lata: 7790895000232

## Cadenas y filtros

**Excluidas del análisis** (IDs): 4, 19 (YPF/FULL), 2013 (Mercado Libre), 3001 (Easy)
**Sucursales Web**: excluir (`sucursales_tipo == 'Web'`)
**CABA mal clasificadas**: excluir coordenadas fuera de lat[-34.71,-34.53] lon[-58.53,-58.34]

**Bandera IDs de ChangoMas** (verificado): (11,2)=ChangoMas, (11,4)=Hiper ChangoMas, (11,5)=Mi ChangoMas
**Hipermercado Libertad**: (16,1)=Hipermercado Libertad, (16,2)=Mini Libertad

## Detección de escala de precios

Usar medianas de Sal + Fideos + Lavandina:
- 30–5.000 → factor=1 (precios ya en pesos)
- 3.000–500.000 → factor=100 (dividir por 100)
- >500.000 → factor=10.000 (dividir por 10.000)

## Ponderación nacional (Censo INDEC 2022)

Buenos Aires 17.523.996, Córdoba 3.840.905, Santa Fe 3.544.908, CABA 3.121.707
Total: 45.892.285 habitantes. Ver `src/sepa/config/settings.py:POPULATION_WEIGHTS`

## Barrios CABA

48 barrios con bounding boxes en `src/sepa/config/geo.py:BARRIOS_CABA_BBOX`.
Clasificar por coordenadas GPS, NO por nombre de sucursal (evita falsos positivos).
Caso Belgrano: 33 sucursales por nombre vs. ~28-30 por coordenadas (5 falsos positivos en Boedo).

## Resultados de referencia — Abril 2026

- ICM-UADE nacional ponderado: $322.566 (+3,01% mensual)
- 2.369 sucursales, 24 provincias, 477 localidades, 14 cadenas
- Más barata: Hipermercado Libertad ($298.914)
- Más cara: La Anónima ($335.213)
- Dispersión nacional: 12,1% | Dispersión AMBA: 5,4%

## Fuentes de datos SEPA

- Portal oficial: https://datos.produccion.gob.ar/dataset/sepa-precios
- 2018-2023: Google Drive https://drive.google.com/drive/folders/13GONeBs5lQCSUdBioHYk-8GhfDtIyliD
- 2024-2026: Google Drive https://drive.google.com/drive/folders/1GNs9SrZ4BIoBsviBVWYYqRcsj4dwPF-I
- IPC INDEC: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31

## Pendientes del proyecto (al 22-05-2026)

- Procesar mayo 2026 cuando estén disponibles los archivos `052026_pais_parte*COMPLETO.csv.gz`
- IPC INDEC abril 2026 (publicado ~13 mayo) — actualizar en `data/masters/IPC.xlsx`
- Mapa coroplético GeoJSON 48 barrios CABA (mejora futura)
- Cruzamiento con datos socioeconómicos Censo 2022 (futuro)
