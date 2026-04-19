from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import cv2

try:
    import mediapipe as mp
except ImportError:  # pragma: no cover
    mp = None


@dataclass
class MotionFrame:
    actions: dict[str, bool]
    fps: float


class MotionEngine:
    def __init__(self, cfg: dict[str, Any], preview: bool = True) -> None:
        self.cfg = cfg
        self.preview = preview
        self.cap: cv2.VideoCapture | None = None
        self.pose = None
        self.last_t = time.perf_counter()
        self.fps = 0.0
        self.smoothed = {"x": 0.0, "y": 0.0, "depth": 0.0}
        self.active_count = {k: 0 for k in ["w", "a", "s", "d", "space", "shift", "left_click", "right_click"]}

    def start(self) -> bool:
        self.cap = cv2.VideoCapture(self.cfg.get("camera_index", 0))
        if not self.cap or not self.cap.isOpened() or mp is None:
            return False
        self.pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        return True

    def stop(self) -> None:
        if self.pose:
            self.pose.close()
            self.pose = None
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()

    def _smooth(self, key: str, value: float) -> float:
        alpha = float(self.cfg.get("smoothing_alpha", 0.35))
        self.smoothed[key] = alpha * value + (1.0 - alpha) * self.smoothed[key]
        return self.smoothed[key]

    def _hysteresis(self, key: str, value: float, enter: float, exit_: float, positive: bool = True) -> bool:
        active_frames = self.active_count[key]
        threshold_on = enter if positive else -enter
        threshold_off = exit_ if positive else -exit_
        is_on = value > threshold_on if positive else value < threshold_on
        is_off = value < threshold_off if positive else value > threshold_off
        if active_frames == 0 and is_on:
            self.active_count[key] = 1
        elif active_frames > 0 and is_off:
            self.active_count[key] = 0
        return self.active_count[key] > 0

    def read(self) -> MotionFrame | None:
        if not self.cap or not self.pose:
            return None
        ok, frame = self.cap.read()
        if not ok:
            return None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)

        actions = {k: False for k in self.active_count.keys()}

        if result.pose_landmarks:
            lm = result.pose_landmarks.landmark
            ls, rs = lm[11], lm[12]
            lh, rh = lm[23], lm[24]
            lw, rw = lm[15], lm[16]

            torso_x = ((ls.x + rs.x) / 2.0 + (lh.x + rh.x) / 2.0) / 2.0
            torso_y = ((ls.y + rs.y) / 2.0 + (lh.y + rh.y) / 2.0) / 2.0
            shoulder_y = (ls.y + rs.y) / 2.0
            hip_y = (lh.y + rh.y) / 2.0
            torso_depth = shoulder_y - hip_y

            neutral = self.cfg["neutral_pose"]
            sens = self.cfg["sensitivity"]
            dx = self._smooth("x", torso_x - neutral["torso_x"])
            dy = self._smooth("y", torso_y - neutral["torso_y"])
            dz = self._smooth("depth", torso_depth - neutral["torso_depth"])

            enter = float(self.cfg.get("hysteresis_enter", 0.12))
            exit_ = float(self.cfg.get("hysteresis_exit", 0.08))

            actions["d"] = self._hysteresis("d", dx, sens["lean_x"], sens["lean_x"] * 0.7)
            actions["a"] = self._hysteresis("a", dx, sens["lean_x"], sens["lean_x"] * 0.7, positive=False)
            actions["s"] = self._hysteresis("s", dz, sens["lean_depth"], sens["lean_depth"] * 0.7)
            actions["w"] = self._hysteresis("w", dz, sens["lean_depth"], sens["lean_depth"] * 0.7, positive=False)
            actions["shift"] = self._hysteresis("shift", dy, sens["crouch_threshold"], sens["crouch_threshold"] * 0.7)

            arm_up = (lw.y < ls.y - sens["jump_arm_raise_threshold"]) and (rw.y < rs.y - sens["jump_arm_raise_threshold"])
            actions["space"] = arm_up

            # gesto simples mão fechada/aberta baseado em distância mão-ombro
            left_dist = abs(lw.x - ls.x) + abs(lw.y - ls.y)
            right_dist = abs(rw.x - rs.x) + abs(rw.y - rs.y)
            actions["left_click"] = left_dist < sens["left_click_fist_threshold"]
            actions["right_click"] = right_dist > sens["right_click_open_palm_threshold"]

            if self.preview and self.cfg.get("show_overlay", True):
                cv2.putText(frame, f"dx={dx:.3f} dy={dy:.3f} dz={dz:.3f}", (16, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        now = time.perf_counter()
        dt = max(now - self.last_t, 1e-6)
        self.fps = 1.0 / dt
        self.last_t = now

        if self.preview:
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (16, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 200, 255), 2)
            cv2.imshow("CaptureLive", frame)

        return MotionFrame(actions=actions, fps=self.fps)
