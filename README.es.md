# ZeroBreak

[English](README.md) | **Español**

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://docs.python.org/3/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-146%20passed-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](tests/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)

Marco de Spec-Driven Development (SDD) para **refactorizar Python sin romper contratos** (filosofía Zero Breakage). Objetivo canónico: Python 3.12+, validado con `pytest`.

Todo cambio recorre un ciclo obligatorio de 5 fases: análisis de contratos → baseline `pytest` → propuesta → verificación en sandbox → confirmación humana → **respaldo didáctico** (`<modulo>_legacy_anotado.py`) → aplicación en disco. Nada se persiste sin una suite en verde y aprobación explícita.

## Casos de prueba (modular)

Cada caso vive aislado en `test_cases/<nombre_caso>/`, con su código y su suite `test_*.py` en el mismo directorio. Se trabaja un caso a la vez.

## Uso rápido

```bash
pytest                       # todos los casos + los tests del framework
pytest test_cases/tienda     # baseline y verificación de un caso
```

Ciclo completo desde el agente:

```text
/refactor test_cases/tienda
```

## Interfaz de línea de comandos

El paquete incluye la CLI `zerobreak`, que hace cumplir la parte **mecánica** del ciclo (baseline, respaldo, aplicación con rollback automático). Es determinista y no usa IA.

```bash
pip install -e ".[dev]"        # instala la CLI y las herramientas de desarrollo

zerobreak cases                                  # lista los casos de test_cases/
zerobreak new mi_caso                            # crea plantillas y estructura para un nuevo caso

# Orquestador de alto nivel (módulo y propuesta autodetectados; interactivo):
zerobreak run tienda                              # baseline + respaldo + diff + confirmación
zerobreak run tienda --source propuesta.py        # usa una propuesta concreta
zerobreak run tienda --lint                       # además analiza la propuesta con ruff/mypy si están
zerobreak run tienda --yes                        # omite la confirmación (CI / scripts)

# Modo Archivo Libre (en cualquier script fuera de test_cases/):
zerobreak run --target mi_app/pagos.py --tests tests/test_pagos.py --source propuesta.py

# Scaffolding de Tests y Testing Diferencial (Golden Master + Hypothesis):
zerobreak scaffold-tests modulo_legacy.py       # genera tests/test_autogen_modulo_legacy.py
zerobreak run --target legacy.py --scaffold-tests  # scaffolding automático si falta la suite de tests

# Control granular, paso a paso:
zerobreak baseline tienda                        # ejecuta pytest y registra un baseline verde
zerobreak snapshot tienda --module tienda.py     # crea el respaldo didáctico
zerobreak apply tienda --module tienda.py --source propuesta.py --yes    # aplica
zerobreak verify tienda                          # ejecuta los tests
zerobreak bench tienda                           # compara rendimiento legacy vs actual
zerobreak status                                 # muestra el estado guardado
```

`run` autodetecta el módulo (un único archivo de implementación, o `<caso>.py` por convención) y, si omites `--source`, busca una propuesta estándar en `propuestas/<caso>_mejorado.py`. Valida las guardas de integridad, muestra el diff y pide confirmación interactivamente (Enter/y para aplicar, n para cancelar); `--yes` omite la pregunta para CI. Con `--lint` además ejecuta `ruff`/`mypy` sobre la propuesta si están instalados (si no, avisa y continúa). `apply` se niega a escribir si no hay un baseline verde y el hash del módulo no coincide, crea siempre el respaldo `<modulo>_legacy_anotado.py` y revierte automáticamente si los tests fallan.

Ver [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) para el tutorial práctico y resolución de errores, [`docs/JUNIOR_ONBOARDING.md`](docs/JUNIOR_ONBOARDING.md) para la guía de incorporación y laboratorio guiado, y [`docs/architecture.md`](docs/architecture.md) para el análisis técnico archivo por archivo del paquete. Para una vista visual del flujo completo (conceptual + mecánico), ver [`docs/flow.md`](docs/flow.md).

## Medición

- **Cobertura:** `pytest --cov=zerobreak --cov-report=term-missing` (actualmente 100%; umbral ≥ 90% en CI).
- **Complejidad:** `radon cc -s -a src test_cases` y `radon mi src test_cases`.
- **Lint y tipos:** `ruff check src tests` y `mypy src` (aplicado en CI).
- **Rendimiento:** `zerobreak bench tienda` compara el código original con el refactorizado. Resultados en [`docs/benchmarks.md`](docs/benchmarks.md). El refactor de `buscar_productos_duplicados` muestra una mejora medida de O(n²) → O(n) (hasta ~670× con n=5000).

## Tecnologías y herramientas utilizadas

- **Núcleo y Ejecución (Cero Dependencias Externas en Producción):**
  - **Biblioteca Estándar de Python 3.12+:**
    - `ast`: Análisis estático del árbol sintáctico, extracción de firmas públicas e inspección de contratos de tipado/docstrings sin ejecutar código.
    - `hashlib`: Huellas criptográficas SHA-256 para verificar la integridad del estado en disco y detectar modificaciones externas.
    - `difflib`: Cálculo de diffs unificados para previsualización interactiva en terminal.
    - `timeit`: Micro-benchmarks deterministas con calibración `autorange` y filtrado de ruido (tiempo mínimo).
    - `importlib`: Carga dinámica y aislada de módulos en espacios de nombres protegidos sin contaminar `sys.modules`.
    - `argparse`: Interfaz de línea de comandos estándar y sin dependencias.
    - `os.replace`: Reemplazo atómico de archivos a nivel de sistema de archivos.
- **Testing y Arnés de Seguridad:**
  - `pytest`: Ejecutor de pruebas modular, aislamiento de tests mediante `conftest.py` raíz (`collect_ignore_glob`) y fixtures.
  - `pytest-cov`: Medición estricta de cobertura de líneas y ramas (100% alcanzado, umbral ≥90% en CI).
  - `hypothesis`: Testing diferencial basado en propiedades (`@given`) generado automáticamente por `testgen.py`.
  - `mutmut`: Testing de mutaciones para auditar la eficacia real de la suite de pruebas y evitar tests ciegos.
- **Análisis Estático y Calidad de Código:**
  - `ruff`: Linter de alto rendimiento (PEP 8, pyflakes, pycodestyle).
  - `mypy`: Verificación estática de tipos según PEP 484, 585 y 604.
  - `radon`: Puertas de calidad para complejidad ciclomática (`radon cc`) e índice de mantenibilidad (`radon mi`).
- **Empaquetado y Estándares:**
  - `hatchling`: Backend de construcción moderno compatible con PEP 517 y PEP 621.
- **Herramientas de Desarrollo y Graph-First:**
  - `codegraph-mcp`: Servidor MCP para navegación semántica del grafo de código basada en AST (arquitectura Graph-First).

## Estructura

| Ruta | Propósito |
|------|-----------|
| `AGENTS.md` | Reglas operativas (SSOT; en español) |
| `specs/constitution.md` | Misión, alcance y stack |
| `specs/features/001-safe-refactor-loop.md` | Proceso detallado por fases |
| `specs/features/002-differential-and-golden-testing.md` | Especificación de Golden Master y Testing Diferencial |
| `src/zerobreak/` | Paquete de la CLI (guardarraíl mecánico) |
| `src/zerobreak/testgen.py` | Generador de scaffolding de tests y pruebas diferenciales |
| `tests/` | Tests del propio framework |
| `docs/USER_GUIDE.md` | Guía de usuario paso a paso, aislamiento `.venv` y troubleshooting |
| `docs/JUNIOR_ONBOARDING.md` | Guía de onboarding para juniors, filosofía SDD y ejercicio práctico |
| `docs/architecture.md` | Arquitectura interna del paquete de la CLI (análisis profundo) |
| `docs/flow.md` | Diagrama de flujo (SVG) con el ciclo SDD y las guardas |
| `docs/benchmarks.md` | Resultados medidos (legacy vs refactorizado) |
| `.opencode/` | Skills, comandos y subagente del agente |
| `conftest.py` | Aislamiento de tests (excluye `*_legacy_anotado.py`) |
| `test_cases/<caso>/` | Casos aislados: código + `test_*.py` |
| `test_cases/<caso>/<modulo>_legacy_anotado.py` | Respaldo didáctico del código original (no es test) |
| `PROGRESS.md` | Trazabilidad de cambios |

> Los documentos operativos (`AGENTS.md`, `specs/`, `.opencode/`) están en español; las entradas públicas están en inglés (README) y el código usa docstrings en español.

## Configuración

- `opencode.json`: la escritura sobre `test_cases/**` requiere aprobación (`edit: ask`), reforzando la Fase 5.
- `pyproject.toml`: empaquetado, punto de entrada `zerobreak`, dependencias de desarrollo, `testpaths` y ajustes de cobertura.

## Agradecimientos

Desarrollado con la asistencia y colaboración de **Antigravity** (Google DeepMind) y **DeepSeek** como compañeros de pair-programming con IA.

## Licencia

MIT — ver [LICENSE](LICENSE).
