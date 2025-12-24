import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from skill_loader import SkillLoader, create_state_modifier_from_skills

# スキルローダーを初期化
loader = SkillLoader(skills_base_dir="./skills/skills")

# 使用したいスキルをロード
skills = loader.load_skills([
    "pdf",
    # 必要に応じて他のスキルも追加可能
    # "docx",
    # "pptx",
    # "xlsx",
])

# すべてのスキルのツールを集約
all_tools = []
for skill in skills:
    all_tools.extend(skill["tools"])
    print(f"✓ Loaded {skill['name']} skill: {len(skill['tools'])} tools")

# スキルの説明を含むシステムメッセージを作成
skill_instructions = create_state_modifier_from_skills(skills)

# LangGraph Agentを作成
llm = ChatOllama(model="ministral-3")

# LangGraph 1.0の新しいAPIを使用
agent = create_react_agent(
    llm,
    all_tools,
)

# 実行例
if __name__ == "__main__":
    print("\n=== Available Tools ===")
    for tool in all_tools:
        print(f"  - {tool.name}: {tool.description}")

    print("\n=== Running Agent ===")

    # スキルの説明をシステムメッセージとして追加
    messages = [
        {"role": "system", "content": skill_instructions},
        {"role": "user", "content": "/home/hoge/langgraph-test/chapter_1.pdfをPNG画像に変換して"}
    ]

    for chunk in agent.stream({"messages": messages}, stream_mode="values"):
        chunk["messages"][-1].pretty_print()
