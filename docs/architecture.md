# Arquitectura interna de `src/zerobreak/`

Documentación técnica del **guardarraíl mecánico** de ZeroBreak. Explica
cómo está construido el paquete, qué hace cada función paso a paso y qué
condiciones de guardia impiden que se rompa o se escriba en disco por accidente.

> Principio de diseño: **la herramienta garantiza lo mecánico; el agente/humano
> decide lo semántico**. Nada de IA, nada de red, nada aleatorio: dadas las
> mismas entradas, la CLI toma siempre las mismas decisiones.

---

## 0. Vista general y mapa de dependencias

El paquete es una capa fina y determinista sobre tres cosas: el sistema de
archivos, `pytest` (vía subproceso) y un pequeño archivo de estado en JSON.

```
                                ┌─────────────────────────────┐
                                │            cli.py           │  (argparse: entra aquí)
                                └──────────────┬──────────────┘
      ┌─────────┬─────────┬─────────┬──────────┼──────────┬──────────┬──────────┬──────────┐
      ▼         ▼         ▼         ▼          ▼          ▼          ▼          ▼          ▼
  ┌───────┐ ┌────────┐┌────────┐┌────────┐┌─────────┐┌────────┐┌──────────┐┌────────┐┌─────────┐
  │cases  │ │runner  ││ state  ││backup  ││  apply  ││  lint  ││scaffold  ││ bench  ││ testgen │
  └───────┘ └────────┘└────────┘└───┬────┘└────┬────┘└────────┘└──────────┘└────────┘└────┬────┘
      ▲                             │          │                                       │
      │                             │   usa    ├──▶ contracts.py ◀── metrics.py        │
      │                             │          │            ▲                          │
      │                             │          │            └──────────────────────────┘
      └─────────────────────────────┴──────────┘
                   (apply usa backup, contracts, runner, state y cases)
```

- **Sin ciclos de dependencia.** `apply` compone `backup`, `contracts`, `runner`,
  `state` y `cases`; `metrics` y `testgen` reutilizan `contracts` para analizar las firmas públicas.
- **Sin dependencias externas en runtime.** Solo biblioteca estándar. Esto
  mantiene el paquete instalable en cualquier entorno y sin riesgo de cadena de
  suministro, en coherencia con la propia constitución del proyecto
  (`specs/constitution.md`: "preferir la biblioteca estándar").

---

## 1. Desglose archivo por archivo

### `__init__.py`
- **Propósito:** declarar el paquete y su versión (`__version__ = "0.1.0"`).
- **Responsabilidad única:** metadatos del paquete.
- **Imports:** ninguno.

### `__main__.py`
- **Propósito:** permitir `python -m zerobreak`.
- **Responsabilidad única:** delegar en la CLI.
- **Imports:** `sys` (para propagar el código de salida) y `.cli.main`.

### `cases.py` — descubrimiento de casos y modo archivo libre
- **Propósito:** saber qué casos existen en `test_cases/`, dónde está la raíz y resolver archivos libres fuera de `test_cases/` (`resolve_free_case`).
- **Responsabilidad única:** traducir el sistema de archivos a objetos `Case` (tanto en `test_cases/` como vía `--target`).
- **Imports:**
  - `dataclasses.dataclass` → define `Case` como *value object* inmutable.
  - `pathlib.Path` → rutas multiplataforma (Windows/Linux) sin concatenar strings.
- **Constantes:** `CASE_ROOT_NAME = "test_cases"`, `LEGACY_SUFFIX = "_legacy_anotado.py"`, `BENCH_PREFIX = "bench_"`.

### `runner.py` — ejecución de pytest
- **Propósito:** correr la suite de un caso y devolver un resultado tipado.
- **Responsabilidad única:** lanzar `pytest` y capturar su resultado.
- **Imports:**
  - `subprocess` → ejecutar pytest en un **proceso separado** (aislamiento).
  - `sys` → usar `sys.executable` para invocar exactamente el mismo Python.
  - `dataclasses` y `pathlib` → `RunResult` y rutas.

### `state.py` — estado persistente
- **Propósito:** recordar el baseline (verde + huellas de los módulos).
- **Responsabilidad única:** leer/escribir `.zerobreak/state.json` y calcular hashes.
- **Imports:**
  - `hashlib` → SHA-256 para huellas de archivo.
  - `json` → estado legible y depurable por humanos.
  - `datetime`/`timezone` → marca temporal en UTC (sin ambigüedad de zona horaria).
  - `pathlib` → rutas.
  - `typing.Any` → el estado es un diccionario heterogéneo.

### `backup.py` — respaldo didáctico
- **Propósito:** crear `<modulo>_legacy_anotado.py` antes de sobrescribir.
- **Responsabilidad única:** generar (una vez) la copia verbatim con cabecera.
- **Imports:** `pathlib` y `LEGACY_SUFFIX` (de `cases.py`) para no duplicar la convención.

### `contracts.py` — verificación de contratos públicos (`ast`)
- **Propósito:** comprobar que ninguna función, clase o método público se elimine ni altere los nombres u orden de sus parámetros.
- **Responsabilidad única:** extraer firmas públicas mediante `ast.parse` y comparar el código original contra el propuesto.
- **Imports:** `ast` (biblioteca estándar; cero dependencias).

### `apply.py` — aplicación con guardas
- **Propósito:** validar, aplicar de forma atómica y **revertir si algo falla**.
- **Responsabilidad única:** orquestar el cambio seguro.
- **Imports:**
  - `difflib` → diff unificado legible para la previsualización.
  - `os` → reemplazo atómico en disco (`os.replace`).
  - `dataclasses`, `pathlib`, y los módulos hermanos `backup`, `contracts`, `runner`, `state`, `cases`.

### `lint.py` — linters opcionales
- **Propósito:** ejecutar `ruff`/`mypy` sobre una propuesta **si están disponibles**.
- **Responsabilidad única:** detectar las herramientas, ejecutarlas y clasificar su salida.
- **Imports:** `importlib.util` (detectar el paquete), `subprocess` y `sys` (ejecutarlas
  como `python -m <tool>`), `dataclasses`, `pathlib`. **Sin dependencias nuevas**: si
  una herramienta no está (o falla al arrancar), se omite con un aviso.

### `scaffold.py` — generación de plantillas (scaffolding)
- **Propósito:** crear la estructura inicial y plantillas para nuevos casos (`zerobreak new <caso>`).
- **Responsabilidad única:** validar el nombre del caso y escribir los archivos iniciales (`<caso>.py`, `test_<caso>.py`, `propuestas/<caso>_mejorado.py`).
- **Imports:** `dataclasses`, `pathlib`, `CASE_ROOT_NAME` (de `cases.py`).

### `metrics.py` — métricas comparativas
- **Propósito:** calcular y formatear la comparativa del impacto del refactor (líneas efectivas SLOC, símbolos públicos, funciones tipadas y docstrings).
- **Responsabilidad única:** analizar el AST y formatear el bloque visual de métricas antes/después.
- **Imports:** `ast`, `dataclasses`, y `contracts` (para conteo de firmas públicas).

### `bench.py` — banco de pruebas comparativo integrado
- **Propósito:** medir el rendimiento empírico de la versión legacy (`*_legacy_anotado.py`) frente a la actual con `timeit`.
- **Responsabilidad única:** cargar dinámicamente ambos módulos y ejecutar los escenarios declarados en `test_cases/<caso>/bench_<caso>.py`.
- **Imports:** `importlib.util`, `timeit`, `dataclasses`, `pathlib`, `sys`. Cero dependencias externas.

### `testgen.py` — scaffolding de tests y testing diferencial
- **Propósito:** generar suites de prueba automáticas con snapshot Golden Master y Property-Based Testing diferencial (`hypothesis`).
- **Responsabilidad única:** inspeccionar AST de funciones públicas, derivar seeds y estrategias de Hypothesis, registrar salidas congeladas y sintetizar el archivo `tests/test_autogen_<nombre>.py`.
- **Imports:** `ast`, `dataclasses`, `importlib.util`, `inspect`, `pathlib`, `sys`.

### `cli.py` — interfaz de línea de comandos
- **Propósito:** parsear argumentos y despachar a los comandos.
- **Responsabilidad única:** capa de entrada/salida; no contiene lógica de negocio.
- **Imports:**
  - `argparse` → elegido sobre `click`/`typer` para mantener **cero dependencias**.
  - `sys`, `pathlib` y los módulos del paquete.

---

## 2. Análisis de funciones y métodos

### 2.1 `cases.py`

**`Case` (dataclass `frozen`)**
- **Campos:** `name: str`, `path: Path`, `test_target: Path | None = None`, `target_module: Path | None = None`.
- **Propiedad `test_path -> Path`:** devuelve `test_target` si se especificó (modo archivo libre) o `path` (modo carpeta `test_cases/<caso>`).
- **Por qué `frozen`:** es un *value object*; al ser inmutable y "hashable" se puede
  pasar entre funciones sin miedo a que alguien lo modifique por el camino.

**`Case.modules -> list[Path]`**
- **Qué hace:** en modo archivo libre devuelve `[self.target_module]`; en un caso modular recorre `*.py` (ordenados) del caso y devuelve solo los módulos de implementación.
- **Mecanismo:** excluye los que empiezan por `test_` o `bench_` y los que terminan en
  `_legacy_anotado.py`.
- **Guardas:** ninguna (función pura, no puede fallar).

**`Case.tests -> list[Path]`**
- **Qué hace:** devuelve los `test_*.py` ordenados del caso (o `[self.test_target]` en modo archivo libre).

**`find_root(start: Path | None = None) -> Path`**
- **Firma:** `Path | None` es **PEP 604** (unión con `|`).
- **Paso a paso:**
  1. Parte de `start` o del directorio actual y lo resuelve a ruta absoluta.
  2. Recorre el directorio y **todos sus padres**.
  3. Devuelve el primero que contenga una carpeta `test_cases/`.
- **Guarda:** si llega a la raíz del disco sin encontrarlo, lanza
  `FileNotFoundError` con un mensaje claro. Esto permite usar la CLI desde
  cualquier subcarpeta del proyecto.

**`list_cases(root: Path) -> list[Case]`**
- **Paso a paso:**
  1. Si `root/test_cases/` no existe → devuelve `[]` (**guarda** contra un root equivocado).
  2. Itera los subdirectorios ordenados.
  3. Incluye solo los que tienen al menos un `test_*.py`.

**`resolve_case(root: Path, name: str) -> Case`**
- **Qué hace:** convierte `"tienda"` o `"test_cases/tienda"` en un `Case`.
- **Truco:** `Path(name).name` normaliza cualquier ruta dejando solo el último
  segmento; así acepta ambas formas.
- **Guarda:** si no coincide ninguno, lanza `FileNotFoundError` **listando los
  casos disponibles** (mejor experiencia de error).

**`resolve_free_case(target: Path, tests: Path | None = None, root: Path | None = None) -> tuple[Path, Case]`**
- **Qué hace:** construye un objeto `Case` para cualquier archivo `.py` fuera de `test_cases/` (`--target`).
- **Autodetección de tests:** si `tests` es `None`, busca `test_<archivo>.py` en la misma carpeta del archivo objetivo.
- **Guardas:** lanza `FileNotFoundError` si el archivo objetivo no existe, no es `.py` o no se encuentran sus tests asociados.

### 2.2 `runner.py`

**`RunResult` (dataclass `frozen`)**
- **Campos:** `returncode: int`, `output: str`.
- **Propiedad `ok -> bool`:** `returncode == 0`. Centraliza la semántica
  "verde/rojo" en un único sitio.

**`run_pytest(root: Path, target: Path) -> RunResult`**
- **Firma:** recibe la raíz (contexto) y el objetivo (caso) y devuelve `RunResult`.
- **Paso a paso:**
  1. Lanza `subprocess.run([sys.executable, "-m", "pytest", str(target), "-q"], cwd=root, capture_output=True, text=True)`.
  2. Combina `stdout + stderr` y los devuelve sin espacios sobrantes.
- **Decisiones técnicas y por qué:**
  - **Subproceso, no `pytest.main()`:** aísla el estado de pytest del proceso de
    la CLI, evita contaminación entre ejecuciones y da un **código de salida real**.
  - **`sys.executable`:** garantiza el mismo intérprete (con las mismas
    dependencias) que ejecuta la CLI.
  - **`cwd=root`:** pytest descubre `pyproject.toml`/`conftest.py` desde la raíz
    correcta, igual que si lo lanzaras tú a mano.
  - **`-q`:** salida compacta y estable, fácil de mostrar al usuario.
- **Guardas:** ninguna; el propio `returncode` **es** la señal de éxito/fracaso.

### 2.3 `state.py`

**`state_path(root: Path) -> Path`** → `root/.zerobreak/state.json`.

**`sha256_file(path: Path) -> str`** — **cálculo de hash**
- **Paso a paso:** crea un objeto `hashlib.sha256()`, le pasa **todos los bytes**
  del archivo (`path.read_bytes()`) y devuelve el digest en hexadecimal.
- **Por qué SHA-256:** es una huella resistente a colisiones; con ella detectamos
  si un módulo cambió aunque solo sea un carácter. Es rápido y está en la stdlib,
  sin dependencias.

**`load_state(root: Path) -> dict[str, Any]`**
- **Guarda:** si el archivo no existe, devuelve el esqueleto `{"cases": {}}` en
  lugar de fallar (primer arranque limpio).

**`save_state(root: Path, state: dict[str, Any]) -> None`**
- **Paso a paso:** asegura que `.zerobreak/` existe (`mkdir(parents=True, exist_ok=True)`)
  y escribe el JSON con indentación y `ensure_ascii=False` (para conservar acentos).

**`get_entry(root: Path, case_name: str) -> dict[str, Any] | None`**
- Devuelve la entrada de un caso o `None`. Usa `.get()` encadenado para no lanzar
  nunca `KeyError`.

**`record_baseline(root: Path, case_name: str, modules: list[Path]) -> None`**
- **Paso a paso (mecanismo de baseline):**
  1. Carga el estado.
  2. Crea/obtiene la entrada del caso (`setdefault`).
  3. Marca `baseline_ok = True`.
  4. Escribe la marca temporal en **UTC** (`timespec="seconds"`).
  5. Guarda un mapa `{nombre_modulo: sha256}` de los módulos dados.
  6. Persiste.
- **Por qué guarda hashes:** es lo que permite detectar, más tarde, si el módulo
  cambió después del baseline.

### 2.4 `backup.py`

**`legacy_path(module: Path) -> Path`**
- Devuelve el hermano con sufijo: `tienda.py` → `tienda_legacy_anotado.py`
  (`module.with_name(f"{module.stem}{LEGACY_SUFFIX}")`).

**`ensure_backup(module: Path) -> tuple[Path, bool]`** — **generación del respaldo**
- **Firma:** tupla `(ruta_del_respaldo, creado)`; el `bool` distingue "lo acabo de
  crear" de "ya existía".
- **Paso a paso:**
  1. Calcula la ruta destino.
  2. **Guarda de idempotencia:** si el respaldo ya existe, lo devuelve con
     `created=False` y **no lo toca** (nunca pisa anotaciones hechas a mano).
  3. Si no existe: lee el cuerpo original y escribe **cabecera + cuerpo verbatim**.
- **Por qué una cabecera:** deja claro a cualquier lector que es una copia
  pre-refactor, que no es producción ni un test, y dónde anotar.

### 2.5 `apply.py` (y `contracts.py`)

**`ApplyResult` (dataclass `frozen`)**
- **Campos:** `ok: bool`, `message: str`, `diff: str`.

**`_unified_diff(before, after, name) -> str`**
- **Qué hace:** genera el diff en formato unificado con `difflib`.
- **Detalle:** usa `splitlines(keepends=True)` para **conservar los saltos de
  línea** en el diff (si no, las líneas saldrían pegadas).

**`_atomic_write_bytes(target: Path, data: bytes) -> None`**
- **Qué hace:** escribe en un archivo temporal hermano (`.<nombre>.tmp`) y usa
  `os.replace(tmp, target)` para reemplazar el destino de forma atómica a nivel de
  sistema operativo (tanto al escribir la propuesta como al revertir en el rollback).

**`plan_apply(root: Path, case: Case, module: Path, source: Path) -> ApplyResult`**
— **la validación previa, sin escribir nada**
- **Paso a paso (cuatro guardas en orden):**
  1. **¿Existe `--source`?** Si no → `ok=False`, mensaje "no existe".
  2. **¿Hay baseline verde?** Consulta `state.get_entry`; si falta o no está en
     verde → `ok=False` ("Ejecuta 'baseline' primero").
  3. **¿El hash actual coincide con el guardado?** Compara
     `state.sha256_file(module)` con el registrado. Si difieren → `ok=False`
     ("El módulo cambió desde el baseline").
  4. **¿Se preserva el contrato público (`contracts.check_contracts`)?** Compara
     mediante `ast.parse` las funciones, clases y métodos públicos (incluido `__init__`)
     ignorando anotaciones de tipo. Si algún símbolo público desaparece, altera los
     nombres/orden de sus parámetros o hay un error de sintaxis → `ok=False`
     ("Contrato público roto").
- Si pasa las cuatro, construye el `diff` y devuelve `ok=True` **sin tocar disco**.
- **Qué protege:** que nadie aplique un cambio sobre un estado desconocido, modificado
  por otra vía o que rompa las firmas públicas del módulo.

**`apply(root: Path, case: Case, module: Path, source: Path) -> ApplyResult`**
— **la aplicación con rollback**
- **Paso a paso:**
  1. Llama a `plan_apply`; si falla, devuelve el resultado tal cual (**no escribe**).
  2. `backup.ensure_backup(module)` → garantiza el respaldo **antes** de sobrescribir.
  3. Lee los **bytes originales** en memoria (`original = module.read_bytes()`).
  4. Escribe el contenido propuesto de forma atómica (`_atomic_write_bytes`).
  5. Ejecuta `runner.run_pytest(root, case.test_path)`.
  6. **Si los tests fallan (rojo):** restaura `_atomic_write_bytes(module, original)` y
     devuelve `ok=False` con la salida de pytest → **rollback**.
  7. **Si los tests pasan (verde):** `state.record_baseline(...)` actualiza el
     estado con los **nuevos** hashes (el nuevo baseline es la versión ya
     refactorizada) y devuelve `ok=True`.
- **Qué protege:** que un cambio que rompe los tests **nunca** quede persistido.

### 2.6 `cli.py`

**`_root(args) -> Path`**
- Devuelve `--root` resuelto si se pasó; si no, autodetecta con `cases.find_root()`.

**`_cmd_cases(args) -> int`** — lista los casos (o avisa si no hay).

**`_cmd_new(args) -> int`** — crea la estructura de directorios y plantillas de un nuevo caso (`scaffold.create_case`).

**`_cmd_baseline(args) -> int`**
- Corre pytest; imprime salida; si está rojo devuelve `1` **sin registrar** nada;
  si está verde, `state.record_baseline` y devuelve `0`.
- **Guarda:** el baseline solo se registra si las pruebas pasan.

**`_cmd_verify(args) -> int`** — corre pytest y propaga su `returncode`.

**`_cmd_snapshot(args) -> int`**
- **Guarda:** si el `--module` no existe → imprime y devuelve `1`.
- Si existe, crea el respaldo (`ensure_backup`).

**`_cmd_apply(args) -> int`**
- **Paso a paso:**
  1. **Guarda:** si el `--module` no existe → `1`.
  2. `plan_apply` → imprime el diff si lo hay.
  3. Si la planificación no es válida → imprime el motivo y devuelve `1`.
  4. Si **no** se pasó `--yes` → imprime "Previsualización únicamente" y devuelve `0`
     (**no escribe**).
  5. Con `--yes`: `apply` y devuelve `0`/`1` según el resultado.

**`_cmd_run(args) -> int`** — orquestador de alto nivel (interactivo; soporta `test_cases/<caso>` y `--target`)
- **Paso a paso:**
  1. Resuelve el objetivo con `_resolve_run_target` (caso modular o `--target` libre con `--tests` opcional; si falta la suite de tests y se pasó `--scaffold-tests`, la genera en el acto) y el **módulo** con `cases.resolve_module`.
  2. Ejecuta el **baseline** (`case.test_path`); si sale rojo → `1`, si verde → `state.record_baseline`.
  3. Crea el **respaldo didáctico** automáticamente (`backup.ensure_backup`).
  4. Resuelve la propuesta: `--source`, o autodetectada con `_discover_source`
     (`propuestas/<caso>_mejorado.py`, luego `propuestas/<caso>.py`). Sin ninguna → `0`.
  5. `plan_apply` (las 4 guardas de integridad y contratos AST), imprime la comparativa de **métricas estáticas** (`metrics.format_metrics_comparison`) y el **diff** propuesto.
  6. Con `--lint`, ejecuta `lint.run_linters` sobre la propuesta: si hay **hallazgos
     reales**, no aplica y devuelve `1`; si las herramientas no están disponibles
     (o fallan al arrancar), avisa y continúa.
  7. Si no hay `--yes`, pausa con `_ask_confirmation` (Enter/y aplica, n cancela;
     entrada no interactiva o Ctrl-C → cancela). Al cancelar **descarta el respaldo
     recién creado** y devuelve `0` sin tocar el módulo.
  8. Con confirmación (o `--yes`) llama a `apply` (escribe de forma atómica, verifica y revierte si falla).
- **Por qué existe:** reduce el ciclo a un comando, sin quitar los subcomandos
  granulares (`baseline`, `snapshot`, `apply`, `verify`).

**`_cmd_bench(args) -> int`** — ejecuta el banco de pruebas comparativo (`bench.run_benchmark`) entre `*_legacy_anotado.py` y el módulo actual.

**`_cmd_scaffold_tests(args) -> int`** — genera una suite de tests con snapshots Golden Master y pruebas diferenciales (`hypothesis`) para un archivo Python vía `testgen.generate_tests`.

**`_cmd_status(args) -> int`** — muestra el estado (de un caso o global).

**`build_parser() -> argparse.ArgumentParser`**
- Crea el parser principal con subcomandos (`cases`, `new`, `baseline`, `verify`,
  `snapshot`, `apply`, `run`, `bench`, `scaffold-tests`, `status`) y un **parser "padre" (`parents=[common]`)** que
  aporta `--root` a todos ellos.

**`main(argv: list[str] | None = None) -> int`**
- Parsea y despacha a `args.func`.
- **Guarda global:** captura `FileNotFoundError` (raíz o caso inexistente),
  imprime `Error: ...` y devuelve `2`.

**Convención de códigos de salida:**

| Código | Significado |
|---|---|
| `0` | Operación correcta (o previsualización sin `--yes`). |
| `1` | Fallo de validación u operación (baseline rojo, guarda incumplida, tests rojos). |
| `2` | Error de uso/entorno (raíz o caso no encontrado, argumentos incompatibles). |

---

### 2.7 `testgen.py`

**`TestGenResult` (dataclass `frozen`)**
- **Campos:** `test_file: Path`, `functions: list[str]`, `created: bool`.

**`FunctionContract` (dataclass `frozen` en `contracts.py`)**
- **Campos:** `name: str`, `params: list[str]`, `param_types: dict[str, str]`, `defaults_count: int`.
- Extraído mediante `inspect_functions(source: str)` analizando el AST de todas las funciones públicas a nivel de módulo.

**`generate_tests(target: Path, out: Path | None = None, root: Path | None = None) -> TestGenResult`**
- **Paso a paso:**
  1. **Guarda 1:** comprueba que `target` existe y tiene extensión `.py` (si no, lanza `FileNotFoundError`).
  2. **Guarda 2:** extrae funciones públicas con `contracts.inspect_functions`. Si no hay ninguna, lanza `ValueError` ("No se encontraron funciones públicas").
  3. Importa el módulo en memoria mediante `importlib.util` de manera aislada para capturar las salidas Golden Master con semillas deterministas (`_seed_for_param`). Si la llamada lanza una excepción predecible (p. ej. `TypeError`), captura el tipo de excepción para verificar que el refactor mantenga el mismo comportamiento de error.
  4. Deduce estrategias de Hypothesis (`_strategy_for_param`) en base al tipo inferido (diferenciando `list`, `dict`, `int`, `str`, etc.) o heurísticas por nombre de parámetro.
  5. Construye el contenido del archivo de test (`build_test_file_content`):
     - Fixture dual `current_mod` y `legacy_mod`: si aún no existe `*_legacy_anotado.py`, ejecuta sobre `current_mod`; una vez generado el respaldo legacy tras `apply`, compara `legacy_func(*args) == current_func(*args)`.
     - Tests Golden Master: `test_golden_<func>` con aserciones exactas del resultado congelado o de la excepción esperada.
     - Tests diferenciales: `@given(...)` con Hypothesis ejecutando tests masivos con entradas extremas y aleatorias.
  6. Escribe el archivo en disco (`tests/test_autogen_<target>.py` o en la ruta `out` solicitada).

---

## 3. Resumen de guardas (qué protege cada una)

| Guarda | Dónde | Protege contra |
|---|---|---|
| `raise FileNotFoundError` si no hay `test_cases/` | `cases.find_root` | Ejecutar en un directorio que no es el proyecto. |
| `return []` si no existe `test_cases/` | `cases.list_cases` | Iterar sobre una base inexistente. |
| `raise FileNotFoundError` con casos disponibles | `cases.resolve_case` | Usar un nombre de caso inexistente. |
| `raise FileNotFoundError` si falta `--target` o tests | `cases.resolve_free_case` | Ejecutar en modo archivo libre sin archivo `.py` o sin suite de tests. |
| `if not target.is_file() or target.suffix != ".py"` | `testgen.generate_tests` | Intentar generar tests para archivos inexistentes o no Python. |
| `if not funcs: raise ValueError` | `testgen.generate_tests` | Generar suites vacías para archivos sin funciones públicas. |
| `if not path.is_file(): return {"cases": {}}` | `state.load_state` | Fallar en el primer arranque sin estado. |
| `if target.is_file(): return (target, False)` | `backup.ensure_backup` | Pisar un respaldo ya anotado (idempotencia). |
| `if not source.is_file()` | `apply.plan_apply` | Aplicar una fuente que no existe (Guarda 1). |
| `if not entry or not entry.get("baseline_ok")` | `apply.plan_apply` | Aplicar sin baseline verde (Guarda 2). |
| `if recorded != sha256_file(module)` | `apply.plan_apply` | Aplicar sobre un módulo modificado después del baseline (Guarda 3). |
| `contracts.check_contracts(before, after)` | `apply.plan_apply` | Eliminar símbolos públicos o alterar nombres/orden de parámetros (Guarda 4 - AST). |
| `_atomic_write_bytes(target, data)` (`os.replace`) | `apply.apply` | Dejar archivos corruptos o truncados a mitad de escritura. |
| `if not result.ok: _atomic_write_bytes(module, original)` | `apply.apply` | Dejar persistido un cambio que rompe los tests (**rollback**). |
| `if not args.yes` | `cli._cmd_apply` | Escribir sin confirmación explícita. |
| `except FileNotFoundError: return 2` | `cli.main` | Mostrar una traza fea al usuario ante errores de uso. |

---

## 4. Flujo determinista integrado: `zerobreak apply`

Suponemos:

```bash
zerobreak apply tienda --module tienda.py --source propuesta.py --yes
```

Secuencia de llamadas y decisiones:

```
zerobreak apply tienda --module tienda.py --source propuesta.py --yes
   │
   ├─ cli._root()                 → raíz del proyecto (--root o find_root())
   ├─ cases.resolve_case()        → valida que el caso 'tienda' existe
   ├─ cli._cmd_apply()
   │    │
   │    ├─ ¿existe test_cases/tienda/tienda.py? ── no ─▶ return 1
   │    │
   │    ├─ apply.plan_apply()  ── SIN ESCRIBIR EN DISCO ──────────────────────
   │    │     ├─ guarda 1: ¿existe propuesta.py?            ── no ─▶ ok=False
   │    │     ├─ guarda 2: ¿hay baseline verde?             ── no ─▶ ok=False
   │    │     │             (state.get_entry)
   │    │     ├─ guarda 3: ¿sha256(tienda.py) == guardado?   ── no ─▶ ok=False
   │    │     │             (state.sha256_file)
   │    │     ├─ guarda 4: ¿contratos AST intactos?          ── no ─▶ ok=False
   │    │     │             (contracts.check_contracts)
   │    │     └─ diff = difflib.unified_diff(actual, propuesta)
   │    │
   │    ├─ si plan.ok == False ─▶ imprime motivo · return 1
   │    ├─ si no hay --yes     ─▶ imprime diff   · return 0   (previsualización)
   │    │
   │    └─ apply.apply()  ── LA ÚNICA PARTE QUE ESCRIBE ──────────────────────
   │          ├─ backup.ensure_backup()  → tienda_legacy_anotado.py (idempotente)
   │          ├─ original = tienda.py.read_bytes()            (copia en memoria)
   │          ├─ _atomic_write_bytes(tienda.py, propuesta)     (escritura os.replace)
   │          ├─ runner.run_pytest(case.test_path)            (subproceso)
   │          │      │
   │          │      ├─ returncode != 0 ─▶ _atomic_write_bytes(tienda.py, original) ◀ ROLLBACK
   │          │      │                     return ok=False
   │          │      │
   │          │      └─ returncode == 0 ─▶ state.record_baseline(nuevos hashes)
   │          │                            return ok=True
   │          │
   │          └─ ApplyResult(ok, message, diff)
   │
   └─ imprime mensaje · devuelve 0 (verde) o 1 (rojo/rollback)
```

**Lectura clave del flujo:**

1. **Todo lo que decide pasa en `plan_apply`, y ahí no se escribe nada.** Las cuatro
   guardas son la puerta de entrada.
2. **La escritura vive en un único punto** (`apply.apply` mediante `os.replace`), y está flanqueada por
   un respaldo (antes) y una verificación con rollback (después).
3. **El estado solo se actualiza cuando los tests están en verde**, así que el
   "baseline" siempre refleja una versión que funciona.
4. **Es determinista:** mismos archivos y mismo estado → mismo resultado. No hay
   red, ni aleatoriedad, ni decisiones de IA en esta ruta.

---

## 5. Cómo verificarlo tú mismo

```bash
pip install -e ".[dev]"                     # instala la CLI y las herramientas

zerobreak cases                         # ¿qué casos hay?
zerobreak baseline tienda               # deja el caso en verde y guarda hashes
zerobreak status tienda                 # consulta el estado guardado

# Simula una propuesta (previsualización, no escribe):
copy test_cases\tienda\tienda.py propuesta.py
zerobreak apply tienda --module tienda.py --source propuesta.py
#   → imprime el diff y "Previsualización únicamente"

# Aplica de verdad y observa el respaldo + verificación:
zerobreak apply tienda --module tienda.py --source propuesta.py --yes

# O el atajo de alto nivel (módulo autodetectado; baseline + respaldo + aplicación):
zerobreak run tienda --source propuesta.py --yes
```

Si quieres ver las **guardas en acción**: ejecuta `apply` **sin** haber hecho
`baseline` (te lo pedirá), o edita `tienda.py` a mano después del baseline y
vuelve a intentar `apply` (te avisará de que el hash cambió).

---

## 6. Qué verifica cada capa (CLI · herramientas · agente)

ZeroBreak separa a propósito **lo mecánico** de **lo semántico**:

| Qué se verifica | Capa | ¿Automático? | Dónde |
|---|---|---|---|
| No romper el comportamiento | **CLI** | ✅ | `apply` → `runner` (pytest) |
| Integridad (nadie editó por detrás) | **CLI** | ✅ | `apply.plan_apply` (SHA-256) |
| Rollback ante fallo | **CLI** | ✅ | `apply.apply` |
| Lint/tipos de la propuesta (opt-in) | **CLI** (`run --lint`) | ⚙️ | `lint.py` (ruff/mypy si están) |
| Cobertura ≥ 90% | **CI** | ✅ | job `coverage` |
| Estilo / lint (PEP 8) | **CI** | ✅ | job `quality` → `ruff` |
| Tipado estático (PEP 484/585/604) | **CI** | ✅ | job `quality` → `mypy` |
| Complejidad ciclomática | **CI** | ✅ | job `quality` → `radon` |
| Rendimiento (O(n) vs O(n²)) | **CI** (manual) | ⚙️ | job `benchmark` |
| Equivalencia semántica | **Agente / humano** | ❌ | skill `python-refactor-guard` |
| ¿La docstring es correcta? ¿el diseño es mejor? | **Agente / humano** | ❌ | juicio |

Puntos clave:

- **El CLI no usa IA.** Es determinista, offline y sin dependencias de runtime
  (`dependencies = []`). Ejecutarlo consume **0 tokens** de cualquier API de LLM.
- **Las herramientas de calidad son deterministas** (`pytest`, `coverage`, `ruff`,
  `mypy`, `radon`): no dependen de un modelo ni de credenciales.
- **El agente (LLM) solo aporta el *cambio*** y el juicio sobre lo subjetivo; vive
  fuera del paquete (`.opencode/`), es opcional, y su coste de API no lo paga el CLI.
- Las reglas duras (lint, tipos, cobertura, complejidad) **bloquean el PR** si fallan:
  eso es "buenas prácticas" verificadas automáticamente, sin LLM de por medio.
