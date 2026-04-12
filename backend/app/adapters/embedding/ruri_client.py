import logging
from sentence_transformers import SentenceTransformer
from typing import List
from app.adapters.embedding.base import BaseEmbeddingClient

logger = logging.getLogger(__name__)

class RuriEmbeddingClient(BaseEmbeddingClient):
    def __init__(self, model_name: str = "cl-nagoya/ruri-v3-310m"):
        logger.info(f"Initializing RuriEmbeddingClient with model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        try:
            vector = self.model.encode(text, normalize_embeddings=True).tolist()
            return vector
        except Exception as e:
            logger.error(f"Error during Ruri vector generation: {e}")
            raise