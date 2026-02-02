from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models import PatientsView, DocumentsView
from app.schemas.schemas import PatientCreate

class PatientRepository:
    """
    患者データ (PatientsView) へのアクセスを担当するクラス
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
            admission_date=patient.admission_date
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
        指定された患者の最新の状態（doc_type='latest_state'）のentitiesデータを取得する。
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