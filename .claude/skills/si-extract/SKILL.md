---
name: si-extract
description: Extrae patrones probados de este proyecto como skills reutilizables para otros proyectos. Usar con /si:extract cuando un patrón del ICM-UADE podría ser útil en otros proyectos de análisis de datos.
---

# /si:extract — Extraer skills reutilizables

Convierte patrones específicos del proyecto en skills portables a otros proyectos.

## Cuándo extraer

Un patrón merece extracción si:
- Resuelve un problema que otros proyectos enfrentarán
- Es independiente del dominio del ICM-UADE
- Tiene al menos 2-3 usos probados en este proyecto
- Se puede encapsular limpiamente con interfaz clara

## Proceso

1. **Identificar** el patrón y su alcance
2. **Generalizar** eliminando especificidades del ICM-UADE
3. **Crear** archivo SKILL.md con frontmatter, descripción, ejemplos
4. **Testear** el skill con un ejemplo mínimo
5. **Guardar** en `~/.claude/skills/` o compartir al equipo

## Patrones candidatos en ICM-UADE

- Detección automática de factor de escala de precios → útil para cualquier sistema de precios
- Pipeline de descompresión de ZIPs anidados → útil para cualquier ingesta SEPA/gobierno
- Imputación de valores faltantes con promedio de grupo → útil para análisis de canastas
- Mapeo de coordenadas + filtro geográfico → útil para análisis de sucursales
- Construcción de coropleta con matplotlib + GeoJSON → útil para cualquier análisis geográfico

## Formato del skill extraído

```markdown
---
name: [nombre-kebab-case]
description: [qué hace, cuándo usarlo, en 1-2 oraciones]
---

# [Nombre del Skill]

[Instrucciones para Claude sobre cómo aplicar este patrón]

## Ejemplos
## Casos límite
## Referencias
```
