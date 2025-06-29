@echo off
chcp 65001 > nul
echo ========================================
echo ポータブル版パッケージ作成スクリプト
echo ========================================
echo.

REM distフォルダが存在するか確認
if not exist "dist\extract_prompts.exe" (
    echo エラー: extract_prompts.exeが見つかりません。
    echo 先にsetup_and_build.batを実行してください。
    pause
    exit /b 1
)

REM ポータブル版用のフォルダを作成
set PORTABLE_DIR=SD_Prompt_Extractor_Portable
echo ポータブル版フォルダを作成しています: %PORTABLE_DIR%

if exist "%PORTABLE_DIR%" (
    echo 既存のフォルダを削除しています...
    rmdir /s /q "%PORTABLE_DIR%"
)

mkdir "%PORTABLE_DIR%"

REM 必要なファイルをコピー
echo.
echo ファイルをコピーしています...

copy "dist\extract_prompts.exe" "%PORTABLE_DIR%\" >nul
if errorlevel 1 goto :copy_error

copy "extract_prompts_standalone.bat" "%PORTABLE_DIR%\" >nul
if errorlevel 1 goto :copy_error

REM 使用説明書を作成
echo 使用説明書を作成しています...
(
echo Stable Diffusionプロンプト抽出ツール - ポータブル版
echo ================================================
echo.
echo ■ 使い方
echo.
echo 1. PNG画像が入っているフォルダを用意します
echo.
echo 2. そのフォルダを「extract_prompts_standalone.bat」に
echo    ドラッグ＆ドロップします
echo.
echo 3. 処理が完了すると、画像フォルダ内に
echo    「prompts_日付_時刻.txt」が作成されます
echo.
echo ■ 注意事項
echo.
echo - PNG画像のみ対応（JPG、WEBP等は非対応）
echo - 最大1,000枚まで一括処理可能
echo - Windows 10/11（64-bit）で動作
echo.
echo ■ トラブルシューティング
echo.
echo もし動作しない場合:
echo - extract_prompts.exeを右クリック→プロパティ
echo - 「ブロックの解除」にチェックを入れて「OK」
echo.
) > "%PORTABLE_DIR%\使い方.txt"

REM ZIPファイルの作成（PowerShellを使用）
echo.
echo ZIPファイルを作成しています...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%PORTABLE_DIR%\*' -DestinationPath '%PORTABLE_DIR%.zip' -Force"

if exist "%PORTABLE_DIR%.zip" (
    echo.
    echo ========================================
    echo パッケージ作成完了！
    echo.
    echo 作成されたファイル:
    echo - %PORTABLE_DIR%\ （フォルダ）
    echo - %PORTABLE_DIR%.zip （配布用ZIP）
    echo.
    echo このZIPファイルを配布できます。
    echo 使用者は解凍して使うだけでOKです。
    echo ========================================
) else (
    echo.
    echo 警告: ZIPファイルの作成に失敗しました。
    echo %PORTABLE_DIR%フォルダは正常に作成されています。
)

echo.
pause
exit /b 0

:copy_error
echo エラー: ファイルのコピーに失敗しました。
pause
exit /b 1