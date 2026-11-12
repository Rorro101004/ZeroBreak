# Benchmarks — caso `tienda`

Comparación entre el código original (`*_legacy_anotado.py`) y el
refactorizado. Medición con `timeit` (mejor de varias repeticiones).
Los valores son orientativos y dependen de la máquina.

Reproducir: `zerobreak bench tienda`

## `buscar_productos_duplicados`

| n | legacy (ms) | refactor (ms) | speedup |
|---:|---:|---:|---:|
| 1000 | 9.259 | 0.069 | 134× |
| 2000 | 35.393 | 0.132 | 268× |
| 5000 | 217.054 | 0.325 | 667× |

## `generar_recibo_texto`

| n | legacy (ms) | refactor (ms) | speedup |
|---:|---:|---:|---:|
| 500 | 0.257 | 0.171 | 2× |
| 1000 | 0.527 | 0.358 | 1× |
| 2000 | 1.087 | 0.643 | 2× |

## Conclusiones

- `buscar_productos_duplicados`: mejora real de complejidad (O(n²) → O(n)). Al quintuplicar n, el legacy crece ~×32 (cuadrático) mientras el refactor crece ~×5 (lineal).
- `generar_recibo_texto`: en CPython, `+=` sobre una variable local aplica una optimización in-place, por lo que la mejora medida es modesta (~2×). El cambio a `"".join(...)` es idiomático y **garantiza** linealidad en cualquier implementación, pero NO debe presentarse como una mejora de complejidad medida.

