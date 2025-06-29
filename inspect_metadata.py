#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PNG画像のメタデータを詳細に調査するスクリプト
"""

import sys
from pathlib import Path
from PIL import Image
import piexif

def inspect_png_metadata(file_path):
    """PNG画像のメタデータを詳細に表示"""
    print(f"\n=== {file_path.name} ===")
    
    try:
        with Image.open(file_path) as img:
            print(f"Format: {img.format}")
            print(f"Mode: {img.mode}")
            print(f"Size: {img.size}")
            
            # PNGテキストチャンクを確認
            if hasattr(img, 'text'):
                print("\nPNG Text Chunks:")
                if img.text:
                    for key, value in img.text.items():
                        print(f"  [{key}]:")
                        # 長いテキストは最初の200文字のみ表示
                        if len(value) > 200:
                            print(f"    {value[:200]}...")
                        else:
                            print(f"    {value}")
                else:
                    print("  (No text chunks found)")
            
            # info属性を確認
            if hasattr(img, 'info'):
                print("\nImage info:")
                for key, value in img.info.items():
                    if key not in ['text', 'exif']:
                        print(f"  {key}: {str(value)[:100]}")
            
            # EXIFデータを確認
            if hasattr(img, '_getexif') and img._getexif():
                print("\nEXIF data found")
                try:
                    exif_data = img.info.get('exif', b'')
                    if exif_data:
                        exif_dict = piexif.load(exif_data)
                        for ifd in exif_dict:
                            if exif_dict[ifd]:
                                print(f"  {ifd}: {len(exif_dict[ifd])} entries")
                except:
                    print("  (Could not parse EXIF data)")
                    
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python inspect_metadata.py <画像ファイルまたはフォルダ>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_file():
        inspect_png_metadata(path)
    elif path.is_dir():
        png_files = list(path.glob('*.png'))
        for png_file in png_files:
            inspect_png_metadata(png_file)
    else:
        print(f"エラー: パスが見つかりません: {path}")
        sys.exit(1)

if __name__ == '__main__':
    main()