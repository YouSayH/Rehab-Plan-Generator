from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.infrastructure.db.models import PatientsView, DocumentsView
from app.schemas.schemas import PatientCreate

class PatientRepository:
    """
    患者データ (PatientsView) へのアクセスおよび検索を担当するクラス
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, patient: PatientCreate) -> PatientsView:
        """
        患者を新規登録します。
        """
        print(f"[PatientRepository] Creating patient with hash_id: {patient.hash_id}")
        
        # モデルインスタンスの作成
        db_patient = PatientsView(
            hash_id=patient.hash_id,
            age=patient.age,
            gender=patient.gender,
            diagnosis_code=patient.diagnosis_code,
            admission_date=patient.admission_date,
            # 追加カラム
            onset_date=patient.onset_date,
            outcome=patient.outcome,
            total_fim_admission=patient.total_fim_admission,
            mental_min=patient.mental_min,
            social_vector=patient.social_vector
        )
        
        # DBに追加してコミット
        self.db.add(db_patient)
        await self.db.commit()
        
        # 最新の状態（生成されたタイムスタンプなど）を再取得
        await self.db.refresh(db_patient)
        print(f"[PatientRepository] Patient created successfully: {db_patient.hash_id}")
        
        return db_patient

    async def get(self, hash_id: str) -> PatientsView | None:
        """
        ハッシュIDを指定して患者を取得します。存在しない場合は None を返します。
        """
        print(f"[PatientRepository] Fetching patient by hash_id: {hash_id}")
        
        # select文の構築と実行
        query = select(PatientsView).where(PatientsView.hash_id == hash_id)
        result = await self.db.execute(query)
        
        # 最初の1件を取得（なければNone）
        patient = result.scalars().first()
        
        if patient:
            print(f"[PatientRepository] Found patient: {patient.hash_id}")
        else:
            print(f"[PatientRepository] Patient not found: {hash_id}")
            
        return patient

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[PatientsView]:
        """
        患者一覧を取得します（ページネーション対応）。
        """
        print(f"[PatientRepository] Fetching all patients (skip={skip}, limit={limit})")
        
        query = select(PatientsView).offset(skip).limit(limit)
        result = await self.db.execute(query)
        patients = result.scalars().all()
        
        print(f"[PatientRepository] Retrieved {len(patients)} patients.")
        return patients
    

    async def get_latest_state(self, hash_id: str) -> dict | None:
        """
        指定された患者の最新の状態（entities）を取得する。
        """
        print(f"[PatientRepository] Fetching latest state for: {hash_id}")
        
        query = select(DocumentsView).where(
            (DocumentsView.hash_id == hash_id) & 
            (DocumentsView.doc_type == "latest_state")
        )
        result = await self.db.execute(query)
        doc = result.scalars().first()
        
        if doc and doc.entities:
            print(f"[PatientRepository] Latest state found for {hash_id}")
            return doc.entities
        
        print(f"[PatientRepository] No latest state found for {hash_id}")
        return None

    # -------------------------------------------------------
    # Hybrid Search Implementation (SQL + Vector)
    # -------------------------------------------------------
    async def search_similar_patients(
        self, 
        target_vector: List[float], 
        filters: dict, 
        limit: int = 3
    ) -> List[PatientsView]:
        """
        Hybrid Searchを実行し、類似患者を返却します。
        
        Args:
            target_vector: 検索対象(ターゲット患者)の社会背景ベクトル
            filters: SQLで絞り込むための条件 (diagnosis_code, age_range, fim_range等)
            limit: 取得件数
        
        Returns:
            類似度の高い順にソートされたPatientsViewのリスト
        """
        print(f"[PatientRepository] executing Hybrid Search with filters: {filters}")

        # 1. Base Query
        stmt = select(PatientsView)
        
        conditions = []
        
        # 2. Hard Filters (SQL)
        # 疾患コードの一致（前方一致など、要件に合わせて調整）
        if "diagnosis_code" in filters and filters["diagnosis_code"]:
            # 例: I63.9 -> I63 (カテゴリ一致)
            code_prefix = filters["diagnosis_code"][:3] 
            conditions.append(PatientsView.diagnosis_code.startswith(code_prefix))
        
        # 年齢フィルタ (±10歳)
        if "age" in filters and filters["age"]:
            target_age = filters["age"]
            conditions.append(PatientsView.age.between(target_age - 10, target_age + 10))

        # FIMフィルタ (±15点)
        if "total_fim_admission" in filters and filters["total_fim_admission"]:
            target_fim = filters["total_fim_admission"]
            conditions.append(PatientsView.total_fim_admission.between(target_fim - 15, target_fim + 15))

        # フィルタ適用
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # 3. Soft Rerank (Vector Similarity)
        # pgvectorの L2 distance ( <-> 演算子 ) または cosine distance ( <=> ) を使用
        # 近い順（距離が小さい順）にソート
        if target_vector:
            stmt = stmt.order_by(PatientsView.social_vector.l2_distance(target_vector))
        
        stmt = stmt.limit(limit)

        # 実行
        result = await self.db.execute(stmt)
        similar_patients = result.scalars().all()
        
        print(f"[PatientRepository] Found {len(similar_patients)} similar patients.")
        return similar_patients