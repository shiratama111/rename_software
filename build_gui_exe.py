#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstallerを使用してWindows用の実行ファイルをビルド
GUI版とCLI版の両方をサポート
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path

def build_gui_exe():
    """GUI版実行ファイルをビルド"""
    print("GUI版実行ファイルのビルドを開始します...")
    
    # PyInstallerコマンド
    command = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',  # 単一の実行ファイルを作成
        '--windowed',  # GUIアプリケーション（コンソールなし）
        '--name', 'prompt_extractor_gui',  # 実行ファイル名
        '--icon', 'icon.ico' if os.path.exists('icon.ico') else None,  # アイコンがあれば使用
        '--add-data', 'requirements.txt;.',  # データファイルを含める（Windows用セミコロン）
        '--hidden-import', 'PIL._tkinter_finder',  # 隠れた依存関係
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.filedialog',
        '--hidden-import', 'tkinter.messagebox',
        '--clean',  # クリーンビルド
        'main_gui.py'
    ]
    
    # Noneを除去
    command = [c for c in command if c is not None]
    
    # ビルド実行
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("GUI版ビルド成功！")
        print("実行ファイルは dist/prompt_extractor_gui.exe に作成されました。")
        return True
    else:
        print("GUI版ビルドエラー:")
        print(result.stderr)
        return False

def build_cli_exe():
    """CLI版実行ファイルをビルド"""
    print("\nCLI版実行ファイルのビルドを開始します...")
    
    # PyInstallerコマンド
    command = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',  # 単一の実行ファイルを作成
        '--console',  # コンソールアプリケーション
        '--name', 'prompt_extractor_cli',  # 実行ファイル名
        '--add-data', 'requirements.txt;.',  # データファイルを含める（Windows用セミコロン）
        '--hidden-import', 'PIL._tkinter_finder',  # 隠れた依存関係
        '--clean',  # クリーンビルド
        'extract_prompts.py'
    ]
    
    # ビルド実行
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("CLI版ビルド成功！")
        print("実行ファイルは dist/prompt_extractor_cli.exe に作成されました。")
        return True
    else:
        print("CLI版ビルドエラー:")
        print(result.stderr)
        return False

def create_portable_package():
    """ポータブルパッケージを作成"""
    print("\nポータブルパッケージを作成しています...")
    
    # パッケージディレクトリの作成
    package_dir = Path("prompt_extractor_portable")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # ファイルをコピー
    files_to_copy = [
        ("dist/prompt_extractor_gui.exe", "prompt_extractor_gui.exe"),
        ("main_gui.bat", "実行.bat"),
        ("README.md", "README.md"),
    ]
    
    # CLI版もビルドされている場合
    if os.path.exists("dist/prompt_extractor_cli.exe"):
        files_to_copy.append(("dist/prompt_extractor_cli.exe", "prompt_extractor_cli.exe"))
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, package_dir / dst)
            print(f"  {dst} をコピーしました")
    
    # 簡易説明書を作成
    quick_guide = """Stable Diffusionプロンプト抽出ツール - クイックガイド

使い方:
1. prompt_extractor_gui.exe をダブルクリック
2. PNG画像が含まれるフォルダを選択
3. 処理完了後、同じフォルダ内にprompts_日付_時刻.txtが作成されます

注意事項:
- PNG画像のみ対応しています
- 最大1,000枚まで処理可能です
- Windows Defenderが警告を出す場合は「詳細情報」→「実行」を選択してください
"""
    
    with open(package_dir / "使い方.txt", 'w', encoding='utf-8') as f:
        f.write(quick_guide)
    
    print(f"\nポータブルパッケージが {package_dir} に作成されました。")
    return True

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='実行ファイルをビルドします')
    parser.add_argument('--both', action='store_true', help='GUI版とCLI版の両方をビルド')
    parser.add_argument('--cli', action='store_true', help='CLI版のみビルド')
    parser.add_argument('--package', action='store_true', help='ビルド後にポータブルパッケージを作成')
    args = parser.parse_args()
    
    # PyInstallerがインストールされているか確認
    try:
        import PyInstaller
    except ImportError:
        print("PyInstallerがインストールされていません。")
        print("以下のコマンドでインストールしてください:")
        print("pip install pyinstaller")
        sys.exit(1)
    
    # ビルド実行
    success = True
    
    if args.cli:
        # CLI版のみ
        success = build_cli_exe()
    elif args.both:
        # 両方ビルド
        success = build_gui_exe() and build_cli_exe()
    else:
        # デフォルトはGUI版のみ
        success = build_gui_exe()
    
    # ポータブルパッケージの作成
    if success and args.package:
        create_portable_package()
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()