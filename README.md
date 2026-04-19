# CaptureLive

CaptureLive é um companion app para Windows que fica residente e **ativa automaticamente** o controle por movimentos quando o Minecraft está aberto e em foco.

## Objetivo de uso (sem ações manuais repetidas)
1. Abra o terminal na pasta do projeto.
2. Execute `capturelive start` (ou `capturelive.cmd start` no Windows).
3. Deixe rodando.
4. Abra/foque o Minecraft.
5. O CaptureLive detecta o jogo automaticamente e inicia captura/inputs.

Quando o Minecraft perde foco ou fecha, o CaptureLive pausa captura e envio de input imediatamente.

---

## Comandos
- `capturelive start`
- `capturelive calibrate`
- `capturelive test-camera`
- `capturelive demo`
- `capturelive status`
- `capturelive config`

### `capturelive start`
- Inicia serviço residente.
- Monitora Minecraft Java/Bedrock por título + processo + foco.
- Ativa webcam e rastreio quando Minecraft entra em foco.
- Logs em PT-BR:
  - `Minecraft detectado`
  - `Capture ativa`
  - `Minecraft fora de foco, captura pausada`
- ESC encerra modo ativo.
- CTRL+C encerra serviço inteiro.

### `capturelive calibrate`
- Calibração guiada de posição neutra.
- Ajuste de sensibilidade.
- Salva em JSON (`%USERPROFILE%\.capturelive\config.json`).

### `capturelive test-camera`
- Testa webcam com preview.
- Exibe resolução e FPS.

### `capturelive demo`
- Detecta movimentos e imprime no terminal quais comandos seriam enviados.
- Não injeta teclado/mouse reais.

### `capturelive status`
- Mostra status persistido do serviço:
  - rodando ou não
  - Minecraft detectado/focado
  - webcam ativa
  - captura ativa/pausada

### `capturelive config`
- Mostra config atual.
- `--edit` abre JSON no editor padrão (Windows).
- `--reset` restaura padrão.

---

## Mapeamento inicial de gestos
- Inclinar tronco para frente = `W`
- Inclinar tronco para trás = `S`
- Inclinar para esquerda = `A`
- Inclinar para direita = `D`
- Levantar dois braços = `Space`
- Agachar corpo = `Shift`
- Gesto simples de mão fechada = clique esquerdo
- Gesto simples de mão aberta = clique direito

Inclui suavização, histerese, debounce básico por cooldown de clique e manutenção de tecla enquanto gesto estiver ativo.

---

## Segurança de input
- Input só é permitido com Minecraft detectado **e em foco**.
- Perdeu foco: solta todas as teclas imediatamente.
- Fail-safe de limpeza no encerramento para evitar `W/A/S/D/Shift` presos.

---

## Instalação de desenvolvimento
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Executar local:
```bash
python -m capturelive start
```

---

## Build standalone (Windows)
### CMD
```bat
scripts\build_windows.bat
```

### PowerShell
```powershell
./scripts/build_windows.ps1
```

Saída esperada:
- `dist/capturelive.exe`
- cópia em `release/capturelive.exe`
- wrapper em `release/capturelive.cmd`


### Se aparecer `ModuleNotFoundError: No module named "capturelive.cli.main"`
Faça build limpo com os scripts atualizados (eles já adicionam `--paths .`, `--hidden-import` e `--collect-submodules capturelive`):

```bat
scripts\build_windows.bat
```

ou

```powershell
./scripts/build_windows.ps1
```

Apague builds antigos (`build/`, `dist/`, `release/capturelive.exe`) antes de gerar novamente.

---

## Wrapper `capturelive.cmd`
O arquivo na raiz prioriza:
1. `release\capturelive.exe`
2. `dist\capturelive.exe`
3. fallback para `python -m capturelive`

Assim você pode usar:
```bat
capturelive.cmd start
```

---

## Detecção automática do Minecraft
O módulo responsável é:
- `capturelive/minecraft/minecraft_detector.py`

Estratégia de prioridade:
1. título da janela ativa
2. processo compatível
3. confirmação de foco (foreground window)
4. só então libera envio de input

---

## Estrutura
```text
capturelive/
  cli/
  core/
  vision/
  input/
  minecraft/
  config/
  utils/
scripts/
```

