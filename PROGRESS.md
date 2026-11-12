# Registro de Progreso y Cambios - CorrectorCode

## Estado Actual
- [x] Inicialización de arquitectura SDD y guardarraíles.
- [x] Reestructuración para eficiencia de contexto y SDD funcional.
- [x] Fase 1: Refactorización segura de `calculadora.py`.
- [x] Reorganización modular de `test_cases/` (antes `sujeto_prueba/`) en casos aislados.
- [x] Refactor seguro de `test_cases/tienda/tienda.py` completado (respaldado con `tienda_legacy_anotado.py`).
- [x] Fase 5 con respaldo didáctico (`<modulo>_legacy_anotado.py`) y aislamiento de tests.
- [x] Preparación para publicación (licencia MIT, CI, README bilingüe, renombres).
- [x] CLI mecánica, medición (cobertura/radon/benchmark) y CI multi-job.
- [x] Documentación técnica interna (`docs/architecture.md`).
- [x] Diagrama de flujo en SVG (`docs/assets/flow.svg`, incrustado en `docs/flow.md`).
- [ ] Caso de práctica `inventario` listo para ejecutar el flujo en vivo (restaurado al estado pre-refactor para el laboratorio de onboarding).
- [x] Comando orquestador `correctorcode run` (baseline + respaldo + apply en un paso).
- [x] Puertas de calidad deterministas (`ruff` + `mypy`) en la CI.
- [x] `correctorcode run --lint` (lint opcional de la propuesta).
- [x] Verificador determinista de contratos públicos (`contracts.py` con `ast`) y escritura atómica (`os.replace`).
- [x] Scaffolding de nuevos casos (`correctorcode new <caso>`).
- [x] Comparativa de métricas estáticas en la previsualización de `run` (`metrics.py`).
- [x] Banco de pruebas de rendimiento integrado (`correctorcode bench <caso>`).
- [x] Modo Archivo Libre fuera de test_cases/ (`correctorcode run --target`).
- [x] Integración de servidor MCP CodeGraph en .venv y regla Graph-First.
- [x] Guías de Usuario y Onboarding Junior (`docs/USER_GUIDE.md`, `docs/JUNIOR_ONBOARDING.md`) y política de sincronización documental.
- [x] Scaffolding de tests Golden Master y Testing Diferencial con Hypothesis (`testgen.py`).
- [x] Directriz permanente de "Graph-First Development" (Fase 1: CodeGraph, Fase 2: Implementación, Transparencia Operativa).
- [x] Auditoría pre-publicación: limpieza de rutas absolutas y enriquecimiento de stack tecnológico en documentación pública.
- [x] Renombrado integral del framework a ZeroBreak (paquete zerobreak, CLI, suite y documentación sincrónica).

## Historial de Tareas

> **Nota histórica:** En las Tareas 002 a 007 el directorio de casos se denominaba `sujeto_prueba/`; en la Tarea 008 fue renombrado de forma definitiva a `test_cases/`.

### Tarea 001: Inicialización
- **Fecha:** 2026-09-28
- **Archivos creados:** `specs/`, `.agents/skills/`, `.opencode/commands/`, `README.md`.
- **Estado de tests:** Base lista para ejecución.

### Tarea 002: Reestructuración SDD y optimización de contexto
- **Fecha:** 2026-09-29
- **Cambios:** SSOT en `AGENTS.md` + `specs/constitution.md` (fusiona mission/stack); skill movida a `.opencode/skills/python-refactor-guard/SKILL.md` (descubrible); `/refactor` como prompt real; nuevo subagente `refactor-guard`; `opencode.json` (edit `ask`), `pyproject.toml`, `.gitignore`; carpeta `sujeto de prueba` → `sujeto_prueba`.
- **Estado de tests:** 5 passed (0.01s) con `configfile: pyproject.toml` y `testpaths: sujeto_prueba`.
- **Pendiente:** `git init` no ejecutado (git no está instalado en el entorno); `.gitignore` ya está listo.

### Tarea 003: Refactorización segura de `calculadora_lenta.py`
- **Fecha:** 2026-09-29
- **Archivo:** `sujeto_prueba/calculadora_lenta.py`
- **Cambios:** añadidos docstrings (Google Style) y tipado PEP 484/604 (`int | float`, retorno `float` en `dividir`); sin cambios de lógica ni de contratos públicos.
- **Estado de tests:** 5 passed (0.02s) — baseline y post-cambio verdes.

### Tarea 004: Reorganización modular de `sujeto_prueba/`
- **Fecha:** 2026-09-29
- **Cambios:** creado caso aislado `sujeto_prueba/calculadora/` y movidos `calculadora_lenta.py` + `test_calculadora.py`; sin cambios en las importaciones (pytest inyecta el directorio del test). `/refactor` ahora resuelve la ruta de baseline dinámicamente desde `$ARGUMENTS`; `AGENTS.md`, `specs/features/001-…md` y `README.md` documentan la convención `sujeto_prueba/<caso>/`.
- **Estado de tests:** 5 passed (0.02s) con `pytest sujeto_prueba/calculadora` y con recolección global `pytest`.

### Tarea 005: Nuevo caso modular `tienda`
- **Fecha:** 2026-10-01
- **Archivos:** `sujeto_prueba/tienda/tienda.py`, `sujeto_prueba/tienda/test_tienda.py`
- **Cambios:** alta de un caso aislado con código deliberadamente sin optimizar (duplicados O(n²) con `.count()`, iteración redundante por categoría, concatenación de strings con `+=`, sin tipado ni docstrings completos) y suite de 13 tests (totales, duplicados, formato de recibo y carrito vacío).
- **Estado de tests:** 13 passed (0.03s) — baseline verde; refactor pendiente de propuesta.

### Tarea 006: Respaldo didáctico y aislamiento de tests (Fase 5)
- **Fecha:** 2026-10-01
- **Archivos:** `AGENTS.md`, `specs/features/001-safe-refactor-loop.md`, `.opencode/commands/refactor.md`, `README.md`, `pyproject.toml`, `conftest.py` (nuevo).
- **Cambios:** nueva regla 5.1 (crear `<modulo>_legacy_anotado.py` anotado antes de aplicar) y 5.2 (aplicar); diagrama de flujo y checklist actualizados; aislamiento de `*_legacy_anotado.py` con `collect_ignore_glob` en `conftest.py` (se descartó la opción inexistente en `pyproject.toml`, que emitía warning).
- **Estado de tests:** 18 passed (0.03s); verificado que un archivo `*_legacy_anotado.py` no se recolecta.

### Tarea 007: Refactor seguro de `tienda.py` (ciclo completo)
- **Fecha:** 2026-10-01
- **Archivos:** `sujeto_prueba/tienda/tienda.py` (refactorizado), `sujeto_prueba/tienda/tienda_legacy_anotado.py` (respaldo didáctico nuevo).
- **Cambios:** duplicados O(n²)→O(n) con `Counter`; recibo con `"".join(...)`; totales con `sum(generator)`; tipado PEP 484/589/604 (`Producto` TypedDict) y docstrings Google. Sin cambios de contratos públicos.
- **Estado de tests:** baseline 13 passed → post-cambio 13 passed (tienda) y 18 passed (global); el `_legacy_anotado.py` no se recolecta.

### Tarea 008: Preparación para publicación en GitHub
- **Fecha:** 2026-10-02
- **Archivos:** `LICENSE` (MIT), `.github/workflows/tests.yml` (CI), `README.md` (EN) + `README.es.md` (ES), `CONTRIBUTING.md` + `CONTRIBUTING.es.md`, `pyproject.toml`, `opencode.json`, `.vscode/settings.json`, `AGENTS.md`, `specs/features/001-…md`, `.opencode/commands/refactor.md`.
- **Cambios:** renombrados `sujeto_prueba/` → `test_cases/` y `calculadora_lenta.py` → `calculadora.py` (clase `CalculadoraLenta` → `Calculadora`); retro-respaldo `calculadora_legacy_anotado.py`; README/CONTRIBUTING bilingües; licencia MIT; CI que ejecuta `pytest` en push/PR. Las entradas históricas de este log conservan los nombres antiguos a propósito.
- **Estado de tests:** 18 passed (global) tras los renombres.

### Tarea 009: CLI mecánica, medición y CI
- **Fecha:** 2026-10-02
- **Archivos:** `src/correctorcode/` (paquete nuevo), `tests/` (tests del framework), `scripts/benchmark.py`, `docs/benchmarks.md`, `pyproject.toml`, `.github/workflows/tests.yml`, `README*.md`, `CONTRIBUTING*.md`, `.gitignore`.
- **Cambios:** CLI `correctorcode` (`cases`/`baseline`/`verify`/`snapshot`/`apply` con rollback automático/`status`); cobertura y `radon` integrados; CI con jobs de tests (matriz Ubuntu+Windows, py3.12/3.13), cobertura (≥90%) y complejidad; benchmark honesto (duplicados O(n²)→O(n) medido; el recibo no muestra mejora medible por la optimización in-place de CPython).
- **Estado de tests:** 48 passed; cobertura 95%; `radon cc` sin bloques C o peores; benchmark reproducible.

### Tarea 010: Documentación técnica interna (`docs/architecture.md`)
- **Fecha:** 2026-10-03
- **Archivos:** `docs/architecture.md` (nuevo), `README.md` y `README.es.md` (enlace añadido).
- **Cambios:** análisis archivo por archivo del paquete (propósito, responsabilidad única, imports y el porqué de cada uno); desglose de funciones con firma/tipos PEP 484/604, mecanismo paso a paso y guardas; resumen de guardas y flujo determinista de `correctorcode apply`.
- **Estado de tests:** 48 passed (los cambios son solo de documentación).

### Tarea 011: Diagrama Mermaid del flujo (`docs/flow.md`)
- **Fecha:** 2026-10-05
- **Archivos:** `docs/flow.md` (nuevo), `README.md` y `README.es.md` (enlaces + fila en la tabla de estructura).
- **Cambios:** diagrama Mermaid de dos capas (ciclo SDD conceptual + ruta mecánica de `correctorcode apply`) con guardas, punto único de escritura, respaldo y rollback; incluye "cómo leerlo" y lista de garantías. Generado con el subagente `explore` y validado contra el código.
- **Estado de tests:** 48 passed (solo documentación).

### Tarea 012: Diagrama Mermaid en dos bloques legibles
- **Fecha:** 2026-10-05
- **Archivos:** `docs/flow.md`.
- **Cambios:** dividido en dos bloques Mermaid secuenciales (conceptual y mecánico) para que cada uno renderice grande; directiva `%%{init: ...}%%` con `fontSize: 16px` al inicio de cada bloque; se conservan la leyenda de colores, una tabla de sincronización con `architecture.md` y las garantías.
- **Estado de tests:** 48 passed (solo documentación).

### Tarea 013: Reversión de `docs/flow.md` a la versión de la Tarea 011
- **Fecha:** 2026-10-05
- **Archivos:** `docs/flow.md`.
- **Cambios:** revertido a un único bloque Mermaid con las dos capas (SDD + CLI) en columnas, sin directiva `init`; se conservan leyenda, sección "cómo leerlo", garantías y enlace a `architecture.md`. La Tarea 012 se mantiene como historial.
- **Estado de tests:** 48 passed (solo documentación).

### Tarea 014: Diagrama SVG dark mode y comparativa en `docs/flow.md`
- **Fecha:** 2026-10-05
- **Archivos:** `docs/assets/flow.svg` (nuevo), `docs/flow.md` (referencia de imagen al inicio).
- **Cambios:** SVG vectorial dark mode (fondo `#0d1117`, bordes `#30363d`, acentos verde/azul/amarillo/rojo) con el ciclo SDD de 5 fases y las guardas del guardarraíl; en `docs/flow.md` se añade `![Flujo de CorrectorCode](assets/flow.svg)` como primera línea. El bloque Mermaid se conserva **intacto** para poder comparar ambas versiones.
- **Estado de tests:** 48 passed (solo documentación).

### Tarea 015: Chips Sí/No explícitos en las decisiones del SVG
- **Fecha:** 2026-10-05
- **Archivos:** `docs/assets/flow.svg`.
- **Cambios:** en las 3 tarjetas de decisión se sustituye la nota única `No ▸ …` por **dos chips** explícitos (`Sí ▸ continuar`/`Sí ▸ cerrar` en verde `#238636`, y `No ▸ detener`/`esperar`/`rollback` en rojo `#da3633`), con texto claro sobre fondo tintado. Se mantienen paleta, fuentes (13px), tamaños y márgenes; XML revalidado.
- **Estado de tests:** 48 passed (solo documentación).

### Tarea 016: Tarjeta de validaciones de seguridad más clara en el SVG
- **Fecha:** 2026-10-05
- **Archivos:** `docs/assets/flow.svg`.
- **Cambios:** retitulada la tarjeta de guardas a "Validaciones de seguridad (antes de tocar disco)" (en dos líneas para no desbordar el panel); simplificados los 3 puntos ("Archivo propuesto existe", "Baseline original en verde", "Archivo no fue alterado (SHA-256 idéntico)"); y separado el rollback con una divisoria + subtítulo "Post-escritura" + aclaración "Rollback automático si pytest sale en rojo". Misma estética y tipografía.
- **Estado de tests:** 48 passed (solo documentación).

### Tarea 017: `docs/flow.md` finalizado con el SVG
- **Fecha:** 2026-10-05
- **Archivos:** `docs/flow.md`, `README.md`, `README.es.md`, `PROGRESS.md`.
- **Cambios:** eliminados los bloques ```mermaid; el diagrama queda incrustado arriba como `![Flujo y guardas de CorrectorCode](assets/flow.svg)`. Se conserva el texto explicativo, se añaden tablas (leyenda de colores y sincronización con `architecture.md`) y se mantienen las garantías. Actualizadas las descripciones de `docs/flow.md` en los README (ya no es Mermaid).
- **Estado de tests:** 48 passed (solo documentación).

### Tarea 018: Suite unitaria por módulo del framework
- **Fecha:** 2026-10-05
- **Archivos:** `tests/test_cases.py` (renombra `test_discovery.py`), `tests/test_state.py` (nuevo), `tests/test_runner.py` (nuevo), `tests/test_backup.py` (ampliado).
- **Cambios:** tests por módulo con `tmp_path` (sin tocar el repo): `cases` (`find_root`/`list_cases`/`resolve_case`, incluida la excepción con casos disponibles), `state` (`sha256_file` y detección de cambio de byte, `load_state` con esqueleto, `save`/`load` roundtrip, `record_baseline`), `backup` (`legacy_path`, idempotencia) y `runner` (subproceso pytest en verde y en rojo). Se conservan `test_apply.py` y `test_cli.py`.
- **Estado de tests:** 42 passed en `tests/`; 60 passed global; cobertura 95%.

### Tarea 019: Caso de práctica `inventario` + propuestas
- **Fecha:** 2026-10-05
- **Archivos:** `test_cases/inventario/inventario.py`, `test_cases/inventario/test_inventario.py`, `propuestas/inventario_mejorado.py`, `propuestas/inventario_roto.py`.
- **Cambios:** nuevo caso modular con smells deliberados (O(n²) y `+=`) y 6 tests; dos propuestas para demostrar el flujo en vivo (aplicación con `--yes` y rollback). **No** se ejecutó el CLI (`baseline`/`apply`) todavía: queda para ejecución en vivo.
- **Estado de tests:** 6 passed en `test_cases/inventario`; la propuesta mejorada pasa la suite en sandbox (6 passed).

### Tarea 020: Comando orquestador `correctorcode run`
- **Fecha:** 2026-10-05
- **Archivos:** `src/correctorcode/cases.py` (`resolve_module`), `src/correctorcode/cli.py` (`_cmd_run` + subcomando `run`), `tests/test_cases.py`, `tests/test_cli.py`, `README.md`, `README.es.md`, `docs/architecture.md`.
- **Cambios:** nuevo `correctorcode run <caso> [--module] [--source] [--yes]` que **autodetecta el módulo** (único, o `<caso>.py` por convención), registra el baseline, crea el respaldo didáctico y, si se pasa `--source`, valida las guardas y aplica con rollback. Los subcomandos existentes quedan intactos.
- **Estado de tests:** 81 passed; cobertura 99% (`cli.py` y `cases.py` al 100%).

### Tarea 021: Cobertura al 100%
- **Fecha:** 2026-10-05
- **Archivos:** `tests/test_apply.py`, `README.md`, `README.es.md`.
- **Cambios:** nuevo test que llama a `apply()` **directamente en estado inválido** para cubrir la guarda defensiva `apply.py:90` (el `return check` cuando `plan_apply` falla y el flujo normal de la CLI nunca alcanza); READMEs actualizados a cobertura 100%.
- **Estado de tests:** 82 passed; cobertura **100%** en todos los módulos.

### Tarea 022: `run` interactivo con autodescubrimiento de propuesta
- **Fecha:** 2026-10-05
- **Archivos:** `src/correctorcode/cli.py`, `tests/test_cli.py`, `README.md`, `README.es.md`, `docs/architecture.md`.
- **Cambios:** `run` ahora **autodescubre la propuesta** (`propuestas/<caso>_mejorado.py`, luego `propuestas/<caso>.py`), muestra el diff y hace una **pausa interactiva** (Enter/y aplica · n cancela · entrada no interactiva o Ctrl-C cancela). Al cancelar **descarta el respaldo recién creado** y no toca el módulo. `--yes` omite la pregunta (CI/scripts). Los subcomandos granulares quedan intactos.
- **Estado de tests:** 89 passed; cobertura **100%**.

### Tarea 023: Puertas de calidad deterministas (`ruff` + `mypy`) en la CI
- **Fecha:** 2026-10-05
- **Archivos:** `pyproject.toml`, `.github/workflows/tests.yml`, `docs/architecture.md`, `README.md`, `README.es.md`.
- **Cambios:** añadidos `ruff` y `mypy` a las dev-dependencies y configurados (`[tool.ruff]`, `[tool.mypy]`); el job `quality` de la CI ahora corre `ruff check src tests` + `mypy src` + `radon cc -n C`. Documentada la separación de capas (CLI mecánico · herramientas deterministas · agente LLM) en `architecture.md` §6.
- **Estado de tests:** 89 passed. Nota honesta: `ruff`/`mypy` **no** pudieron ejecutarse en local (la política de Control de aplicaciones de Windows bloquea los `.exe`/`.pyd` nuevos); se verificó el mismo subconjunto con `pyflakes`/`pycodestyle` (limpio). La verificación definitiva la hará la CI.

### Tarea 024: `run --lint` (lint opcional de la propuesta)
- **Fecha:** 2026-10-05
- **Archivos:** `src/correctorcode/lint.py` (nuevo), `src/correctorcode/cli.py`, `tests/test_lint.py` (nuevo), `tests/test_cli.py`, `README.md`, `README.es.md`, `docs/architecture.md`.
- **Cambios:** flag `--lint` en `run` que ejecuta `ruff`/`mypy` sobre la propuesta **si están disponibles** (detección por `--version`; los crashes de la herramienta se clasifican como "no disponible", no como hallazgo). Con hallazgos reales **no aplica** (`return 1`); si faltan las herramientas, **avisa y continúa**. Sin dependencias nuevas en runtime.
- **Estado de tests:** 100 passed; cobertura **100%**.

### Tarea 025: Cuaderno de aprendizaje (`docs/aprendizaje.md`)
- **Fecha:** 2026-10-05
- **Archivos:** `docs/aprendizaje.md` (nuevo), `PROGRESS.md`.
- **Cambios:** documento para *comprender* el código (diagnóstico de propiedad, reglas, hoja de ruta por módulo y ejercicios). No es código de producción; sesión 1 (`backup.py`) en curso.
- **Estado de tests:** no aplica (solo documentación; sin cambios de código).

### Tarea 026: Verificación determinista de contratos públicos (`ast`) y escritura atómica
- **Fecha:** 2026-10-16
- **Archivos:** `src/correctorcode/contracts.py` (nuevo), `src/correctorcode/apply.py`, `tests/test_contracts.py` (nuevo), `tests/test_apply.py`, `docs/architecture.md`, `PROGRESS.md`.
- **Cambios:** nuevo módulo `contracts.py` que extrae firmas públicas con `ast.parse` y detecta símbolos eliminados, parámetros alterados o errores de sintaxis; integrado como 4.ª guarda en `plan_apply`; reemplazo de escrituras por `_atomic_write_bytes` (`os.replace`) en `apply.py`.
- **Estado de tests:** 106 passed; cobertura **100%** (líneas y ramas).

### Tarea 027: Scaffolding de nuevos casos (`correctorcode new <caso>`)
- **Fecha:** 2026-10-17
- **Archivos:** `src/correctorcode/scaffold.py` (nuevo), `src/correctorcode/cli.py`, `tests/test_scaffold.py` (nuevo), `tests/test_cli.py`, `docs/architecture.md`, `README.md`, `README.es.md`, `PROGRESS.md`.
- **Cambios:** nuevo comando `correctorcode new <caso>` que valida identificadores y genera la estructura de carpetas y plantillas funcionales (`<caso>.py`, `test_<caso>.py` y `propuestas/<caso>_mejorado.py`) con baseline verde inmediato.
- **Estado de tests:** 114 passed; cobertura **100%** (líneas y ramas).

### Tarea 028: Comparativa de métricas estáticas en la previsualización de `run`
- **Fecha:** 2026-10-17
- **Archivos:** `src/correctorcode/metrics.py` (nuevo), `src/correctorcode/cli.py`, `tests/test_metrics.py` (nuevo), `docs/architecture.md`, `PROGRESS.md`.
- **Cambios:** nuevo módulo `metrics.py` que calcula SLOC, símbolos públicos, funciones tipadas y docstrings antes y después del cambio; integrado en `_cmd_run` para mostrar el impacto visual del refactor antes de confirmar.
- **Estado de tests:** 116 passed; cobertura **100%** (líneas y ramas).

### Tarea 029: Banco de pruebas de rendimiento integrado (`correctorcode bench <caso>`)
- **Fecha:** 2026-10-17
- **Archivos:** `src/correctorcode/bench.py` (nuevo), `src/correctorcode/cases.py`, `src/correctorcode/cli.py`, `test_cases/tienda/bench_tienda.py` (nuevo), `tests/test_bench.py` (nuevo), `tests/test_cases.py`, `docs/architecture.md`, `README.md`, `README.es.md`, `PROGRESS.md`.
- **Cambios:** nuevo módulo `bench.py` y subcomando `correctorcode bench` que compara con `timeit` el respaldo legacy (`*_legacy_anotado.py`) frente a la versión actual según los escenarios de `bench_<caso>.py`; `cases.py` excluye `bench_*.py` de los módulos de implementación.
- **Estado de tests:** 127 passed; cobertura **100%** (líneas y ramas).

### Tarea 030: Modo Archivo Libre (`--target` y `--tests`)
- **Fecha:** 2026-10-17
- **Archivos:** `src/correctorcode/cases.py`, `src/correctorcode/apply.py`, `src/correctorcode/cli.py`, `tests/test_cases.py`, `tests/test_cli.py`, `docs/architecture.md`, `README.md`, `README.es.md`, `PROGRESS.md`.
- **Cambios:** soporte para ejecutar `correctorcode run` sobre cualquier archivo Python fuera de `test_cases/` mediante `--target <archivo.py>` y `--tests <suite.py>`; autodetección de tests compañeros (`test_<archivo>.py`); desacoplamiento de la ruta de tests respecto a la raíz del caso (`case.test_path`); suite de tests completa y documentación técnica.
- **Estado de tests:** 132 passed; cobertura **100%** (líneas y ramas).

### Tarea 031: Integración de servidor MCP CodeGraph y regla Graph-First
- **Fecha:** 2026-10-17
- **Archivos:** `opencode.json`, `~/.gemini/config/mcp_config.json`, `AGENTS.md`, `.gitignore`, `PROGRESS.md`.
- **Cambios:** instalación aislada de `codegraph-mcp-server` en el `.venv` del proyecto; configuración del servidor MCP `codegraph` en `opencode.json` y en la configuración global de Antigravity (`mcp_config.json`); inclusión de `.codegraph/` en `.gitignore`; nueva directriz operativa "Exploración de código (Graph-First)" en `AGENTS.md` para priorizar la navegación por AST sobre lecturas completas de archivos.
- **Estado de tests:** 132 passed; cobertura **100%** (líneas y ramas); ruff y mypy limpios.

### Tarea 032: Guías de Usuario y Onboarding Junior, limpieza de obsoletos y sincronización documental
- **Fecha:** 2026-10-17
- **Archivos:** `docs/USER_GUIDE.md` (nuevo), `docs/JUNIOR_ONBOARDING.md` (nuevo), `docs/aprendizaje.md` (eliminado), `scripts/benchmark.py` (eliminado), `test_cases/inventario/inventario.py` (restaurado pre-refactor), `docs/architecture.md`, `docs/flow.md`, `docs/benchmarks.md`, `README.md`, `README.es.md`, `.github/workflows/tests.yml`, `AGENTS.md`, `PROGRESS.md`.
- **Cambios:** redacción de `USER_GUIDE.md` (instalación `.venv`, flujos reales, modo libre y troubleshooting) y `JUNIOR_ONBOARDING.md` (SDD/Zero Breakage, diagrama ASCII `CLI -> AST -> Tests`, mapa de lectura y laboratorio guiado); eliminación de `docs/aprendizaje.md` y `scripts/benchmark.py`; restauración de `inventario.py` para el laboratorio en vivo; sincronización de las 4 guardas y escritura atómica en `architecture.md` y `flow.md`; regla permanente de sincronización documental en `AGENTS.md`.
- **Estado de tests:** 132 passed; cobertura **100%** (líneas y ramas); ruff y mypy limpios.

### Tarea 033: Scaffolding de tests Golden Master y Testing Diferencial con Hypothesis
- **Fecha:** 2026-10-17
- **Archivos:** `specs/features/002-differential-and-golden-testing.md` (nuevo), `pyproject.toml`, `src/correctorcode/contracts.py`, `src/correctorcode/testgen.py` (nuevo), `src/correctorcode/cli.py`, `tests/test_contracts.py`, `tests/test_testgen.py` (nuevo), `tests/test_cli.py`, `docs/USER_GUIDE.md`, `docs/JUNIOR_ONBOARDING.md`, `docs/architecture.md`, `README.md`, `README.es.md`, `PROGRESS.md`.
- **Cambios:** especificación de Feature 002 (Golden Master + testing diferencial); instalación e incorporación de `hypothesis` y `mutmut` como dependencias opcionales de desarrollo/testing; extensión de `contracts.py` (`FunctionContract`, `inspect_functions`); nuevo módulo `testgen.py` que inspecciona AST, extrae seeds deterministas, deduce estrategias de Hypothesis, captura outputs congelados y sintetiza `test_autogen_<nombre>.py` con tests Golden Master y pruebas diferenciales `@given` contra el respaldo legacy; integración en CLI (`scaffold-tests` y `run --scaffold-tests`); suite completa de tests unitarios y CLI alcanzando 100% de cobertura (líneas y ramas); sincronización de todas las guías y documentación del repositorio.
- **Estado de tests:** 146 passed; cobertura **100%** (816/816 líneas y 240/240 ramas); ruff y mypy limpios.

### Tarea 034: Formalización permanente de Graph-First Architecture
- **Fecha:** 2026-10-17
- **Archivos:** `AGENTS.md`, `docs/JUNIOR_ONBOARDING.md`, `PROGRESS.md`.
- **Cambios:** formalización de la directriz permanente "Flujo de Trabajo Obligatorio: Graph-First Architecture" estructurada en 3 secciones: Fase 1 (Exploración y diagnóstico exclusivamente con CodeGraph y prohibición de lecturas masivas en disco), Fase 2 (Implementación y validación con permiso total de edición y ejecución de tests) y Transparencia Operativa y Manejo de Errores (reporte explícito de fallos del grafo y citación de entidades justificativas); sincronización en las reglas operativas de `AGENTS.md` y en la lista de control de `docs/JUNIOR_ONBOARDING.md`.
- **Estado de tests:** 146 passed; suite 100% verde.

### Tarea 035: Auditoría pre-publicación y enriquecimiento del stack tecnológico
- **Fecha:** 2026-11-12
- **Archivos:** `opencode.json`, `README.md`, `README.es.md`, `PROGRESS.md`.
- **Cambios:** limpieza de rutas absolutas locales en `opencode.json` desacoplando paths del host para máxima portabilidad multiplataforma; adición de badges de estado y calidad (`tests 146 passed`, `coverage 100%`, `code style ruff`, `types mypy`); desglose explícito del Stack Tecnológico en `README.md` y `README.es.md` (librería estándar Python 3.12+ sin dependencias en runtime, testing diferencial con Hypothesis, auditoría con Mutmut, calidad con Ruff/Mypy/Radon y arquitectura Graph-First con CodeGraph).
- **Estado de tests:** 146 passed; cobertura 100% (816/816 líneas y 240/240 ramas).

### Tarea 036: Renombrado integral a ZeroBreak
- **Fecha:** 2026-11-12
- **Archivos:** `src/zerobreak/` (renombrado desde `src/correctorcode/`), `pyproject.toml`, `.gitignore`, `.github/workflows/tests.yml`, `conftest.py`, `tests/*.py`, `test_cases/tienda/bench_tienda.py`, `README.md`, `README.es.md`, `CONTRIBUTING*.md`, `AGENTS.md`, `docs/*`, `specs/*`, `PROGRESS.md`.
- **Cambios:** renombrado completo del paquete a `zerobreak` y del producto a **ZeroBreak**; actualización de punto de entrada CLI (`zerobreak = zerobreak.cli:main`), directorio de estado (`.zerobreak/state.json`), cabeceras didácticas y comandos; actualización integral de todas las suites de pruebas y documentación bilingüe.
- **Estado de tests:** 146 passed; cobertura 100% (816/816 líneas y 240/240 ramas).

### Tarea 037: Agradecimientos y formalización de licencia
- **Fecha:** 2026-11-12
- **Archivos:** `LICENSE`, `README.md`, `README.es.md`, `PROGRESS.md`.
- **Cambios:** sincronización de pull remoto con copyright atribuido a Rorro101004; incorporación de sección de Agradecimientos / Acknowledgements en README bilingüe reconociendo la colaboración de Antigravity (Google DeepMind) y DeepSeek como compañeros de pair-programming.
- **Estado de tests:** 146 passed; suite 100% verde.



