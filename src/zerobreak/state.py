"""Estado persistente del baseline (``.zerobreak/state.json``)."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_DIR = ".zerobreak"
STATE_FILE = "state.json"


def state_path(root: Path) -> Path:
    """Ubicación del archivo de estado para ``root``."""
    return root / STATE_DIR / STATE_FILE


def sha256_file(path: Path) -> str:
    """Devuelve el digest SHA-256 (hex) del archivo ``path``."""
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def load_state(root: Path) -> dict[str, Any]:
    """Carga el estado; devuelve un esqueleto vacío si no existe."""
    path = state_path(root)
    if not path.is_file():
        return {"cases": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(root: Path, state: dict[str, Any]) -> None:
    """Persiste ``state`` en disco."""
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def get_entry(root: Path, case_name: str) -> dict[str, Any] | None:
    """Devuelve la entrada guardada de ``case_name`` si existe."""
    return load_state(root).get("cases", {}).get(case_name)


def record_baseline(root: Path, case_name: str, modules: list[Path]) -> None:
    """Registra un baseline verde y los hashes de ``modules``.

    Args:
        root: Raíz del proyecto.
        case_name: Nombre del caso.
        modules: Módulos de implementación cuyo hash se guarda.
    """
    state = load_state(root)
    entry = state.setdefault("cases", {}).setdefault(case_name, {})
    entry["baseline_ok"] = True
    entry["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entry["modules"] = {module.name: sha256_file(module) for module in modules}
    save_state(root, state)
