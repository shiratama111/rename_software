@echo off
chcp 65001 > nul
title Stable Diffusionプロンプト抽出ツール

REM 実行ファイルが存在する場合はそちらを優先
if exist "dist\prompt_extractor_gui.exe" (
    start "" "dist\prompt_extractor_gui.exe"
    exit /b 0
)

REM Python環境の確認
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo.
    echo 以下の方法で対処してください：
    echo 1. Pythonをインストールする（https://python.org）
    echo 2. build.batを実行して実行ファイルを作成する
    pause
    exit /b 1
)

REM GUI版を起動
echo Stable Diffusionプロンプト抽出ツールを起動しています...
python "%~dp0main_gui.py"

if errorlevel 1 (
    echo.
    echo エラーが発生しました。
    echo 必要なパッケージがインストールされていない可能性があります。
    echo.
    echo 以下のコマンドを実行してください：
    echo pip install -r requirements.txt
    pause
)