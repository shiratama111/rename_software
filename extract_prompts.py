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
import platform

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
        
        # Windows環境でのエンコーディング問題を回避
        if sys.platform == 'win32':
            import codecs
            # stdout/stderrをUTF-8でラップ
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    def _setup_logging(self):
        """ログ設定"""
        log_file = self.target_folder / 'error.log'
        
        # 既存のハンドラをクリア
        logger = logging.getLogger()
        logger.handlers = []
        
        # ファイルハンドラ（BOMなしUTF-8）
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # コンソールハンドラ
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
    
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
        
        # 出力ファイル名（YAML形式）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.target_folder / f'prompts_{timestamp}.yaml'
        
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
        
        # 出力ファイルの場所を強調表示
        print(f"\n" + "="*60)
        print("出力ファイルが作成されました:")
        print(f"  場所: {output_file.parent}")
        print(f"  ファイル名: {output_file.name}")
        print(f"  フルパス: {output_file}")
        print("="*60)
        
        # CLI版では自動的にフォルダを開かない（GUI版で処理）
        
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
        結果をファイルに書き込み（YAML形式）
        
        Args:
            output_file: 出力ファイルパス
            results: (ファイル名, プロンプト) のリスト
        """
        # ファイル名を.yamlに変更
        yaml_file = output_file.with_suffix('.yaml')
        
        # YAMLファイルに保存
        with open(yaml_file, 'w', encoding='utf-8-sig' if sys.platform == 'win32' else 'utf-8') as f:
            # YAMLヘッダー
            f.write("# Stable Diffusion Prompts\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total images: {len(results)}\n\n")
            
            # プロンプトデータ
            f.write("prompts:\n")
            for filename, prompt in results:
                # ファイル名から拡張子を除いてキーを生成
                key = filename.replace('.png', '')
                # プロンプトの改行を保持しつつ、YAMLのリテラルスタイルで出力
                f.write(f"  {key}: |\n")
                # プロンプトの各行をインデントして出力
                for line in prompt.strip().split('\n'):
                    f.write(f"    {line}\n")
                f.write("\n")


# GUI版で使用されるため、インタラクティブモードは削除


def show_error(message: str):
    """エラーメッセージを表示"""
    print("\n" + "="*60)
    print("エラーが発生しました")
    print("="*60)
    print(f"\n{message}\n")
    print("="*60)


def main():
    """メイン処理"""
    try:
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
            show_error(f"フォルダが存在しません: {target_folder}")
            sys.exit(1)
        
        if not target_folder.is_dir():
            show_error(f"ディレクトリではありません: {target_folder}")
            sys.exit(1)
        
        print(f"対象フォルダ: {target_folder}")
        
        # 処理実行
        processor = PromptProcessor(target_folder, max_workers=args.workers)
        output_file, success_count, error_count, elapsed_time = processor.process_folder()
        
        # PNG画像が見つからなかった場合の処理
        if success_count == 0 and error_count == 0:
            show_error(
                f"指定されたフォルダにPNG画像が見つかりませんでした。\n"
                f"フォルダ: {target_folder}\n\n"
                f"PNG形式の画像ファイルが含まれているか確認してください。"
            )
            sys.exit(1)
            
    except Exception as e:
        show_error(f"予期しないエラーが発生しました:\n{str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()