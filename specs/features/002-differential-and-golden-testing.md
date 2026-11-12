# Feature 002: Differential Testing & Golden Master Scaffolding

## Estado
Vigente

## Objetivo
Evolucionar el sistema de verificación de ZeroBreak más allá de los tests unitarios basados en ejemplos fijos, proporcionando:
1. **Scaffolding de Tests Golden Master:** Generación automática de suites de caracterización determinista cuando un archivo objetivo legacy no dispone de pruebas previas.
2. **Testing Diferencial Basado en Propiedades (Hypothesis):** Ejecución masiva y adversarial de cientos de combinaciones de entradas generadas aleatoriamente para verificar la equivalencia estricta entre la versión previa (`*_legacy_anotado.py`) y la versión refactorizada.

---

## 1. Scaffolding de Tests y Golden Master

### 1.1 Comando y CLI
- **Subcomando explícito:**
  ```bash
  zerobreak scaffold-tests <archivo.py> [--out <ruta_test.py>]
  ```
- **Integración en `run` (flag opcional):**
  ```bash
  zerobreak run --target <archivo.py> --scaffold-tests
  ```
  Si no se encuentra una suite de pruebas para `<archivo.py>`, genera automáticamente `tests/test_autogen_<stem>.py` y procede con el ciclo transaccional.

### 1.2 Extracción de API y Caracterización AST
1. Analiza el AST de nivel superior del archivo objetivo mediante `contracts.inspect_functions`.
2. Identifica funciones públicas (cuyo nombre no empiece por `_`).
3. Para cada función, carga el módulo en memoria y ejecuta una serie de vectores de entrada semilla representativos (fronteras numéricas, strings vacíos/poblados, listas vacías y con elementos repetidos).
4. Congela el comportamiento observable:
   - Si retorna un valor determinista con representación exacta (`repr`), genera:
     ```python
     assert modulo.funcion(*semilla) == resultado_congelado
     ```
   - Si lanza una excepción esperada (ej. `ZeroDivisionError`), genera:
     ```python
     with pytest.raises(ZeroDivisionError):
         modulo.funcion(*semilla)
     ```

---

## 2. Testing Diferencial con Hypothesis

### 2.1 Principio de Equivalencia Funcional
El archivo autogenerado incluye tests de propiedades con `@given(...)` de `hypothesis`:
$$\forall x \in \text{Domain}(f): \quad f_{\text{legacy}}(x) == f_{\text{refactor}}(x)$$

### 2.2 Dinámica de Respaldo y Rollback
1. **Carga dual:** El test diferencial resuelve dinámicamente el módulo actual `<modulo>.py` y su respaldo `<modulo>_legacy_anotado.py` (si existe).
2. **Fase Baseline:** Si el respaldo aún no se ha generado, el test valida determinismo y ausencia de excepciones inesperadas sobre el módulo actual.
3. **Fase Verificación Post-Apply:** Una vez aplicado el refactor en RAM/disco, el test ejecuta cientos de combinaciones aleatorias. Si `hypothesis` encuentra un contraejemplo donde el nuevo código difiere del legacy o rompe un caso borde, `pytest` falla en rojo y dispara el **Rollback automático** de `zerobreak apply`.

---

## 3. Restricciones y Compatibilidad (Zero Breakage)
- **Cero dependencias obligatorias en runtime:** El paquete `zerobreak` sigue funcionando con biblioteca estándar; `hypothesis` se carga únicamente en la suite de pruebas generada o entornos con `[dev]`/`[testing]`.
- **Inmutabilidad de contratos existentes:** Las funciones públicas de `contracts.py`, `cases.py` y `apply.py` conservan sus firmas y excepciones originales.
- **Trazabilidad:** Cada suite generada se registra en `PROGRESS.md` y queda lista para ser auditada por desarrolladores humanos o agentes de IA.
