import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.usecases.plan_generation import PlanGenerationUseCase
from app.schemas.extraction_schemas import (
    PatientExtractionSchema, BasicInfoSchema, MedicalRiskSchema, 
    FunctionalStatusSchema, BasicMovementSchema, AdlSchema, 
    NutritionSchema, SocialSchema, GoalSettingSchema, SignatureSchema
)

# テスト用のダミーデータ生成ヘルパー
def create_dummy_patient_data():
    return PatientExtractionSchema(
        basic=BasicInfoSchema(name="テスト太郎", age=80, gender="男"),
        medical=MedicalRiskSchema(),
        function=FunctionalStatusSchema(),
        basic_movement=BasicMovementSchema(),
        adl=AdlSchema(),
        nutrition=NutritionSchema(),
        social=SocialSchema(),
        goals=GoalSettingSchema(),
        signature=SignatureSchema()
    )

@pytest.mark.asyncio
async def test_plan_generation_flow():
    """
    正常系テスト: 
    1. 患者データを受け取る
    2. LLMを3回呼び出して、各パート(現状・目標・計画)を生成する
    3. 結果をマージしてDBに保存する
    ...というフローが正しく実行されるか検証
    """
    # ----------------------------------------------------
    # 1. モックの準備
    # ----------------------------------------------------
    mock_db = AsyncMock()
    
    # begin() は非同期コンテキストマネージャを返す同期メソッドとして振る舞う必要がある
    # AsyncMockのデフォルトだと begin() 自体がコルーチンになってしまうため、MagicMockで上書きする
    mock_db.begin = MagicMock()
    # begin() が返すオブジェクト(トランザクション)は async with で使える必要があるため AsyncMock にする
    mock_tx = AsyncMock()
    mock_db.begin.return_value = mock_tx

    # LLMクライアントのモック
    mock_llm_client = MagicMock()
    mock_llm_client.generate_json = AsyncMock(side_effect=[
        {"risk_assessment": "リスクなし"},      # 1回目
        {"short_term_goal": "歩行自立"},        # 2回目
        {"rehab_program": "歩行訓練"}           # 3回目
    ])

    # リポジトリのモック
    mock_repo_instance = AsyncMock()
    mock_created_plan = MagicMock()
    mock_created_plan.plan_id = 123
    mock_repo_instance.create.return_value = mock_created_plan

    # ----------------------------------------------------
    # 2. テスト対象の実行 (依存関係を差し替え)
    # ----------------------------------------------------
    with patch("app.usecases.plan_generation.get_llm_client", return_value=mock_llm_client), \
         patch("app.usecases.plan_generation.PlanRepository", return_value=mock_repo_instance), \
         patch("app.usecases.plan_generation.prepare_patient_facts", return_value={"基本情報": {"年齢": "80代"}}):
        
        usecase = PlanGenerationUseCase(mock_db)
        
        result = await usecase.execute(
            hash_id="test_hash_123", 
            patient_data=create_dummy_patient_data(),
            therapist_notes="特になし"
        )

        # ----------------------------------------------------
        # 3. 検証 (Assertion)
        # ----------------------------------------------------
        assert result == mock_created_plan
        assert result.plan_id == 123
        
        # LLM呼び出し回数確認
        assert mock_llm_client.generate_json.call_count == 3
        
        # DB保存確認
        mock_repo_instance.create.assert_called_once()
        
        # トランザクションが開始されたか確認
        mock_db.begin.assert_called_once()
        # トランザクションの __aenter__ が呼ばれたか（async withに入ったか）確認
        mock_tx.__aenter__.assert_awaited_once()

@pytest.mark.asyncio
async def test_plan_generation_error_handling():
    """
    異常系テスト:
    LLMの生成途中でエラーが発生した場合、処理が中断されエラーが送出されるか
    """
    mock_db = AsyncMock()
    # 異常系でもDBモックの設定は必要（使われないかもしれないが初期化しておく）
    mock_db.begin = MagicMock()
    mock_db.begin.return_value = AsyncMock()

    mock_llm_client = MagicMock()
    # 2回目の呼び出しでエラーを発生させる
    mock_llm_client.generate_json = AsyncMock(side_effect=[
        {"risk": "ok"},
        RuntimeError("LLM API Error"),
        {"plan": "ok"}
    ])

    with patch("app.usecases.plan_generation.get_llm_client", return_value=mock_llm_client), \
         patch("app.usecases.plan_generation.prepare_patient_facts", return_value={}):
        
        usecase = PlanGenerationUseCase(mock_db)
        patient_data = create_dummy_patient_data()

        with pytest.raises(RuntimeError) as excinfo:
            await usecase.execute("hash_err", patient_data)
        
        assert "Failed to generate plan part" in str(excinfo.value)