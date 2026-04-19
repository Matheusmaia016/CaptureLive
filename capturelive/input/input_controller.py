from __future__ import annotations

import time
from typing import Any

from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
from pynput.mouse import Button, Controller as MouseController


class InputController:
    KEY_MAP = {
        "w": "w",
        "a": "a",
        "s": "s",
        "d": "d",
        "space": Key.space,
        "shift": Key.shift,
    }

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.held: set[str] = set()
        self.last_click = {"left_click": 0.0, "right_click": 0.0}

    def _press(self, key_name: str) -> None:
        if key_name in self.held:
            return
        self.keyboard.press(self.KEY_MAP[key_name])
        self.held.add(key_name)

    def _release(self, key_name: str) -> None:
        if key_name not in self.held:
            return
        self.keyboard.release(self.KEY_MAP[key_name])
        self.held.remove(key_name)

    def release_all(self) -> None:
        for key in list(self.held):
            self._release(key)

    def apply_actions(self, actions: dict[str, bool], allow_output: bool) -> None:
        if not allow_output:
            self.release_all()
            return

        for key in ["w", "a", "s", "d", "space", "shift"]:
            if actions.get(key, False):
                self._press(key)
            else:
                self._release(key)

        now = time.time() * 1000.0
        if actions.get("left_click", False) and now - self.last_click["left_click"] > self.cfg["output"]["left_click_cooldown_ms"]:
            self.mouse.click(Button.left, 1)
            self.last_click["left_click"] = now

        if actions.get("right_click", False) and now - self.last_click["right_click"] > self.cfg["output"]["right_click_cooldown_ms"]:
            self.mouse.click(Button.right, 1)
            self.last_click["right_click"] = now

    def shutdown(self) -> None:
        self.release_all()
