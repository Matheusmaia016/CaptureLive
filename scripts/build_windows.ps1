python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --name capturelive --collect-all mediapipe --collect-all cv2 --collect-all pynput capturelive/__main__.py
New-Item -ItemType Directory -Force -Path release | Out-Null
Copy-Item dist/capturelive.exe release/capturelive.exe -Force
Copy-Item capturelive.cmd release/capturelive.cmd -Force
Write-Host "Build concluído em release/capturelive.exe"
