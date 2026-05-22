# Archivos maestros requeridos

Colocar aquí los siguientes archivos (no versionados por `.gitignore`):

| Archivo | Descripción | Tamaño aprox. |
|---------|-------------|---------------|
| `Maestro de Productos Interno.xlsx` | 176K productos con EAN, marca, rubro, categoría, proveedor | ~21 MB |
| `maestro_sucursales_completo.xlsx` | 3.6K sucursales con coordenadas (lat/lng), provincia, región | ~480 KB |
| `IPC.xlsx` | IPC INDEC mensual por división (Jan 2017 en adelante) | ~25 KB |
| `ar.json` | GeoJSON de polígonos de provincias argentinas | ~1 MB |

## Fuentes

- **Maestros SEPA**: Generados internamente o descargables desde INECO
- **IPC INDEC**: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31
- **GeoJSON Argentina**: https://github.com/deldersveld/topojson (convertir a GeoJSON)
  o buscar "argentina provinces geojson" en datos.gob.ar
