# backend/tests/unit/usecases/utils/test_context_builder.py (新規作成)

from app.usecases.utils.context_builder import prepare_patient_facts

def test_prepare_patient_facts_basic():
    # 入力データ（フラットな辞書）
    input_data = {
        "name": "テスト太郎",
        "age": 82,
        "gender": "男性",
        "func_pain_chk": True,
        "func_pain_txt": "右膝に痛みあり",
        "adl_eating_fim_current_val": 7
    }
    
    # 実行
    result = prepare_patient_facts(input_data)
    
    # 検証
    assert result["基本情報"]["氏名"] == "テスト太郎"
    assert result["基本情報"]["年齢"] == "82歳"
    assert result["心身機能・構造"]["疼痛"] == "右膝に痛みあり"
    assert result["ADL評価"]["FIM(現在値)"]["Eating"] == "7点"