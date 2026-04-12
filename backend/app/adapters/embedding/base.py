"""
File: backend/app/adapters/embedding/base.py
"""
from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingClient(ABC):
    """エンベディングクライアントの抽象ベースクラス"""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        テキストを受け取り、ベクトル（List[float]）を返す
        """
        pass