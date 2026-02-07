import asyncio
import logging
import sys
import os
import random  # 【追加】ベクトル生成用
from datetime import date
import json

# パス解決: backendディレクトリをPYTHONPATHに含める
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from app.infrastructure.db.database import AsyncSessionLocal
from app.infrastructure.db.models import PatientsView, DocumentsView
from app.schemas.extraction_schemas import PatientExtractionSchema

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# ダミーデータ生成ヘルパー
# ==========================================
def create_extraction_data(
    name="田中 太郎", age=82, gender="男", 
    diagnosis="脳梗塞 (右片麻痺)", 
    fim_motor=35, fim_cog=20
):
    """
    PatientExtractionSchema に準拠した辞書データを生成する
    """
    return {
        "basic": {
            "name": name,
            "age": age,
            "gender": gender,
            "disease_name": diagnosis,
            "onset_date": "2026-04-01",
            "evaluation_date": str(date.today()),
        },
        "medical": {
            "comorbidities": "高血圧症, 糖尿病",
            "risks": "転倒リスクあり, 嚥下障害あり",
            "hypertension": True,
            "diabetes": True
        },
        "function": {
            "paralysis": True,
            "jcs_gcs": "I-1",
            "rom_limitation": True,
            "rom_detail": "右肩関節屈曲 90°",
            "muscle_weakness": True,
            "muscle_detail": "右上下肢 MMT 2"
        },
        "basic_movement": {
            "rolling_level": "assistance",
            "getting_up_level": "assistance",
            "standing_up_level": "assistance",
            "sitting_balance_level": "partial_assistance",
            "standing_balance_level": "not_performed"
        },
        "adl": {
            # 簡易的に一部のみ数値を入れる
            "eating": {"fim_current": 5},
            "transfer_bed": {"fim_current": 3},
            "toileting": {"fim_current": 4},
            "locomotion_walk": {"fim_current": 1},
            "comprehension": {"fim_current": fim_cog // 5}, # 適当な配分
            "expression": {"fim_current": fim_cog // 5},
            "social": {"fim_current": fim_cog // 5},
            "problem_solving": {"fim_current": fim_cog // 5},
            "memory": {"fim_current": fim_cog // 5},
        },
        "nutrition": {
            "bmi_check": True,
            "bmi": 22.5
        },
        "social": {
            "care_level": "care_2",
            "care_level_status": True
        },
        "goals": {
            "short_term_goal": "トイレ動作の見守りレベル, 端坐位保持30分",
            "long_term_goal": "自宅復帰, 屋内歩行自立"
        },
        "signature": {}
    }

# ダミーベクトル生成関数
def generate_dummy_vector(dim=768):
    return [random.random() for _ in range(dim)]

# ==========================================
# 投入データ定義
# ==========================================
DUMMY_PATIENTS = [
    {
        "hash_id": "patient_001",
        "age": 82,
        "gender": "男性",
        "diagnosis_code": "I63.9",
        "admission_date": date(2026, 4, 1),
        "desc": "脳梗塞・標準",
        
        # 新カラム用のデータ
        "onset_date": date(2026, 3, 25),
        "outcome": "自宅復帰",
        "total_fim_admission": 55,
        "total_fim_discharge": 85,
        "mental_min": -0.2, "mental_mean": 0.5, "mental_std": 0.1, "physical_mean": -0.8,
        "plan_text": "【長期目標】妻の介助のもと、自宅での生活が可能となる。\n【短期目標】杖歩行が見守りで可能となる。",

        "extraction_data": create_extraction_data(
            name="田中 太郎", age=82, gender="男", 
            diagnosis="脳梗塞 (右片麻痺)", fim_motor=35, fim_cog=25
        )
    },
    {
        "hash_id": "patient_002",
        "age": 75,
        "gender": "女性",
        "diagnosis_code": "S72.00",
        "admission_date": date(2026, 4, 10),
        "desc": "大腿骨骨折・認知症なし",
        
        "onset_date": date(2026, 4, 9),
        "outcome": "自宅復帰",
        "total_fim_admission": 95,
        "total_fim_discharge": 115,
        "mental_min": 0.1, "mental_mean": 0.9, "mental_std": 0.05, "physical_mean": -0.4,
        "plan_text": "【長期目標】受傷前と同じレベルで家事が可能となる。\n【短期目標】独歩で屋内移動が自立する。",

        "extraction_data": create_extraction_data(
            name="鈴木 花子", age=75, gender="女", 
            diagnosis="左大腿骨頸部骨折", fim_motor=60, fim_cog=35
        )
    },
    {
        "hash_id": "patient_003",
        "age": 68,
        "gender": "男性",
        "diagnosis_code": "I61.9",
        "admission_date": date(2026, 3, 20),
        "desc": "脳出血・失語症",

        "onset_date": date(2026, 3, 15),
        "outcome": "施設入所",
        "total_fim_admission": 35,
        "total_fim_discharge": 50,
        "mental_min": -0.9, "mental_mean": -0.3, "mental_std": 0.8, "physical_mean": -0.5,
        "plan_text": "【長期目標】施設にて車椅子での離床時間を確保できる。\n【短期目標】移乗動作が中等度介助レベルとなる。",

        "extraction_data": create_extraction_data(
            name="佐藤 次郎", age=68, gender="男", 
            diagnosis="左被殻出血 (右片麻痺・失語)", fim_motor=20, fim_cog=15
        )
    }
]

async def seed_patients():
    """
    ダミーの患者データと、その詳細情報(ExtractionData)をDBに投入する。
    """
    logger.info("Starting database seeding...")
    
    async with AsyncSessionLocal() as session:
        for p_data in DUMMY_PATIENTS:
            # 1. PatientsView (基本情報) のUpsert
            stmt = select(PatientsView).where(PatientsView.hash_id == p_data["hash_id"])
            result = await session.execute(stmt)
            patient = result.scalars().first()

            # ダミーベクトルの生成
            dummy_social_vector = generate_dummy_vector(768)

            if not patient:
                patient = PatientsView(
                    hash_id=p_data["hash_id"],
                    age=p_data["age"],
                    gender=p_data["gender"],
                    diagnosis_code=p_data["diagnosis_code"],
                    admission_date=p_data["admission_date"],
                    # 新カラムへの値セット
                    onset_date=p_data["onset_date"],
                    outcome=p_data["outcome"],
                    total_fim_admission=p_data["total_fim_admission"],
                    total_fim_discharge=p_data["total_fim_discharge"],
                    mental_min=p_data["mental_min"],
                    mental_mean=p_data["mental_mean"],
                    mental_std=p_data["mental_std"],
                    physical_mean=p_data["physical_mean"],
                    social_vector=dummy_social_vector,
                    plan_text=p_data["plan_text"]
                )
                session.add(patient)
                logger.info(f"[Patient] Created: {p_data['hash_id']} ({p_data['desc']})")
            else:
                # 更新時も新しい値を入れる（必要なら）
                patient.social_vector = dummy_social_vector
                patient.plan_text = p_data["plan_text"]
                logger.info(f"[Patient] Exists (Updated vector/text): {p_data['hash_id']}")
            
            # 2. DocumentsView (詳細データ) のUpsert
            stmt_doc = delete(DocumentsView).where(
                (DocumentsView.hash_id == p_data["hash_id"]) & 
                (DocumentsView.doc_type == "latest_state")
            )
            await session.execute(stmt_doc)
            
            # 本文用ダミーベクトル
            dummy_content_vector = generate_dummy_vector(768)

            # バリデーションチェック (Pydantic)
            try:
                # 辞書データをPydanticモデルに通して整合性チェック
                schema_obj = PatientExtractionSchema(**p_data["extraction_data"])
                # DB保存用にdictに戻す (jsonable_encoder等が無いのでmodel_dumpを使用)
                valid_json_data = schema_obj.model_dump(mode='json')
                
                new_doc = DocumentsView(
                    hash_id=p_data["hash_id"],
                    doc_date=date.today(),
                    doc_type="latest_state",
                    source_type="SEED",
                    summary_text="初期シードデータによる現在の患者状態",
                    entities=valid_json_data,
                    # ベクトルをセット
                    content_vector=dummy_content_vector
                )
                session.add(new_doc)
                logger.info(f"[Document] Inserted latest_state for {p_data['hash_id']}")
                
            except Exception as e:
                logger.error(f"Validation failed for {p_data['hash_id']}: {e}")

        await session.commit()
        logger.info("Seeding completed successfully.")

if __name__ == "__main__":
    try:
        asyncio.run(seed_patients())
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)