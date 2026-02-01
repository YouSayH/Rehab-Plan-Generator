import asyncio
import logging
import sys
import os
from datetime import date

# パス解決: backendディレクトリをPYTHONPATHに含める
# これにより 'app' モジュールのインポートが可能になります
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.infrastructure.db.database import AsyncSessionLocal
from app.infrastructure.db.models import PatientsView

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 投入するダミーデータ定義
DUMMY_PATIENTS = [
    {
        "hash_id": "patient_001",
        "age": 82,
        "gender": "男性",
        "diagnosis_code": "I63.9",  # 脳梗塞
        "admission_date": date(2026, 4, 1),
        "desc": "脳梗塞・右片麻痺の標準的なケース"
    },
    {
        "hash_id": "patient_002",
        "age": 75,
        "gender": "女性",
        "diagnosis_code": "S72.00", # 大腿骨頚部骨折
        "admission_date": date(2026, 4, 10),
        "desc": "整形疾患・認知症なしのケース"
    },
    {
        "hash_id": "patient_003",
        "age": 68,
        "gender": "男性",
        "diagnosis_code": "I61.9",  # 脳出血
        "admission_date": date(2026, 3, 20),
        "desc": "脳出血・若年・高次脳機能障害のケース"
    }
]

async def seed_patients():
    """
    ダミーの患者データをDBに投入する。
    既に同じhash_idが存在する場合はスキップする。
    """
    logger.info("Starting database seeding...")
    
    async with AsyncSessionLocal() as session:
        for p_data in DUMMY_PATIENTS:
            # 存在確認
            stmt = select(PatientsView).where(PatientsView.hash_id == p_data["hash_id"])
            result = await session.execute(stmt)
            existing = result.scalars().first()

            if existing:
                logger.info(f"Skip: Patient '{p_data['hash_id']}' already exists.")
                continue

            # 新規作成
            new_patient = PatientsView(
                hash_id=p_data["hash_id"],
                age=p_data["age"],
                gender=p_data["gender"],
                diagnosis_code=p_data["diagnosis_code"],
                admission_date=p_data["admission_date"]
            )
            session.add(new_patient)
            logger.info(f"Inserted: {p_data['hash_id']} ({p_data['desc']})")
        
        await session.commit()
        logger.info("Seeding completed successfully.")

if __name__ == "__main__":
    try:
        asyncio.run(seed_patients())
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)