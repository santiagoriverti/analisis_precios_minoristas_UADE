---
name: si-remember
description: Guarda conocimiento importante del proyecto en memoria persistente con contexto y timestamp. Usar con /si:remember. Ideal para decisiones arquitectónicas, convenciones del proyecto, gotchas de herramientas, y preferencias que Claude debe recordar entre sesiones.
---

# /si:remember — Guardar en memoria del proyecto

Guarda conocimiento importante en la memoria auto-gestionada del proyecto con contexto y timestamp.

## Cuándo usar

- Insights difíciles de debuggear
- Convenciones del proyecto no documentadas en otro lugar
- Gotchas específicos de herramientas
- Decisiones arquitectónicas
- Preferencias del equipo que deben persistir entre sesiones

## Cuándo NO usar

- Contexto temporal de una sola sesión
- Reglas que ya están en CLAUDE.md o .claude/rules/ (usar /si:promote)
- Conocimiento que aplica a otros proyectos distintos
- Datos sensibles como credenciales

## Flujo de trabajo

1. **Parsear** el conocimiento: qué es, por qué importa, alcance
2. **Verificar duplicados** en MEMORY.md antes de escribir
3. **Escribir** entradas concisas de una sola línea cuando sea posible
4. **Sugerir promoción** si la entrada parece una regla que debería ser permanente
5. **Confirmar** el guardado con conteo de líneas

## Formato de memoria

Preferir concreto sobre abstracto:
- ✅ "Ejecutar con `pip install -e .` desde la raíz del proyecto"
- ❌ "El proyecto tiene un modo de instalación especial"

Si MEMORY.md supera las 180 líneas → advertir al usuario que ejecute /si:review.

## Aplicación en este proyecto (ICM-UADE)

Memoria relevante para guardar:
- Cambios en la estructura del SEPA (nuevas cadenas, cambios de formato)
- EANs que cambiaron de producto entre semestres
- Factores de escala detectados por período
- Decisiones sobre qué cadenas incluir/excluir
- Rutas de datos en el entorno del usuario
