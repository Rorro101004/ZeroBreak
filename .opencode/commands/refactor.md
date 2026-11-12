---
description: Ejecuta el ciclo de refactorización segura (5 fases) sobre un caso de prueba en test_cases/
agent: plan
---

Ejecuta el ciclo completo de refactorización segura de ZeroBreak sobre el objetivo: $ARGUMENTS

Convención modular: cada caso de prueba vive aislado en `test_cases/<nombre_caso>/`, con su código y su suite `test_*.py` juntos. El objetivo puede ser el directorio de un caso (p. ej. `test_cases/tienda`) o un archivo concreto dentro de él.

Sigue estrictamente `AGENTS.md` y `specs/features/001-safe-refactor-loop.md`:

1. **Resolución del objetivo** — Si `$ARGUMENTS` está vacío, lista los subdirectorios de `test_cases/` (los casos disponibles) y detente pidiendo que se elija uno. Si hay argumento, trátalo como el caso objetivo a refactorizar.
2. **Análisis** — Lee el código del caso objetivo y su `test_*.py`; inventaría la API pública exacta (nombres, firmas, excepciones, retornos).
3. **Baseline** — Ejecuta `pytest <ruta_del_sujeto>` usando la ruta recibida en `$ARGUMENTS` (directorio o archivo del caso, p. ej. `pytest test_cases/tienda`) y confirma 100% verde. Si falla, detente y repórtalo sin continuar.
4. **Propuesta** — Diseña la mejora según `specs/constitution.md` (rendimiento, PEP 484/585, docstrings, código limpio). No apliques cambios todavía.
5. **Verificación** — Valida la propuesta con la skill `python-refactor-guard` (o el subagente `refactor-guard`) y muestra el informe. Puedes comprobar el cambio en sandbox/memoria, sin escribir en disco.
6. **Confirmación** — Presenta el diff y las justificaciones técnicas. No escribas en disco sin aprobación explícita del usuario.
7. **Respaldo didáctico y aplicación (solo tras la confirmación humana)** — Al recibir el visto bueno:
   - **7.1 Respaldo** — Crea `<modulo>_legacy_anotado.py` en la carpeta del caso (p. ej. `test_cases/tienda/tienda_legacy_anotado.py`) con el código original **íntegro**, intercalado con comentarios inline que señalen cada ineficiencia/code smell, por qué penaliza el rendimiento o la mantenibilidad, y la solución aplicada.
   - **7.2 Aplicación** — Sobrescribe el código objetivo y re-ejecuta `pytest test_cases/<caso>`.
   - Recuerda: los archivos `*_legacy_anotado.py` **no son tests** y no deben ejecutarse con `pytest` (aislados vía `python_files` y `collect_ignore_glob`).
   - **Nota:** este comando fija `agent: plan` (explora y propone, no escribe). Para ejecutar 7.1/7.2 hay que pasar a un agente con permiso de escritura (p. ej. Build); `opencode.json` volverá a pedir confirmación antes de escribir sobre `test_cases/**`.
