"""Configuración de recolección de pytest para ZeroBreak.

Excluye de la recolección los respaldos didácticos `*_legacy_anotado.py`,
que no son tests y provocarían duplicaciones o falsos negativos.
"""

collect_ignore_glob = ["**/*_legacy_anotado.py"]
