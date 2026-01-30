from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db
from app.schemas.schemas import PlanCreate, PlanRead, PlanUpdate
from app.infrastructure.repositories.plan_repository import PlanRepository

router = APIRouter()

@router.post("/", response_model=PlanRead, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_in: PlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    計画書を新規作成します。
    """
    print(f"[API] POST /plans/ Request received. Patient: {plan_in.hash_id}")
    
    repo = PlanRepository(db)
    
    try:
        # DBに保存
        new_plan = await repo.create(plan_in)
        return new_plan
    except Exception as e:
        # 外部キー制約違反（存在しない患者IDを指定した場合など）
        print(f"[API] Error creating plan: {e}")
        raise HTTPException(
            status_code=400, 
            detail="Could not create plan. Please check if the patient exists."
        )

@router.get("/patient/{hash_id}", response_model=List[PlanRead])
async def read_plans_by_patient(
    hash_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    特定の患者の計画書一覧を取得します（新しい順）。
    """
    print(f"[API] GET /plans/patient/{hash_id} Request received.")
    
    repo = PlanRepository(db)
    plans = await repo.get_by_patient(hash_id)
    
    return plans

@router.get("/{plan_id}", response_model=PlanRead)
async def read_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ID指定で計画書1件を取得します。
    """
    print(f"[API] GET /plans/{plan_id} Request received.")
    
    repo = PlanRepository(db)
    plan = await repo.get_by_id(plan_id)
    
    if not plan:
        print(f"[API] Plan {plan_id} not found.")
        raise HTTPException(status_code=404, detail="Plan not found")
        
    return plan

@router.put("/{plan_id}", response_model=PlanRead)
async def update_plan(
    plan_id: int,
    plan_in: PlanUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    計画書の内容（JSONデータ）を更新します。
    """
    print(f"[API] PUT /plans/{plan_id} Request received.")
    
    repo = PlanRepository(db)
    updated_plan = await repo.update(plan_id, plan_in)
    
    if not updated_plan:
        print(f"[API] Plan {plan_id} not found for update.")
        raise HTTPException(status_code=404, detail="Plan not found")
        
    return updated_plan