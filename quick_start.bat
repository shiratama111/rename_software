@echo off
chcp 65001 > nul
echo ========================================
echo プロンプト抽出ツール - クイックスタート
echo ========================================
echo.

REM 実行ファイルが存在するか確認
if exist "dist\extract_prompts.exe" (
    echo 実行ファイルが見つかりました。
    goto :run_exe
)

REM 実行ファイルがない場合、ビルドを試みる
echo 実行ファイルが見つかりません。
echo セットアップを開始します...
echo.

REM setup_and_build.batを実行
if exist "setup_and_build.bat" (
    call setup_and_build.bat
    if errorlevel 1 (
        echo セットアップに失敗しました。
        pause
        exit /b 1
    )
) else (
    echo エラー: setup_and_build.batが見つかりません。
    pause
    exit /b 1
)

:run_exe
REM フォルダが指定されているか確認
if "%~1"=="" (
    echo.
    echo 使用方法: 画像フォルダをこのファイルにドラッグ＆ドロップしてください
    echo.
    pause
    exit /b 1
)

REM プロンプト抽出を実行
echo.
echo 対象フォルダ: %~1
echo 処理を開始します...
echo.

dist\extract_prompts.exe "%~1"

echo.
echo 処理が完了しました。
pause