import logging
from datetime import date
from typing import Any, Dict, Optional

# 定数定義をインポート（ハードコーディングを解消）
from app.core.constants import PATIENT_FIELD_LABELS, CHECKBOX_TEXT_PAIRS

logger = logging.getLogger(__name__)

def format_value(value: Any) -> Optional[str]:
    """
    値を人間が読みやすい形に整形する。
    Noneや空文字、Falseは None を返すことで後続処理でスキップさせる。
    """
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return "あり" if value else None  # Falseなら表示しない
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return str(value)

def prepare_patient_facts(flat_patient_data: Dict[str, Any], therapist_notes: str = "") -> Dict[str, Any]:
    """
    プロンプトに渡すための患者の事実情報を整形する。
    DBのフラットなデータを、カテゴリごとの構造化データに変換します。

    Args:
        flat_patient_data: Pydanticモデルからexport_to_mapping_format()等で変換された辞書
        therapist_notes: 療法士の申し送り事項（自由記述）

    Returns:
        Dict[str, Any]: LLMのコンテキストとして使用する辞書
    """
    
    # 出力構造の初期化
    facts = {
        "基本情報": {},
        "心身機能・構造": {},
        "基本動作": {},
        "ADL評価": {"FIM(現在値)": {}, "BI(現在値)": {}},
        "栄養状態": {},
        "社会保障サービス": {},
        "目標（参加）": {},
        "目標（活動）": {},
        "目標（環境・対応）": {},
        "担当者からの所見": therapist_notes if therapist_notes else "特になし",
    }

    # 1. 基本情報の固定フィールド処理
    facts["基本情報"]["氏名"] = flat_patient_data.get("name", "匿名")
    
    if "age" in flat_patient_data and flat_patient_data["age"] is not None:
         facts["基本情報"]["年齢"] = f"{flat_patient_data['age']}歳"
    
    if "gender" in flat_patient_data:
        facts["基本情報"]["性別"] = flat_patient_data.get("gender")

    # 2. 汎用的なマッピング処理
    for key, value in flat_patient_data.items():
        formatted_value = format_value(value)
        
        # 値がない、または「なし」相当の場合はスキップ
        if formatted_value is None:
            continue

        # チェックボックス+テキストのペアになっているキーは、後続のステップで処理するためここではスキップ
        # (例: func_pain_chk があっても、ここでは処理せず func_pain_txt とセットで扱う)
        if key in CHECKBOX_TEXT_PAIRS or key in CHECKBOX_TEXT_PAIRS.values():
            continue

        # 定数ファイルに定義されているラベルを取得
        jp_name = PATIENT_FIELD_LABELS.get(key)
        if not jp_name:
            continue

        # カテゴリの自動判定（プレフィックスベース）
        category = "心身機能・構造" # デフォルト
        
        if key.startswith(("header_", "main_")):
            category = "基本情報"
        elif key.startswith("func_basic_"):
            category = "基本動作"
        elif key.startswith("nutrition_"):
            category = "栄養状態"
        elif key.startswith("social_"):
            category = "社会保障サービス"
        elif key.startswith("goal_p_"):
            category = "目標（参加）"
        elif key.startswith("goal_a_"):
            category = "目標（活動）"
        elif key.startswith("goal_s_"):
            category = "目標（環境・対応）"

        # 辞書への格納
        if category in facts:
            facts[category][jp_name] = formatted_value

    # 3. チェックボックス + 詳細テキストのペア項目の処理
    # (例: 「疼痛」にチェックがあれば、その詳細テキストを表示する)
    for chk_key, txt_key in CHECKBOX_TEXT_PAIRS.items():
        jp_name = PATIENT_FIELD_LABELS.get(chk_key)
        if not jp_name:
            continue

        is_checked = flat_patient_data.get(chk_key)
        # 文字列の 'true' や 'on' も考慮してBoolean判定
        is_truly_checked = str(is_checked).lower() in ["true", "1", "on"]

        if is_truly_checked:
            txt_value = flat_patient_data.get(txt_key)
            if not txt_value or txt_value.strip() == "特記なし":
                facts["心身機能・構造"][jp_name] = "あり（詳細は不明）"
            else:
                facts["心身機能・構造"][jp_name] = txt_value

    # 4. ADLスコア (FIM/BI) の抽出処理
    for key, value in flat_patient_data.items():
        if value is not None and "_val" in key:
            val_str = str(value)
            
            # FIMの処理
            if "fim_current_val" in key:
                # 例: adl_eating_fim_current_val -> Eating
                item_name = key.replace("adl_", "").replace("_fim_current_val", "").replace("_", " ").title()
                facts["ADL評価"]["FIM(現在値)"][item_name] = f"{val_str}点"
            
            # BIの処理
            elif "bi_current_val" in key:
                item_name = key.replace("adl_", "").replace("_bi_current_val", "").replace("_", " ").title()
                facts["ADL評価"]["BI(現在値)"][item_name] = f"{val_str}点"

    # 5. 不要な空カテゴリのクリーンアップ
    final_facts = {k: v for k, v in facts.items() if v}
    
    # ADLカテゴリ内の空チェック
    if "ADL評価" in final_facts:
        adl = final_facts["ADL評価"]
        if not adl.get("FIM(現在値)"):
            del adl["FIM(現在値)"]
        if not adl.get("BI(現在値)"):
            del adl["BI(現在値)"]
        
        # サブカテゴリも空なら親も削除
        if not adl:
            del final_facts["ADL評価"]

    return final_facts