"""
File: backend/app/adapters/embedding/gemini_embedding_client.py
"""
import os
import math
import logging
from typing import List

from google import genai
from google.genai import types

from app.adapters.embedding.base import BaseEmbeddingClient

logger = logging.getLogger(__name__)

class GeminiEmbeddingClient(BaseEmbeddingClient):
    """
    Google Gemini (gemini-embedding-2-preview) を使用したベクトル生成クライアント。
    ruri-v3と互換性を持たせるため、出力次元数を768次元に設定します。
    """
    def __init__(self):
        logger.info("Initializing GeminiEmbeddingClient with gemini-embedding-2-preview")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("[GeminiEmbeddingClient] Warning: GEMINI_API_KEY is not set.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-embedding-2-preview"

    def embed_text(self, text: str) -> List[float]:
        try:
            # gemini-embedding-2-preview の推奨フォーマット
            # 患者同士の類似度検索（Symmetric format）に最適化するため、タスクプレフィックスを追加します。
            formatted_text = f"task: sentence similarity | query: {text}"

            # 次元数を768に切り詰めて生成
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=formatted_text,
                config=types.EmbedContentConfig(
                    output_dimensionality=768
                )
            )
            
            # APIから返却されたベクトルを取得
            values = result.embeddings[0].values

            # 【重要】768次元など小さい次元に切り詰めた場合、手動でのL2正規化(Normalization)が推奨されています
            # 外部ライブラリ(numpy)に依存しない標準のmathモジュールで計算します
            magnitude = math.sqrt(sum(v * v for v in values))
            
            if magnitude > 0:
                normed_embedding = [v / magnitude for v in values]
            else:
                normed_embedding = values
                
            return normed_embedding

        except Exception as e:
            logger.error(f"Error during Gemini vector generation: {e}", exc_info=True)
            raise