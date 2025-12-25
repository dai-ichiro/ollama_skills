# Ollama-Skills

このプロジェクトは、以下の環境で動作確認をしています。

```
Ubuntu 24.04以上
```

## 前提条件

Ubuntuには事前に以下のパッケージをインストールする必要があります。

```bash
sudo apt install poppler-utils
```

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/dai-ichiro/ollama_skills
cd ollama_skills
```

### 2. Skillsの導入
Agent Skillsを使用するために、以下のリポジトリをクローンする必要があります。

```bash
git clone https://github.com/anthropics/skills
```

### 3. 環境構築 (Python)

このプロジェクトはパッケージ管理に `uv` を使用しています。

1. **uvのインストール** (未インストールの場合):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **依存関係のインストール**:
   ```bash
   uv sync
   ```

### 4. LLMのセットアップ

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

## アーキテクチャに関する注意点

現在の実装では、`anthropics/skills`のリポジトリに含まれるAgent Skillsを、LangChainのToolsとして一律に変換して使用しています。
そのため、本来のAgent Skillsが持つ以下のメリットはこの実装では活用されていません：

* **段階的開示 (Progressive Disclosure)**: 必要に応じて詳細な情報やツールを提示する仕組みがなく、すべてのツールが最初から提示されます。
* **コンテキスト効率化 (Context Efficiency)**: すべてのスキルの説明やツール定義を一度にコンテキストに含めるため、トークン消費量が多くなり、コンテキストウィンドウを圧迫する可能性があります。

このプロジェクトは、既存のSkills資産をLangGraph環境で簡易に動作させることを主眼としています。
