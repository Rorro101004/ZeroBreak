# AGENTS.md — Directrices Operativas de ZeroBreak

Ecosistema SDD para refactorizar Python sin romper contratos. Este archivo es la fuente de verdad (SSOT) de las reglas operativas; el detalle vive en `specs/`.

## Filosofía: Zero Breakage
Ninguna refactorización se persiste si rompe pruebas existentes o carece de aprobación explícita del usuario.

## Convención modular de casos de prueba
Cada caso vive aislado en `test_cases/<nombre_caso>/`, con su código y su suite de pruebas (`test_*.py`) en el mismo directorio. Se trabaja un caso a la vez con `pytest test_cases/<nombre_caso>`.

## Ciclo obligatorio (5 fases, en orden)

Flujo: Análisis → Baseline pytest → Propuesta → Verificación (sandbox) → Confirmación humana → Respaldo didáctico (`<modulo>_legacy_anotado.py`) → Aplicación en disco → pytest post.

1. **Análisis de contratos** — Leer el caso objetivo (código y su `test_*.py`). Identificar la API pública exacta (funciones, clases, firmas, excepciones, retornos). No se altera ningún nombre/firma/comportamiento observable.
2. **Baseline pytest** — Ejecutar `pytest test_cases/<nombre_caso>` sobre el caso objetivo. Debe estar 100% verde. Si falla, detenerse y avisar; no se optimiza código roto.
3. **Propuesta** — Diseñar la mejora (rendimiento, PEP 484/585, docstrings, código limpio) respetando los contratos. Sin aplicar todavía.
4. **Implementación y verificación en sandbox** — Aplicar el cambio **en memoria/sandbox** (sin escribir en disco) y re-ejecutar `pytest test_cases/<nombre_caso>`. Corregir hasta 100% verde.
5. **Confirmación y aplicación (post-aprobación)** — Presentar el diff y la justificación y esperar. **Nada se escribe de forma definitiva sin aprobación explícita.** Tras la aprobación:
   - **5.1 Respaldo didáctico** — Antes de sobrescribir el código objetivo, crear `<modulo>_legacy_anotado.py` en la carpeta del caso (p. ej. `test_cases/tienda/tienda_legacy_anotado.py`) con el código original **íntegro**, intercalado con comentarios inline que señalen cada ineficiencia/code smell, por qué penaliza el rendimiento o la mantenibilidad, y la solución técnica aplicada.
   - **5.2 Aplicación** — Sobrescribir el archivo objetivo y re-ejecutar `pytest test_cases/<nombre_caso>`.

## Respaldo didáctico (`<modulo>_legacy_anotado.py`)
- Contiene el código **original sin cambios funcionales**; solo se añaden comentarios.
- Vive en la misma carpeta del sujeto y **no es código de producción ni un test**.
- Cada comentario inline cubre: (a) el punto exacto de la ineficiencia/code smell; (b) por qué penaliza el rendimiento o la mantenibilidad; (c) la solución aplicada en la versión refactorizada.
- **Aislamiento de tests:** `pytest` no debe considerarlo ejecutable. No coincide con `test_*.py` (`python_files`) y además se excluye con `collect_ignore_glob` en `conftest.py`, evitando duplicaciones y falsos negativos.

## Flujo de Trabajo Obligatorio: Graph-First Architecture

1. **Fase 1: Exploración y Diagnóstico (Exclusivamente CodeGraph):**
   - Antes de modificar cualquier archivo o planificar cambios, es obligatorio usar las herramientas MCP de `codegraph` (`find_callers`, `find_callees`, `query_codebase`, `find_dependencies`, etc.) para mapear dependencias y entidades afectadas.
   - Queda terminantemente prohibido realizar lecturas indiscriminadas de archivos enteros (`view_file`, `cat`, búsquedas globales en texto plano) para explorar el proyecto. 
   - Si se requiere ver la implementación exacta de una función tras localizarla en el grafo, se debe usar `codegraph:read_file_content` o `codegraph:get_code_snippet` acotando los rangos de líneas estrictamente necesarios.

2. **Fase 2: Implementación y Validación (Permiso Total de Código):**
   - Se autoriza y requiere el uso normal de herramientas de edición de archivos (`write_to_file`, `replace_file_content`, etc.) tanto en código fuente (`src/`) como en pruebas (`tests/`) y documentación cuando la tarea lo exija.
   - La ejecución de suites de pruebas (`pytest`, `hypothesis`, `mutmut`) y scripts en la terminal forma parte del ciclo normal de trabajo.

3. **Transparencia Operativa y Manejo de Errores:**
   - Si una llamada a `codegraph` falla, retorna un error o detecta desincronización, el agente debe reportar el error exacto y los parámetros utilizados en lugar de saltarse el protocolo en silencio.
   - Todo informe de cambios o refactorización debe citar las entidades consultadas en el grafo que justificaron la intervención.

## Restricciones duras
- Nunca modificar firmas/nombres públicos ni las aserciones de los tests.
- Nunca sobrescribir archivos en disco sin visto bueno.
- Nunca aplicar (5.2) sin haber generado el respaldo didáctico (5.1).
- Los archivos `*_legacy_anotado.py` nunca se ejecutan como tests.
- Preferir la biblioteca estándar (`itertools`, `collections`, `functools`) sobre dependencias externas.
- Solo el cambio propuesto (sin scope creep); cambios atómicos, una mejora por ciclo.

## Fuentes de verdad
- `specs/constitution.md` — misión, alcance y stack (Python 3.12+, pytest, PEP 8/484/585).
- `specs/features/001-safe-refactor-loop.md` — entregables y criterios por fase.
- Skill `python-refactor-guard` — criterios de auditoría.
- Comando `/refactor <ruta>` — orquesta el ciclo completo.
- Subagente `refactor-guard` — auditor sin permiso de escritura.

## Trazabilidad y sincronización documental
- **Registro en `PROGRESS.md`:** Tras crear o modificar cualquier archivo, actualizar `PROGRESS.md` (fecha, archivo, resumen ≤3 líneas, resultado de `pytest`). Cada refactor deja además su `<modulo>_legacy_anotado.py` como evidencia didáctica. Al iniciar sesión, consultar primero `PROGRESS.md` antes de releer el árbol.
- **Sincronización documental obligatoria:** Cualquier tarea, subcomando o funcionalidad nueva debe actualizar automáticamente `README.md`, `README.es.md` y la sección correspondiente en `docs/` (`docs/USER_GUIDE.md`, `docs/JUNIOR_ONBOARDING.md`, `docs/architecture.md` o `docs/flow.md`) dentro del mismo ciclo de cambio. Ninguna tarea se considerará completa si el código avanza pero la documentación queda desfasada.
