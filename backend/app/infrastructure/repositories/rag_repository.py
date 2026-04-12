import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# pgvector の演算子を使用するために必要
from pgvector.sqlalchemy import Vector

from app.infrastructure.db.models import DocumentsView, PatientsView

logger = logging.getLogger(__name__)

class RAGRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_similar_documents(
        self, 
        query_vector: List[float], 
        filters: Optional[Dict[str, Any]] = None,
        exclude_hash_id: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        ハイブリッド検索 (メタデータフィルタ + ベクトル類似度) で類似ドキュメントを取得する。
        """
        logger.info(f"RAG Search initiated: limit={limit}, filters={filters}, exclude_hash_id={exclude_hash_id}")
        
        stmt = select(DocumentsView)
        
        # [Hard Filter] 自身（現在作成中の患者）の過去ドキュメントを除外（他者の事例を検索する場合）
        if exclude_hash_id:
            stmt = stmt.where(DocumentsView.hash_id != exclude_hash_id)

        # [Hard Filter] メタデータ(entities)による絞り込み
        # 例: 同じ疾患名の事例のみに絞る
        if filters and "diagnosis" in filters:
            # SQLAlchemyのJSONBオペレーターを利用して照合
            stmt = stmt.where(DocumentsView.entities['diagnosis'].astext == filters['diagnosis'])
                
        # [Soft Rerank] ベクトル距離順に並び替え (L2距離を使用)
        # PostgreSQLの演算子 `<->` に相当
        stmt = stmt.order_by(DocumentsView.content_vector.l2_distance(query_vector))
        stmt = stmt.limit(limit)

        try:
            result = await self.db.execute(stmt)
            documents = result.scalars().all()
            
            # LLMのコンテキストとして扱いやすいように辞書化して返す
            similar_docs = []
            for doc in documents:
                similar_docs.append({
                    "doc_id": doc.doc_id,
                    "doc_type": doc.doc_type,
                    "summary": doc.summary_text,
                    "entities": doc.entities
                })
                logger.debug(f"Found similar document: doc_id={doc.doc_id}, type={doc.doc_type}")
                
            return similar_docs
            
        except Exception as e:
            logger.error(f"Failed to execute vector search query: {e}", exc_info=True)
            return []