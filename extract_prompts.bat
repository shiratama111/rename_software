@echo off
chcp 65001 > nul
echo Stable Diffusionプロンプト抽出ツール
echo.

if "%~1"=="" (
    echo ============================================================
    echo 使い方:
    echo.
    echo 1. PNG画像が入っているフォルダを用意してください
    echo 2. そのフォルダをこのファイルにドラッグ＆ドロップしてください
    echo.
    echo または、このバッチファイルをダブルクリックして、
    echo 現在のフォルダから画像を検索することもできます。
    echo ============================================================
    echo.
    echo 現在のフォルダで実行しますか？ (Y/N)
    choice /C YN /M "選択してください"
    if errorlevel 2 (
        echo 終了します。
        pause
        exit /b 0
    )
    echo.
    python "%~dp0extract_prompts.py"
) else (
    echo 対象フォルダ: %~1
    echo.
    python "%~dp0extract_prompts.py" "%~1"
)

REM エラーレベルをチェック（必要に応じて）
if errorlevel 1 (
    echo.
    echo エラーが発生しました。上記のメッセージを確認してください。
)

echo.
pause