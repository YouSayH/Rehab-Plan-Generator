from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models import PlanDataStore
from app.schemas.schemas import PlanCreate, PlanUpdate

class PlanRepository:
    """
    計画書データ (PlanDataStore) へのアクセスを担当するクラス
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, plan: PlanCreate) -> PlanDataStore:
        """
        計画書を新規作成します。
        """
        print(f"[PlanRepository] Creating plan for patient: {plan.hash_id}")
        
        db_plan = PlanDataStore(
            hash_id=plan.hash_id,
            doc_date=plan.doc_date,
            format_version=plan.format_version,
            raw_data=plan.raw_data  # JSONデータはそのまま辞書として渡せます
        )
        
        self.db.add(db_plan)
        await self.db.commit()
        await self.db.refresh(db_plan)
        
        print(f"[PlanRepository] Plan created successfully. ID: {db_plan.plan_id}")
        return db_plan

    async def get_by_patient(self, hash_id: str) -> List[PlanDataStore]:
        """
        特定の患者の計画書一覧を取得します（日付の新しい順）。
        """
        print(f"[PlanRepository] Fetching plans for patient: {hash_id}")
        
        query = (
            select(PlanDataStore)
            .where(PlanDataStore.hash_id == hash_id)
            .order_by(PlanDataStore.doc_date.desc(), PlanDataStore.plan_id.desc())
        )
        result = await self.db.execute(query)
        plans = result.scalars().all()
        
        return plans

    async def get_by_id(self, plan_id: int) -> Optional[PlanDataStore]:
        """
        ID指定で計画書を取得します。
        """
        print(f"[PlanRepository] Fetching plan by ID: {plan_id}")
        
        query = select(PlanDataStore).where(PlanDataStore.plan_id == plan_id)
        result = await self.db.execute(query)
        plan = result.scalars().first()
        
        return plan

    async def update(self, plan_id: int, plan_in: PlanUpdate) -> Optional[PlanDataStore]:
        """
        計画書の内容（JSONデータ）を更新します。
        """
        print(f"[PlanRepository] Updating plan ID: {plan_id}")
        
        # まず存在確認
        db_plan = await self.get_by_id(plan_id)
        if not db_plan:
            print(f"[PlanRepository] Plan ID {plan_id} not found.")
            return None

        # raw_data を上書き更新
        # ※ SQLAlchemyのモデル属性への代入で更新検知されます
        db_plan.raw_data = plan_in.raw_data
        
        # update_timeなどはDB側(onupdate)で自動更新されるか、必要ならここでセット
        # db_plan.updated_at = datetime.now() 

        await self.db.commit()
        await self.db.refresh(db_plan)
        
        print(f"[PlanRepository] Plan ID {plan_id} updated successfully.")
        return db_plan