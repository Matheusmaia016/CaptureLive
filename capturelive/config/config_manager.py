from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "config" / "default_config.json"
USER_DIR = Path.home() / ".capturelive"
USER_CONFIG_PATH = USER_DIR / "config.json"
STATUS_PATH = USER_DIR / "status.json"


@dataclass
class ConfigManager:
    config_path: Path = USER_CONFIG_PATH

    def ensure(self) -> None:
        USER_DIR.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.reset()

    def load(self) -> dict[str, Any]:
        self.ensure()
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def save(self, config: dict[str, Any]) -> None:
        self.ensure()
        self.config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    def reset(self) -> dict[str, Any]:
        data = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
        self.save(data)
        return data

    def save_status(self, status: dict[str, Any]) -> None:
        USER_DIR.mkdir(parents=True, exist_ok=True)
        STATUS_PATH.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_status(self) -> dict[str, Any]:
        if not STATUS_PATH.exists():
            return {
                "service_running": False,
                "minecraft_detected": False,
                "minecraft_focused": False,
                "webcam_active": False,
                "capture_active": False,
                "edition": "unknown",
            }
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
