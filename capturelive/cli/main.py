from __future__ import annotations

import json
import time
from pathlib import Path

import typer

from capturelive.config.config_manager import ConfigManager

app = typer.Typer(help="CaptureLive: assistente residente por gestos para Minecraft no Windows")


@app.command()
def start(
    no_preview: bool = typer.Option(False, "--no-preview", help="Executa sem janela de preview"),
    minimizado: bool = typer.Option(False, "--minimizado", help="Reduz logs no terminal"),
) -> None:
    from capturelive.core.service_loop import ServiceLoop

 codex/task-title-3iiu10

    import cv2
    from capturelive.vision.motion_engine import MotionEngine

 main
    cfgm = ConfigManager()
    cfg = cfgm.load()
    cfg["preview"] = not no_preview
    cfg["minimize_logs"] = minimizado
    ServiceLoop(cfg, demo=False, preview=not no_preview).run()


@app.command("test-camera")
def test_camera(duration: int = typer.Option(15, help="Duração em segundos")) -> None:
    import cv2

    cfg = ConfigManager().load()
    cap = cv2.VideoCapture(cfg.get("camera_index", 0))
    if not cap.isOpened():
        typer.echo("[ERRO] Webcam não encontrada.")
        raise typer.Exit(code=1)

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    typer.echo(f"Webcam OK | resolução={w}x{h} | fps={fps:.1f}")
    t0 = time.time()

    while time.time() - t0 < duration:
        ok, frame = cap.read()
        if not ok:
            break
        cv2.imshow("CaptureLive test-camera", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


@app.command()
def demo(no_preview: bool = typer.Option(False, "--no-preview")) -> None:
    from capturelive.core.service_loop import ServiceLoop

    cfg = ConfigManager().load()
    ServiceLoop(cfg, demo=True, preview=not no_preview).run()


@app.command()
def status() -> None:
    st = ConfigManager().load_status()
    typer.echo(json.dumps(st, indent=2, ensure_ascii=False))


@app.command()
def calibrate() -> None:
    import cv2
    from capturelive.vision.motion_engine import MotionEngine

    cfgm = ConfigManager()
    cfg = cfgm.load()
    typer.echo("Calibração guiada: fique em posição neutra por 5 segundos...")

    engine = MotionEngine(cfg, preview=True)
    if not engine.start():
        typer.echo("[ERRO] Não foi possível iniciar webcam/MediaPipe para calibrar.")
        raise typer.Exit(code=1)

    samples = []
    start_t = time.time()
    while time.time() - start_t < 5:
        frame = engine.read()
        if frame:
            samples.append(engine.smoothed.copy())
        if cv2.waitKey(1) & 0xFF == 27:
            break

    engine.stop()
    if not samples:
        typer.echo("[ERRO] Sem amostras de pose para calibração.")
        raise typer.Exit(code=1)

    cfg["neutral_pose"]["torso_x"] = sum(s["x"] for s in samples) / len(samples) + cfg["neutral_pose"]["torso_x"]
    cfg["neutral_pose"]["torso_y"] = sum(s["y"] for s in samples) / len(samples) + cfg["neutral_pose"]["torso_y"]
    cfg["neutral_pose"]["torso_depth"] = sum(s["depth"] for s in samples) / len(samples) + cfg["neutral_pose"]["torso_depth"]

    sens = cfg["sensitivity"]
    sens["lean_x"] = float(typer.prompt("Sensibilidade lateral (lean_x)", default=sens["lean_x"]))
    sens["lean_depth"] = float(typer.prompt("Sensibilidade frente/trás (lean_depth)", default=sens["lean_depth"]))
    sens["crouch_threshold"] = float(typer.prompt("Sensibilidade agachar", default=sens["crouch_threshold"]))

    cfgm.save(cfg)
    typer.echo("Calibração concluída e salva no config JSON.")


@app.command()
def config(
 codex/task-title-3iiu10
    show: bool = typer.Option(False, "--show", help="Mostra o JSON atual"),
    no_show: bool = typer.Option(False, "--no-show", help="Não imprime JSON no terminal"),

    show: bool = typer.Option(True, "--show/--no-show", help="Mostra o JSON atual"),
 main
    edit: bool = typer.Option(False, "--edit", help="Abre o arquivo de config no editor padrão"),
    reset: bool = typer.Option(False, "--reset", help="Restaura configuração padrão"),
) -> None:
    cfgm = ConfigManager()
    if reset:
        cfgm.reset()
        typer.echo("Configuração resetada para o padrão.")
    if edit:
        import os

        os.startfile(str(cfgm.config_path))  # type: ignore[attr-defined]
 codex/task-title-3iiu10
    should_show = show or (not no_show and not edit)
    if should_show:

    if show:
 main
        typer.echo(cfgm.config_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    app()
