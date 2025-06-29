#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusionプロンプト抽出ツール - GUI版
フォルダ選択ダイアログから簡単に実行
"""

import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import os


def main():
    """GUI版のメイン処理"""
    # tkinterのルートウィンドウを作成（非表示）
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # タイトル表示
    messagebox.showinfo(
        "プロンプト抽出ツール",
        "PNG画像からStable Diffusionのプロンプトを抽出します。\n\n"
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
        subprocess.run([sys.executable, str(extract_script), str(folder)])
    except Exception as e:
        print(f"エラー: {e}")
        messagebox.showerror("エラー", f"実行中にエラーが発生しました:\n{e}")


if __name__ == '__main__':
    main()