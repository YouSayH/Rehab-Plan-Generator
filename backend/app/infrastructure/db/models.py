import datetime
from typing import Optional, List, Any

from sqlalchemy import String, Integer, Date, Text, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

# 共通のBaseクラス定義 (通常は別ファイル base.py に定義しますが、今回はここに含めます)
class Base(DeclarativeBase):
    pass

# ----------------------------------------------------------------
# 1. 患者属性管理 (Intermediate DB / Read-Only)
# ----------------------------------------------------------------
class PatientsView(Base):
    """
    電子カルテから連携される患者属性情報。
    個人特定情報(PHI)は持たず、ハッシュIDで管理する。
    """
    __tablename__ = "patients_view"

    # プライバシー保護のため実IDではなくハッシュIDをPKとする
    hash_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    diagnosis_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="ICD-10等の疾患コード")
    admission_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    
    # 監査用タイムスタンプ
    synced_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), comment="中間DBへの同期日時"
    )

    # Relationships
    plans: Mapped[List["PlanDataStore"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    documents: Mapped[List["DocumentsView"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


# ----------------------------------------------------------------
# 2. 計画書データストア (Schema-less Architecture)
# ----------------------------------------------------------------
class PlanDataStore(Base):
    """
    生成または編集された計画書のデータを保存する。
    300項目以上の詳細データは 'raw_data' (JSONB) に集約し、スキーマ変更に強くする。
    """
    __tablename__ = "plan_data_store"

    plan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hash_id: Mapped[str] = mapped_column(ForeignKey("patients_view.hash_id"), nullable=False, index=True)
    
    doc_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, default=func.current_date())
    format_version: Mapped[str] = mapped_column(String(20), default="v1.0", comment="様式のバージョン管理")
    
    # 【重要】様式23の全項目（テキスト、数値、チェックボックス）をJSONとして格納
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationship
    patient: Mapped["PatientsView"] = relationship(back_populates="plans")


# ----------------------------------------------------------------
# 3. RAG / Hybrid CLEAR 検索用ドキュメント
# ----------------------------------------------------------------
class DocumentsView(Base):
    """
    RAG検索対象となる過去のカルテ記事やサマリ。
    Hybrid Search (Keyword + Vector) のために最適化されたテーブル。
    """
    __tablename__ = "documents_view"

    doc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hash_id: Mapped[str] = mapped_column(ForeignKey("patients_view.hash_id"), nullable=False, index=True)
    
    doc_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="リハビリ実施録, 退院サマリ, etc.")
    source_type: Mapped[str] = mapped_column(String(20), default="EHR", comment="EHR, UPLOAD(外部資料)")
    
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="LLMコンテキスト用の要約")
    original_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="参照用の原文（匿名化済み）")

    # --- Hybrid CLEAR Search Core Columns ---
    
    # 1. 構造化タグ (Hard Filter用)
    # 例: {"diagnosis": ["脳梗塞"], "symptoms": ["右片麻痺", "失語症"], "fim_motor": 35}
    entities: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)

    # 2. ベクトル埋め込み (Semantic Search用)
    # 次元数は利用するEmbeddingモデルに合わせる (OpenAI=1536, Local/HuggingFace=768 が一般的)
    # ここでは一般的な 768 を設定
    content_vector: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)

    # Relationship
    patient: Mapped["PatientsView"] = relationship(back_populates="documents")

    # Indexes
    __table_args__ = (
        # JSONB内のタグ検索を高速化するためのGINインデックス
        Index("ix_documents_entities", "entities", postgresql_using="gin"),
        
        # ベクトル検索を高速化するためのHNSWインデックス (必要に応じてIVFFlatに変更可)
        # ※ pgvectorのインデックス作成はデータ量が増えてから有効化するのが一般的ですが、定義として記載します
        Index(
            "ix_documents_vector",
            "content_vector",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"content_vector": "vector_l2_ops"}
        ),
    )

"""
副作用・デメリット (Trade-offs)
    この設計はメリットが大きい反面、以下の副作用（注意点）があります。

1.データの整合性担保がアプリケーション任せになる
    詳細: 以前の plan.py では Column(Integer) のようにDBレベルで型が決まっていましたが、JSONB (raw_data) になると、DB側では数値か文字列かのチェックが行われません。
    対策: Frontend/Backendのアプリケーションコード（Pydanticスキーマ）で厳密なバリデーションを行う必要があります。

2.SQLクエリの複雑化
    詳細: 「FIM運動項目が30点以上の人」を探す場合、WHERE raw_data->>'fim_motor_score' >= 30 のような特殊なJSON演算子を使う必要があり、通常のSQLより記述が難しくなります。

3.デバッグの難易度上昇
    詳細: DBの中身を見ても hash_id: "a1b2..." としか書かれていないため、開発中に「これが誰のデータか」を直感的に把握できません。
    対策: 開発環境（Dev）限定で、ハッシュIDと実名の対応表を持つ別の管理ツールやスクリプトを用意する必要があります。
"""
