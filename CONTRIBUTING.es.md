# Contribuir a ZeroBreak

[English](CONTRIBUTING.md) | **Español**

## El ciclo de cinco fases

Todo cambio en un caso bajo `test_cases/<caso>/` sigue el Safe Refactor Loop:

1. **Análisis de contratos** — lee el código y su `test_*.py`; inventaría la API pública (nombres, firmas, excepciones, retornos).
2. **Baseline `pytest`** — debe estar 100% verde antes de tocar nada.
3. **Propuesta** — diseña la mejora (rendimiento, PEP 484/585/604, docstrings) sin aplicarla.
4. **Verificación en sandbox** — valida el cambio sin escribir en disco.
5. **Confirmación humana** — después crea el respaldo didáctico y aplica en disco.

Las fases 1–4 nunca escriben en disco. Solo la fase 5 persiste cambios.

## Añadir un caso nuevo

1. Crea la carpeta `test_cases/<nombre_caso>/`.
2. Añade el módulo de implementación (p. ej. `micaso.py`).
3. Añade la suite `test_micaso.py` junto a él; importa con `from micaso import ...`.
4. Ejecuta `pytest test_cases/<nombre_caso>` hasta que esté verde.

## Ejecutar los tests

```bash
pytest                          # todos los casos + los tests del framework (tests/)
pytest test_cases/<nombre_caso> # un caso
```

## Interfaz de línea de comandos

La CLI `zerobreak` hace cumplir la parte mecánica del ciclo:

```bash
pip install -e ".[dev]"
zerobreak baseline <caso>
zerobreak apply <caso> --module <modulo>.py --source propuesta.py --yes
```

Se niega a aplicar sin un baseline verde, crea primero el respaldo didáctico y revierte automáticamente si los tests fallan.

## Respaldos didácticos

Cuando se aplica un refactor, el código original se conserva como
`<modulo>_legacy_anotado.py` en la misma carpeta, anotado inline con el smell
exacto, por qué perjudica y la solución aplicada. Estos archivos **no son
tests** y se excluyen de la recolección vía `conftest.py` y `python_files`.

## Estilo

- Python 3.12+.
- PEP 8, tipado (PEP 484 / 585 / 604) y docstrings Google Style.
- Preferir la biblioteca estándar (`itertools`, `collections`, `functools`).
- Nunca modificar nombres/firmas públicas ni las aserciones de tests existentes.

## Licencia

Al contribuir, aceptas que tus aportes se licencian bajo la licencia MIT (ver `LICENSE`).
