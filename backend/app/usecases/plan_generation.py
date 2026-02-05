import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import create_model, Field

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

        # =========================================================================
        # [Privacy Protection] PII Scrubbing
        # システム側に個人情報を残さないため、処理開始直後に氏名をハッシュIDに置換し、
        # メモリ上の実名情報を破棄する。
        # これにより、以降の export_to_mapping_format や LLMプロンプトには実名が含まれなくなる。
        # =========================================================================
        if patient_data.basic:
            # 実名をログに出力しないよう注意しながら、ハッシュIDで上書き
            patient_data.basic.name = hash_id
        
        # 1. データの正規化 (Pydantic -> Flat Dict)
        # ネストされた構造を、context_builderが処理しやすいフラットな形式に変換
        # ※ここで変換されるデータも、上記で置換したハッシュIDとなる
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

    async def execute_custom(
        self,
        patient_data: Dict[str, Any],
        prompt: str,
        current_plan: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        カスタムプロンプトによる部分生成を実行します。
        
        Args:
            patient_data (Dict): 患者データ（辞書形式）
            prompt (str): ユーザー定義のプロンプト
            current_plan (Optional[Dict]): 既に生成済みの計画書データ（文脈用）

        Returns:
            str: 生成されたテキスト
        """
        # 簡易的に事実情報を構築（Validationなしでdictをそのまま使用する簡易版）
        # 注意: export_to_mapping_formatを通していないため、patient_dataの構造に依存します。
        # 本格運用時はPatientExtractionSchemaでバリデーションしてから変換推奨。
        
        facts_str = json.dumps(patient_data, ensure_ascii=False, indent=2)
        
        # 既存計画のコンテキスト化
        plan_context_str = ""
        if current_plan:
            plan_str = json.dumps(current_plan, ensure_ascii=False, indent=2)
            plan_context_str = f"\n【既存の計画書データ (参考)】\nすでに決定している以下の計画内容と整合性が取れるように生成してください。\n{plan_str}\n"

        full_prompt = f"""
あなたはリハビリテーション計画書の作成支援AIです。
以下の患者データを参照し、ユーザーの指示に従って計画書の一部を作成してください。

【患者データ】
{facts_str}
{plan_context_str}
【指示】
{prompt}

出力は指示された内容のみをテキストで返してください。余計な挨拶は不要です。
"""
        logger.info(f"Executing Custom Generation Prompt: {prompt[:50]}...")
        
        # テキスト生成としてLLMを呼び出し
        response_text = await self.llm_client.generate_text(full_prompt)
        
        return response_text

    async def execute_batch(
        self,
        patient_data: Dict[str, Any],
        items: List[Any],
        current_plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        指定された複数の項目(キーとプロンプト)に基づいて一括生成を行う。
        """
        # 1. 事実情報の構築 (簡易版)
        facts_str = json.dumps(patient_data, ensure_ascii=False, indent=2)

        # 2. 動的なPydanticモデルの生成
        # itemsの内容に基づいて、{ "risk_txt": (str, Field(...)), "goal_txt": ... } という定義を作る
        field_definitions = {
            item.target_key: (str, Field(description=item.prompt))
            for item in items
        }
        # モデル名は動的に生成
        DynamicBatchSchema = create_model('DynamicBatchSchema', **field_definitions)

        # 3. プロンプト作成
        # 既存計画のコンテキスト化
        plan_context_str = ""
        if current_plan:
            plan_str = json.dumps(current_plan, ensure_ascii=False, indent=2)
            plan_context_str = f"\n【既存の計画書データ (参考)】\nすでに決定している以下の計画内容と整合性が取れるように生成してください。\n{plan_str}\n"

        prompt = f"""
あなたはリハビリテーション計画書の作成支援AIです。
以下の患者データを参照し、指定された項目の内容を生成してください。

【患者データ】
{facts_str}
{plan_context_str}
【指示】
各項目について、それぞれのdescription（指示）に従って適切な内容を生成してください。
JSON形式で出力してください。
"""
        logger.info(f"Executing Batch Generation for keys: {[i.target_key for i in items]}")

        # 4. LLM実行 (Structured Output)
        try:
            response_dict = await self.llm_client.generate_json(prompt, DynamicBatchSchema)
            return response_dict
        except Exception as e:
            logger.error(f"Batch generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Batch generation failed: {e}") from e