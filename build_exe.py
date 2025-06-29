#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstallerを使用してWindows用の実行ファイルをビルド
"""

import subprocess
import sys
import os

def build_exe():
    """実行ファイルをビルド"""
    print("Windows用実行ファイルのビルドを開始します...")
    
    # PyInstallerコマンド
    command = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',  # 単一の実行ファイルを作成
        '--console',  # コンソールアプリケーション
        '--name', 'extract_prompts',  # 実行ファイル名
        '--add-data', 'requirements.txt;.',  # データファイルを含める（Windows用セミコロン）
        '--hidden-import', 'PIL._tkinter_finder',  # 隠れた依存関係
        '--clean',  # クリーンビルド
        'extract_prompts.py'
    ]
    
    # ビルド実行
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("ビルド成功！")
        print("実行ファイルは dist/extract_prompts.exe に作成されました。")
    else:
        print("ビルドエラー:")
        print(result.stderr)
        sys.exit(1)

def main():
    """メイン処理"""
    # PyInstallerがインストールされているか確認
    try:
        import PyInstaller
    except ImportError:
        print("PyInstallerがインストールされていません。")
        print("以下のコマンドでインストールしてください:")
        print("pip install pyinstaller")
        sys.exit(1)
    
    build_exe()

if __name__ == '__main__':
    main()