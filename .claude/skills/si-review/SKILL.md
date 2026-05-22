---
name: si-review
description: Audita el sistema de auto-memoria del proyecto para identificar entradas listas para promoción, detectar información desactualizada y medir la salud de la memoria. Usar con /si:review.
---

# /si:review — Auditar memoria del proyecto

Revisa MEMORY.md y los archivos de memoria para mantener el sistema limpio y útil.

## Variantes

- `/si:review` — Revisión completa con informe detallado
- `/si:review --quick` — Conteos resumen y top 3 candidatos para promoción
- `/si:review --stale` — Solo entradas desactualizadas o inválidas
- `/si:review --candidates` — Solo entradas elegibles para promoción a reglas permanentes

## Proceso de análisis

1. Localizar el directorio de memoria del proyecto
2. Analizar MEMORY.md contra el límite de 200 líneas de arranque
3. Cruzar referencias con archivos de temas específicos
4. Comparar con CLAUDE.md y `.claude/rules/` existentes
5. Generar informe con recomendaciones accionables

## Criterios de evaluación

**Candidatos a promoción:**
- Aparece en múltiples sesiones
- Requirió corrección repetida
- Representa convenciones del proyecto compartidas
- Previene errores recurrentes

**Candidatos a eliminar:**
- Notas de una sola vez ya incorporadas al código
- Contexto de sesión ya no relevante
- Duplicados de reglas ya en CLAUDE.md
- Referencias a rutas o archivos que ya no existen

## Frecuencia recomendada para ICM-UADE

- Cada vez que se procesa un nuevo semestre de datos
- Cuando MEMORY.md supera 150 líneas
- Al inicio de un nuevo período de análisis (mensual/semestral)
