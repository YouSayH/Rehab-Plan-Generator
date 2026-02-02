import json
import logging
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.llm.factory import get_llm_client
from app.core.constants import PATIENT_FIELD_LABELS
from app.infrastructure.repositories.plan_repository import PlanRepository
from app.schemas.extraction_schemas import PatientExtractionSchema
from app.schemas.legacy_schemas import GENERATION_GROUPS
from app.schemas.schemas import PlanCreate
from app.usecases.utils.context_builder import prepare_patient_facts
# プロンプト構築ロジックをインポート（utils/prompts.py が存在することを前提）
from app.usecases.utils.prompts import build_group_prompt

logger = logging.getLogger(__name__)

class PlanGenerationUseCase:
    """
    LLMを使用してリハビリテーション総合実施計画書（様式23）のドラフトを生成するユースケース。
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.plan_repo = PlanRepository(db)
        self.llm_client = get_llm_client()

    async def execute(
        self, 
        hash_id: str, 
        patient_data: PatientExtractionSchema, 
        therapist_notes: str = ""
    ) -> Dict[str, Any]:
        """
        計画書生成のメインフローを実行します。

        Args:
            hash_id (str): 対象患者のハッシュID
            patient_data (PatientExtractionSchema): フロントエンドから送信された抽出済み患者データ
            therapist_notes (str): 療法士による特記事項・申し送り

        Returns:
            Dict[str, Any]: 生成・保存された計画書データ（PlanDataStoreのインスタンス辞書表現など）
        """
        logger.info(f"Starting plan generation for patient: {hash_id}")

        # 1. データの正規化 (Pydantic -> Flat Dict)
        # ネストされた構造を、context_builderが処理しやすいフラットな形式に変換
        flat_data = patient_data.export_to_mapping_format()

        # 2. 事実情報の構築 (Context Builder)
        # LLMへの入力用に、コード値や数値を自然言語に近い形に整形
        facts = prepare_patient_facts(flat_data, therapist_notes)
        facts_str = json.dumps(facts, ensure_ascii=False, indent=2)
        
        # デバッグ用: 生成の根拠となる事実情報をログ出力
        logger.debug(f"Patient Facts prepared: {len(facts_str)} chars")

        # 生成結果を蓄積する辞書
        generated_plan: Dict[str, Any] = {}

        # 3. 段階的生成 (Generation Loop)
        # 情報を一度に生成すると整合性が取れないため、依存関係順にグループごとに生成する
        # (例: 現状評価 -> 目標 -> 具体的アプローチ)
        for group_schema in GENERATION_GROUPS:
            schema_name = group_schema.__name__
            logger.info(f"Generating group: {schema_name}")

            try:
                # プロンプト作成
                # これまでの生成結果(generated_plan)を渡すことで、文脈を踏まえた一貫性のある生成が可能
                prompt = build_group_prompt(
                    group_schema=group_schema,
                    patient_facts_str=facts_str,
                    generated_plan_so_far=generated_plan
                )
                logger.info(f"\n{'='*20} PROMPT FOR {schema_name} {'='*20}\n{prompt}\n{'='*60}")

                # LLM実行 (Structured Output)
                # 指定したPydanticスキーマに準拠したJSONが返される
                response_dict = await self.llm_client.generate_json(prompt, group_schema)
                
                # 結果を統合
                generated_plan.update(response_dict)

            except Exception as e:
                logger.error(f"Error generating {schema_name}: {e}", exc_info=True)
                # 一部の生成に失敗しても、そこまでの結果で保存するか、エラーとして中断するか。
                # ここでは安全のため中断し、上位にエラーを通知する方針とする。
                raise RuntimeError(f"Failed to generate plan part '{schema_name}': {e}") from e

        # 4. DBへの保存
        # 生成プロセスが完了した後、DBに保存する
        # ※ PlanRepository.create 内で commit されるため、ここでは明示的なトランザクションブロックは不要
        try:
            plan_in = PlanCreate(
                hash_id=hash_id,
                raw_data=generated_plan
            )
            created_plan = await self.plan_repo.create(plan_in)
                
            logger.info(f"Plan generation completed and saved. Plan ID: {created_plan.plan_id}")
            return created_plan

        except Exception as e:
            logger.error(f"Database save failed: {e}", exc_info=True)
            raise RuntimeError("Failed to save generated plan to database.") from e

        except Exception as e:
            logger.error(f"Database transaction failed: {e}", exc_info=True)
            raise RuntimeError("Failed to save generated plan to database.") from e