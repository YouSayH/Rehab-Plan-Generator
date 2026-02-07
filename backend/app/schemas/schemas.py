from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

# ----------------------------------------------------------------
# 1. 患者 (Patient) スキーマ
# ----------------------------------------------------------------
class PatientBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis_code: Optional[str] = None
    admission_date: Optional[date] = None
    
    onset_date: Optional[date] = None
    outcome: Optional[str] = None
    total_fim_admission: Optional[int] = None
    total_fim_discharge: Optional[int] = None
    
    # ONNXスコア
    mental_min: Optional[float] = None
    mental_mean: Optional[float] = None
    mental_std: Optional[float] = None
    physical_mean: Optional[float] = None
    
    # 正解データ (Plan text)
    plan_text: Optional[str] = None

class PatientCreate(PatientBase):
    # 作成時はハッシュIDが必須
    hash_id: str
    # ベクトルはList[float]で受け取る（任意）
    social_vector: Optional[List[float]] = None

class PatientRead(PatientBase):
    hash_id: str
    synced_at: datetime
    
    # ベクトルデータはサイズが大きいので、通常リスト表示では含めないことが多いが、
    # 必要ならここで定義する (今回は省略またはOptional)
    # social_vector: Optional[List[float]] = None 

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------------
# 2. 計画書 (Plan) スキーマ
# ----------------------------------------------------------------
class PlanBase(BaseModel):
    doc_date: date = Field(default_factory=date.today)
    format_version: str = "v1.0"
    # 様式23の全データを格納する自由な辞書
    raw_data: Dict[str, Any] = {}

class PlanCreate(PlanBase):
    hash_id: str

class PlanUpdate(BaseModel):
    # 部分更新用
    raw_data: Dict[str, Any]

class PlanRead(PlanBase):
    plan_id: int
    hash_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------------
# 3. ドキュメント (Document / RAG source) スキーマ
# ----------------------------------------------------------------
class DocumentBase(BaseModel):
    doc_date: date
    doc_type: str
    source_type: str = "EHR"
    summary_text: Optional[str] = None
    original_text: Optional[str] = None
    # 検索用タグ (GiNZA抽出結果)
    entities: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    hash_id: str
    # ベクトルデータは作成時に計算して入れる（オプション）
    content_vector: Optional[List[float]] = None

class DocumentRead(DocumentBase):
    doc_id: int
    hash_id: str
    # レスポンスサイズ削減のため、通常はベクトル(content_vector)を返さない設計にする

    model_config = ConfigDict(from_attributes=True)

# ----------------------------------------------------------------
# 4. 検索結果表示用 (Search Result)
# ----------------------------------------------------------------
class SearchResult(BaseModel):
    doc_id: int
    score: float
    summary: str
    tags: Dict[str, Any]

# ----------------------------------------------------------------
# 5. カスタム生成用 (Custom Generation)
# ----------------------------------------------------------------
class PlanCustomGenerate(BaseModel):
    # 循環参照を避けるため、厳密なPatientExtractionSchemaではなくDictで受け取る
    patient_data: Dict[str, Any]
    prompt: str
    target_key: Optional[str] = None
    current_plan: Optional[Dict[str, Any]] = None

class BatchGenerateItem(BaseModel):
    target_key: str
    prompt: str

class PlanBatchGenerate(BaseModel):
    patient_data: Dict[str, Any]
    items: List[BatchGenerateItem]
    current_plan: Optional[Dict[str, Any]] = None