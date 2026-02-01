import json
from typing import Any, Dict, Type, Optional
from pydantic import BaseModel

# 先ほど作成したマネージャーをインポート
from app.usecases.utils.prompt_manager import load_prompt

# FIMのガイドライン定数は、変数としてテンプレートに渡すためにここに定義します
FIM_GUIDELINES = """
    【FIM（機能的自立度評価法）の点数目安】
    ・7点：完全自立（安全にかつ合理的な時間内で遂行）
    ・6点：修正自立（補助具の使用や時間を要するが自立）
    ・5点：監視または準備（監視下での実施）
    ・4点：最小介助（患者が75%以上を自分で行う）
    ・3点：中等度介助（50%以上～75%未満を自分で行う）
    ・2点：最大介助（25%以上～50%未満を自分で行う）
    ・1点：全介助（25%未満しか行えない）
"""

def build_group_prompt(
    group_schema: Type[BaseModel],
    patient_facts_str: str,
    generated_plan_so_far: Dict[str, Any],
) -> str:
    """
    計画書生成（グループ単位）用のプロンプトを構築する
    """
    # テンプレートに渡す変数を辞書として準備
    variables = {
        "patient_facts": patient_facts_str,
        "generated_plan": json.dumps(generated_plan_so_far, indent=2, ensure_ascii=False, default=str),
        "fim_guidelines": FIM_GUIDELINES,
        "schema_json": json.dumps(group_schema.model_json_schema(), indent=2, ensure_ascii=False)
    }

    # テンプレートファイル 'plan_generation.txt' を読み込んで変数を展開
    return load_prompt("plan_generation", **variables)


def build_regeneration_prompt(
    patient_facts_str: str,
    generated_plan_so_far: Dict[str, Any],
    item_key_to_regenerate: str,
    current_text: str,
    instruction: str,
    rag_context: Optional[str] = None
) -> str:
    """
    項目再生成用のプロンプトを構築する
    """
    # RAGコンテキストがある場合のみヘッダーを付ける
    rag_text = ""
    if rag_context:
        rag_text = f"# 参考情報 (専門知識)\n{rag_context}\n"

    variables = {
        "patient_facts": patient_facts_str,
        "generated_plan": json.dumps(generated_plan_so_far, indent=2, ensure_ascii=False, default=str),
        "rag_context": rag_text,
        "item_label": item_key_to_regenerate,
        "current_text": current_text,
        "instruction": instruction
    }

    # テンプレートファイル 'item_regeneration.txt' を読み込んで変数を展開
    return load_prompt("item_regeneration", **variables)