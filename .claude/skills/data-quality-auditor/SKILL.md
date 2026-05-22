---
name: data-quality-auditor
description: Audita la calidad de los datos SEPA en cada etapa del pipeline. Detecta precios inválidos, EANs malformados, coordenadas fuera de rango, sucursales duplicadas y anomalías en la serie temporal. Activar al cargar nuevos datos o antes de publicar resultados.
---

# Data Quality Auditor — Pipeline SEPA / ICM-UADE

Auditoría sistemática de calidad de datos en el pipeline de precios minoristas.

## Dimensiones de calidad a verificar

### 1. Precios
- [ ] Sin valores negativos ni cero
- [ ] Sin precios < $5 (placeholders del SEPA)
- [ ] Factor de escala correcto (detect_price_scale ejecutado)
- [ ] Sin saltos de precio > 10x entre meses consecutivos para el mismo EAN+sucursal
- [ ] Cobertura diaria ≥ 50% de días del mes por archivo

### 2. EANs / Productos
- [ ] EANs normalizados (sin ceros a la izquierda)
- [ ] Los 30 EANs de la canasta presentes en el dataset
- [ ] Sin EANs de longitud anormal (< 6 dígitos o > 14 dígitos)
- [ ] Coincidencia EAN ↔ descripción consistente con el maestro de productos

### 3. Sucursales
- [ ] Coordenadas dentro de Argentina: lat [-55, -22], lng [-73, -53]
- [ ] Sin sucursales duplicadas por (id_comercio, id_bandera, id_sucursal)
- [ ] Cadenas excluidas correctamente removidas (IDs: 4, 19, 2013, 3001, 3002)
- [ ] Al menos 20 de 30 productos propios para sucursales incluidas en canasta

### 4. Cobertura temporal
- [ ] Sin brechas de más de 15 días en la serie
- [ ] Semestres procesados sin solapamiento de meses
- [ ] Verificar meses de mayo y junio 2023 (variaciones nullificadas)

### 5. Agregaciones
- [ ] Suma de pesos poblacionales ≈ 1.0 (±0.001)
- [ ] Canasta nacional dentro del rango esperado (±30% de meses adyacentes)
- [ ] Ninguna provincia con canasta = 0 o NaN en el output final

## Proceso de auditoría

```python
# Ejemplo de uso básico
from sepa.pipeline.cleaner import detect_price_scale, filter_valid_coordinates
from sepa.config.canasta import CANASTA_EANS

# 1. Verificar escala
factor = detect_price_scale(df, ean_col='ean_norm', price_col='precio_raw')
assert factor in [1, 100, 10000], f"Factor inesperado: {factor}"

# 2. Verificar cobertura de canasta
found_eans = set(df['ean_norm'].unique()) & CANASTA_EANS
missing = CANASTA_EANS - found_eans
if missing:
    print(f"ADVERTENCIA: {len(missing)} EANs de canasta no encontrados: {missing}")

# 3. Verificar coordenadas
df_valid = filter_valid_coordinates(df)
pct_invalid = (1 - len(df_valid)/len(df)) * 100
if pct_invalid > 5:
    print(f"ADVERTENCIA: {pct_invalid:.1f}% de registros con coordenadas inválidas")

# 4. Verificar rango de precios post-limpieza
assert df['precio'].min() >= 5, "Precios < $5 no eliminados"
assert df['precio'].max() < 10_000_000, "Precios anómalos detectados"
```

## Alertas críticas (detener pipeline)

🔴 **STOP si:**
- Menos de 10 de 30 EANs de canasta encontrados
- Factor de escala imposible de determinar
- > 50% de sucursales con coordenadas inválidas
- Canasta nacional > 200% del mes anterior (probable error de escala)

## Alertas de advertencia (continuar con nota)

🟡 **ADVERTIR si:**
- Entre 10 y 20 EANs de canasta encontrados
- Alguna provincia sin datos (usar imputación)
- > 20% de registros filtrados por precio < $5
- Brechas temporales > 7 días en un mes

## Reporte de calidad

Al finalizar el procesamiento de un semestre, registrar en memoria:
- Factor de escala detectado
- % de datos filtrados por cada criterio
- EANs faltantes de la canasta
- Provincias con imputación
