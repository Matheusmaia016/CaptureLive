from __future__ import annotations

import time
from typing import Any

import cv2
from pynput import keyboard

from capturelive.config.config_manager import ConfigManager
from capturelive.input.input_controller import InputController
from capturelive.minecraft.minecraft_detector import MinecraftDetector
from capturelive.utils.logger import log
from capturelive.vision.motion_engine import MotionEngine


class ServiceLoop:
    def __init__(self, cfg: dict[str, Any], demo: bool = False, preview: bool = True) -> None:
        self.cfg = cfg
        self.demo = demo
        self.preview = preview
        self.detector = MinecraftDetector(cfg)
        self.input = InputController(cfg)
        self.motion: MotionEngine | None = None
        self.running = True
        self.capture_active = False
        self.config_manager = ConfigManager()

    def _update_status(self, detected: bool, focused: bool, webcam: bool, active: bool, edition: str) -> None:
        self.config_manager.save_status(
            {
                "service_running": True,
                "minecraft_detected": detected,
                "minecraft_focused": focused,
                "webcam_active": webcam,
                "capture_active": active,
                "edition": edition,
                "updated_at": time.time(),
            }
        )

    def _on_key(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if key == keyboard.Key.esc:
            log("ESC pressionado. Encerrando modo ativo.", "WARN")
            self.running = False

    def run(self) -> None:
        poll_ms = self.cfg["minecraft_detection"]["poll_interval_ms"]
        listener = keyboard.Listener(on_press=self._on_key)
        listener.start()
        log("Serviço residente iniciado. Aguardando Minecraft em foco...")

        try:
            while self.running:
                state = self.detector.poll()
                allow_output = state.detected and state.focused

                if allow_output and self.motion is None:
                    self.motion = MotionEngine(self.cfg, preview=self.preview)
                    if self.motion.start():
                        log(f"Minecraft detectado ({state.edition}). Capture ativa.")
                        self.capture_active = True
                    else:
                        log("Falha ao iniciar webcam/MediaPipe.", "ERROR")
                        self.motion = None
                        self.capture_active = False

                if (not allow_output) and self.motion is not None:
                    log("Minecraft fora de foco, captura pausada.", "WARN")
                    self.motion.stop()
                    self.motion = None
                    self.input.release_all()
                    self.capture_active = False

                if self.motion is not None:
                    frame = self.motion.read()
                    if frame:
                        if self.demo:
                            actions = [k for k, v in frame.actions.items() if v]
                            if actions:
                                log(f"[DEMO] Comandos: {', '.join(actions)}")
                        else:
                            self.input.apply_actions(frame.actions, allow_output=allow_output)

                    if cv2.waitKey(1) & 0xFF == 27:
                        log("ESC detectado na janela de preview.", "WARN")
                        self.running = False

                self._update_status(state.detected, state.focused, self.motion is not None, self.capture_active, state.edition)
                time.sleep(poll_ms / 1000.0)

        except KeyboardInterrupt:
            log("CTRL+C recebido. Encerrando serviço inteiro.", "WARN")
        finally:
            listener.stop()
            if self.motion:
                self.motion.stop()
            self.input.shutdown()
            self.config_manager.save_status(
                {
                    "service_running": False,
                    "minecraft_detected": False,
                    "minecraft_focused": False,
                    "webcam_active": False,
                    "capture_active": False,
                    "edition": "none",
                    "updated_at": time.time(),
                }
            )
            log("CaptureLive finalizado com limpeza de input.")
