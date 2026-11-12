# Feature 001: Safe Refactor Loop

## Estado
Vigente

## Objetivo
Definir un ciclo determinista de refactorización Python que garantice cero regresiones funcionales. Las reglas operativas y los estándares viven en `AGENTS.md` y `specs/constitution.md`; este documento detalla los entregables y criterios de cada fase.

## Flujo
Análisis → Baseline pytest → Propuesta → Verificación (sandbox) → Confirmación humana → Respaldo didáctico → Aplicación en disco → pytest post.

## Convención modular
Cada caso de prueba es un directorio aislado `test_cases/<nombre_caso>/` que contiene el código bajo prueba y su suite `test_*.py`. Los casos no comparten módulos ni estado; el ciclo se ejecuta sobre un caso a la vez, con `pytest test_cases/<nombre_caso>`.

## Fases y entregables

### Fase 1 — Análisis de contratos
- **Entrada:** código del caso y su `test_*.py` asociado.
- **Salida:** inventario de la API pública (funciones, clases, firmas, excepciones, retornos) y hallazgos (cuellos de botella, antipatrones, carencias de tipado).

### Fase 2 — Baseline pytest
- **Comando:** `pytest test_cases/<nombre_caso>` (resuelto dinámicamente desde el objetivo; si no se especifica, listar los subdirectorios de `test_cases/`).
- **Criterio de salida:** 100% verde. Si no, detener y notificar. No se refactoriza código roto.

### Fase 3 — Propuesta
- **Salida:** diff propuesto + justificación técnica + referencias a `specs/constitution.md`.
- **Criterio:** contratos intactos; sin dependencias externas; cumplimiento PEP 8 / 484 / 585.

### Fase 4 — Implementación y verificación en sandbox
- **Acción:** aplicar el cambio **en memoria/sandbox** (sin escribir en disco) y re-ejecutar `pytest test_cases/<nombre_caso>`.
- **Criterio:** bucle de corrección hasta 100% verde, todavía sin persistir.

### Fase 5 — Confirmación y aplicación
- **5.0 Confirmación:** presentar diff detallado + logs de `pytest`; esperar aprobación explícita. **Nada se persiste antes.**
- **5.1 Respaldo didáctico:** antes de sobrescribir, crear `<modulo>_legacy_anotado.py` en la carpeta del caso con el código original íntegro, intercalado con comentarios inline que indiquen: (a) el punto exacto de la ineficiencia/code smell; (b) por qué penaliza el rendimiento o la mantenibilidad; (c) la solución aplicada.
- **5.2 Aplicación:** sobrescribir el archivo objetivo y re-ejecutar `pytest test_cases/<nombre_caso>`.
- **Criterio de cierre:** aprobación explícita + respaldo creado + suite en verde.

## Respaldo didáctico (`<modulo>_legacy_anotado.py`)
- **Contenido:** código original sin cambios funcionales; solo comentarios añadidos.
- **Ubicación:** misma carpeta del sujeto (p. ej. `test_cases/tienda/tienda_legacy_anotado.py`).
- **Propósito:** material didáctico y evidencia de trazabilidad del cambio.
- **Aislamiento de tests:** nunca se ejecuta con `pytest`; no coincide con `test_*.py` (`python_files`) y se excluye con `collect_ignore_glob` en `conftest.py`, evitando duplicaciones y falsos negativos.

## Restricciones
- **Zero Breakage:** si un test falla en Fase 4 o 5.2, revertir al estado de Fase 2.
- **Respaldo obligatorio:** no aplicar (5.2) sin haber generado el respaldo (5.1).
- **Sin scope creep:** solo el cambio propuesto en Fase 3.
- **Cambios atómicos:** una mejora por ciclo para minimizar el riesgo.

## Trazabilidad
Registrar cada ciclo en `PROGRESS.md` con fecha, archivos afectados (incluido el `_legacy_anotado.py`), resumen ≤3 líneas y resultado de `pytest`.
