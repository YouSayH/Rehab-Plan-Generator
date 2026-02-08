from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.api.dependencies import get_db
from app.infrastructure.db.models import PlanTemplate
from app.schemas.schemas import TemplateCreate, TemplateRead

router = APIRouter()

@router.post("/", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_in: TemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    現在のシート状態をテンプレートとして登録します。
    """
    new_template = PlanTemplate(
        name=template_in.name,
        description=template_in.description,
        data=template_in.data
    )
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    return new_template

@router.get("/", response_model=List[TemplateRead])
async def list_templates(
    db: AsyncSession = Depends(get_db)
):
    """
    登録済みテンプレートの一覧を取得します。
    """
    # data(中身)は重いので一覧では除外しても良いが、今回は簡易的に全取得
    stmt = select(PlanTemplate).order_by(PlanTemplate.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{template_id}", response_model=TemplateRead)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    テンプレートの詳細（データ本体含む）を取得します。
    """
    template = await db.get(PlanTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    テンプレートを削除します。
    """
    template = await db.get(PlanTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await db.delete(template)
    await db.commit()
    return