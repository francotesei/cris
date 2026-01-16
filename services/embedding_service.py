"""Text Embedding Service.

Provides text vectorization using sentence-transformers.
"""

from typing import List, Union

import numpy as np
from sentence_transformers import SentenceTransformer

from config.settings import get_settings
from utils.logger import get_logger


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = None) -> None:
        """Initialize the embedding model."""
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self.logger = get_logger("service.embedding")
        
        self.logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.logger.info("Embedding model loaded successfully")

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single string.
        
        Args:
            text: The text to embed.
            
        Returns:
            List of floats representing the vector.
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of strings.
        
        Args:
            texts: List of strings.
            
        Returns:
            List of vectors.
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def cosine_similarity(self, vec1: Union[List[float], np.ndarray], vec2: Union[List[float], np.ndarray]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        return float(dot_product / (norm_v1 * norm_v2))
