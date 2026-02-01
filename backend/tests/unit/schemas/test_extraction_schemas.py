# backend/tests/unit/schemas/test_extraction_schemas.py

import pytest
from datetime import date
from app.schemas.extraction_schemas import (
    PatientExtractionSchema,
    BasicInfoSchema,
    MedicalRiskSchema,
    FunctionalStatusSchema,
    BasicMovementSchema,
    AdlSchema,
    PhysicalAdlItem,
    CognitiveAdlItem,
    NutritionSchema,
    SocialSchema,
    GoalSettingSchema,
    SignatureSchema
)

class TestExtractionSchemas:
    """
    PatientExtractionSchema の変換ロジック (export_to_mapping_format) を検証するテスト
    """

    def test_basic_info_export(self):
        """基本情報が正しくフラット化されるか"""
        basic = BasicInfoSchema(
            name="田中 太郎",
            age=80,
            gender="男",
            evaluation_date=date(2026, 4, 1),
            therapy_pt=True,
            therapy_st=False
        )
        # 他のフィールドは空で初期化
        schema = self._create_dummy_schema(basic=basic)
        
        flat = schema.export_to_mapping_format()
        
        assert flat["name"] == "田中 太郎"
        assert flat["age"] == 80
        assert flat["gender"] == "男"
        assert flat["header_evaluation_date"] == date(2026, 4, 1)
        assert flat["header_therapy_pt_chk"] is True
        assert flat["header_therapy_st_chk"] is False
        assert flat["header_therapy_ot_chk"] is None  # 指定していない場合はNone

    def test_medical_risk_calculation(self):
        """リスク因子の有無(func_risk_factors_chk)が自動計算されるか"""
        # ケース1: リスクなし
        schema_none = self._create_dummy_schema(medical=MedicalRiskSchema())
        assert schema_none.export_to_mapping_format()["func_risk_factors_chk"] is False

        # ケース2: 高血圧のみあり -> リスクありと判定されるべき
        schema_has_risk = self._create_dummy_schema(
            medical=MedicalRiskSchema(hypertension=True)
        )
        flat = schema_has_risk.export_to_mapping_format()
        assert flat["func_risk_hypertension_chk"] is True
        assert flat["func_risk_factors_chk"] is True

    def test_basic_movement_literal_mapping(self):
        """Literal型(寝返りレベル等)が正しいBooleanフラグに展開されるか"""
        # ケース1: 自立 (independent)
        bm_indep = BasicMovementSchema(rolling_level="independent")
        schema = self._create_dummy_schema(basic_movement=bm_indep)
        flat = schema.export_to_mapping_format()
        
        assert flat["func_basic_rolling_independent_chk"] is True
        assert flat["func_basic_rolling_partial_assistance_chk"] is False
        assert flat["func_basic_rolling_assistance_chk"] is False

        # ケース2: 全介助 (assistance)
        bm_assist = BasicMovementSchema(rolling_level="assistance")
        schema = self._create_dummy_schema(basic_movement=bm_assist)
        flat = schema.export_to_mapping_format()
        
        assert flat["func_basic_rolling_independent_chk"] is False
        assert flat["func_basic_rolling_assistance_chk"] is True

    def test_adl_mapping_and_bi_logic(self):
        """ADL項目のマッピングと、BIスコアの特殊処理(身体/認知の区別)の検証"""
        adl = AdlSchema(
            # 身体項目: FIMとBIがある
            eating=PhysicalAdlItem(
                fim_start=5, fim_current=6,
                bi_start=5, bi_current=10
            ),
            # 認知項目: FIMのみ (CognitiveAdlItemには bi_start フィールド自体がない)
            comprehension=CognitiveAdlItem(
                fim_start=4, fim_current=5
            ),
            # 更衣（上半身）: BIの集約キーのソースになる
            dressing_upper=PhysicalAdlItem(
                bi_start=5, bi_current=10
            ),
            # 移乗（ベッド）: BIの集約キーのソースになる
            transfer_bed=PhysicalAdlItem(
                bi_start=10, bi_current=15
            )
        )
        schema = self._create_dummy_schema(adl=adl)
        flat = schema.export_to_mapping_format()

        # 1. 通常のマッピング確認 (食事)
        assert flat["adl_eating_fim_start_val"] == 5
        assert flat["adl_eating_bi_start_val"] == 5

        # 2. 認知項目の確認 (理解)
        assert flat["adl_comprehension_fim_start_val"] == 4
        # BIキーが存在しない、またはNoneであることを確認
        # (ロジック修正によりキー自体が生成されないか、Noneになるかを確認)
        assert "adl_comprehension_bi_start_val" not in flat

        # 3. BI集約キーの確認 (更衣・移乗)
        # 更衣のBIは dressing_upper から取得される仕様
        assert flat["adl_dressing_bi_start_val"] == 5  
        assert flat["adl_dressing_bi_current_val"] == 10
        # 移乗のBIは transfer_bed から取得される仕様
        assert flat["adl_transfer_bi_start_val"] == 10

    def test_social_care_level_mapping(self):
        """介護度のLiteralが複数のフラグに正しく変換されるか"""
        # ケース: 要介護2
        social = SocialSchema(care_level="care_2")
        schema = self._create_dummy_schema(social=social)
        flat = schema.export_to_mapping_format()

        # 要介護フラグがON
        assert flat["social_care_level_care_slct"] is True
        # 要支援フラグはOFF
        assert flat["social_care_level_support_chk"] is False
        # 個別の数値フラグ
        assert flat["social_care_level_care_num2_slct"] is True
        assert flat["social_care_level_care_num1_slct"] is False

    def test_goal_setting_literals(self):
        """目標設定のLiteral展開"""
        # 食事: 自立, 入浴: 介助
        goals = GoalSettingSchema(
            eating_status="independent",
            bathing_status="assistance"
        )
        schema = self._create_dummy_schema(goals=goals)
        flat = schema.export_to_mapping_format()

        assert flat["goal_a_eating_independent_chk"] is True
        assert flat["goal_a_eating_assistance_chk"] is False
        
        assert flat["goal_a_bathing_independent_chk"] is False
        assert flat["goal_a_bathing_assistance_chk"] is True

    # --- Helper Method ---
    def _create_dummy_schema(
        self, 
        basic=None, medical=None, function=None, basic_movement=None,
        adl=None, nutrition=None, social=None, goals=None, signature=None
    ):
        """テスト用に一部のデータだけ指定し、他はデフォルト(空)で埋めるヘルパー"""
        return PatientExtractionSchema(
            basic=basic or BasicInfoSchema(),
            medical=medical or MedicalRiskSchema(),
            function=function or FunctionalStatusSchema(),
            basic_movement=basic_movement or BasicMovementSchema(),
            adl=adl or AdlSchema(),
            nutrition=nutrition or NutritionSchema(),
            social=social or SocialSchema(),
            goals=goals or GoalSettingSchema(),
            signature=signature or SignatureSchema()
        )
    
    def test_age_display_logic(self):
        """年齢が正しく年代・前半後半に変換されるか"""
        # 83歳 -> 80代前半
        schema1 = self._create_dummy_schema(basic=BasicInfoSchema(age=83))
        assert schema1.basic.age_display == "80代前半"

        # 78歳 -> 70代後半
        schema2 = self._create_dummy_schema(basic=BasicInfoSchema(age=78))
        assert schema2.basic.age_display == "70代後半"
        
        # None -> 不明
        schema3 = self._create_dummy_schema(basic=BasicInfoSchema(age=None))
        assert schema3.basic.age_display == "不明"