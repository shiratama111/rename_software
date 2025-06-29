#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テストスクリプト - プロンプト抽出機能の動作確認
"""

import os
from pathlib import Path
from PIL import Image
from PIL.PngImagePlugin import PngInfo

def create_test_png_with_prompt(filename: str, prompt: str):
    """テスト用のPNG画像を作成（プロンプト付き）"""
    # 100x100の白い画像を作成
    img = Image.new('RGB', (100, 100), color='white')
    
    # PNGInfoにメタデータを追加
    metadata = PngInfo()
    # Stable Diffusion形式のパラメータを追加
    parameters = f"""Positive prompt: {prompt}
Negative prompt: worst quality, low quality
Steps: 20, Sampler: Euler a, CFG scale: 7, Seed: 12345, Size: 512x512"""
    
    metadata.add_text("parameters", parameters)
    
    # 画像を保存
    img.save(filename, "PNG", pnginfo=metadata)
    print(f"テスト画像作成: {filename}")

def main():
    """テスト実行"""
    # テストディレクトリを作成
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    # テスト用プロンプト
    test_prompts = [
        ("test1.png", "a beautiful landscape, highly detailed, 4k resolution"),
        ("test2.png", "portrait of a young woman, professional photography, studio lighting"),
        ("test3.png", "futuristic city, cyberpunk style, neon lights, rain"),
        ("test_no_prompt.png", "")  # プロンプトなしのテストケース
    ]
    
    # テスト画像を作成
    for filename, prompt in test_prompts:
        filepath = test_dir / filename
        if prompt:
            create_test_png_with_prompt(filepath, prompt)
        else:
            # プロンプトなしの画像
            img = Image.new('RGB', (100, 100), color='gray')
            img.save(filepath, "PNG")
            print(f"テスト画像作成（プロンプトなし）: {filename}")
    
    print(f"\nテスト画像を {test_dir} に作成しました。")
    print("\n以下のコマンドでプロンプト抽出を実行できます:")
    print(f"python extract_prompts.py {test_dir}")

if __name__ == '__main__':
    main()