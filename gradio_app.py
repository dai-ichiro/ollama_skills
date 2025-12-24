import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import gradio as gr
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from skill_loader import SkillLoader, create_state_modifier_from_skills

print("🔧 スキルをロード中...")

# スキルローダーを初期化
loader = SkillLoader(skills_base_dir="./skills/skills")
skills = loader.load_skills(["pdf"])

# ツールを集約
all_tools = []
for skill in skills:
    all_tools.extend(skill["tools"])
    print(f"✓ {skill['name']} skill: {len(skill['tools'])} tools")

# システムメッセージ
skill_instructions = create_state_modifier_from_skills(skills)

# エージェント作成
llm = ChatOllama(model="ministral-3")
agent = create_react_agent(llm, all_tools)

print(f"✅ エージェント準備完了 ({len(all_tools)} ツール)")


def extract_text_content(msg_dict):
    """Gradio 6形式のメッセージからテキストを抽出"""
    content = msg_dict.get("content", "")

    # content がリスト形式の場合（Gradio 6の構造化形式）
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return " ".join(text_parts)

    # content が文字列の場合（単純な形式）
    return str(content)


def process_message_stream(message):
    """メッセージ処理（ストリーミング対応）"""
    # メッセージ構築
    messages = [
        {"role": "system", "content": skill_instructions},
        {"role": "user", "content": message}
    ]

    # エージェント実行（ストリーミング）
    try:
        accumulated_response = ""
        for chunk in agent.stream({"messages": messages}, stream_mode="values"):
            last_msg = chunk["messages"][-1]

            # メッセージの内容を取得
            if hasattr(last_msg, 'content'):
                content = last_msg.content

                # ツール呼び出しやAIメッセージの場合
                if content and isinstance(content, str):
                    accumulated_response = content
                    yield accumulated_response

    except Exception as e:
        error_msg = f"**エラーが発生しました:**\n\n```\n{str(e)}\n```"
        yield error_msg


# Gradio UI（左右分割レイアウト）
with gr.Blocks(title="LangGraph Agent") as demo:
    gr.Markdown("# 🤖 LangGraph Agent with Claude Skills")
    gr.Markdown(f"**PDFスキル搭載** - {len(all_tools)}個のツールが利用可能")

    with gr.Row():
        # 左側：入力エリア
        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="入力",
                placeholder="メッセージを入力してください...",
                lines=10
            )
            submit_btn = gr.Button("実行", variant="primary")
            clear_btn = gr.Button("クリア")

            gr.Markdown("### サンプル")
            gr.Examples(
                examples=[
                    ["/home/hoge/ollama_skills/chapter_1.pdfをPNG画像に変換して"],
                    ["PDFの処理方法を教えて"],
                    ["利用可能なツールを教えて"],
                ],
                inputs=input_text,
            )

        # 右側：出力エリア
        with gr.Column(scale=1):
            output_md = gr.Markdown(label="出力", value="ここに結果が表示されます")

    # イベント処理
    def on_submit(message):
        if not message.strip():
            yield "**入力が空です。メッセージを入力してください。**"
            return

        # ストリーミング処理
        for response in process_message_stream(message):
            yield response

    # ストリーミングを有効にして接続
    submit_btn.click(on_submit, inputs=input_text, outputs=output_md)
    input_text.submit(on_submit, inputs=input_text, outputs=output_md)
    clear_btn.click(lambda: ("", "ここに結果が表示されます"), outputs=[input_text, output_md])

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Gradioサーバーを起動します...")
    print("="*60 + "\n")
    demo.launch()
