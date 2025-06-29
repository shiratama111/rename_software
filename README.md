# Stable Diffusionプロンプト抽出ツール

PNG画像に埋め込まれたStable Diffusionのポジティブプロンプトを一括抽出するツールです。

## 機能

- PNG画像からポジティブプロンプトを自動抽出
- 最大1,000枚まで一括処理
- マルチスレッド処理による高速化
- エラーログ出力
- Windows向けドラッグ＆ドロップ対応

## 必要環境

- Python 3.8以上（開発時はPython 3.12推奨）
- Windows 10/11（64-bit）

## インストール

### Python環境での実行

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

### スタンドアロン版（.exe）の作成

1. PyInstallerをインストール:
```bash
pip install pyinstaller
```

2. ビルドスクリプトを実行:
```bash
python build_exe.py
```

## 使い方

### 方法1: インタラクティブモード（推奨）

実行ファイルまたはバッチファイルをダブルクリックすると、以下の選択肢が表示されます：

1. **フォルダ選択ダイアログを開く** - GUIでフォルダを選択（推奨）
2. **フォルダパスを直接入力** - パスを手動で入力
3. **現在のフォルダを使用** - 実行ファイルがあるフォルダを処理

### 方法2: GUI版（Python環境）

```bash
python extract_prompts_gui.py
# または
extract_prompts_gui.bat
```

フォルダ選択ダイアログが開き、視覚的にフォルダを選択できます。

### 方法3: ドラッグ＆ドロップ

1. `extract_prompts.bat`（Python環境）または`extract_prompts_standalone.bat`（.exe版）を使用
2. 画像フォルダをバッチファイルにドラッグ＆ドロップ

### 方法4: コマンドライン

```bash
# 現在のフォルダを処理
python extract_prompts.py

# 特定のフォルダを処理
python extract_prompts.py "C:\path\to\images"

# ワーカー数を指定（デフォルト: 4）
python extract_prompts.py "C:\path\to\images" --workers 8
```

## 出力形式

抽出されたプロンプトは以下の形式で保存されます：

```
image1.pngのprompt
a beautiful landscape, highly detailed, 4k resolution

image2.pngのprompt
portrait of a young woman, professional photography

...
```

### 出力ファイルの詳細

- **ファイル名**: `prompts_YYYYMMDD_HHMMSS.txt`
- **文字コード**: UTF-8（BOMあり）
- **保存場所**: **選択したPNG画像フォルダ内に直接保存されます**

### 処理完了後

1. 出力ファイルの場所が画面に表示されます
2. 「フォルダを開きますか？」と確認されます
3. 「Y」を選択すると、エクスプローラーが自動的に開きます

**例**: `C:\Users\名前\Pictures\AI画像` を選択した場合
→ `C:\Users\名前\Pictures\AI画像\prompts_20250629_170000.txt` が作成されます

## テスト

テスト用画像を作成して動作確認:

```bash
python test_extract.py
python extract_prompts.py test_images
```

## 制限事項

- PNG画像のみ対応（JPG、WEBP等は非対応）
- ポジティブプロンプトのみ抽出（ネガティブプロンプトは非対応）
- サブフォルダは検索対象外
- 最大処理数: 1,000枚/回

## エラー処理

- プロンプトが見つからない画像はスキップ
- エラー詳細は`error.log`に記録
- 処理中のエラーでもプログラムは継続実行

## ライセンス

MIT License