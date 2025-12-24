# langgraph-test

このプロジェクトは、以下の環境で動作確認をしています。

- Ubuntu 24.04以上

## 前提条件

Ubuntuには事前に以下のパッケージをインストールする必要があります。

```bash
sudo apt install poppler-utils
```

## セットアップ

### 1. リポジトリのクローン

Agent Skillsを使用するために、以下のリポジトリをクローンする必要があります。

```bash
git clone https://github.com/anthropics/skills
```

### 2. 環境構築 (Python)

このプロジェクトはパッケージ管理に `uv` を使用しています。

1. **uvのインストール** (未インストールの場合):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **依存関係のインストール**:
   ```bash
   uv sync
   ```

### 3. LLMのセットアップ

このアプリケーションは [Ollama](https://ollama.com/) を使用してローカルLLMを実行します。
※ **Ollama 0.13.1以上** が必要です。

1. **Ollamaのインストールと起動**:
   [公式サイト](https://ollama.com/download) からOllamaをインストールし、サーバーを起動してください。

2. **モデルのプル**:
   以下のコマンドで `ministral-3` モデルをダウンロードします。
   ```bash
   ollama pull ministral-3
   ```

## 実行方法

以下のコマンドでGradioアプリケーションを起動します。

```bash
uv run gradio_app.py
```

起動後、ブラウザで `http://localhost:7860` にアクセスしてください。
