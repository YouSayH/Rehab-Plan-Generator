import logging
from pathlib import Path
from string import Template
from typing import Any

logger = logging.getLogger(__name__)

# テンプレートファイルが配置されているディレクトリ
# このファイル(prompt_manager.py)と同じ階層の 'templates' フォルダを指します
# 構成: backend/app/usecases/utils/templates/*.txt
PROMPT_DIR = Path(__file__).parent / "templates"

def load_prompt(template_name: str, **kwargs: Any) -> str:
    """
    指定されたテンプレートファイルを読み込み、変数を展開して返します。

    Args:
        template_name (str): テンプレートファイル名（拡張子 .txt は省略可）
        **kwargs: テンプレート内の変数($variable)に埋め込む値

    Returns:
        str: 変数が展開されたプロンプト文字列

    Raises:
        FileNotFoundError: テンプレートファイルが見つからない場合
    """
    # 拡張子がない場合は .txt を付与して補完
    if not template_name.endswith(".txt"):
        filename = f"{template_name}.txt"
    else:
        filename = template_name

    template_path = PROMPT_DIR / filename

    try:
        if not template_path.exists():
            # 開発者がパス構成を間違えた場合に気づきやすいようログを出力
            logger.error(f"Prompt template not found at: {template_path}")
            raise FileNotFoundError(f"Template '{filename}' not found in {PROMPT_DIR}")

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # string.Template を使用して変数を置換 ($variable 形式)
        # safe_substitute を使うことで、万が一コード側から渡す変数が不足していても
        # エラーにならず、プレースホルダー($variable)がそのまま残るためデバッグしやすい。
        return Template(template_content).safe_substitute(**kwargs)

    except Exception as e:
        logger.error(f"Error loading prompt template '{template_name}': {e}")
        raise