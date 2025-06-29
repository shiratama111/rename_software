@echo off
chcp 65001 > nul
echo ========================================
echo Stable Diffusionプロンプト抽出ツール
echo 自動セットアップ＆ビルドスクリプト
echo ========================================
echo.

REM Pythonがインストールされているか確認
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo Python 3.8以上をインストールしてください。
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Pythonが検出されました。
python --version
echo.

REM 仮想環境の作成（既存の場合はスキップ）
if not exist "venv" (
    echo 仮想環境を作成しています...
    python -m venv venv
    if errorlevel 1 (
        echo エラー: 仮想環境の作成に失敗しました。
        pause
        exit /b 1
    )
) else (
    echo 既存の仮想環境を使用します。
)

REM 仮想環境の有効化
echo 仮想環境を有効化しています...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo エラー: 仮想環境の有効化に失敗しました。
    pause
    exit /b 1
)

REM pipのアップグレード
echo.
echo pipをアップグレードしています...
python -m pip install --upgrade pip

REM 必要なパッケージのインストール
echo.
echo 必要なパッケージをインストールしています...
pip install -r requirements.txt
if errorlevel 1 (
    echo エラー: パッケージのインストールに失敗しました。
    pause
    exit /b 1
)

REM PyInstallerのインストール
echo.
echo PyInstallerをインストールしています...
pip install pyinstaller
if errorlevel 1 (
    echo エラー: PyInstallerのインストールに失敗しました。
    pause
    exit /b 1
)

REM 実行ファイルのビルド
echo.
echo 実行ファイルをビルドしています...
python build_exe.py
if errorlevel 1 (
    echo エラー: ビルドに失敗しました。
    pause
    exit /b 1
)

REM ビルド成功
echo.
echo ========================================
echo ビルドが完了しました！
echo.
echo 実行ファイル: dist\extract_prompts.exe
echo.
echo 使用方法:
echo 1. dist\extract_prompts.exe を任意の場所にコピー
echo 2. extract_prompts_standalone.bat も同じ場所にコピー
echo 3. 画像フォルダをextract_prompts_standalone.batに
echo    ドラッグ＆ドロップ
echo ========================================
echo.
pause