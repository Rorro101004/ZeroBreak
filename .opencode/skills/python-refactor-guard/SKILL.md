---
name: Python Refactor Guard
description: Criterios de auditoría para validar refactorizaciones Python de ZeroBreak sin romper contratos. Úsala antes de confirmar cualquier cambio de código.
---

# Python Refactor Guard

Checklist de auditoría para validar una refactorización antes de proponerla a confirmación humana. **No modifica archivos**: solo evalúa y reporta.

## Criterios

1. **Validez sintáctica** — El código compila (`ast.parse` / `py_compile`). Sin errores de sintaxis nuevos.
2. **Tipado** — Anotaciones válidas según PEP 484 / PEP 585; genéricos nativos (`list[int]`, no `list`); sin `Any` injustificado.
3. **Equivalencia semántica** — Comportamiento observable, firmas, retornos y excepciones intactos.
4. **Compatibilidad de tests** — Toda la suite existente pasa; los archivos de test no se modifican.
5. **Estilo** — Cumple PEP 8; sin nuevos errores de linting.
6. **Guardarraíl** — Si falla cualquier criterio, se rechaza la propuesta; solo continúa con aprobación explícita del usuario.

## Salida esperada
Un informe con: resultado global (válido / rechazado), errores agrupados por criterio y advertencias no fatales.

## Uso
Invocar desde el comando `/refactor` (Fase 4) o delegar en el subagente `refactor-guard`.
