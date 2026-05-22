---
name: si-promote
description: Promueve patrones probados desde auto-memoria a reglas permanentes del proyecto en CLAUDE.md o .claude/rules/. Usar con /si:promote cuando un patrón aparece 3+ veces en memoria.
---

# /si:promote — Promover memoria a reglas permanentes

Convierte notas de auto-memoria en reglas permanentes del proyecto.

## Cuándo promover

Promover patrones que:
- Aparecen 3+ veces en auto-memoria
- Requirieron corrección repetida
- Representan convenciones del proyecto compartidas
- Previenen errores recurrentes

NO promover:
- Notas de una sola vez
- Contexto específico de sesión
- Reglas ya existentes en CLAUDE.md

## Proceso

1. **Parsear** el patrón — pedir aclaración si es vago
2. **Buscar** entradas relacionadas en MEMORY.md
3. **Elegir destino:**
   - Reglas globales → `CLAUDE.md`
   - Patrones específicos → `.claude/rules/[nombre].md`
4. **Destilar** a formato imperativo conciso
5. **Escribir** la regla bajo la sección apropiada
6. **Limpiar** la entrada en MEMORY.md

## Transformación de formato

De descriptivo:
> "El proyecto SEPA usa factores de escala — revisé que 2023B tiene factor=100"

A prescriptivo:
> "Siempre ejecutar detect_price_scale() antes de procesar cualquier semestre SEPA. Algunos períodos (especialmente 2023) reportan precios en centavos."

## Destinos en este proyecto (ICM-UADE)

- **CLAUDE.md** → convenciones de datos, decisiones metodológicas
- **`.claude/rules/pipeline.md`** → reglas del pipeline de datos
- **`.claude/rules/canasta.md`** → reglas de la canasta ICM-UADE
