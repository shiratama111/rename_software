@echo off
chcp 65001 > nul
echo Stable Diffusionプロンプト抽出ツール - GUI版
echo.

REM Python環境の確認
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo.
    echo 実行ファイル版を使用してください。
    pause
    exit /b 1
)

REM GUI版を起動
echo フォルダ選択ダイアログを起動しています...
python "%~dp0extract_prompts_gui.py"

if errorlevel 1 (
    echo.
    echo エラーが発生しました。
    pause
)