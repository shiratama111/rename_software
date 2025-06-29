@echo off
chcp 65001 > nul
echo Stable Diffusionプロンプト抽出ツール
echo.

if "%~1"=="" (
    echo フォルダをドラッグ＆ドロップしてください
    pause
    exit /b 1
)

echo 対象フォルダ: %~1
echo.

python "%~dp0extract_prompts.py" "%~1"

echo.
echo 処理が完了しました。
pause