# Guía de Onboarding para Juniors — ZeroBreak

Bienvenido al equipo de ingeniería de **ZeroBreak**. Esta guía está diseñada para que entiendas **por qué** existe este proyecto, **cómo** funciona por dentro sin magia y cómo hacer tu primera refactorización verificada en menos de 15 minutos.

---

## 1. La Filosofía sin Rodeos: SDD y Zero Breakage

Cuando entras a trabajar en un repositorio profesional, el error más común es pensar que "mejorar código" significa reescribirlo para que parezca más corto o ingenioso. En ingeniería senior, **un código más rápido que rompe a un cliente es un bug, no una mejora**.

### ¿Qué es Spec-Driven Development (SDD)?
En ZeroBreak no programamos por intuición; programamos guiados por especificaciones:
1. **Las reglas de arquitectura y negocio viven en [`AGENTS.md`](../AGENTS.md) y [`specs/`](../specs/constitution.md).**
2. **Los contratos ejecutables viven en los tests (`test_*.py`).**
3. **El código de implementación solo es válido si satisface simultáneamente la especificación y el 100% de los tests.**

### ¿Qué es Zero Breakage (Cero Roturas)?
Significa que puedes optimizar el código para que sea 100 veces más rápido o reorganizarlo para que quede mucho más limpio, pero el resto del programa ni se entera ni se rompe.

Para quien utiliza tu función, esta se comporta como una caja negra: solo le importa qué datos le entrega y qué resultado recibe. Si la función sigue aceptando lo mismo y devolviendo lo mismo, lo que hagas por dentro no romperá el trabajo de nadie, por lo que:
- **No se cambian nombres** de funciones, clases ni métodos públicos.
- **No se cambian nombres ni orden** de parámetros.
- **No se tocan las aserciones de los tests** para "hacer que pasen".

### Separación de poderes: Semántica vs. Mecánica
En este proyecto separamos radicalmente quién propone un cambio de quién lo autoriza en disco:
- **El humano o el agente IA (Capa Semántica):** Lee el problema, detecta el *code smell* y escribe una propuesta en `propuestas/`. Puede equivocarse.
- **El paquete `src/zerobreak/` (Capa Mecánica):** Es 100% determinista, no usa IA ni red. Desconfía de la propuesta, verifica los contratos con `ast`, exige un baseline en verde, guarda copia de seguridad, escribe de forma atómica y revierte automáticamente si un solo test falla.

---

## 2. El Flujo Técnico de un Vistazo (`CLI → AST → Tests`)

Este diagrama ASCII resume qué ocurre exactamente dentro de `src/zerobreak/` cuando ejecutas un cambio con `zerobreak run` o `zerobreak apply`:

```text
  [Usuario / Agente]
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 1. ENTRADA CLI (cli.py)                                             │
  │    Resuelve el caso (cases.py: test_cases/<caso> o --target libre)  │
  │    Si es `run`: ejecuta baseline pytest y guarda SHA-256 (state.py) │
  └──────┬──────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 2. PLANIFICACIÓN SIN TOCAR DISCO: apply.plan_apply()                │
  │                                                                     │
  │    ├── Guarda 1 (Archivo)  : ¿Existe el archivo --source?           │
  │    ├── Guarda 2 (Baseline) : ¿state.json tiene baseline_ok == True? │
  │    ├── Guarda 3 (SHA-256)  : ¿sha256(modulo) == hash en state.json? │
  │    └── Guarda 4 (AST)      : contracts.check_contracts()            │
  │          └─ Parsea con `ast.parse` original y propuesta.            │
  │          └─ ¿Símbolos públicos o parámetros eliminados/alterados?   │
  │                                                                     │
  │    [Si falla cualquiera de las 4] ──▶ RECHAZA (Exit 1, 0 escrituras)│
  └──────┬──────────────────────────────────────────────────────────────┘
         │ (Las 4 guardas pasan en verde)
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 3. PREVISUALIZACIÓN Y LINT OPCIONAL (metrics.py / lint.py)          │
  │    Muestra tabla de métricas (SLOC, tipos, docstrings) + Diff.      │
  │    Si hay `--lint`: corre `ruff` y `mypy` sobre la propuesta.       │
  │    Pide confirmación humana [Y/n] (salvo flag `--yes`).             │
  └──────┬──────────────────────────────────────────────────────────────┘
         │ (Confirmado)
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 4. TRANSACCIÓN ATÓMICA Y VERIFICACIÓN: apply.apply()                │
  │                                                                     │
  │    a) Respaldo didáctico : backup.ensure_backup()                   │
  │                            Crea `<modulo>_legacy_anotado.py`        │
  │    b) Copia en RAM       : `original = module.read_bytes()`         │
  │    c) Escritura atómica  : `_atomic_write_bytes()` via `os.replace` │
  │    d) Ejecución aislada  : runner.run_pytest() (subproceso limpio)  │
  └──────┬──────────────────────────────────────────────────────────────┘
         │
         ├─── ¿Pytest returncode == 0 (VERDE)?
         │       ├── SÍ (COMMIT)   ─▶ Actualiza hashes en `state.json` (Exit 0)
         │       └── NO (ROLLBACK) ─▶ `_atomic_write_bytes(module, original)`
         │                            Restaura el archivo original intacto (Exit 1)
```

---

## 3. Recorrido Guiado por `src/zerobreak/`

No intentes leer los archivos en orden alfabético. Léelos en este orden de complejidad creciente (de las piezas puras al orquestador):

### Nivel 1: Piezas puras y aisladas (sin dependencias internas complejas)
1. **[`backup.py`](../src/zerobreak/backup.py) (12 sentencias):**
   - **Qué aprenderás:** Uso de `pathlib.Path.with_name` e **idempotencia**. Observa cómo `ensure_backup` devuelve `(ruta, creado: bool)` y jamás sobrescribe un archivo `*_legacy_anotado.py` si ya existe (para no borrar comentarios didácticos escritos por un compañero).
2. **[`runner.py`](../src/zerobreak/runner.py) (15 sentencias):**
   - **Qué aprenderás:** Por qué ejecutamos `pytest` mediante `subprocess.run([sys.executable, "-m", "pytest", ...])` en lugar de importar `pytest.main()`. Ejecutarlo en un subproceso evita que la caché de `sys.modules` de Python contamine las pruebas entre antes y después de aplicar el cambio.
3. **[`contracts.py`](../src/zerobreak/contracts.py) (40 sentencias):**
   - **Qué aprenderás:** Introspección estática con el módulo estándar `ast`. Lee `_extract_signatures`: recorre nodos `ast.FunctionDef`, `ast.AsyncFunctionDef` y `ast.ClassDef`, extrayendo los nombres y argumentos públicos mientras ignora las anotaciones de tipo (permitiendo añadir *type hints* sin que salte una falsa alarma).
4. **[`metrics.py`](../src/zerobreak/metrics.py) (24 sentencias):**
   - **Qué aprenderás:** Cómo contar líneas efectivas de código (SLOC), funciones completamente tipadas y docstrings usando `ast.get_docstring`.

### Nivel 2: Estado y descubrimiento del sistema de archivos
5. **[`state.py`](../src/zerobreak/state.py) (31 sentencias):**
   - **Qué aprenderás:** Persistencia ligera en `.zerobreak/state.json` y huellas criptográficas con `hashlib.sha256()`. Entenderás cómo la CLI detecta si alguien modificó un archivo manualmente después de pasar los tests.
6. **[`cases.py`](../src/zerobreak/cases.py) (80 sentencias):**
   - **Qué aprenderás:** El *Value Object* inmutable `@dataclass(frozen=True) class Case`. Fíjate en cómo unifica dos mundos: los casos dentro de `test_cases/<caso>/` (`resolve_case`) y cualquier archivo externo en **Modo Archivo Libre** (`resolve_free_case` mediante `target_module` y `test_target`).

### Nivel 3: El núcleo transaccional
7. **[`apply.py`](../src/zerobreak/apply.py) (52 sentencias):**
   - **Qué aprenderás:** El patrón **Plan vs. Execute** (`plan_apply` vs `apply`).
   - *Pregunta clásica de entrevista en este repo:* ¿Por qué separar `plan_apply` de `apply`? Porque `plan_apply` evalúa las 4 guardas y calcula el `diff` con **efecto secundario cero** (sirve para previsualizar), mientras que `apply` es el **único punto de todo el paquete que modifica el módulo objetivo**, envolviéndolo en escritura atómica (`_atomic_write_bytes`) y rollback.

### Nivel 4: Herramientas satélite y fachada CLI
8. **[`scaffold.py`](../src/zerobreak/scaffold.py), [`lint.py`](../src/zerobreak/lint.py), [`bench.py`](../src/zerobreak/bench.py) y [`testgen.py`](../src/zerobreak/testgen.py):**
   - Generación de plantillas (`new`), ejecución tolerante a fallos de `ruff`/`mypy` (`--lint`), carga dinámica de módulos con `importlib.util.spec_from_file_location` para medir `timeit` (`bench`), y caracterización automática Golden Master + Property-Based Testing con `hypothesis` (`testgen.py`).
9. **[`cli.py`](../src/zerobreak/cli.py) (280 sentencias):**
   - **Qué aprenderás:** Construcción de subcomandos con `argparse` sin librerías externas y el flujo interactivo de `_cmd_run`.

> Para una referencia detallada función por función, consulta [`docs/architecture.md`](architecture.md) y el diagrama visual en [`docs/flow.md`](flow.md).

---

## 4. Tu Primer Ejercicio Práctico Guiado (Hands-on Lab)

En el repositorio tienes preparado el caso `test_cases/inventario/inventario.py` en su estado **original sin optimizar** (tiene una búsqueda de duplicados cuadrática $O(n^2)$ con `.count()`, sumas manuales, concatenación de strings con `+=` y cero anotaciones de tipo). Además, en `propuestas/` tienes dos archivos listos:
- `propuestas/inventario_roto.py` (una propuesta con un bug lógico que ordena la lista y rompe el orden de inserción).
- `propuestas/inventario_mejorado.py` (la refactorización correcta con `collections.Counter`, `sum()`, `"".join()` y tipado).

Abre tu terminal en la raíz del proyecto y ejecuta estos 3 pasos usando el Python del `.venv`:

### Paso 1: Comprobar el estado inicial y provocar un Rollback controlado
Vamos a intentar aplicar primero la propuesta **rota** para que veas cómo el guardarraíl te salva de subir un bug:

```powershell
.\.venv\Scripts\python.exe -m zerobreak run inventario --source propuestas/inventario_roto.py --yes
```
**Observa lo que ocurre en la consola:**
1. El baseline inicial pasa en verde (`6 passed`).
2. Los contratos públicos (AST) pasan porque las firmas coinciden.
3. Se aplica el cambio y se ejecuta `pytest`... ¡pero falla `test_duplicados_conservan_orden_de_aparicion`!
4. `zerobreak` imprime: `Tests en rojo tras aplicar; rollback realizado sobre 'inventario.py'.` y devuelve código de salida `1`.
5. Si abres `test_cases/inventario/inventario.py`, comprobarás que **sigue intacto con su código original**.

### Paso 2: Aplicar la refactorización buena con verificación de Lint
Ahora lancemos la propuesta correcta activando los linters:

```powershell
.\.venv\Scripts\python.exe -m zerobreak run inventario --source propuestas/inventario_mejorado.py --lint
```
1. Revisa la tabla de **Métricas (antes -> después)**: verás cómo bajan las líneas de código (SLOC) de 32 a 18 y suben las funciones tipadas a `6/6`.
2. Revisa que `ruff` y `mypy` pasen en verde.
3. Confirma con `y` (o `Enter`).
4. Verás `Aplicado 'inventario_mejorado.py' -> 'inventario.py'` y los 6 tests en verde.

### Paso 3: El Respaldo Didáctico (Fase 5.1)
Mira ahora dentro de `test_cases/inventario/`: se ha creado automáticamente `inventario_legacy_anotado.py` con el código original íntegro.
- En un flujo real de ZeroBreak, tu trabajo final antes de cerrar la tarea es añadir comentarios explicativos en ese `*_legacy_anotado.py` detallando qué *code smell* había, por qué penalizaba el rendimiento y cómo se solucionó (fíjate en `test_cases/tienda/tienda_legacy_anotado.py` como ejemplo modelo).
- *(Si quieres dejar `inventario` de nuevo limpio para practicar otro día, basta con restaurar el código original de `inventario_legacy_anotado.py` dentro de `inventario.py` y borrar el archivo `_legacy_anotado.py`).*

---

## 5. Reglas de Oro para Contribuir al Repositorio

Antes de dar cualquier tarea por terminada, verifica siempre esta lista de control:

1. **Flujo Obligatorio Graph-First Architecture (MCP `codegraph`):**
   - **Fase 1: Exploración y Diagnóstico (Exclusivamente CodeGraph):** Antes de modificar cualquier archivo o planificar cambios, es obligatorio usar las herramientas MCP de `codegraph` (`find_callers`, `find_callees`, `query_codebase`, `find_dependencies`, etc.) para mapear dependencias y entidades afectadas. Queda terminantemente prohibido realizar lecturas indiscriminadas de archivos enteros (`view_file`, `cat`, búsquedas globales en texto plano) para explorar el proyecto. Si se requiere ver la implementación exacta de una función tras localizarla en el grafo, se debe usar `codegraph:read_file_content` o `codegraph:get_code_snippet` acotando los rangos de líneas estrictamente necesarios.
   - **Fase 2: Implementación y Validación (Permiso Total de Código):** Se autoriza y requiere el uso normal de herramientas de edición de archivos (`write_to_file`, `replace_file_content`, etc.) tanto en código fuente (`src/`) como en pruebas (`tests/`) y documentación cuando la tarea lo exija. La ejecución de suites de pruebas (`pytest`, `hypothesis`, `mutmut`) y scripts en la terminal forma parte del ciclo normal de trabajo.
   - **Transparencia Operativa y Manejo de Errores:** Si una llamada a `codegraph` falla, retorna un error o detecta desincronización, se debe reportar el error exacto y los parámetros utilizados en lugar de saltarse el protocolo en silencio. Todo informe de cambios o refactorización debe citar las entidades consultadas en el grafo que justificaron la intervención.
2. **Aislamiento en `.venv`:** Ejecuta todas las herramientas desde `.\.venv\Scripts\python.exe`.
3. **Batería de calidad 100% en verde:**
   ```powershell
   .\.venv\Scripts\python.exe -m pytest --cov=src/zerobreak --cov-report=term-missing
   .\.venv\Scripts\ruff.exe check src tests
   .\.venv\Scripts\mypy.exe src
   ```
   La cobertura de código sobre `src/zerobreak/` es actualmente del **100%** (líneas y ramas); cualquier código nuevo debe incluir sus tests en `tests/`.
4. **Sincronización Documental Obligatoria:** Ninguna funcionalidad o cambio en la CLI se considera terminado si no se actualizan en el mismo ciclo `README.md`, `README.es.md`, la guía correspondiente en `docs/` y el registro en `PROGRESS.md`.
