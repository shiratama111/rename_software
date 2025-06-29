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
        
        # 出力ファイルの場所を強調表示
        print(f"\n" + "="*60)
        print("出力ファイルが作成されました:")
        print(f"  場所: {output_file.parent}")
        print(f"  ファイル名: {output_file.name}")
        print(f"  フルパス: {output_file}")
        print("="*60)
        
        # Windowsの場合、エクスプローラーで開くオプションを提供
        if sys.platform == 'win32' and sys.stdin.isatty():
            print("\nフォルダを開きますか？ (Y/N): ", end='')
            try:
                choice = input().strip().upper()
                if choice == 'Y':
                    os.startfile(str(output_file.parent))
            except:
                pass
        
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


def select_folder_dialog() -> Optional[Path]:
    """フォルダ選択ダイアログを表示"""
    folder_path = None
    
    if sys.platform == 'win32':
        # Windows: tkinterを使用
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()  # メインウィンドウを非表示
            root.attributes('-topmost', True)  # 最前面に表示
            
            folder_path = filedialog.askdirectory(
                title='PNG画像が含まれるフォルダを選択してください',
                initialdir=os.getcwd()
            )
            
            root.destroy()
            
            if folder_path:
                return Path(folder_path)
        except ImportError:
            # tkinterが利用できない場合
            print("警告: フォルダ選択ダイアログが利用できません")
    else:
        # macOS/Linux: tkinterを試す
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            folder_path = filedialog.askdirectory(
                title='PNG画像が含まれるフォルダを選択してください',
                initialdir=os.getcwd()
            )
            
            root.destroy()
            
            if folder_path:
                return Path(folder_path)
        except:
            print("警告: フォルダ選択ダイアログが利用できません")
    
    return None


def prompt_for_folder() -> Optional[Path]:
    """フォルダ選択の対話的プロンプト"""
    print("\n" + "="*60)
    print("フォルダを選択してください")
    print("="*60)
    print("\n選択方法:")
    print("1. フォルダ選択ダイアログを開く（推奨）")
    print("2. フォルダパスを直接入力")
    print("3. 現在のフォルダを使用")
    print("4. 終了")
    print("\n選択してください (1-4): ", end='')
    
    try:
        choice = input().strip()
        
        if choice == '1':
            # フォルダ選択ダイアログ
            folder = select_folder_dialog()
            if folder:
                return folder
            else:
                print("\nフォルダが選択されませんでした。")
                return None
                
        elif choice == '2':
            # 直接入力
            print("\nフォルダのパスを入力してください: ", end='')
            path_str = input().strip()
            if path_str:
                folder = Path(path_str)
                if folder.exists() and folder.is_dir():
                    return folder
                else:
                    print(f"\nエラー: フォルダが見つかりません: {path_str}")
                    return None
            
        elif choice == '3':
            # 現在のフォルダ
            return Path.cwd()
            
        elif choice == '4':
            # 終了
            return None
            
        else:
            print("\n無効な選択です。")
            return None
            
    except (EOFError, KeyboardInterrupt):
        return None


def show_error_and_wait(message: str):
    """エラーメッセージを表示して入力を待つ"""
    print("\n" + "="*60)
    print("エラーが発生しました")
    print("="*60)
    print(f"\n{message}\n")
    print("="*60)
    print("\n対処方法:")
    print("1. PNG画像が含まれるフォルダを指定してください")
    print("2. コマンドラインから実行する場合:")
    print("   extract_prompts.exe \"C:\\画像フォルダのパス\"")
    print("3. またはextract_prompts_standalone.batに")
    print("   画像フォルダをドラッグ＆ドロップしてください")
    print("\n何かキーを押すと終了します...")
    
    # コンソールがある場合のみ入力を待つ
    if sys.stdin.isatty():
        try:
            # Windowsの場合
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.getch()
            else:
                # Unix系の場合
                input()
        except:
            # エラーが発生した場合は何もしない
            pass


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
        if args.target_folder == '.' and sys.stdin.isatty():
            # 引数なしで実行された場合、対話的にフォルダを選択
            print("Stable Diffusionプロンプト抽出ツール")
            print("="*60)
            target_folder = prompt_for_folder()
            if not target_folder:
                print("\nフォルダが選択されませんでした。終了します。")
                if sys.platform == 'win32':
                    print("\n何かキーを押すと終了します...")
                    import msvcrt
                    msvcrt.getch()
                sys.exit(0)
        else:
            target_folder = Path(args.target_folder).resolve()
            if not target_folder.exists():
                show_error_and_wait(f"フォルダが存在しません: {target_folder}")
                sys.exit(1)
            
            if not target_folder.is_dir():
                show_error_and_wait(f"ディレクトリではありません: {target_folder}")
                sys.exit(1)
        
        print(f"対象フォルダ: {target_folder}")
        
        # 処理実行
        processor = PromptProcessor(target_folder, max_workers=args.workers)
        output_file, success_count, error_count, elapsed_time = processor.process_folder()
        
        # PNG画像が見つからなかった場合の処理
        if success_count == 0 and error_count == 0:
            show_error_and_wait(
                f"指定されたフォルダにPNG画像が見つかりませんでした。\n"
                f"フォルダ: {target_folder}\n\n"
                f"PNG形式の画像ファイルが含まれているか確認してください。"
            )
            sys.exit(1)
        
        # 処理完了後、少し待機（コンソールがある場合のみ）
        if sys.stdin.isatty():
            print("\n処理が完了しました。何かキーを押すと終了します...")
            try:
                if sys.platform == 'win32':
                    import msvcrt
                    msvcrt.getch()
                else:
                    input()
            except:
                pass
            
    except Exception as e:
        show_error_and_wait(f"予期しないエラーが発生しました:\n{str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()