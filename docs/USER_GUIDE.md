# Guía de Usuario — ZeroBreak

Bienvenido a la guía práctica de **ZeroBreak**, el guardarraíl determinista para refactorizar código Python bajo la filosofía **Zero Breakage** (cero roturas de contratos o pruebas).

---

## 1. ¿Qué resuelve ZeroBreak en 30 segundos?

Cuando refactorizas un módulo Python (manualmente o con ayuda de un agente de IA), existen tres riesgos clásicos:
1. **Romper contratos públicos sin darte cuenta** (cambiar el nombre de un parámetro, eliminar una función auxiliar pública o alterar el orden de argumentos).
2. **Perder el código original** antes de poder comparar su rendimiento o documentar por qué se cambió.
3. **Dejar el repositorio en un estado roto** si un cambio falla en los tests a mitad de proceso.

`zerobreak` actúa como un **transaccional mecánico** entre tu propuesta de mejora y el disco:
- Verifica que los tests pasen **antes** de empezar (*baseline* verde).
- Comprueba con SHA-256 que nadie haya modificado el archivo por detrás.
- Analiza el árbol sintáctico (**AST**) para asegurar que ninguna firma pública haya sido eliminada o alterada.
- Guarda automáticamente un respaldo didáctico (`<modulo>_legacy_anotado.py`).
- Escribe el cambio de forma atómica (`os.replace`), ejecuta `pytest` y, **si un solo test falla, revierte el archivo al instante (Rollback)**.

---

## 2. Instalación y Aislamiento en `.venv`

Por diseño, `zerobreak` **no tiene dependencias externas en tiempo de ejecución** (usa exclusivamente la biblioteca estándar de Python 3.12+). Las herramientas de verificación (`pytest`, `pytest-cov`, `ruff`, `mypy`, `radon`) viven aisladas dentro del entorno virtual `.venv` del proyecto.

### 2.1 Creación y activación del entorno virtual

**En Windows (PowerShell):**
```powershell
# 1. Crear el entorno virtual (si no existe)
python -m venv .venv

# 2. Instalar el paquete en modo editable junto con las herramientas de desarrollo
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"

# 3. Verificar la instalación
.\.venv\Scripts\zerobreak.exe --help
```

**En Linux / macOS:**
```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[dev]"
./.venv/bin/zerobreak --help
```

> **Regla de aislamiento:** Si no activas el entorno en tu shell (`.\.venv\Scripts\Activate.ps1`), invoca siempre los comandos a través de `.\.venv\Scripts\python.exe -m zerobreak` o `.\.venv\Scripts\zerobreak.exe`.

---

## 3. Casos de Uso Reales Paso a Paso

`zerobreak` soporta dos modalidades de trabajo:
- **Modo A (Casos Modulares en `test_cases/`):** Ideal para laboratorios de optimización, katas, entrevistas técnicas o módulos autocontenidos con benchmarks.
- **Modo B (Modo Archivo Libre con `--target`):** Ideal para refactorizar cualquier archivo `.py` en un proyecto real externo sin moverlo a `test_cases/`.

---

### Modo A: Flujo Completo sobre un Caso Modular (`test_cases/<caso>`)

#### Paso 1: Crear un nuevo caso (o listar los existentes)
```powershell
# Listar casos disponibles en test_cases/
zerobreak cases

# Crear la estructura base para un caso nuevo llamado 'facturacion'
zerobreak new facturacion
```
El comando `new` genera automáticamente:
- `test_cases/facturacion/facturacion.py` (módulo inicial)
- `test_cases/facturacion/test_facturacion.py` (suite de pytest lista en verde)
- `propuestas/facturacion_mejorado.py` (plantilla donde escribirás tu refactorización)

#### Paso 2: Ejecutar el orquestador interactivo (`run`)
Una vez que hayas editado tu propuesta en `propuestas/<caso>_mejorado.py` (por ejemplo, para el caso de práctica `inventario`), lanza:

```powershell
zerobreak run inventario --lint
```

¿Qué hace este comando en un solo paso?
1. Ejecuta `pytest` sobre `test_cases/inventario` y registra el **baseline** en `.zerobreak/state.json`.
2. Prepara el respaldo `<modulo>_legacy_anotado.py`.
3. Valida las **4 guardas de seguridad** (existencia de propuesta, baseline verde, integridad SHA-256 y preservación de contratos AST).
4. Muestra la **tabla comparativa de métricas estáticas** y el **diff unificado**:
   ```text
   Métricas (antes -> después):
     SLOC (líneas efectivas): 32 -> 21 (-11)
     Símbolos públicos      : 6 -> 6 (+0)
     Funciones tipadas      : 0/6 -> 6/6
     Docstrings             : 0/7 -> 1/7
   ```
5. Si pasaste `--lint`, ejecuta `ruff` y `mypy` sobre la propuesta antes de tocar el módulo.
6. Te pide confirmación interactiva: `¿Aplicar estos cambios a inventario.py? [Y/n]:`
   - Si pulsas `Enter` o `y`: aplica el cambio de forma atómica y re-ejecuta `pytest`.
   - Si pulsas `n`: cancela limpiamente y deja el directorio intacto.
   - *(Para scripts o CI sin pausa interactiva, añade la bandera `--yes`).*

#### Paso 3: Medir la mejora real de rendimiento (`bench`)
Si tu caso incluye un archivo `test_cases/<caso>/bench_<caso>.py` (como ocurre en `tienda`), puedes medir empíricamente con `timeit` cuánto ha mejorado la versión refactorizada frente al respaldo `*_legacy_anotado.py`:

```powershell
zerobreak bench tienda
```
Salida esperada:
```text
Benchmark — caso: tienda (tienda_legacy_anotado.py vs tienda.py)
Escenario                            Legacy (ms)   Actual (ms)    Speedup
-------------------------------------------------------------------------
buscar_duplicados (n=1000)                  9.20          0.07     131.4x
buscar_duplicados (n=5000)                215.40          0.33     652.7x
generar_recibo (n=1000)                     0.52          0.35       1.5x
```

---

### Modo B: Modo Archivo Libre (`--target` y `--tests`)

¿Quieres refactorizar un módulo que vive fuera de `test_cases/` (por ejemplo, en `mi_app/pagos.py`) sin mover archivos? Usa `--target`:

```powershell
# Si test_pagos.py está en la misma carpeta que pagos.py (se autodetecta):
zerobreak run --target mi_app/pagos.py --source propuestas/pagos_v2.py --lint

# Si los tests están en otra carpeta (p. ej. tests/unit/test_pagos.py):
zerobreak run --target mi_app/pagos.py --tests tests/unit/test_pagos.py --source propuestas/pagos_v2.py

# ¿El módulo no tiene tests todavía? Genera Golden Master + Hypothesis automáticamente:
zerobreak run --target mi_app/pagos.py --source propuestas/pagos_v2.py --scaffold-tests --lint
```

El comportamiento de seguridad es idéntico: registra el baseline, verifica contratos AST, crea `mi_app/pagos_legacy_anotado.py`, aplica de forma atómica y hace rollback si los tests fallan.

---

### Modo C: Scaffolding de Tests y Testing Diferencial (`scaffold-tests` + `Hypothesis`)

Cuando necesitas refactorizar código legacy sin pruebas, los tests unitarios manuales suelen ser superficiales y dejan escapar casos borde. ZeroBreak ofrece una alternativa de nivel industrial:

```powershell
zerobreak scaffold-tests mi_app/calculos.py
```
Salida esperada:
```text
Suite Golden Master + Hypothesis generada para 'calculos.py':
  - Archivo de tests: tests/test_autogen_calculos.py
  - Funciones caracterizadas: sumar, calcular_tasa, procesar_lote

Ejecuta los tests con: pytest tests/test_autogen_calculos.py
```

El archivo generado contiene dos capas de defensa:
1. **Golden Master (Snapshot de caracterización):** Ejecuta el código original con vectores frontera y congela sus retornos y excepciones exactas.
2. **Testing Diferencial con Hypothesis:** Genera cientos de combinaciones aleatorias y extremas con `@given(...)` y comprueba que para cualquier entrada:
   $$\text{legacy\_func}(*x) == \text{current\_func}(*x)$$
   Si tu refactorización introduce una discrepancia sutil ante números negativos, cadenas vacías o enteros astronómicos, Hypothesis encuentra el contraejemplo y aborta la transacción con **Rollback automático**.

---

## 4. Referencia Rápida de Comandos Granulares

Si prefieres ejecutar cada etapa manualmente en lugar de usar `zerobreak run`:

| Comando | Qué hace | ¿Modifica el módulo objetivo? |
| :--- | :--- | :--- |
| `zerobreak cases` | Lista los casos válidos dentro de `test_cases/`. | No |
| `zerobreak new <caso>` | Crea la carpeta del caso, su test inicial y plantilla de propuesta. | Crea caso nuevo |
| `zerobreak scaffold-tests <archivo>` | Genera suite Golden Master + Differential Testing con Hypothesis. | Crea archivo de test |
| `zerobreak baseline <caso>` | Corre `pytest` y, si pasa al 100%, guarda el SHA-256 en `.zerobreak/state.json`. | No |
| `zerobreak snapshot <caso> --module <m.py>` | Crea `<modulo>_legacy_anotado.py` (idempotente: nunca sobrescribe uno ya existente). | No (crea copia) |
| `zerobreak apply <caso> --module <m.py> --source <p.py>` | **Modo previsualización** (sin `--yes`): valida las 4 guardas y muestra el diff. | **No** |
| `zerobreak apply <caso> --module <m.py> --source <p.py> --yes` | Respalda, escribe atómicamente, corre `pytest` y hace commit o rollback. | **Sí** (con rollback) |
| `zerobreak verify <caso>` | Ejecuta `pytest` sobre el caso y devuelve su código de salida (`0` o `1`). | No |
| `zerobreak bench <caso>` | Compara tiempos de ejecución entre `*_legacy_anotado.py` y el módulo actual. | No |
| `zerobreak status [caso]` | Muestra si el caso tiene baseline en verde, su fecha UTC y los hashes registrados. | No |

---

## 5. Troubleshooting (Resolución de Problemas Frecuentes)

### Error 1: `"No hay baseline en verde para '<caso>'. Ejecuta 'baseline' primero."`
- **Causa:** Intentaste ejecutar `zerobreak apply` directamente sin haber corrido antes `baseline`, o el último intento de `baseline` falló en rojo.
- **Solución:** Ejecuta `zerobreak baseline <caso>` (o usa `zerobreak run <caso>`, que ejecuta el baseline automáticamente al inicio).

### Error 2: `"El módulo '<archivo>.py' cambió desde el baseline. Re-ejecuta 'baseline'."`
- **Causa:** Registraste un baseline, pero después editaste y guardaste `<archivo>.py` manualmente en tu editor. El hash SHA-256 actual ya no coincide con el guardado en `.zerobreak/state.json`.
- **Solución:** Es una medida de seguridad para no pisar ediciones manuales. Ejecuta `zerobreak baseline <caso>` para validar que tu edición manual pasa los tests y actualizar la huella SHA-256.

### Error 3: `"Contrato público roto: Símbolo público eliminado: '...' / Parámetros alterados en '...'"`
- **Causa:** Tu archivo `--source` eliminó una función/clase/método público (que no empieza por `_`) o cambió el nombre/orden de los argumentos respecto al archivo original.
- **Qué permite el verificador AST (`contracts.py`):**
  - ✅ Añadir o modificar anotaciones de tipo (`def sumar(a: int, b: int) -> int:`).
  - ✅ Añadir o mejorar docstrings y comentarios.
  - ✅ Crear nuevas funciones auxiliares privadas (`def _helper():`) o nuevas funciones públicas.
  - ❌ Renombrar parámetros (`def sumar(x, y):` cuando antes era `def sumar(a, b):`).
  - ❌ Eliminar o renombrar funciones/clases/métodos públicos existentes.
- **Solución:** Restaura los nombres exactos de las funciones y parámetros públicos en tu archivo de propuesta.

### Error 4: `"Tests en rojo tras aplicar; rollback realizado sobre '<archivo>.py'."`
- **Causa:** Tu propuesta respetaba las firmas públicas, pero introdujo un bug lógico que hizo fallar uno o más tests de `pytest`.
- **Estado de tus archivos:** Tranquilo, **`<archivo>.py` ha sido restaurado byte a byte a su versión original**. Revisa la traza de fallo de `pytest` impresa en consola, corrige tu archivo en `propuestas/` y vuelve a lanzar `zerobreak run`.

### Error 5: `"Lint falló sobre la propuesta; no se aplicaron cambios."` (al usar `--lint`)
- **Causa:** Pasaste la bandera `--lint` y `ruff` o `mypy` detectaron errores de estilo (PEP 8, imports sin usar) o discrepancias de tipos en tu propuesta.
- **Solución:** Revisa el bloque `--- ruff ---` o `--- mypy ---` en la salida de la terminal, corrige el archivo de propuesta y reintenta.
