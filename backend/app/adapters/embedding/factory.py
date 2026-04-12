"""
File: backend/app/adapters/embedding/factory.py
"""
import os
import logging
from app.adapters.embedding.base import BaseEmbeddingClient

logger = logging.getLogger(__name__)

def get_embedding_client() -> BaseEmbeddingClient:
    """
    環境変数 EMBEDDING_PROVIDER に基づいて、適切なエンベディングクライアントを返す。
    デフォルトは 'ruri'。
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "ruri").lower()
    
    if provider == "gemini":
        logger.info("Using Gemini Embedding Client")
        from app.adapters.embedding.gemini_embedding_client import GeminiEmbeddingClient
        return GeminiEmbeddingClient()
    else:
        logger.info("Using Local Ruri Embedding Client")
        from app.adapters.embedding.ruri_client import RuriEmbeddingClient
        return RuriEmbeddingClient()