# Memoria del proyecto — ICM-UADE / analisis_precios_minoristas_UADE

Auto-memoria del proyecto. Las primeras 200 líneas se cargan en cada sesión.
Usar `/si:remember` para agregar, `/si:review` para auditar, `/si:promote` para promover a reglas permanentes.

---

## Decisiones arquitectónicas

- El paquete Python está en `src/sepa/` — siempre hacer `sys.path.insert(0, 'src')` o instalar con `pip install -e .`
- La canasta tiene 30 EANs fijos definidos en `src/sepa/config/canasta.py` — NO modificar sin documentar la razón
- La memoria persistente del agente va en `memory/state.db` (SQLite) — NO en archivos temporales
- Los outputs publicables van en `products/` — los datos intermedios en `data/cache/` (Parquet)

## Convenciones de datos SEPA

- Los EANs deben normalizarse siempre con `.str.lstrip('0')` antes de cualquier join
- Período válido de análisis: desde 2023-05 (cobertura SEPA estable)
- Variaciones de mayo y junio 2023 se nullifican (panel en consolidación)
- El factor de escala se detecta automáticamente pero debe verificarse con los productos de referencia: Sal (7790380000057), Fideos (7792260000101), Lavandina (7790230512009)

## Cadenas excluidas del análisis

IDs excluidos: 4 (Mercado Libre), 19 (FULL), 2013 (Easy), 3001 (Farmacity), 3002 (Simplicity)

## Rutas de datos (entorno local de Santiago)

- Maestros en: `C:\Users\sriverti\Desktop\INECO\Repositorios\analisis_precios_minoristas_UADE\data\masters\`
- ZIPs semestrales en: `data/input/semestrales/`

## Semestres procesados

(Actualizar al procesar cada semestre)

## Hallazgos a recordar

- Dispersión AMBA (~5.4%) < Nacional (~12.1%) → más competencia en zona metropolitana
- DIA domina en cobertura (~990 sucursales), pero no es la más barata
- La escala de precios varió entre semestres — siempre verificar con detect_price_scale()
