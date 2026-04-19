from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psutil

try:
    import win32gui
    import win32process
except ImportError:  # pragma: no cover
    win32gui = None
    win32process = None


@dataclass
class MinecraftState:
    detected: bool
    focused: bool
    edition: str
    window_title: str
    process_name: str


class MinecraftDetector:
    def __init__(self, cfg: dict[str, Any]) -> None:
        det_cfg = cfg["minecraft_detection"]
        self.title_keywords = [k.lower() for k in det_cfg["window_title_keywords"]]
        self.process_names = [p.lower() for p in det_cfg["process_names"]]

    def _get_foreground(self) -> tuple[str, str]:
        if not win32gui or not win32process:
            return "", ""
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return "", ""
        title = (win32gui.GetWindowText(hwnd) or "").strip()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc_name = ""
        try:
            proc_name = psutil.Process(pid).name()
        except Exception:
            proc_name = ""
        return title, proc_name

    def _infer_edition(self, title: str, process_name: str) -> str:
        t = title.lower()
        p = process_name.lower()
        if "minecraft.windows" in p or "uwp" in p or "bedrock" in t:
            return "bedrock"
        if "javaw.exe" == p or "java" in p or "java edition" in t:
            return "java"
        if "minecraft" in t:
            return "unknown"
        return "none"

    def poll(self) -> MinecraftState:
        title, proc = self._get_foreground()
        t = title.lower()
        p = proc.lower()

        title_match = any(key in t for key in self.title_keywords)
        process_match = p in self.process_names
        focused = bool(title and (title_match or process_match))

        detected = focused
        if not detected:
            for proc_info in psutil.process_iter(["name"]):
                name = (proc_info.info.get("name") or "").lower()
                if name in self.process_names:
                    detected = True
                    break

        return MinecraftState(
            detected=detected,
            focused=focused,
            edition=self._infer_edition(title, proc),
            window_title=title,
            process_name=proc,
        )
