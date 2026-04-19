@echo off
setlocal
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --name capturelive --collect-all mediapipe --collect-all cv2 --collect-all pynput capturelive/__main__.py
if not exist release mkdir release
copy /Y dist\capturelive.exe release\capturelive.exe
copy /Y capturelive.cmd release\capturelive.cmd
echo Build concluído em release\capturelive.exe
endlocal
