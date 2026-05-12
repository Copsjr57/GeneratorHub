import json
import os
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from utils.paths import data_dir


_LOCK = threading.RLock()


def _read_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: str, obj: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


class AppStorage:
    def __init__(self) -> None:
        self._settings_path = os.path.join(data_dir(), "settings.json")
        self._state_path = os.path.join(data_dir(), "state.json")

        with _LOCK:
            self._settings: Dict[str, Any] = _read_json(self._settings_path, {})
            self._state: Dict[str, Any] = _read_json(
                self._state_path,
                {"favorites": [], "recent": [], "export_history": []},
            )

    # ---------------- Settings ----------------
    def get_setting(self, key: str, default: Any = None) -> Any:
        with _LOCK:
            return self._settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        with _LOCK:
            self._settings[key] = value
            _write_json(self._settings_path, self._settings)

    # ---------------- Favorites ----------------
    def list_favorites(self) -> List[str]:
        with _LOCK:
            return list(self._state.get("favorites", []))

    def toggle_favorite(self, generator_id: str) -> bool:
        with _LOCK:
            fav = self._state.setdefault("favorites", [])
            if generator_id in fav:
                fav.remove(generator_id)
                _write_json(self._state_path, self._state)
                return False
            fav.append(generator_id)
            _write_json(self._state_path, self._state)
            return True

    def is_favorite(self, generator_id: str) -> bool:
        with _LOCK:
            return generator_id in self._state.get("favorites", [])

    # ---------------- Recent ----------------
    def list_recent(self) -> List[str]:
        with _LOCK:
            return list(self._state.get("recent", []))

    def add_recent(self, generator_id: str) -> None:
        with _LOCK:
            recent = self._state.setdefault("recent", [])
            if generator_id in recent:
                recent.remove(generator_id)
            recent.insert(0, generator_id)
            del recent[12:]
            _write_json(self._state_path, self._state)

    # ---------------- Export history ----------------
    def add_export_history(self, item: Dict[str, Any]) -> None:
        with _LOCK:
            hist = self._state.setdefault("export_history", [])
            hist.insert(0, item)
            del hist[50:]
            _write_json(self._state_path, self._state)

    def list_export_history(self) -> List[Dict[str, Any]]:
        with _LOCK:
            return list(self._state.get("export_history", []))
