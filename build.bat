@echo off
chcp 65001 > nul
title ビルドスクリプト - プロンプト抽出ツール

echo ========================================
echo Stable Diffusionプロンプト抽出ツール
echo Windows実行ファイルビルド
echo ========================================
echo.

REM Python環境の確認
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo Pythonをインストールしてから再度実行してください。
    pause
    exit /b 1
)

REM 必要なパッケージのインストール
echo 依存パッケージをインストールしています...
pip install -r requirements.txt
if errorlevel 1 (
    echo エラー: パッケージのインストールに失敗しました。
    pause
    exit /b 1
)

echo.
echo PyInstallerをインストールしています...
pip install pyinstaller
if errorlevel 1 (
    echo エラー: PyInstallerのインストールに失敗しました。
    pause
    exit /b 1
)

echo.
echo ========================================
echo ビルドオプションを選択してください:
echo.
echo 1. GUI版のみビルド（推奨）
echo 2. CLI版とGUI版の両方をビルド
echo 3. キャンセル
echo.
choice /C 123 /M "選択してください"

if errorlevel 3 (
    echo ビルドをキャンセルしました。
    pause
    exit /b 0
)

if errorlevel 2 (
    echo.
    echo CLI版とGUI版の両方をビルドします...
    python build_gui_exe.py --both
    goto :check_result
)

if errorlevel 1 (
    echo.
    echo GUI版をビルドします...
    python build_gui_exe.py
    goto :check_result
)

:check_result
if errorlevel 1 (
    echo.
    echo ビルドに失敗しました。
    pause
    exit /b 1
)

echo.
echo ========================================
echo ビルドが完了しました！
echo.
echo 実行ファイルの場所:
echo   dist\prompt_extractor_gui.exe
echo.
echo 使い方:
echo   1. prompt_extractor_gui.exeをダブルクリック
echo   2. またはmain_gui.batを実行
echo ========================================
echo.

REM distフォルダを開くか確認
choice /C YN /M "distフォルダを開きますか？"
if errorlevel 2 goto :end
if errorlevel 1 (
    explorer dist
)

:end
pause