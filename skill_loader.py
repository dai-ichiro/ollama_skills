"""Claude Skillsを動的にロードしてLangGraphツールに変換するモジュール"""
import os
import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.tools import tool
import subprocess


class SkillLoader:
    """Claude Skillsをロードしてツールとして提供するクラス"""

    def __init__(self, skills_base_dir: str = "./skills/skills"):
        self.skills_base_dir = Path(skills_base_dir)

    def load_skill_md(self, skill_name: str) -> str:
        """SKILL.mdの内容を読み込む"""
        skill_dir = self.skills_base_dir / skill_name
        skill_md_path = skill_dir / "SKILL.md"

        if skill_md_path.exists():
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_skill_scripts(self, skill_name: str) -> List[Path]:
        """スキルのscriptsディレクトリ内のPythonファイルを取得"""
        scripts_dir = self.skills_base_dir / skill_name / "scripts"

        if not scripts_dir.exists():
            return []

        return list(scripts_dir.glob("*.py"))

    def create_script_tool(self, script_path: Path, skill_name: str):
        """Pythonスクリプトをツールとして登録"""
        script_name = script_path.stem

        # スクリプトのdocstringと使用方法を読み取って説明を取得
        description, usage = self._extract_description_and_usage(script_path)

        # convert_pdf_to_images の特別な処理
        if script_name == "convert_pdf_to_images":
            @tool
            def pdf_convert_pdf_to_images(pdf_path: str, output_dir: str = "./output") -> str:
                """PDFの各ページをPNG画像に変換する

                Args:
                    pdf_path: 変換するPDFファイルのパス
                    output_dir: PNG画像を保存するディレクトリ（デフォルト: ./output）
                """
                # 出力ディレクトリを作成
                os.makedirs(output_dir, exist_ok=True)

                cmd_args = [sys.executable, str(script_path), pdf_path, output_dir]

                try:
                    result = subprocess.run(
                        cmd_args,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        return result.stdout
                    else:
                        return f"エラー (exit code {result.returncode}):\n{result.stderr}"
                except subprocess.TimeoutExpired:
                    return "エラー: スクリプトの実行がタイムアウトしました（120秒）"
                except Exception as e:
                    return f"エラー: {str(e)}"

            return pdf_convert_pdf_to_images

        # 汎用的なツール作成
        def run_script(script_args: str = "") -> str:
            f"""スクリプトを実行: {description}

            Usage: {usage}

            Args:
                script_args: スクリプトに渡す引数（スペース区切り）
            """
            # 引数を構築
            cmd_args = [sys.executable, str(script_path)]

            # 引数文字列を分割して追加
            if script_args:
                # シェルライクな引数パースを行う（簡易版）
                import shlex
                cmd_args.extend(shlex.split(script_args))

            try:
                result = subprocess.run(
                    cmd_args,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"エラー (exit code {result.returncode}):\n{result.stderr}"
            except subprocess.TimeoutExpired:
                return "エラー: スクリプトの実行がタイムアウトしました（60秒）"
            except Exception as e:
                return f"エラー: {str(e)}"

        # ツール名と説明を設定
        tool_name = f"{skill_name}_{script_name}"
        tool_description = f"{skill_name} skill: {description}\nUsage: {usage}"

        # ツールのメタデータを設定
        run_script.__name__ = tool_name
        run_script.__doc__ = tool_description

        return tool(run_script)

    def _extract_description_and_usage(self, script_path: Path) -> tuple[str, str]:
        """スクリプトファイルから説明と使用方法を抽出"""
        description = ""
        usage = ""

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                # Usage行を探す
                for line in lines:
                    if 'Usage:' in line or 'usage:' in line:
                        usage = line.strip().replace('print(', '').replace('"', '').replace("'", '').replace(')', '')
                        break

                # 関数のdocstringまたはコメントを探す
                for i, line in enumerate(lines):
                    if 'def ' in line and i + 1 < len(lines):
                        # 次の行がdocstringか確認
                        if '"""' in lines[i + 1] or "'''" in lines[i + 1]:
                            doc_lines = []
                            j = i + 1
                            while j < len(lines):
                                doc_lines.append(lines[j].strip())
                                if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                                    break
                                j += 1
                            description = ' '.join(doc_lines).strip('"""').strip("'''").strip()
                            break

                # 見つからない場合、ファイル先頭のコメントを探す
                if not description:
                    for line in lines[:15]:
                        if line.strip().startswith('#') and len(line.strip()) > 2 and 'Usage' not in line:
                            description = line.strip('# \n')
                            break

                if not description:
                    description = script_path.stem.replace('_', ' ')

        except Exception as e:
            description = script_path.stem.replace('_', ' ')

        return description, usage

    def _extract_description(self, script_path: Path) -> str:
        """スクリプトファイルから説明を抽出（後方互換性のため）"""
        description, _ = self._extract_description_and_usage(script_path)
        return description

    def load_skill(self, skill_name: str) -> Dict[str, Any]:
        """スキル全体をロード（SKILL.md + ツール）"""
        skill_md = self.load_skill_md(skill_name)
        scripts = self.get_skill_scripts(skill_name)

        tools = []
        for script_path in scripts:
            try:
                tool_obj = self.create_script_tool(script_path, skill_name)
                tools.append(tool_obj)
            except Exception as e:
                print(f"Warning: {script_path.name}のツール化に失敗: {e}")

        return {
            "name": skill_name,
            "instructions": skill_md,
            "tools": tools
        }

    def load_skills(self, skill_names: List[str]) -> List[Dict[str, Any]]:
        """複数のスキルをロード"""
        return [self.load_skill(name) for name in skill_names]


def create_state_modifier_from_skills(skills: List[Dict[str, Any]]) -> str:
    """スキルからstate_modifierを生成"""
    instructions = ["あなたはClaude Skillsを使う専門家です。以下のスキルが利用可能です:\n"]

    for skill in skills:
        instructions.append(f"\n## {skill['name']} Skill")
        if skill['instructions']:
            # SKILL.mdの内容を追加（最初の500文字程度）
            skill_text = skill['instructions'][:1000]
            instructions.append(skill_text)
        instructions.append(f"\n利用可能なツール: {len(skill['tools'])}個")

    return "\n".join(instructions)
