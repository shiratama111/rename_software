#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusionプロンプト抽出ツール - メインGUIアプリケーション
PNG画像からプロンプトを抽出する使いやすいGUIインターフェース
"""

import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import locale


def main():
    """メインGUIアプリケーションの処理"""
    # エンコーディング設定
    if sys.platform == 'win32':
        # Windows環境でUTF-8を使用
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    # tkinterのルートウィンドウを作成（非表示）
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # タイトル表示
    messagebox.showinfo(
        "Stable Diffusionプロンプト抽出ツール",
        "PNG画像からStable Diffusionのプロンプトを抽出します。\n\n"
        "機能:\n"
        "・最大1,000枚のPNG画像を一括処理\n"
        "・マルチスレッドによる高速処理\n"
        "・抽出結果をテキストファイルに保存\n\n"
        "次の画面で画像が含まれるフォルダを選択してください。"
    )
    
    # フォルダ選択ダイアログ
    folder_path = filedialog.askdirectory(
        title='PNG画像が含まれるフォルダを選択',
        initialdir=os.getcwd()
    )
    
    if not folder_path:
        messagebox.showwarning("キャンセル", "フォルダが選択されませんでした。")
        root.destroy()
        return
    
    # 選択されたフォルダの確認
    folder = Path(folder_path)
    png_count = len(list(folder.glob('*.png')))
    
    if png_count == 0:
        result = messagebox.askyesno(
            "確認",
            f"選択されたフォルダにPNG画像が見つかりません。\n\n"
            f"フォルダ: {folder}\n\n"
            f"このまま続行しますか？"
        )
        if not result:
            root.destroy()
            return
    else:
        result = messagebox.askyesno(
            "確認",
            f"以下のフォルダを処理します。\n\n"
            f"フォルダ: {folder}\n"
            f"PNG画像数: {png_count}枚\n\n"
            f"続行しますか？"
        )
        if not result:
            root.destroy()
            return
    
    root.destroy()
    
    # extract_prompts.pyを実行
    script_dir = Path(__file__).parent
    extract_script = script_dir / "extract_prompts.py"
    
    if not extract_script.exists():
        print(f"エラー: {extract_script} が見つかりません")
        return
    
    # Pythonスクリプトを実行
    try:
        # Windows環境でのエンコーディング問題を回避
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # subprocessのエンコーディングを明示的に設定
        if sys.platform == 'win32':
            # Windowsの場合、UTF-8を強制
            result = subprocess.run(
                [sys.executable, '-X', 'utf8', str(extract_script), str(folder)], 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='replace',
                env=env
            )
        else:
            result = subprocess.run(
                [sys.executable, str(extract_script), str(folder)], 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='replace',
                env=env
            )
        
        if result.returncode == 0:
            # 成功時、出力ファイルの場所を取得して表示
            output_lines = result.stdout.split('\n')
            output_file = None
            
            # 出力ファイルのパスを探す
            for line in output_lines:
                if 'フルパス:' in line:
                    output_file = line.split('フルパス:')[1].strip()
                    break
            
            if output_file and Path(output_file).exists():
                # 処理完了のメッセージ
                yaml_file = output_file
                txt_file = str(Path(output_file).with_suffix('.txt'))
                
                response = messagebox.askyesno(
                    "処理完了",
                    f"プロンプトの抽出が完了しました。\n\n"
                    f"出力ファイル:\n"
                    f"1. YAML形式（構造化）:\n   {Path(yaml_file).name}\n\n"
                    f"2. テキスト形式（プロンプトのみ）:\n   {Path(txt_file).name}\n\n"
                    f"フォルダを開きますか？"
                )
                
                if response:
                    # Windowsの場合、エクスプローラーで開く
                    if sys.platform == 'win32':
                        os.startfile(str(Path(output_file).parent))
                    elif sys.platform == 'darwin':
                        subprocess.run(['open', str(Path(output_file).parent)])
                    else:
                        subprocess.run(['xdg-open', str(Path(output_file).parent)])
            else:
                messagebox.showinfo("処理完了", "処理が完了しました。")
        else:
            # エラー時
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{result.stderr}")
            
    except Exception as e:
        print(f"エラー: {e}")
        messagebox.showerror("エラー", f"実行中にエラーが発生しました:\n{e}")


if __name__ == '__main__':
    main()