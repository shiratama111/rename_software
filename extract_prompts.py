#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusionメタデータ抽出ツール
PNG画像からポジティブプロンプトを抽出してテキストファイルに出力
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Tuple, List
import time

from PIL import Image
from PIL.PngImagePlugin import PngInfo
import piexif
from tqdm import tqdm


class PromptExtractor:
    """PNG画像からプロンプトを抽出するクラス"""
    
    def __init__(self, output_encoding='utf-8'):
        self.output_encoding = output_encoding
        self.logger = logging.getLogger(__name__)
    
    def extract_prompt_from_png(self, file_path: Path) -> Optional[str]:
        """
        PNGファイルからポジティブプロンプトを抽出
        
        Args:
            file_path: PNG画像のパス
            
        Returns:
            抽出したプロンプト文字列、見つからない場合はNone
        """
        try:
            with Image.open(file_path) as img:
                # PNGのテキストチャンクを確認
                if hasattr(img, 'text'):
                    # 優先順位: parameters > Prompt > Description
                    for key in ['parameters', 'Prompt', 'Description']:
                        if key in img.text:
                            prompt = self._extract_positive_prompt(img.text[key])
                            if prompt:
                                return prompt
                
                # EXIFデータを確認
                if hasattr(img, '_getexif') and img._getexif():
                    exif_dict = piexif.load(img.info.get('exif', b''))
                    if piexif.ExifIFD.UserComment in exif_dict.get('Exif', {}):
                        user_comment = exif_dict['Exif'][piexif.ExifIFD.UserComment]
                        # バイト列をデコード
                        if isinstance(user_comment, bytes):
                            try:
                                comment_str = user_comment.decode('utf-8', errors='ignore')
                                prompt = self._extract_positive_prompt(comment_str)
                                if prompt:
                                    return prompt
                            except:
                                pass
                
                return None
                
        except Exception as e:
            self.logger.error(f"エラー発生 ({file_path}): {str(e)}")
            return None
    
    def _extract_positive_prompt(self, text: str) -> Optional[str]:
        """
        テキストからポジティブプロンプトを抽出
        
        Args:
            text: 検索対象のテキスト
            
        Returns:
            ポジティブプロンプト文字列
        """
        if not text:
            return None
        
        # "Positive prompt:" を検索
        positive_marker = "Positive prompt:"
        if positive_marker in text:
            start_idx = text.index(positive_marker) + len(positive_marker)
            # 改行までを取得
            end_idx = text.find('\n', start_idx)
            if end_idx == -1:
                # 改行がない場合は最後まで
                prompt = text[start_idx:].strip()
            else:
                prompt = text[start_idx:end_idx].strip()
            
            return prompt if prompt else None
        
        # "Positive prompt:" がない場合、parametersキーの内容をそのまま使用
        # ただし、"Negative prompt:" が含まれる場合はその前までを抽出
        negative_marker = "Negative prompt:"
        if negative_marker in text:
            # Negative promptの前までを取得
            prompt = text[:text.index(negative_marker)].strip()
        else:
            # 最初の改行までを取得（ComfyUIなどの形式対応）
            end_idx = text.find('\n')
            if end_idx == -1:
                prompt = text.strip()
            else:
                prompt = text[:end_idx].strip()
        
        return prompt if prompt else None


class PromptProcessor:
    """プロンプト抽出処理の管理クラス"""
    
    def __init__(self, target_folder: Path, max_workers: int = 4):
        self.target_folder = target_folder
        self.max_workers = max_workers
        self.extractor = PromptExtractor()
        self.logger = logging.getLogger(__name__)
        
        # ログ設定
        self._setup_logging()
    
    def _setup_logging(self):
        """ログ設定"""
        log_file = self.target_folder / 'error.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def process_folder(self) -> Tuple[str, int, int, float]:
        """
        フォルダ内のPNG画像を処理
        
        Returns:
            (出力ファイルパス, 処理件数, エラー件数, 処理時間)
        """
        start_time = time.time()
        
        # PNG画像を収集
        png_files = list(self.target_folder.glob('*.png'))
        if not png_files:
            self.logger.warning("PNG画像が見つかりませんでした。")
            return "", 0, 0, 0
        
        # 出力ファイル名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.target_folder / f'prompts_{timestamp}.txt'
        
        success_count = 0
        error_count = 0
        results = []
        
        # マルチスレッドで処理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # タスクを投入
            future_to_file = {
                executor.submit(self._process_single_file, png_file): png_file
                for png_file in png_files[:1000]  # 最大1000枚
            }
            
            # プログレスバー付きで結果を収集
            with tqdm(total=len(future_to_file), desc="処理中", unit="ファイル") as pbar:
                for future in as_completed(future_to_file):
                    png_file = future_to_file[future]
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        self.logger.error(f"処理エラー ({png_file.name}): {str(e)}")
                        error_count += 1
                    pbar.update(1)
        
        # 結果をファイルに書き込み
        self._write_results(output_file, results)
        
        elapsed_time = time.time() - start_time
        
        # 完了メッセージ
        print(f"\n処理完了:")
        print(f"  処理件数: {success_count + error_count}")
        print(f"  成功: {success_count}")
        print(f"  エラー: {error_count}")
        print(f"  処理時間: {elapsed_time:.2f}秒")
        print(f"  出力ファイル: {output_file}")
        
        return str(output_file), success_count, error_count, elapsed_time
    
    def _process_single_file(self, png_file: Path) -> Optional[Tuple[str, str]]:
        """
        単一ファイルを処理
        
        Args:
            png_file: 処理対象のPNGファイル
            
        Returns:
            (ファイル名, プロンプト) のタプル、エラーの場合はNone
        """
        prompt = self.extractor.extract_prompt_from_png(png_file)
        if prompt:
            return (png_file.name, prompt)
        else:
            self.logger.warning(f"プロンプトが見つかりません: {png_file.name}")
            return None
    
    def _write_results(self, output_file: Path, results: List[Tuple[str, str]]):
        """
        結果をファイルに書き込み
        
        Args:
            output_file: 出力ファイルパス
            results: (ファイル名, プロンプト) のリスト
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for filename, prompt in results:
                f.write(f"{filename}のprompt\n{prompt}\n\n")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='PNG画像からStable Diffusionのポジティブプロンプトを抽出します'
    )
    parser.add_argument(
        'target_folder',
        nargs='?',
        default='.',
        help='対象フォルダのパス（省略時は現在のディレクトリ）'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='並列処理のワーカー数（デフォルト: 4）'
    )
    
    args = parser.parse_args()
    
    # フォルダパスを確認
    target_folder = Path(args.target_folder).resolve()
    if not target_folder.exists():
        print(f"エラー: フォルダが存在しません: {target_folder}")
        sys.exit(1)
    
    if not target_folder.is_dir():
        print(f"エラー: ディレクトリではありません: {target_folder}")
        sys.exit(1)
    
    print(f"対象フォルダ: {target_folder}")
    
    # 処理実行
    processor = PromptProcessor(target_folder, max_workers=args.workers)
    processor.process_folder()


if __name__ == '__main__':
    main()