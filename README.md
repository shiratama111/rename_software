# Stable Diffusionプロンプト抽出ツール

PNG画像に埋め込まれたStable Diffusionのプロンプトを一括抽出する、使いやすいGUIツールです。

## 主な特徴

- 🖱️ **直感的なGUIインターフェース** - フォルダ選択ダイアログで簡単操作
- ⚡ **高速処理** - マルチスレッドによる並列処理で最大1,000枚を一括抽出
- 🎨 **幅広い互換性** - Stable Diffusion WebUI、ComfyUIなど各種ツールに対応
- 📝 **整理された出力** - ファイル名とプロンプトを見やすく整理してテキスト保存
- 🔧 **柔軟な実行方法** - スタンドアロン実行ファイルまたはPython環境で動作

## クイックスタート

### 方法1: 実行ファイル版（推奨）

1. [Releases](../../releases)から最新版をダウンロード
2. `prompt_extractor_gui.exe`をダブルクリック
3. PNG画像が含まれるフォルダを選択
4. 処理完了！選択したフォルダ内に結果が保存されます

### 方法2: Python環境での実行

```bash
# 依存関係をインストール
pip install -r requirements.txt

# GUIを起動
python main_gui.py
# または
main_gui.bat
```

## システム要件

- **OS**: Windows 10/11（64-bit）
- **Python**: 3.8以上（Python環境で実行する場合）
- **メモリ**: 4GB以上推奨

## 使い方

### GUIモード（メイン）

1. アプリケーションを起動
2. フォルダ選択ダイアログでPNG画像があるフォルダを選択
3. 確認ダイアログで画像数を確認して「続行」
4. 処理完了後、結果ファイルの場所が表示されます
5. 「フォルダを開く」を選択すると自動的にエクスプローラーが開きます

### CLIモード（上級者向け）

コマンドラインから直接実行することも可能です：

```bash
python extract_prompts.py "C:\path\to\images"

# ワーカー数を指定
python extract_prompts.py "C:\path\to\images" --workers 8
```

## 出力形式

抽出されたプロンプトは**2つの形式**で同時に保存されます：

### 1. YAML形式（構造化データ）

```yaml
# Stable Diffusion Prompts
# Generated: 2025-06-29 17:30:00
# Total images: 2

prompts:
  image1: |
    masterpiece, best quality, 1girl, solo, long hair, school uniform
    
  image2: |
    landscape, mountain, sunset, highly detailed, 4k
```

### 2. テキスト形式（プロンプトのみ）

```
masterpiece, best quality, 1girl, solo, long hair, school uniform

---

landscape, mountain, sunset, highly detailed, 4k

---
```

### ファイル詳細

- **YAML形式**: `prompts_YYYYMMDD_HHMMSS.yaml`
  - ファイル名とプロンプトの対応が分かる
  - プログラムでの処理に便利

- **テキスト形式**: `prompts_YYYYMMDD_HHMMSS.txt`
  - プロンプトのみをシンプルに保存
  - コピー＆ペーストに便利

- **保存場所**: 選択したPNG画像フォルダ内
- **文字コード**: UTF-8（Windows環境ではBOM付き）

## ビルド方法（開発者向け）

### 実行ファイルのビルド

```bash
# ビルドスクリプトを実行
build.bat

# または手動でビルド
pip install pyinstaller
python build_gui_exe.py
```

### ビルドオプション

```bash
# GUI版のみ（デフォルト）
python build_gui_exe.py

# GUI版とCLI版の両方
python build_gui_exe.py --both

# ポータブルパッケージも作成
python build_gui_exe.py --package
```

## トラブルシューティング

### Windows Defenderの警告が出る場合

自作の実行ファイルのため、初回実行時に警告が表示される場合があります：
1. 「詳細情報」をクリック
2. 「実行」をクリック

### プロンプトが抽出されない場合

- PNG画像にメタデータが含まれているか確認してください
- 対応形式：Stable Diffusion WebUI、ComfyUI、NovelAIなど
- JPEG、WebPなどは非対応です

### エラーが発生する場合

- `error.log`ファイルを確認してください
- Python環境の場合は依存関係を再インストール：`pip install -r requirements.txt --upgrade`

## 制限事項

- PNG画像のみ対応（JPEG、WebP等は非対応）
- ポジティブプロンプトのみ抽出（ネガティブプロンプトは非対応）
- サブフォルダ内の画像は処理対象外
- 一度に処理できる最大枚数：1,000枚

## 開発

### プロジェクト構造

```
rename_software/
├── main_gui.py          # メインGUIアプリケーション
├── extract_prompts.py   # コア抽出エンジン
├── build_gui_exe.py     # ビルドスクリプト
├── main_gui.bat         # Windows用起動バッチ
├── build.bat            # ビルド用バッチ
├── requirements.txt     # Python依存関係
└── README.md           # このファイル
```

### 貢献

プルリクエストを歓迎します！バグ報告や機能要望は[Issues](../../issues)へ。

## ライセンス

MIT License

## 作者

[あなたの名前]

---

⚡ Powered by Python, PIL, and PyInstaller