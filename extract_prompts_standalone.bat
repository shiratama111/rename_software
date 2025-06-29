@echo off
chcp 65001 > nul
echo Stable Diffusionプロンプト抽出ツール（スタンドアロン版）
echo.

if "%~1"=="" (
    echo ============================================================
    echo Stable Diffusionプロンプト抽出ツール
    echo ============================================================
    echo.
    echo 実行方法を選択してください:
    echo.
    echo 1. フォルダ選択ダイアログを開く（推奨）
    echo 2. 現在のフォルダで実行
    echo 3. 使い方を表示
    echo 4. 終了
    echo.
    choice /C 1234 /M "選択してください"
    
    if errorlevel 4 (
        echo 終了します。
        pause
        exit /b 0
    )
    
    if errorlevel 3 (
        echo.
        echo ============================================================
        echo 使い方:
        echo.
        echo 方法1: このファイルをダブルクリックして、
        echo        メニューから「1」を選択
        echo.
        echo 方法2: PNG画像フォルダをこのファイルに
        echo        ドラッグ＆ドロップ
        echo.
        echo 方法3: コマンドラインから実行
        echo        extract_prompts.exe "フォルダパス"
        echo ============================================================
        pause
        "%~f0"
        exit /b 0
    )
    
    if errorlevel 2 (
        echo.
        "%~dp0extract_prompts.exe"
    )
    
    if errorlevel 1 (
        echo.
        echo フォルダ選択モードで起動しています...
        "%~dp0extract_prompts.exe"
    )
) else (
    echo 対象フォルダ: %~1
    echo.
    "%~dp0extract_prompts.exe" "%~1"
)

REM エラーレベルをチェック（必要に応じて）
if errorlevel 1 (
    echo.
    echo エラーが発生しました。上記のメッセージを確認してください。
) else (
    echo.
    echo ============================================================
    echo 処理が正常に完了しました。
    echo.
    echo 出力ファイルは選択したフォルダ内に保存されています。
    echo ファイル名: prompts_日付_時刻.txt
    echo ============================================================
)

echo.
pause