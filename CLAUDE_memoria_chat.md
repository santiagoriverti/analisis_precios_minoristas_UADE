# Proyecto ICM-UADE — Contexto completo

> Este archivo es la memoria del proyecto **Índice de Consumo Masivo UADE (ICM-UADE)** del INECO (Instituto de Economía, Universidad Argentina de la Empresa). Cargalo en Claude Code (o pegalo en una nueva conversación de Claude) para retomar el trabajo sin reexplicar nada.

---

## 1. Identidad del proyecto

- **Autor**: Santiago Riverti (INECO-UADE)
- **Objetivo**: construir un índice mensual de precios de consumo masivo a partir de los datos abiertos del SEPA (Sistema Electrónico de Publicidad de Precios Argentinos, Ministerio de Economía)
- **Producto final**: informe de prensa mensual con valor de la canasta nacional, evolución temporal, comparativa con IPC INDEC, ranking provincial, mapa por sucursal, ranking de cadenas y ranking de barrios CABA
- **Idioma**: español argentino (rioplatense). Voseo en mensajes ("usás", "tenés", "dale"). Formato numérico argentino: separador de miles con punto, decimales con coma ($314.883, +1,67%).

---

## 2. La canasta — 30 productos fijos

Distribución por categoría (con cantidad mensual de cada producto para hogar tipo 4 personas):

### Lácteos (5 productos)
- 7790742363008 — Leche entera 1L (Serenísima) — **20** unidades/mes
- 7791337007628 — Yogur 190g — **8**
- 7791337061361 — Queso Casancrem 290g — **2**
- 7793940052002 — Manteca 100g — **2**
- 7791337007253 — Cindor 1L — **4**

### Almacén (8 productos)
- 7790272001029 — Aceite girasol 1,5L — **2**
- 7790070433114 — Arroz 500g — **2**
- 7790070320285 — Fideos 500g (Favorita) — **4**
- 7792180140708 — Harina leudante 1kg — **2**
- 7792710000182 — Yerba 500g — **2**
- 7790550000157 — Café 250g — **1**
- 7790040143234 — Chocolinas 250g — **4**
- 7790072002080 — Sal fina 500g (Celusal) — **1**

### Bebidas (5 productos)
- 7790895000232 — Coca Cola lata — **8**
- 7790895067570 — Coca Sin Azúcar 2,25L — **4**
- 7798062548716 — Agua Levite 500ml — **8**
- 7793147118860 — Cerveza lata — **6**
- 7798074864675 — Vino Malbec 750ml — **2**

### Limpieza (3 productos)
- 7790132098459 — Lavandina 1L (Ayudín) — **2**
- 7791290794054 — Detergente 300ml — **2**
- 7793253003500 — Limpiador Poett 900ml — **2**

### Higiene (7 productos)
- 7791293047447 — Shampoo 400ml — **1**
- 7791293045948 — Acondicionador 340ml — **1**
- 7791293051208 — Jabón tocador 90g — **4**
- 7791293049557 — Antitranspirante — **2**
- 7891024183083 — Hilo dental — **1**
- 7790770601899 — Toallas femeninas x16 — **2**
- 7790250015840 — Papel higiénico — **2**

### Snacks (2 productos)
- 7790580327415 — Rocklets 40g — **2**
- 7790580716707 — Saladix 100g — **2**

**Total: 30 productos, 105 unidades mensuales.**

---

## 3. Mapeo verificado de cadenas (SEPA → nombres comerciales)

### Cadenas compuestas (id_comercio + id_bandera)
```python
nombres_cadenas_compuestas = {
    ('9', '1'):  'Vea',
    ('9', '2'):  'Disco',
    ('9', '3'):  'Jumbo',
    ('10', '1'): 'Carrefour',
    ('10', '2'): 'Carrefour Market',
    ('10', '3'): 'Carrefour Express',
    ('11', '2'): 'ChangoMas',
    ('11', '4'): 'Hiper ChangoMas',
    ('11', '5'): 'Mi ChangoMas',
    ('16', '1'): 'Hipermercado Libertad',
    ('16', '2'): 'Mini Libertad',
}
```

### Cadenas simples (solo id_comercio)
```python
nombres_cadenas_simples = {
    '2':  'La Anónima',
    '3':  'Cadena 3',
    '5':  'Hipermercado Misiones',
    '8':  'Cadena 8 (Córdoba)',
    '12': 'Coto',
    '13': 'Cooperativa Obrera',
    '15': 'DIA',
    '20': 'LAR',
    '21': 'Toledo',
    '23': 'Cadena 23',
    '47': 'Pasamonte',
}
```

### Cadenas a filtrar (no representativas)
```python
CADENAS_FILTRAR = ['19', '2013', '3001', '4']
# 19 = FULL/YPF (estaciones de servicio, no supermercado)
# 2013 = Mercado Libre (e-commerce)
# 3001 = Easy (ferretería/hogar)
# 4 = sucursal única no representativa
```

**Nota importante**: DORINKA SRL aparece en algunos documentos viejos pero corresponde a **ChangoMas** (Grupo De Narváez, ex-Walmart Argentina).

---

## 4. Normalización de provincias

```python
NORMALIZAR_PROVINCIA = {
    'Provincia de Buenos Aires':       'Buenos Aires',
    'Ciudad Autónoma de Buenos Aires': 'CABA',
    'Ciudad de Buenos Aires':          'CABA',
    'San juan':                        'San Juan',
    'Entre Rios':                      'Entre Ríos',
    'Cordoba':                         'Córdoba',
    'Rio Negro':                       'Río Negro',
    'Neuquen':                         'Neuquén',
    'Tucuman':                         'Tucumán',
    # Sugeridas para agregar:
    'Tierra del fuego':                'Tierra del Fuego',
    'Tierra del Fuego, Antártida e Islas del Atlántico Sur': 'Tierra del Fuego',
    'Santiago Del Estero':             'Santiago del Estero',
    'La rioja':                        'La Rioja',
    'San luis':                        'San Luis',
    'La pampa':                        'La Pampa',
    'Santa cruz':                      'Santa Cruz',
}
```

---

## 5. Ponderación nacional (Censo INDEC 2022)

```python
POBLACION_2022 = {
    'Buenos Aires':         17_523_996,
    'Córdoba':               3_840_905,
    'Santa Fe':              3_544_908,
    'CABA':                  3_121_707,
    'Mendoza':               2_043_540,
    'Tucumán':               1_731_820,
    'Salta':                 1_441_351,
    'Entre Ríos':            1_425_578,
    'Misiones':              1_278_873,
    'Corrientes':            1_212_696,
    'Chaco':                 1_129_606,
    'Santiago del Estero':   1_060_906,
    'San Juan':                822_853,
    'Jujuy':                   811_611,
    'Río Negro':               750_768,
    'Neuquén':                 710_814,
    'Formosa':                 607_419,
    'Chubut':                  592_621,
    'San Luis':                542_069,
    'Catamarca':               429_562,
    'La Rioja':                383_865,
    'La Pampa':                361_859,
    'Santa Cruz':              337_226,
    'Tierra del Fuego':        185_732,
}
# Total: 45.892.285 habitantes
```

---

## 6. Arquitectura del pipeline — tres notebooks

### Notebook 1: `analisis_SEPA_canasta_evolucion`
**Procesa 1 semestre del SEPA** (~80-90 días de datos diarios).
- Parámetro único: `SEMESTRE = "2026A"` (formato AAAA + A/B)
- Input: `{SEMESTRE}.zip` + maestros + IPC
- Output: `canasta_{SEMESTRE}_serie.xlsx` (7 hojas) + `canasta_{SEMESTRE}_long.parquet`
- Detecta automáticamente factor de precio (1/100/10000) usando sal/fideos/lavandina como referencia
- Normaliza provincias

### Notebook 2: `analisis_SEPA_consolidado`
**Consolida todos los semestres + IPC** → outputs para informe.
- Input: 9 archivos semestrales (2022A-2026A) + `IPC.xlsx` + `ar.json` GeoJSON
- Output principal: `canasta_SEPA_consolidado.xlsx` (7 hojas)
- Outputs adicionales:
  - `grafico_indices_desde_mar24.png` (índice base marzo 2024 = 100)
  - `grafico_variaciones_desde_mar24.png` (variaciones mensuales)
  - `tabla_canasta_provincias_{MES}.tex` (LaTeX listo para pegar)
  - `mapa_canasta_{MES}.png` (coroplético con flecha + inset para CABA)
- Filtra a partir de mayo 2023 (panel SEPA estable). Antes había cobertura insuficiente.
- Anula variaciones mensuales de may-23 y jun-23 (panel inestable).

### Notebook 3: `analisis_SEPA_canasta_geo`
**Procesa 1 mes del SEPA** → mapa interactivo HTML por sucursal.
- Detecta automáticamente el mes desde el nombre del archivo `MMAAAA_pais_parteN_COMPLETO.csv.gz`
- Input: archivos del mes + maestros
- Output principal: `mapa_canasta_pais_{MES}_filtros.html` (Folium con filtros por cadena/provincia/tipo)
- Outputs adicionales:
  - `ranking_cadenas_nacional_{MES}.png`
  - `ranking_cadenas_amba_{MES}.png`
- Aplica filtros: elimina sucursales **Web** y sucursales mal clasificadas como **CABA** (bounding box: lat -34.71/-34.53, lon -58.53/-58.34)
- Clasifica barrios CABA por **coordenadas** (no por nombres) usando bounding boxes de los 48 barrios

---

## 7. Resultados clave — Abril 2026 (último período procesado)

### Valor de la canasta
- **ICM-UADE nacional ponderado**: $322.566
- **Promedio nacional simple** (no ponderado): $323.289
- **Variación mensual**: +3,01%
- **Variación interanual** (vs abril 2025): ~25,7% (verificar)
- **Acumulado mar-24 a abr-26**: ICM-UADE +90,3%, IPC general +107,5%, IPC alimentos +93,4%

### Cobertura del relevamiento
- **2.369 sucursales** (después de filtros: Web + CABA mal clasificadas)
- **24 provincias**, **6 regiones**
- **477 localidades**
- **14 cadenas representativas** identificadas

### Ranking nacional de cadenas (abril 2026, más cara → más barata)
1. La Anónima — $335.213 (170 sucursales)
2. Toledo — $333.076 (28)
3. Jumbo — $331.315 (30)
4. Disco — $329.579 (69)
5. Carrefour Express — $325.608 (395)
6. ChangoMas — $325.359 (51)
7. Mi ChangoMas — $325.055 (31)
8. Vea — $324.988 (153)
9. Coto — $324.201 (119)
10. Cooperativa Obrera — $320.759 (146)
11. DIA — $320.472 (990)
12. Carrefour Market — $320.354 (83)
13. Carrefour — $317.116 (81)
14. Hipermercado Libertad — $298.914 (14)

**Dispersión nacional: 12,1%** (entre cadena más cara y más barata)

### Ranking AMBA (abril 2026)
1. Disco — $336.544 (47)
2. Toledo — $333.076 (28)
3. Jumbo — $332.734 (22)
4. Vea — $328.819 (39)
5. La Anónima — $328.224 (21)
6. Carrefour Express — $327.200 (364)
7. Coto — $324.283 (109)
8. Mi ChangoMas — $323.305 (14)
9. Carrefour Market — $322.145 (54)
10. DIA — $320.860 (866)
11. ChangoMas — $320.155 (12)
12. Carrefour — $319.523 (44)
13. Cooperativa Obrera — $319.299 (86)

**Dispersión AMBA: 5,4%** (mucho menor que nacional → más competencia)

### Ranking 47 barrios CABA (clasificados por coordenadas)
- **668 sucursales asignadas** a barrio (77% de 869 totales en CABA)
- **Top 5 más caros**: San Nicolás ($327.321 +0,90%), Belgrano ($326.332 +0,60%), Recoleta ($325.399 +0,31%), Villa del Parque ($324.978 +0,18%), Caballito ($324.846 +0,14%)
- **Top 5 más baratos**: Villa Soldati ($319.641 -1,47%), La Paternal ($320.163 -1,30%), Villa Real ($320.462 -1,21%), Villa Lugano ($320.636 -1,16%), Vélez Sársfield ($321.217 -0,98%)
- **Dispersión CABA total: 2,40%**
- Patrón geográfico claro: **sur/oeste barato vs norte/centro caro**

### Casos especiales
- **Belgrano** (búsqueda por nombre): 33 sucursales con falsos positivos (5 Carrefour Express en "Av. Belgrano" están en Boedo/Monserrat). Belgrano real ≈ 28-30 sucursales, promedio $326.332.
- **Pinamar**: 3 sucursales (Cooperativa Obrera $323.336, Toledo $326.079, Disco $337.815). Promedio $329.077.
- **Costa Atlántica completa** (66 sucursales): promedio $329.096 (+1,80% vs país). Villa Gesell $328.100, Mar del Plata $328.492, Miramar $328.623, Pinamar $329.077, Necochea $333.490.

---

## 8. Bounding boxes de barrios CABA (clasificación por coordenadas)

```python
BARRIOS_CABA_BBOX = {
    'Agronomía':           (-34.604, -34.587, -58.498, -58.476),
    'Almagro':             (-34.622, -34.598, -58.435, -58.405),
    'Balvanera':           (-34.617, -34.598, -58.418, -58.388),
    'Barracas':            (-34.661, -34.628, -58.395, -58.366),
    'Belgrano':            (-34.575, -34.547, -58.471, -58.434),
    'Boedo':               (-34.638, -34.620, -58.426, -58.408),
    'Caballito':           (-34.628, -34.602, -58.460, -58.421),
    'Chacarita':           (-34.595, -34.575, -58.470, -58.443),
    'Coghlan':             (-34.572, -34.555, -58.485, -58.469),
    'Colegiales':          (-34.580, -34.563, -58.460, -58.439),
    'Constitución':        (-34.631, -34.620, -58.395, -58.378),
    'Flores':              (-34.642, -34.615, -58.480, -58.435),
    'Floresta':            (-34.633, -34.615, -58.500, -58.479),
    'La Boca':             (-34.643, -34.620, -58.371, -58.350),
    'La Paternal':         (-34.605, -34.585, -58.475, -58.456),
    'Liniers':             (-34.652, -34.628, -58.534, -58.506),
    'Mataderos':           (-34.665, -34.641, -58.522, -58.488),
    'Monte Castro':        (-34.628, -34.610, -58.520, -58.500),
    'Monserrat':           (-34.625, -34.605, -58.391, -58.371),
    'Nueva Pompeya':       (-34.658, -34.638, -58.418, -58.396),
    'Núñez':               (-34.553, -34.532, -58.475, -58.443),
    'Palermo':             (-34.595, -34.560, -58.435, -58.398),
    'Parque Avellaneda':   (-34.660, -34.638, -58.495, -58.470),
    'Parque Chacabuco':    (-34.645, -34.625, -58.448, -58.422),
    'Parque Chas':         (-34.591, -34.578, -58.487, -58.475),
    'Parque Patricios':    (-34.652, -34.628, -58.418, -58.395),
    'Puerto Madero':       (-34.625, -34.587, -58.371, -58.349),
    'Recoleta':            (-34.598, -34.575, -58.405, -58.378),
    'Retiro':              (-34.595, -34.578, -58.388, -58.365),
    'Saavedra':            (-34.560, -34.540, -58.495, -58.467),
    'San Cristóbal':       (-34.625, -34.612, -58.408, -58.391),
    'San Nicolás':         (-34.610, -34.595, -58.395, -58.371),
    'San Telmo':           (-34.625, -34.610, -58.378, -58.365),
    'Vélez Sársfield':     (-34.642, -34.624, -58.510, -58.493),
    'Versalles':           (-34.640, -34.621, -58.525, -58.508),
    'Villa Crespo':        (-34.605, -34.585, -58.452, -58.428),
    'Villa del Parque':    (-34.615, -34.595, -58.498, -58.472),
    'Villa Devoto':        (-34.612, -34.585, -58.518, -58.490),
    'Villa General Mitre': (-34.615, -34.600, -58.475, -58.458),
    'Villa Lugano':        (-34.690, -34.660, -58.475, -58.435),
    'Villa Luro':          (-34.645, -34.628, -58.510, -58.491),
    'Villa Ortúzar':       (-34.590, -34.575, -58.475, -58.456),
    'Villa Pueyrredón':    (-34.585, -34.565, -58.510, -58.485),
    'Villa Real':          (-34.628, -34.615, -58.530, -58.512),
    'Villa Riachuelo':     (-34.695, -34.680, -58.470, -58.450),
    'Villa Santa Rita':    (-34.622, -34.605, -58.488, -58.470),
    'Villa Soldati':       (-34.682, -34.655, -58.460, -58.420),
    'Villa Urquiza':       (-34.590, -34.565, -58.495, -58.470),
}
# Formato: (lat_min, lat_max, lon_min, lon_max)
# 48 barrios (Puerto Madero a veces queda con 0-1 sucursales)
```

---

## 9. Filtros de calidad aplicados al notebook del mapa

```python
# Eliminar sucursales Web (sin ubicación física real)
canasta_geo_filtros = canasta_geo_filtros[canasta_geo_filtros['sucursales_tipo'] != 'Web'].copy()

# Eliminar sucursales mal clasificadas como CABA por coordenadas
mascara_caba_mal = (
    (canasta_geo_filtros['PROVINCIA'] == 'Ciudad Autónoma de Buenos Aires') & (
        (canasta_geo_filtros['sucursales_latitud'] < -34.71) |
        (canasta_geo_filtros['sucursales_latitud'] > -34.53) |
        (canasta_geo_filtros['sucursales_longitud'] < -58.53) |
        (canasta_geo_filtros['sucursales_longitud'] > -58.34)
    )
)
# Esto eliminó 2 sucursales en abril 2026:
# - ChangoMas Moreno Derqui (-34.5360, -58.7971)
# - DIA "Villa del Parque" (-34.0725, -58.4782) - en realidad PBA norte
```

---

## 10. Detección automática de factor de precio

El SEPA tiene precios con factor variable según el año (en algunos años divididos por 100, otros por 10000). Para detectarlo automáticamente se usan productos baratos y estables como referencia:

```python
EANS_REFERENCIA = ['7790072002080',  # Sal Celusal 500g
                   '7790070320285',  # Fideos Favorita 500g
                   '7790132098459']  # Lavandina Ayudín 1L

# Lógica:
if 30 <= mediana_ref <= 5000:
    FACTOR = 1
elif 3000 <= mediana_ref <= 500000:
    FACTOR = 100
elif mediana_ref > 500000:
    FACTOR = 10000
else:
    FACTOR = 1
```

---

## 11. Archivos del proyecto (paths en Colab)

### Inputs principales (descargados desde Google Drive/SharePoint)
- `/content/{SEMESTRE}.zip` (ej: `2026A.zip`) — paquetes semestrales SEPA
- `/content/{MMAAAA}_pais_parte1COMPLETO.csv.gz` — archivos mensuales SEPA (ej: `042026_pais_parte1COMPLETO.csv.gz`)
- `/content/{MMAAAA}_pais_parte2COMPLETO.csv.gz`
- `/content/Maestro de Productos Interno.xlsx` (176.702 filas)
- `/content/maestro_sucursales_completo.xlsx` (3.611 filas)
- `/content/IPC.xlsx` (IPC INDEC con todas las divisiones del gasto)
- `/content/ar.json` (GeoJSON 24 jurisdicciones, simplemaps.com)

### Outputs intermedios
- `/content/canasta_{SEMESTRE}_serie.xlsx` (uno por semestre, 9 en total)
- `/content/canasta_{SEMESTRE}_long.parquet`

### Outputs finales
- `/content/canasta_SEPA_consolidado.xlsx` (serie histórica completa, 7 hojas)
- `/content/grafico_indices_desde_mar24.png`
- `/content/grafico_variaciones_desde_mar24.png`
- `/content/mapa_canasta_{ULTIMO_MES}.png` (coroplético provincial)
- `/content/tabla_canasta_provincias_{ULTIMO_MES}.tex`
- `/content/mapa_canasta_pais_{MES}_filtros.html` (Folium interactivo)
- `/content/ranking_cadenas_nacional_{MES}.png`
- `/content/ranking_cadenas_amba_{MES}.png`

---

## 12. Fuentes de datos

- **SEPA**: https://datos.produccion.gob.ar/dataset/sepa-precios — Ministerio de Economía
- **2018-2023**: https://drive.google.com/drive/folders/13GONeBs5lQCSUdBioHYk-8GhfDtIyliD
- **2024-2026**: https://drive.google.com/drive/folders/1GNs9SrZ4BIoBsviBVWYYqRcsj4dwPF-I
- **Últimos meses**: SharePoint UADE (`sriverti_uade_edu_ar/Documents/bases_sepa`)
- **IPC**: INDEC
- **Censo**: INDEC 2022
- **GeoJSON 24 provincias**: simplemaps.com
- **Marco normativo SEPA**: Resolución 12/2016 de la ex Secretaría de Comercio

---

## 13. Mapa publicado (GitHub Pages)

- URL del mapa de abril 2026: `https://santiagoriverti.github.io/mapa_precios_argentina_abril2026/`
- Para publicar nuevo mes: subir el HTML a un repo nuevo (`mapa_precios_argentina_{mes}{año}`) y activar GitHub Pages

---

## 14. Pendientes y mejoras identificadas

### 🔴 Mejoras críticas a aplicar al notebook semestral (`analisis_SEPA_canasta_evolucion`)
1. Aplicar filtros Web + CABA mal clasificadas (actualmente solo están en el notebook del mapa)
2. Aplicar `CADENAS_FILTRAR = ['19', '2013', '3001', '4']` en el notebook semestral
3. Ampliar `NORMALIZAR_PROVINCIA` con las variantes adicionales sugeridas

### 🟡 Mejoras al notebook consolidado (`analisis_SEPA_consolidado`)
4. Parametrizar `MES_BASE_GRAFICOS = '2024-03'` para futuras actualizaciones (sacar de hardcoded)
5. Bajar DPI=600 a DPI=300 en los gráficos (4x más livianos)
6. Verificación cruzada validando promedio ponderado vs simple (±1-2% esperado)
7. Cambiar label "Canasta SEPA-UADE" → "ICM-UADE" en gráficos de la CELDA 8

### 🟢 Correcciones pendientes del informe LaTeX (abril 2026)
- **Críticas**:
  1. Inconsistencia período Metodología: dice "marzo 2024 → mayo 2026 (27 meses)" pero también "marzo 2023 → abril 2026 / 38 meses". Unificar a marzo 2024 → abril 2026.
  2. "base 100 en marzo de 2023" en Comparación con IPC → cambiar a "marzo de 2024".
  3. Verificar variación interanual 25,7% (parece baja).
  4. Dispersión provincial "12,5%" debería ser **12,9%**.
- **Medias**:
  5. Reordenar: primero Ranking barrios CABA, después caso Belgrano.
  6. Unificar "Norte Grande" vs "NEA y NOA".
  7. "ordenados de menor a mayor" debería ser "mayor a menor" en intro tabla barrios.
- **Menores**:
  8. Unificar grafías: "ChangoMas" (no "Changomás"), "DIA" (no "Dia").
  9. "estrategias comerciales agresivas" → "de descuento" (más neutral).

### Próximos pasos
1. Publicar informe LaTeX abril 2026 después de aplicar correcciones críticas
2. Procesar mayo 2026 cuando estén disponibles los archivos `052026_pais_parte*COMPLETO.csv.gz`
3. IPC INDEC abril 2026 (publicado ~13 mayo) — actualizar en `IPC.xlsx`
4. Aplicar mejoras al notebook semestral antes de regenerar consolidado
5. Subir notebooks a GitHub con READMEs en los tres repos
6. Mapa coroplético GeoJSON 48 barrios CABA (futuro)
7. Cruzamiento con datos socioeconómicos Censo 2022 (futuro)

---

## 15. Convenciones de código

- **Imports estándar**: `pandas as pd`, `numpy as np`, `matplotlib.pyplot as plt`, `os`, `re`, `gc`, `glob`
- **Working directory**: `/content/` (Google Colab)
- **Encoding archivos**: UTF-8
- **Separador CSV del SEPA**: coma (no pipe como dice el ANEXO II)
- **Formato fecha precios SEPA**: columnas `precio_YYYYMMDD`
- **IDs como string**: siempre `astype(str)` para `id_comercio`, `id_bandera`, `id_sucursal`
- **EAN normalizado**: `lstrip('0')` (los archivos a veces tienen ceros a la izquierda)
- **Filtro mínimo de productos**: `MIN_PRODUCTOS = 20` (de 30) para considerar una sucursal representativa
- **Filtro mínimo de cadenas para ranking**: `n_sucursales >= 10`

---

## 16. Estructura SEPA (ANEXO II - Resolución 12/2016)

El paquete SEPA contiene 3 archivos CSV en un ZIP:
- `comercio.csv`: datos del comercio y banderas (versión SEPA, última actualización)
- `sucursales.csv`: lista completa de sucursales con coordenadas, horarios, tipo (Hipermercado/Supermercado/Autoservicio/Tradicional/Web)
- `productos.csv`: lista de precios diarios por producto-sucursal

**Campos clave**:
- `id_comercio`, `id_bandera`, `id_sucursal`: identificación única
- `id_producto`: EAN/GTIN o código interno de 13 dígitos
- `sucursales_provincia`: ISO 3166-2 (ej: "AR-B" para Buenos Aires) — **NO usar este campo, usar PROVINCIA del maestro interno**
- `sucursales_tipo`: "Hipermercado" / "Supermercado" / "Autoservicio" / "Tradicional" / "Web"
- `sucursales_latitud` / `sucursales_longitud`: WGS84, 6 decimales con punto

---

## 17. Tono de comunicación

- **Español argentino**: voseo natural ("dale", "tenés", "usás", "le metés")
- **Tipografía**: bullets con `-`, negritas para énfasis, tablas simples
- **Validación incremental**: el usuario prefiere recibir cambios chicos validables paso a paso
- **Bloques copy-paste**: cuando se proponen cambios, mejor pasar el bloque completo corregido listo para pegar
- **Identificar errores por prioridad**: 🔴 crítico / 🟡 medio / 🟢 menor
- **No sobre-explicar**: el usuario sabe del proyecto, ir directo al punto

---

## 18. Contacto y atribución

- **Institución**: INECO - Instituto de Economía, Universidad Argentina de la Empresa (UADE)
- **Autor**: Santiago Riverti
- **Email**: sriverti@uade.edu.ar
- **GitHub**: github.com/santiagoriverti
