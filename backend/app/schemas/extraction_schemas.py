from datetime import date
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, computed_field

# ==========================================
# 1. Basic & Header Information
# ==========================================
class BasicInfoSchema(BaseModel):
    """患者基本情報およびヘッダー情報"""
    name: Optional[str] = Field(None, description="患者氏名")
    age: Optional[int] = Field(None, description="患者の年齢")
    gender: Optional[Literal['男', '女']] = Field(None, description="患者の性別")

    @computed_field
    @property
    def age_display(self) -> str:
        """
        LLMに提示するための年齢表記を生成する。
        例: 83 -> "80代前半", None -> "不明"
        """
        if self.age is None:
            return "不明"
        
        try:
            decade = (self.age // 10) * 10
            half = "前半" if (self.age % 10) < 5 else "後半"
            return f"{decade}代{half}"
        except Exception:
            return "不明"

    # Header Dates & Info
    evaluation_date: Optional[date] = Field(None, description="評価日")
    disease_name: Optional[str] = Field(None, description="算定病名")
    treatment_details: Optional[str] = Field(None, description="治療内容")
    onset_date: Optional[date] = Field(None, description="発症日または手術日")
    rehab_start_date: Optional[date] = Field(None, description="リハビリテーション開始日")

    # Therapy Types
    therapy_pt: Optional[bool] = Field(None, description="理学療法(PT)の実施有無")
    therapy_ot: Optional[bool] = Field(None, description="作業療法(OT)の実施有無")
    therapy_st: Optional[bool] = Field(None, description="言語聴覚療法(ST)の実施有無")

# ==========================================
# 2. Medical Risks & Conditions
# ==========================================
class MedicalRiskSchema(BaseModel):
    """リスク管理・禁忌・併存症"""
    comorbidities: Optional[str] = Field(None, description="併存疾患・合併症")
    risks: Optional[str] = Field(None, description="安静度やリハビリテーション施行上のリスク")
    contraindications: Optional[str] = Field(None, description="禁忌や医学的な特記事項・注意点")

    # Risk Factors
    hypertension: Optional[bool] = Field(None, description="高血圧症")
    dyslipidemia: Optional[bool] = Field(None, description="脂質異常症")
    diabetes: Optional[bool] = Field(None, description="糖尿病")
    ckd: Optional[bool] = Field(None, description="慢性腎臓病(CKD)")
    angina: Optional[bool] = Field(None, description="狭心症")
    omi: Optional[bool] = Field(None, description="陳旧性心筋梗塞(OMI)")
    
    smoking: Optional[bool] = Field(None, description="喫煙歴")
    obesity: Optional[bool] = Field(None, description="肥満")
    hyperuricemia: Optional[bool] = Field(None, description="高尿酸血症")
    family_history: Optional[bool] = Field(None, description="家族歴")

    other_risk: Optional[bool] = Field(None, description="その他の危険因子")
    other_risk_txt: Optional[str] = Field(None, description="その他の危険因子の詳細")


# ==========================================
# 3. Functional Status (Body Functions)
# ==========================================
class FunctionalStatusSchema(BaseModel):
    """心身機能・身体構造"""
    # Consciousness
    consciousness_disorder: Optional[bool] = Field(None, description="意識障害の有無")
    jcs_gcs: Optional[str] = Field(None, description="意識レベル (JCS, GCS)")

    # Orientation
    disorientation: Optional[bool] = Field(None, description="見当識障害の有無")
    disorientation_detail: Optional[str] = Field(None, description="見当識障害の詳細")

    # Physical Functions
    pain: Optional[bool] = Field(None, description="疼痛の有無")
    pain_detail: Optional[str] = Field(None, description="疼痛の詳細")
    rom_limitation: Optional[bool] = Field(None, description="関節可動域制限の有無")
    rom_detail: Optional[str] = Field(None, description="関節可動域制限の詳細")
    muscle_weakness: Optional[bool] = Field(None, description="筋力低下の有無")
    muscle_detail: Optional[str] = Field(None, description="筋力低下の詳細")
    contracture: Optional[bool] = Field(None, description="拘縮・変形の有無")
    contracture_detail: Optional[str] = Field(None, description="拘縮・変形の詳細")

    # Motor Functions
    paralysis: Optional[bool] = Field(None, description="麻痺の有無")
    involuntary_movement: Optional[bool] = Field(None, description="不随意運動の有無")
    ataxia: Optional[bool] = Field(None, description="運動失調の有無")
    parkinsonism: Optional[bool] = Field(None, description="パーキンソニズムの有無")
    muscle_tone_abnormality: Optional[bool] = Field(None, description="筋緊張異常の有無")
    muscle_tone_detail: Optional[str] = Field(None, description="筋緊張異常の詳細")

    # Sensory
    hearing_disorder: Optional[bool] = Field(None, description="聴覚障害の有無")
    vision_disorder: Optional[bool] = Field(None, description="視覚障害の有無")
    sensory_superficial: Optional[bool] = Field(None, description="表在感覚障害の有無")
    sensory_deep: Optional[bool] = Field(None, description="深部感覚障害の有無")
    sensory_dysfunction: Optional[bool] = Field(None, description="感覚機能障害の有無")

    # Speech & Swallowing
    speech_disorder: Optional[bool] = Field(None, description="音声発話障害の有無")
    articulation_disorder: Optional[bool] = Field(None, description="構音障害の有無")
    aphasia: Optional[bool] = Field(None, description="失語症の有無")
    stuttering: Optional[bool] = Field(None, description="吃音の有無")
    speech_other: Optional[bool] = Field(None, description="その他の音声発話障害")
    speech_other_detail: Optional[str] = Field(None, description="その他の音声発話障害の詳細")

    swallowing_disorder: Optional[bool] = Field(None, description="摂食嚥下障害の有無")
    swallowing_detail: Optional[str] = Field(None, description="摂食嚥下障害の詳細")

    # Mental / Cognitive / Developmental
    psychiatric_disorder: Optional[bool] = Field(None, description="精神行動障害の有無")
    psychiatric_detail: Optional[str] = Field(None, description="精神行動障害の詳細")
    
    higher_brain_dysfunction: Optional[bool] = Field(None, description="高次脳機能障害の有無")
    higher_brain_memory: Optional[bool] = Field(None, description="記憶障害(高次脳)の有無")
    higher_brain_attention: Optional[bool] = Field(None, description="注意障害の有無")
    higher_brain_apraxia: Optional[bool] = Field(None, description="失行の有無")
    higher_brain_agnosia: Optional[bool] = Field(None, description="失認の有無")
    higher_brain_executive: Optional[bool] = Field(None, description="遂行機能障害の有無")

    memory_disorder: Optional[bool] = Field(None, description="記憶障害の有無")
    memory_detail: Optional[str] = Field(None, description="記憶障害の詳細")

    developmental_disorder: Optional[bool] = Field(None, description="発達障害の有無")
    developmental_asd: Optional[bool] = Field(None, description="ASDの有無")
    developmental_ld: Optional[bool] = Field(None, description="LDの有無")
    developmental_adhd: Optional[bool] = Field(None, description="ADHDの有無")
    
    # Organ Functions
    respiratory_disorder: Optional[bool] = Field(None, description="呼吸機能障害")
    respiratory_o2: Optional[bool] = Field(None, description="酸素療法")
    respiratory_o2_flow: Optional[str] = Field(None, description="酸素流量")
    respiratory_tracheostomy: Optional[bool] = Field(None, description="気管切開")
    respiratory_ventilator: Optional[bool] = Field(None, description="人工呼吸器")
    
    circulatory_disorder: Optional[bool] = Field(None, description="循環障害")
    circulatory_ef_check: Optional[bool] = Field(None, description="EF測定")
    circulatory_ef_val: Optional[int] = Field(None, description="EF値")
    circulatory_arrhythmia: Optional[bool] = Field(None, description="不整脈")
    circulatory_arrhythmia_detail: Optional[str] = Field(None, description="不整脈詳細")

    excretory_disorder: Optional[bool] = Field(None, description="排泄機能障害")
    excretory_detail: Optional[str] = Field(None, description="排泄機能障害詳細")
    
    pressure_ulcer: Optional[bool] = Field(None, description="褥瘡")
    pressure_ulcer_detail: Optional[str] = Field(None, description="褥瘡詳細")
    
    nutritional_disorder: Optional[bool] = Field(None, description="栄養障害")
    nutritional_detail: Optional[str] = Field(None, description="栄養障害詳細")

    other_disorder: Optional[bool] = Field(None, description="その他の心身機能障害")
    other_detail: Optional[str] = Field(None, description="その他の心身機能障害の詳細")


# ==========================================
# 4. Basic Movements (Optimized with Literals)
# ==========================================
class BasicMovementSchema(BaseModel):
    """基本動作能力"""
    
    # Rolling
    rolling_evaluation: Optional[bool] = Field(None, description="寝返り評価有無")
    rolling_level: Optional[Literal['independent', 'partial_assistance', 'assistance', 'not_performed']] = Field(None)
    
    # Getting Up
    getting_up_evaluation: Optional[bool] = Field(None, description="起き上がり評価有無")
    getting_up_level: Optional[Literal['independent', 'partial_assistance', 'assistance', 'not_performed']] = Field(None)

    # Standing Up
    standing_up_evaluation: Optional[bool] = Field(None, description="立ち上がり評価有無")
    standing_up_level: Optional[Literal['independent', 'partial_assistance', 'assistance', 'not_performed']] = Field(None)

    # Sitting Balance
    sitting_balance_evaluation: Optional[bool] = Field(None, description="座位保持評価有無")
    sitting_balance_level: Optional[Literal['independent', 'partial_assistance', 'assistance', 'not_performed']] = Field(None)

    # Standing Balance
    standing_balance_evaluation: Optional[bool] = Field(None, description="立位保持評価有無")
    standing_balance_level: Optional[Literal['independent', 'partial_assistance', 'assistance', 'not_performed']] = Field(None)
    
    other_basic: Optional[bool] = Field(None, description="その他基本動作評価有無")
    other_basic_detail: Optional[str] = Field(None, description="その他基本動作詳細")


# ==========================================
# 5. ADL Scores (FIM / BI)
# ==========================================
# class AdlItemSchema(BaseModel):
#     fim_start: Optional[int] = Field(None)
#     fim_current: Optional[int] = Field(None)
#     bi_start: Optional[int] = Field(None)
#     bi_current: Optional[int] = Field(None)

# 共通基底クラス（FIMのみ）
# これを認知項目（Cognitive）用としてそのまま使います
class CognitiveAdlItem(BaseModel):
    fim_start: Optional[int] = Field(None, description="開始時FIM")
    fim_current: Optional[int] = Field(None, description="現在FIM")

# 身体項目用クラス（FIM + BI）
# 基底クラスを継承して BI を追加します
class PhysicalAdlItem(CognitiveAdlItem):
    bi_start: Optional[int] = Field(None, description="開始時BI")
    bi_current: Optional[int] = Field(None, description="現在BI")


# class AdlSchema(BaseModel):
#     """ADL評価"""
#     eating: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     grooming: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     bathing: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     dressing_upper: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     dressing_lower: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     toileting: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     bladder: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     bowel: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     transfer_bed: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     transfer_toilet: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     transfer_tub: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     locomotion_walk: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     locomotion_stairs: AdlItemSchema = Field(default_factory=AdlItemSchema)
    
#     # Cognitive FIM (No BI)
#     comprehension: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     expression: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     social: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     problem_solving: AdlItemSchema = Field(default_factory=AdlItemSchema)
#     memory: AdlItemSchema = Field(default_factory=AdlItemSchema)
    
#     equipment_detail: Optional[str] = Field(None, description="ADL補装具・介助詳細")

class AdlSchema(BaseModel):
    """ADL評価"""
    # --- 身体項目 (Physical: BIあり) ---
    eating: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    grooming: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    bathing: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    dressing_upper: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    dressing_lower: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    toileting: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    bladder: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    bowel: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    transfer_bed: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    transfer_toilet: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    transfer_tub: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    locomotion_walk: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    locomotion_stairs: PhysicalAdlItem = Field(default_factory=PhysicalAdlItem)
    
    # --- 認知項目 (Cognitive: BIなし) ---
    # ここで CognitiveAdlItem を指定することで、LLMへのスキーマからBIが消えます
    comprehension: CognitiveAdlItem = Field(default_factory=CognitiveAdlItem)
    expression: CognitiveAdlItem = Field(default_factory=CognitiveAdlItem)
    social: CognitiveAdlItem = Field(default_factory=CognitiveAdlItem)
    problem_solving: CognitiveAdlItem = Field(default_factory=CognitiveAdlItem)
    memory: CognitiveAdlItem = Field(default_factory=CognitiveAdlItem)
    
    equipment_detail: Optional[str] = Field(None, description="ADL補装具・介助詳細")


# ==========================================
# 6. Nutrition & Social
# ==========================================
class NutritionSchema(BaseModel):
    height_check: Optional[bool] = Field(None)
    height: Optional[float] = Field(None)
    weight_check: Optional[bool] = Field(None)
    weight: Optional[float] = Field(None)
    bmi_check: Optional[bool] = Field(None)
    bmi: Optional[float] = Field(None)
    
    method_oral: Optional[bool] = Field(None)
    method_oral_meal: Optional[bool] = Field(None)
    method_oral_supplement: Optional[bool] = Field(None)
    method_tube: Optional[bool] = Field(None)
    method_peg: Optional[bool] = Field(None)
    method_iv: Optional[bool] = Field(None)
    method_iv_peripheral: Optional[bool] = Field(None)
    method_iv_central: Optional[bool] = Field(None)
    
    swallowing_diet_selection: Optional[str] = Field(None)
    diet_code: Optional[str] = Field(None)
    status_selection: Optional[str] = Field(None)
    status_other: Optional[str] = Field(None)

    required_energy: Optional[int] = Field(None)
    required_protein: Optional[int] = Field(None)
    total_energy: Optional[int] = Field(None)
    total_protein: Optional[int] = Field(None)

class SocialSchema(BaseModel):
    care_level_status: Optional[bool] = Field(None)
    care_level: Optional[Literal[
        'support_1', 'support_2', 
        'care_1', 'care_2', 'care_3', 'care_4', 'care_5', 
        'applying', 'none'
    ]] = Field(None)

    physical_cert_check: Optional[bool] = Field(None)
    physical_cert_detail: Optional[str] = Field(None)
    physical_cert_rank: Optional[int] = Field(None)
    physical_cert_type: Optional[str] = Field(None)

    mental_cert_check: Optional[bool] = Field(None)
    mental_cert_rank: Optional[int] = Field(None)

    intellectual_cert_check: Optional[bool] = Field(None)
    intellectual_cert_detail: Optional[str] = Field(None)
    intellectual_cert_grade: Optional[str] = Field(None)
    
    other_cert_check: Optional[bool] = Field(None)
    other_cert_detail: Optional[str] = Field(None)


# ==========================================
# 7. Goals & Plan
# ==========================================
class GoalSettingSchema(BaseModel):
    """目標設定・治療方針"""
    short_term_goal: Optional[str] = Field(None)
    long_term_goal: Optional[str] = Field(None)
    
    planned_hospitalization_check: Optional[bool] = Field(None)
    planned_hospitalization_txt: Optional[str] = Field(None)
    
    discharge_destination_check: Optional[bool] = Field(None)
    discharge_destination_txt: Optional[str] = Field(None)
    
    long_term_care_needed: Optional[bool] = Field(None)
    treatment_policy: Optional[str] = Field(None)
    policy_content: Optional[str] = Field(None)

    # Activity Goals (Literals)
    driving_check: Optional[bool] = Field(None)
    driving_status: Optional[Literal['independent', 'assistance', 'not_performed']] = Field(None)
    driving_modification: Optional[bool] = Field(None)
    driving_modification_detail: Optional[str] = Field(None)
    
    transport_check: Optional[bool] = Field(None)
    transport_status: Optional[Literal['independent', 'assistance', 'not_performed']] = Field(None)
    transport_type: Optional[bool] = Field(None)
    transport_type_detail: Optional[str] = Field(None)
    
    toileting_check: Optional[bool] = Field(None)
    toileting_status: Optional[Literal['independent', 'assistance']] = Field(None)
    toileting_clothing: Optional[bool] = Field(None)
    toileting_wiping: Optional[bool] = Field(None)
    toileting_catheter: Optional[bool] = Field(None)
    toileting_type_check: Optional[bool] = Field(None)
    toileting_western: Optional[bool] = Field(None)
    toileting_japanese: Optional[bool] = Field(None)
    toileting_other: Optional[bool] = Field(None)
    toileting_other_detail: Optional[str] = Field(None)
    
    eating_check: Optional[bool] = Field(None)
    eating_status: Optional[Literal['independent', 'assistance', 'not_performed']] = Field(None)
    eating_chopsticks: Optional[bool] = Field(None)
    eating_fork: Optional[bool] = Field(None)
    eating_tube: Optional[bool] = Field(None)
    eating_diet_form: Optional[str] = Field(None)
    
    bathing_check: Optional[bool] = Field(None)
    bathing_status: Optional[Literal['independent', 'assistance']] = Field(None)
    bathing_tub: Optional[bool] = Field(None)
    bathing_shower: Optional[bool] = Field(None)
    bathing_washing: Optional[bool] = Field(None)
    bathing_transfer: Optional[bool] = Field(None)

    grooming_check: Optional[bool] = Field(None)
    grooming_status: Optional[Literal['independent', 'assistance']] = Field(None)

    dressing_check: Optional[bool] = Field(None)
    dressing_status: Optional[Literal['independent', 'assistance']] = Field(None)
    
    housework_check: Optional[bool] = Field(None)
    housework_status: Optional[Literal['all', 'partial', 'not_performed']] = Field(None)
    housework_detail: Optional[str] = Field(None)

    writing_check: Optional[bool] = Field(None)
    writing_status: Optional[Literal['independent', 'independent_hand_change', 'other']] = Field(None)
    writing_other_detail: Optional[str] = Field(None)

    ict_check: Optional[bool] = Field(None)
    ict_status: Optional[Literal['independent', 'assistance']] = Field(None)

    communication_check: Optional[bool] = Field(None)
    communication_status: Optional[Literal['independent', 'assistance']] = Field(None)
    communication_device: Optional[bool] = Field(None)
    communication_letter_board: Optional[bool] = Field(None)
    communication_cooperation: Optional[bool] = Field(None)
    
    bed_mobility_check: Optional[bool] = Field(None)
    bed_mobility_status: Optional[Literal['independent', 'assistance', 'not_performed']] = Field(None)
    bed_mobility_equipment: Optional[bool] = Field(None)
    bed_mobility_env: Optional[bool] = Field(None)
    
    indoor_mobility_check: Optional[bool] = Field(None)
    indoor_mobility_status: Optional[Literal['independent', 'assistance', 'not_performed']] = Field(None)
    indoor_mobility_equipment: Optional[bool] = Field(None)
    indoor_mobility_equipment_detail: Optional[str] = Field(None)
    
    outdoor_mobility_check: Optional[bool] = Field(None)
    outdoor_mobility_status: Optional[Literal['independent', 'assistance', 'not_performed']] = Field(None)
    outdoor_mobility_equipment: Optional[bool] = Field(None)
    outdoor_mobility_equipment_detail: Optional[str] = Field(None)

    residence_check: Optional[bool] = Field(None)
    residence_slct: Optional[str] = Field(None)
    residence_other: Optional[str] = Field(None)
    
    return_to_work_check: Optional[bool] = Field(None)
    return_to_work_status: Optional[str] = Field(None)
    return_to_work_other: Optional[str] = Field(None)
    return_to_work_commute: Optional[bool] = Field(None)

    schooling_check: Optional[bool] = Field(None)
    schooling_status: Optional[Literal['possible', 'consideration', 'change', 'impossible', 'other']] = Field(None)
    schooling_other_detail: Optional[str] = Field(None)
    schooling_destination_check: Optional[bool] = Field(None)
    schooling_destination: Optional[str] = Field(None)
    schooling_commute: Optional[bool] = Field(None)
    schooling_commute_detail: Optional[str] = Field(None)
    
    household_role_check: Optional[bool] = Field(None)
    household_role_detail: Optional[str] = Field(None)
    
    social_activity_check: Optional[bool] = Field(None)
    social_activity_detail: Optional[str] = Field(None)
    
    hobby_check: Optional[bool] = Field(None)
    hobby_detail: Optional[str] = Field(None)
    
    # Action Plans
    goal_a_action_plan: Optional[str] = Field(None)
    goal_s_env_action_plan: Optional[str] = Field(None)
    goal_p_action_plan: Optional[str] = Field(None)
    goal_s_psychological_action_plan: Optional[str] = Field(None)
    goal_s_3rd_party_action_plan: Optional[str] = Field(None)

    # Support / Environment
    psychological_support_check: Optional[bool] = Field(None)
    psychological_support_detail: Optional[str] = Field(None)
    disability_acceptance_check: Optional[bool] = Field(None)
    disability_acceptance_detail: Optional[str] = Field(None)
    psychological_other_check: Optional[bool] = Field(None)
    psychological_other_detail: Optional[str] = Field(None)
    
    env_home_mod_check: Optional[bool] = Field(None)
    env_home_mod_detail: Optional[str] = Field(None)
    env_assistive_dev_check: Optional[bool] = Field(None)
    env_assistive_dev_detail: Optional[str] = Field(None)
    
    env_social_sec_check: Optional[bool] = Field(None)
    env_social_sec_phys_cert: Optional[bool] = Field(None)
    env_social_sec_pension: Optional[bool] = Field(None)
    env_social_sec_disease: Optional[bool] = Field(None)
    env_social_sec_other: Optional[bool] = Field(None)
    env_social_sec_other_detail: Optional[str] = Field(None)
    
    env_care_ins_check: Optional[bool] = Field(None)
    env_care_ins_detail: Optional[str] = Field(None)
    env_care_ins_outpatient: Optional[bool] = Field(None)
    env_care_ins_home_rehab: Optional[bool] = Field(None)
    env_care_ins_day_care: Optional[bool] = Field(None)
    env_care_ins_nursing: Optional[bool] = Field(None)
    env_care_ins_home_care: Optional[bool] = Field(None)
    env_care_ins_health_facility: Optional[bool] = Field(None)
    env_care_ins_nursing_home: Optional[bool] = Field(None)
    env_care_ins_care_hospital: Optional[bool] = Field(None)
    env_care_ins_other: Optional[bool] = Field(None)
    env_care_ins_other_detail: Optional[str] = Field(None)
    
    env_welfare_check: Optional[bool] = Field(None)
    env_welfare_after_school: Optional[bool] = Field(None)
    env_welfare_child_dev: Optional[bool] = Field(None)
    env_welfare_life_care: Optional[bool] = Field(None)
    env_welfare_other: Optional[bool] = Field(None)
    
    env_other_check: Optional[bool] = Field(None)
    env_other_detail: Optional[str] = Field(None)
    
    party_caregiver_check: Optional[bool] = Field(None)
    party_caregiver_detail: Optional[str] = Field(None)
    party_family_struct_check: Optional[bool] = Field(None)
    party_family_struct_detail: Optional[str] = Field(None)
    party_role_change_check: Optional[bool] = Field(None)
    party_role_change_detail: Optional[str] = Field(None)
    party_activity_change_check: Optional[bool] = Field(None)
    party_activity_change_detail: Optional[str] = Field(None)


# ==========================================
# 8. Signatures
# ==========================================
class SignatureSchema(BaseModel):
    primary_doctor: Optional[str] = Field(None)
    rehab_doctor: Optional[str] = Field(None)
    pt: Optional[str] = Field(None)
    ot: Optional[str] = Field(None)
    st: Optional[str] = Field(None)
    nurse: Optional[str] = Field(None)
    dietitian: Optional[str] = Field(None)
    social_worker: Optional[str] = Field(None)
    explained_to: Optional[str] = Field(None)
    explanation_date: Optional[date] = Field(None)
    explainer: Optional[str] = Field(None)


# ==========================================
# Root: Extraction Result
# ==========================================
class PatientExtractionSchema(BaseModel):
    basic: BasicInfoSchema
    medical: MedicalRiskSchema
    function: FunctionalStatusSchema
    basic_movement: BasicMovementSchema
    adl: AdlSchema
    nutrition: NutritionSchema
    social: SocialSchema
    goals: GoalSettingSchema
    signature: SignatureSchema

    def export_to_mapping_format(self) -> Dict[str, Any]:
        """構造化データから旧フラット形式への変換"""
        flat = {}
        
        # Helper to map literal to multiple boolean keys
        # ★Fix: valueがNoneでもキーを生成するように変更
        def map_literal(value: str | None, mapping: Dict[str, str]):
            for lit_val, legacy_key in mapping.items():
                if value is None:
                    flat[legacy_key] = None
                else:
                    flat[legacy_key] = (value == lit_val)

        # --- 1. Basic ---
        b = self.basic
        flat.update({
            "name": b.name, "age": b.age, 
            "age_display": b.age_display, "gender": b.gender,
            "header_evaluation_date": b.evaluation_date,
            "header_disease_name_txt": b.disease_name,
            "header_treatment_details_txt": b.treatment_details,
            "header_onset_date": b.onset_date,
            "header_rehab_start_date": b.rehab_start_date,
            "header_therapy_pt_chk": b.therapy_pt,
            "header_therapy_ot_chk": b.therapy_ot,
            "header_therapy_st_chk": b.therapy_st,
        })

        # --- 2. Medical ---
        m = self.medical
        flat.update({
            "main_comorbidities_txt": m.comorbidities,
            "main_risks_txt": m.risks,
            "main_contraindications_txt": m.contraindications,
            "func_risk_hypertension_chk": m.hypertension,
            "func_risk_dyslipidemia_chk": m.dyslipidemia,
            "func_risk_diabetes_chk": m.diabetes,
            "func_risk_ckd_chk": m.ckd,
            "func_risk_angina_chk": m.angina,
            "func_risk_omi_chk": m.omi,
            "func_risk_smoking_chk": m.smoking,
            "func_risk_obesity_chk": m.obesity,
            "func_risk_hyperuricemia_chk": m.hyperuricemia,
            "func_risk_family_history_chk": m.family_history,
            "func_risk_other_chk": m.other_risk,
            "func_risk_other_txt": m.other_risk_txt,
            # Calculated flag: if any risk is true, 'func_risk_factors_chk' is True
            "func_risk_factors_chk": any([
                m.hypertension, m.dyslipidemia, m.diabetes, m.ckd, 
                m.angina, m.omi, m.smoking, m.obesity, 
                m.hyperuricemia, m.family_history, m.other_risk
            ])
        })

        # --- 3. Function ---
        f = self.function
        flat.update({
            "func_consciousness_disorder_chk": f.consciousness_disorder,
            "func_consciousness_disorder_jcs_gcs_txt": f.jcs_gcs,
            "func_disorientation_chk": f.disorientation,
            "func_disorientation_txt": f.disorientation_detail,
            "func_pain_chk": f.pain,
            "func_pain_txt": f.pain_detail,
            "func_rom_limitation_chk": f.rom_limitation,
            "func_rom_limitation_txt": f.rom_detail,
            "func_muscle_weakness_chk": f.muscle_weakness,
            "func_muscle_weakness_txt": f.muscle_detail,
            "func_contracture_deformity_chk": f.contracture,
            "func_contracture_deformity_txt": f.contracture_detail,
            "func_motor_paralysis_chk": f.paralysis,
            "func_motor_involuntary_movement_chk": f.involuntary_movement,
            "func_motor_ataxia_chk": f.ataxia,
            "func_motor_parkinsonism_chk": f.parkinsonism,
            "func_motor_muscle_tone_abnormality_chk": f.muscle_tone_abnormality,
            "func_motor_muscle_tone_abnormality_txt": f.muscle_tone_detail,
            "func_sensory_hearing_chk": f.hearing_disorder,
            "func_sensory_vision_chk": f.vision_disorder,
            "func_sensory_superficial_chk": f.sensory_superficial,
            "func_sensory_deep_chk": f.sensory_deep,
            "func_sensory_dysfunction_chk": f.sensory_dysfunction,
            "func_speech_disorder_chk": f.speech_disorder,
            "func_speech_articulation_chk": f.articulation_disorder,
            "func_speech_aphasia_chk": f.aphasia,
            "func_speech_stuttering_chk": f.stuttering,
            "func_speech_other_chk": f.speech_other,
            "func_speech_other_txt": f.speech_other_detail,
            "func_swallowing_disorder_chk": f.swallowing_disorder,
            "func_swallowing_disorder_txt": f.swallowing_detail,
            "func_behavioral_psychiatric_disorder_chk": f.psychiatric_disorder,
            "func_behavioral_psychiatric_disorder_txt": f.psychiatric_detail,
            "func_higher_brain_dysfunction_chk": f.higher_brain_dysfunction,
            "func_higher_brain_memory_chk": f.higher_brain_memory,
            "func_higher_brain_attention_chk": f.higher_brain_attention,
            "func_higher_brain_apraxia_chk": f.higher_brain_apraxia,
            "func_higher_brain_agnosia_chk": f.higher_brain_agnosia,
            "func_higher_brain_executive_chk": f.higher_brain_executive,
            "func_memory_disorder_chk": f.memory_disorder,
            "func_memory_disorder_txt": f.memory_detail,
            "func_developmental_disorder_chk": f.developmental_disorder,
            "func_developmental_asd_chk": f.developmental_asd,
            "func_developmental_ld_chk": f.developmental_ld,
            "func_developmental_adhd_chk": f.developmental_adhd,
            "func_respiratory_disorder_chk": f.respiratory_disorder,
            "func_respiratory_o2_therapy_chk": f.respiratory_o2,
            "func_respiratory_o2_therapy_l_min_txt": f.respiratory_o2_flow,
            "func_respiratory_tracheostomy_chk": f.respiratory_tracheostomy,
            "func_respiratory_ventilator_chk": f.respiratory_ventilator,
            "func_circulatory_disorder_chk": f.circulatory_disorder,
            "func_circulatory_ef_chk": f.circulatory_ef_check,
            "func_circulatory_ef_val": f.circulatory_ef_val,
            "func_circulatory_arrhythmia_chk": f.circulatory_arrhythmia,
            "func_circulatory_arrhythmia_status_slct": f.circulatory_arrhythmia_detail,
            "func_excretory_disorder_chk": f.excretory_disorder,
            "func_excretory_disorder_txt": f.excretory_detail,
            "func_pressure_ulcer_chk": f.pressure_ulcer,
            "func_pressure_ulcer_txt": f.pressure_ulcer_detail,
            "func_nutritional_disorder_chk": f.nutritional_disorder,
            "func_nutritional_disorder_txt": f.nutritional_detail,
            "func_other_chk": f.other_disorder,
            "func_other_txt": f.other_detail,
            "func_motor_dysfunction_chk": any([f.paralysis, f.involuntary_movement, f.ataxia, f.parkinsonism]),
        })

        # --- 4. Basic Movements (Literal Mapping) ---
        bm = self.basic_movement
        flat["func_basic_rolling_chk"] = bm.rolling_evaluation
        map_literal(bm.rolling_level, {
            'independent': 'func_basic_rolling_independent_chk',
            'partial_assistance': 'func_basic_rolling_partial_assistance_chk',
            'assistance': 'func_basic_rolling_assistance_chk',
            'not_performed': 'func_basic_rolling_not_performed_chk'
        })
        flat["func_basic_getting_up_chk"] = bm.getting_up_evaluation
        map_literal(bm.getting_up_level, {
            'independent': 'func_basic_getting_up_independent_chk',
            'partial_assistance': 'func_basic_getting_up_partial_assistance_chk',
            'assistance': 'func_basic_getting_up_assistance_chk',
            'not_performed': 'func_basic_getting_up_not_performed_chk'
        })
        flat["func_basic_standing_up_chk"] = bm.standing_up_evaluation
        map_literal(bm.standing_up_level, {
            'independent': 'func_basic_standing_up_independent_chk',
            'partial_assistance': 'func_basic_standing_up_partial_assistance_chk',
            'assistance': 'func_basic_standing_up_assistance_chk',
            'not_performed': 'func_basic_standing_up_not_performed_chk'
        })
        flat["func_basic_sitting_balance_chk"] = bm.sitting_balance_evaluation
        map_literal(bm.sitting_balance_level, {
            'independent': 'func_basic_sitting_balance_independent_chk',
            'partial_assistance': 'func_basic_sitting_balance_partial_assistance_chk',
            'assistance': 'func_basic_sitting_balance_assistance_chk',
            'not_performed': 'func_basic_sitting_balance_not_performed_chk'
        })
        flat["func_basic_standing_balance_chk"] = bm.standing_balance_evaluation
        map_literal(bm.standing_balance_level, {
            'independent': 'func_basic_standing_balance_independent_chk',
            'partial_assistance': 'func_basic_standing_balance_partial_assistance_chk',
            'assistance': 'func_basic_standing_balance_assistance_chk',
            'not_performed': 'func_basic_standing_balance_not_performed_chk'
        })
        flat["func_basic_other_chk"] = bm.other_basic
        flat["func_basic_other_txt"] = bm.other_basic_detail

        # --- 5. ADL (Nested Mapping) ---
        adl = self.adl
        adl_map = {
            'eating': 'adl_eating',
            'grooming': 'adl_grooming',
            'bathing': 'adl_bathing',
            'dressing_upper': 'adl_dressing_upper',
            'dressing_lower': 'adl_dressing_lower',
            'toileting': 'adl_toileting',
            'bladder': 'adl_bladder_management',
            'bowel': 'adl_bowel_management',
            'transfer_bed': 'adl_transfer_bed_chair_wc',
            'transfer_toilet': 'adl_transfer_toilet',
            'transfer_tub': 'adl_transfer_tub_shower',
            'locomotion_walk': 'adl_locomotion_walk_walkingAids_wc',
            'locomotion_stairs': 'adl_locomotion_stairs',
            'comprehension': 'adl_comprehension',
            'expression': 'adl_expression',
            'social': 'adl_social_interaction',
            'problem_solving': 'adl_problem_solving',
            'memory': 'adl_memory',
        }

        # 旧スキーマには存在しない「詳細項目のBIキー」を生成しないための除外リスト
        # これらは旧スキーマでは 'adl_dressing_bi_...' や 'adl_transfer_bi_...' として
        # まとめて管理されていたため、個別のキーを作ると「Extra」になります。
        bi_skip_items = {
            'dressing_upper', 'dressing_lower', 
            'transfer_bed', 'transfer_toilet', 'transfer_tub'
        }

        for new_f, old_prefix in adl_map.items():
            item = getattr(adl, new_f)
            flat[f"{old_prefix}_fim_start_val"] = item.fim_start
            flat[f"{old_prefix}_fim_current_val"] = item.fim_current

            # クラスが分かれたので、getattr(obj, name, default) を使えば
            # 「BIフィールドを持っていない認知項目」は自然に None になり、
            # 「BIフィールドを持つ身体項目」だけ値が取れるようになります。
            # ホワイトリストによる手動フィルタリングは不要になります。
            # itemが bi_start を持っている場合（つまりPhysicalAdlItemの場合）だけキーを作る
            if hasattr(item, 'bi_start') and new_f not in bi_skip_items:
                flat[f"{old_prefix}_bi_start_val"] = item.bi_start
                flat[f"{old_prefix}_bi_current_val"] = item.bi_current


            # if hasattr(item, 'bi_start'):
            #     flat[f"{old_prefix}_bi_start_val"] = getattr(item, 'bi_start', None)
            #     flat[f"{old_prefix}_bi_current_val"] = getattr(item, 'bi_current', None)
        
        # ★Fix: BI Summary Keys (Dressing & Transfer)
        # Legacy schema has generic 'adl_dressing_bi' and 'adl_transfer_bi' keys.
        # We assume dressing_upper and transfer_bed represent these scores for now.
        flat["adl_dressing_bi_start_val"] = adl.dressing_upper.bi_start
        flat["adl_dressing_bi_current_val"] = adl.dressing_upper.bi_current
        flat["adl_transfer_bi_start_val"] = adl.transfer_bed.bi_start
        flat["adl_transfer_bi_current_val"] = adl.transfer_bed.bi_current

        flat["adl_equipment_and_assistance_details_txt"] = adl.equipment_detail

        # --- 6. Nutrition ---
        n = self.nutrition
        flat.update({
            "nutrition_height_chk": n.height_check, "nutrition_height_val": n.height,
            "nutrition_weight_chk": n.weight_check, "nutrition_weight_val": n.weight,
            "nutrition_bmi_chk": n.bmi_check, "nutrition_bmi_val": n.bmi,
            "nutrition_method_oral_chk": n.method_oral,
            "nutrition_method_oral_meal_chk": n.method_oral_meal,
            "nutrition_method_oral_supplement_chk": n.method_oral_supplement,
            "nutrition_method_tube_chk": n.method_tube,
            "nutrition_method_peg_chk": n.method_peg,
            "nutrition_method_iv_chk": n.method_iv,
            "nutrition_method_iv_peripheral_chk": n.method_iv_peripheral,
            "nutrition_method_iv_central_chk": n.method_iv_central,
            "nutrition_swallowing_diet_slct": n.swallowing_diet_selection,
            "nutrition_swallowing_diet_code_txt": n.diet_code,
            "nutrition_status_assessment_slct": n.status_selection,
            "nutrition_status_assessment_other_txt": n.status_other,
            "nutrition_required_energy_val": n.required_energy,
            "nutrition_required_protein_val": n.required_protein,
            "nutrition_total_intake_energy_val": n.total_energy,
            "nutrition_total_intake_protein_val": n.total_protein,
        })

        # --- 7. Social ---
        soc = self.social
        flat["social_care_level_status_chk"] = soc.care_level_status
        if soc.care_level:
            flat["social_care_level_applying_chk"] = (soc.care_level == 'applying')
            flat["social_care_level_support_chk"] = soc.care_level in ['support_1', 'support_2']
            flat["social_care_level_support_num1_slct"] = (soc.care_level == 'support_1')
            flat["social_care_level_support_num2_slct"] = (soc.care_level == 'support_2')
            
            is_care = soc.care_level in ['care_1', 'care_2', 'care_3', 'care_4', 'care_5']
            flat["social_care_level_care_slct"] = is_care
            flat["social_care_level_care_num1_slct"] = (soc.care_level == 'care_1')
            flat["social_care_level_care_num2_slct"] = (soc.care_level == 'care_2')
            flat["social_care_level_care_num3_slct"] = (soc.care_level == 'care_3')
            flat["social_care_level_care_num4_slct"] = (soc.care_level == 'care_4')
            flat["social_care_level_care_num5_slct"] = (soc.care_level == 'care_5')
        # If None, output None/False for keys
        elif soc.care_level is None:
             flat.update({
                "social_care_level_applying_chk": None,
                "social_care_level_support_chk": None,
                "social_care_level_support_num1_slct": None,
                "social_care_level_support_num2_slct": None,
                "social_care_level_care_slct": None,
                "social_care_level_care_num1_slct": None,
                "social_care_level_care_num2_slct": None,
                "social_care_level_care_num3_slct": None,
                "social_care_level_care_num4_slct": None,
                "social_care_level_care_num5_slct": None,
             })

        flat.update({
            "social_disability_certificate_physical_chk": soc.physical_cert_check,
            "social_disability_certificate_physical_txt": soc.physical_cert_detail,
            "social_disability_certificate_physical_rank_val": soc.physical_cert_rank,
            "social_disability_certificate_physical_type_txt": soc.physical_cert_type,
            "social_disability_certificate_mental_chk": soc.mental_cert_check,
            "social_disability_certificate_mental_rank_val": soc.mental_cert_rank,
            "social_disability_certificate_intellectual_chk": soc.intellectual_cert_check,
            "social_disability_certificate_intellectual_txt": soc.intellectual_cert_detail,
            "social_disability_certificate_intellectual_grade_txt": soc.intellectual_cert_grade,
            "social_disability_certificate_other_chk": soc.other_cert_check,
            "social_disability_certificate_other_txt": soc.other_cert_detail,
        })

        # --- 8. Goals ---
        g = self.goals
        flat.update({
            "goals_1_month_txt": g.short_term_goal,
            "goals_at_discharge_txt": g.long_term_goal,
            "goals_planned_hospitalization_period_chk": g.planned_hospitalization_check,
            "goals_planned_hospitalization_period_txt": g.planned_hospitalization_txt,
            "goals_discharge_destination_chk": g.discharge_destination_check,
            "goals_discharge_destination_txt": g.discharge_destination_txt,
            "goals_long_term_care_needed_chk": g.long_term_care_needed,
            "policy_treatment_txt": g.treatment_policy,
            "policy_content_txt": g.policy_content,
        })
        flat["goal_a_driving_chk"] = g.driving_check
        map_literal(g.driving_status, {
            'independent': 'goal_a_driving_independent_chk',
            'assistance': 'goal_a_driving_assistance_chk',
            'not_performed': 'goal_a_driving_not_performed_chk'
        })
        flat["goal_a_driving_modification_chk"] = g.driving_modification
        flat["goal_a_driving_modification_txt"] = g.driving_modification_detail

        flat["goal_a_public_transport_chk"] = g.transport_check
        map_literal(g.transport_status, {
            'independent': 'goal_a_public_transport_independent_chk',
            'assistance': 'goal_a_public_transport_assistance_chk',
            'not_performed': 'goal_a_public_transport_not_performed_chk'
        })
        flat["goal_a_public_transport_type_chk"] = g.transport_type
        flat["goal_a_public_transport_type_txt"] = g.transport_type_detail

        flat["goal_a_toileting_chk"] = g.toileting_check
        map_literal(g.toileting_status, {
            'independent': 'goal_a_toileting_independent_chk',
            'assistance': 'goal_a_toileting_assistance_chk',
        })
        flat.update({
            "goal_a_toileting_assistance_clothing_chk": g.toileting_clothing,
            "goal_a_toileting_assistance_wiping_chk": g.toileting_wiping,
            "goal_a_toileting_assistance_catheter_chk": g.toileting_catheter,
            "goal_a_toileting_type_chk": g.toileting_type_check,
            "goal_a_toileting_type_western_chk": g.toileting_western,
            "goal_a_toileting_type_japanese_chk": g.toileting_japanese,
            "goal_a_toileting_type_other_chk": g.toileting_other,
            "goal_a_toileting_type_other_txt": g.toileting_other_detail,
        })
        
        flat["goal_a_eating_chk"] = g.eating_check
        map_literal(g.eating_status, {
            'independent': 'goal_a_eating_independent_chk',
            'assistance': 'goal_a_eating_assistance_chk',
            'not_performed': 'goal_a_eating_not_performed_chk'
        })
        flat.update({
            "goal_a_eating_method_chopsticks_chk": g.eating_chopsticks,
            "goal_a_eating_method_fork_etc_chk": g.eating_fork,
            "goal_a_eating_method_tube_feeding_chk": g.eating_tube,
            "goal_a_eating_diet_form_txt": g.eating_diet_form,
        })

        flat["goal_a_bathing_chk"] = g.bathing_check
        map_literal(g.bathing_status, {
            'independent': 'goal_a_bathing_independent_chk',
            'assistance': 'goal_a_bathing_assistance_chk',
        })
        flat.update({
            "goal_a_bathing_type_tub_chk": g.bathing_tub,
            "goal_a_bathing_type_shower_chk": g.bathing_shower,
            "goal_a_bathing_assistance_body_washing_chk": g.bathing_washing,
            "goal_a_bathing_assistance_transfer_chk": g.bathing_transfer,
        })

        flat["goal_a_grooming_chk"] = g.grooming_check
        map_literal(g.grooming_status, {
            'independent': 'goal_a_grooming_independent_chk',
            'assistance': 'goal_a_grooming_assistance_chk',
        })

        flat["goal_a_dressing_chk"] = g.dressing_check
        map_literal(g.dressing_status, {
            'independent': 'goal_a_dressing_independent_chk',
            'assistance': 'goal_a_dressing_assistance_chk',
        })

        flat["goal_a_housework_meal_chk"] = g.housework_check
        map_literal(g.housework_status, {
            'all': 'goal_a_housework_meal_all_chk',
            'partial': 'goal_a_housework_meal_partial_chk',
            'not_performed': 'goal_a_housework_meal_not_performed_chk'
        })
        flat["goal_a_housework_meal_partial_txt"] = g.housework_detail

        flat["goal_a_writing_chk"] = g.writing_check
        map_literal(g.writing_status, {
            'independent': 'goal_a_writing_independent_chk',
            'independent_hand_change': 'goal_a_writing_independent_after_hand_change_chk',
            'other': 'goal_a_writing_other_chk'
        })
        flat["goal_a_writing_other_txt"] = g.writing_other_detail

        flat["goal_a_ict_chk"] = g.ict_check
        map_literal(g.ict_status, {
            'independent': 'goal_a_ict_independent_chk',
            'assistance': 'goal_a_ict_assistance_chk',
        })

        flat["goal_a_communication_chk"] = g.communication_check
        map_literal(g.communication_status, {
            'independent': 'goal_a_communication_independent_chk',
            'assistance': 'goal_a_communication_assistance_chk',
        })
        flat.update({
            "goal_a_communication_device_chk": g.communication_device,
            "goal_a_communication_letter_board_chk": g.communication_letter_board,
            "goal_a_communication_cooperation_chk": g.communication_cooperation,
        })

        flat["goal_a_bed_mobility_chk"] = g.bed_mobility_check
        map_literal(g.bed_mobility_status, {
            'independent': 'goal_a_bed_mobility_independent_chk',
            'assistance': 'goal_a_bed_mobility_assistance_chk',
            'not_performed': 'goal_a_bed_mobility_not_performed_chk'
        })
        flat["goal_a_bed_mobility_equipment_chk"] = g.bed_mobility_equipment
        flat["goal_a_bed_mobility_environment_setup_chk"] = g.bed_mobility_env

        flat["goal_a_indoor_mobility_chk"] = g.indoor_mobility_check
        map_literal(g.indoor_mobility_status, {
            'independent': 'goal_a_indoor_mobility_independent_chk',
            'assistance': 'goal_a_indoor_mobility_assistance_chk',
            'not_performed': 'goal_a_indoor_mobility_not_performed_chk'
        })
        flat["goal_a_indoor_mobility_equipment_chk"] = g.indoor_mobility_equipment
        flat["goal_a_indoor_mobility_equipment_txt"] = g.indoor_mobility_equipment_detail

        flat["goal_a_outdoor_mobility_chk"] = g.outdoor_mobility_check
        map_literal(g.outdoor_mobility_status, {
            'independent': 'goal_a_outdoor_mobility_independent_chk',
            'assistance': 'goal_a_outdoor_mobility_assistance_chk',
            'not_performed': 'goal_a_outdoor_mobility_not_performed_chk'
        })
        flat["goal_a_outdoor_mobility_equipment_chk"] = g.outdoor_mobility_equipment
        flat["goal_a_outdoor_mobility_equipment_txt"] = g.outdoor_mobility_equipment_detail

        flat["goal_p_residence_chk"] = g.residence_check
        flat["goal_p_residence_slct"] = g.residence_slct
        flat["goal_p_residence_other_txt"] = g.residence_other

        flat["goal_p_return_to_work_chk"] = g.return_to_work_check
        flat["goal_p_return_to_work_status_slct"] = g.return_to_work_status
        flat["goal_p_return_to_work_status_other_txt"] = g.return_to_work_other
        flat["goal_p_return_to_work_commute_change_chk"] = g.return_to_work_commute

        flat["goal_p_schooling_chk"] = g.schooling_check
        map_literal(g.schooling_status, {
            'possible': 'goal_p_schooling_status_possible_chk',
            'consideration': 'goal_p_schooling_status_needs_consideration_chk',
            'change': 'goal_p_schooling_status_change_course_chk',
            'impossible': 'goal_p_schooling_status_not_possible_chk',
            'other': 'goal_p_schooling_status_other_chk'
        })
        flat.update({
            "goal_p_schooling_status_other_txt": g.schooling_other_detail,
            "goal_p_schooling_destination_chk": g.schooling_destination_check,
            "goal_p_schooling_destination_txt": g.schooling_destination,
            "goal_p_schooling_commute_change_chk": g.schooling_commute,
            "goal_p_schooling_commute_change_txt": g.schooling_commute_detail,
            "goal_p_household_role_chk": g.household_role_check,
            "goal_p_household_role_txt": g.household_role_detail,
            "goal_p_social_activity_chk": g.social_activity_check,
            "goal_p_social_activity_txt": g.social_activity_detail,
            "goal_p_hobby_chk": g.hobby_check,
            "goal_p_hobby_txt": g.hobby_detail,
            "goal_a_action_plan_txt": g.goal_a_action_plan,
            "goal_s_env_action_plan_txt": g.goal_s_env_action_plan,
            "goal_p_action_plan_txt": g.goal_p_action_plan,
            "goal_s_psychological_action_plan_txt": g.goal_s_psychological_action_plan,
            "goal_s_3rd_party_action_plan_txt": g.goal_s_3rd_party_action_plan,
        })

        # Support & Env
        flat.update({
            "goal_s_psychological_support_chk": g.psychological_support_check,
            "goal_s_psychological_support_txt": g.psychological_support_detail,
            "goal_s_disability_acceptance_chk": g.disability_acceptance_check,
            "goal_s_disability_acceptance_txt": g.disability_acceptance_detail,
            "goal_s_psychological_other_chk": g.psychological_other_check,
            "goal_s_psychological_other_txt": g.psychological_other_detail,
            "goal_s_env_home_modification_chk": g.env_home_mod_check,
            "goal_s_env_home_modification_txt": g.env_home_mod_detail,
            "goal_s_env_assistive_device_chk": g.env_assistive_dev_check,
            "goal_s_env_assistive_device_txt": g.env_assistive_dev_detail,
            "goal_s_env_social_security_chk": g.env_social_sec_check,
            "goal_s_env_social_security_physical_disability_cert_chk": g.env_social_sec_phys_cert,
            "goal_s_env_social_security_disability_pension_chk": g.env_social_sec_pension,
            "goal_s_env_social_security_intractable_disease_cert_chk": g.env_social_sec_disease,
            "goal_s_env_social_security_other_chk": g.env_social_sec_other,
            "goal_s_env_social_security_other_txt": g.env_social_sec_other_detail,
            "goal_s_env_care_insurance_chk": g.env_care_ins_check,
            "goal_s_env_care_insurance_details_txt": g.env_care_ins_detail,
            "goal_s_env_care_insurance_outpatient_rehab_chk": g.env_care_ins_outpatient,
            "goal_s_env_care_insurance_home_rehab_chk": g.env_care_ins_home_rehab,
            "goal_s_env_care_insurance_day_care_chk": g.env_care_ins_day_care,
            "goal_s_env_care_insurance_home_nursing_chk": g.env_care_ins_nursing,
            "goal_s_env_care_insurance_home_care_chk": g.env_care_ins_home_care,
            "goal_s_env_care_insurance_health_facility_chk": g.env_care_ins_health_facility,
            "goal_s_env_care_insurance_nursing_home_chk": g.env_care_ins_nursing_home,
            "goal_s_env_care_insurance_care_hospital_chk": g.env_care_ins_care_hospital,
            "goal_s_env_care_insurance_other_chk": g.env_care_ins_other,
            "goal_s_env_care_insurance_other_txt": g.env_care_ins_other_detail,
            "goal_s_env_disability_welfare_chk": g.env_welfare_check,
            "goal_s_env_disability_welfare_after_school_day_service_chk": g.env_welfare_after_school,
            "goal_s_env_disability_welfare_child_development_support_chk": g.env_welfare_child_dev,
            "goal_s_env_disability_welfare_life_care_chk": g.env_welfare_life_care,
            "goal_s_env_disability_welfare_other_chk": g.env_welfare_other,
            "goal_s_env_other_chk": g.env_other_check,
            "goal_s_env_other_txt": g.env_other_detail,
            "goal_s_3rd_party_main_caregiver_chk": g.party_caregiver_check,
            "goal_s_3rd_party_main_caregiver_txt": g.party_caregiver_detail,
            "goal_s_3rd_party_family_structure_change_chk": g.party_family_struct_check,
            "goal_s_3rd_party_family_structure_change_txt": g.party_family_struct_detail,
            "goal_s_3rd_party_household_role_change_chk": g.party_role_change_check,
            "goal_s_3rd_party_household_role_change_txt": g.party_role_change_detail,
            "goal_s_3rd_party_family_activity_change_chk": g.party_activity_change_check,
            "goal_s_3rd_party_family_activity_change_txt": g.party_activity_change_detail,
        })

        # --- 8. Signatures ---
        s = self.signature
        flat.update({
            "signature_primary_doctor_txt": s.primary_doctor,
            "signature_rehab_doctor_txt": s.rehab_doctor,
            "signature_pt_txt": s.pt,
            "signature_ot_txt": s.ot,
            "signature_st_txt": s.st,
            "signature_nurse_txt": s.nurse,
            "signature_dietitian_txt": s.dietitian,
            "signature_social_worker_txt": s.social_worker,
            "signature_explained_to_txt": s.explained_to,
            "signature_explanation_date": s.explanation_date,
            "signature_explainer_txt": s.explainer,
        })

        return flat