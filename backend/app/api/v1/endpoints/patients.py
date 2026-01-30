from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db
from app.schemas.schemas import PatientCreate, PatientRead
from app.infrastructure.repositories.patient_repository import PatientRepository

# Routerの定義
router = APIRouter()

@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    患者を新規登録します。
    """
    print(f"[API] POST /patients/ Request received. ID: {patient_in.hash_id}")
    
    repo = PatientRepository(db)
    
    # 重複チェック（簡易的）: 既に存在するか確認
    existing_patient = await repo.get(patient_in.hash_id)
    if existing_patient:
        print(f"[API] Error: Patient {patient_in.hash_id} already exists.")
        raise HTTPException(
            status_code=400,
            detail="Patient with this hash_id already exists."
        )

    # 作成実行
    new_patient = await repo.create(patient_in)
    return new_patient


@router.get("/", response_model=List[PatientRead])
async def read_patients(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    患者一覧を取得します。
    """
    print(f"[API] GET /patients/ Request received. skip={skip}, limit={limit}")
    
    repo = PatientRepository(db)
    patients = await repo.get_all(skip=skip, limit=limit)
    
    return patients


@router.get("/{hash_id}", response_model=PatientRead)
async def read_patient(
    hash_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    特定の患者情報を取得します。
    """
    print(f"[API] GET /patients/{hash_id} Request received.")
    
    repo = PatientRepository(db)
    patient = await repo.get(hash_id)
    
    if not patient:
        print(f"[API] Error: Patient {hash_id} not found.")
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )
        
    return patient