import os
import sys

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# Get the directory path of the current file
current_dir_path = os.path.dirname(current_file_path)
# Get the parent directory path
parent_dir_path = os.path.dirname(current_dir_path)
# Add the parent directory path to the sys.path
sys.path.insert(0, parent_dir_path)
from backend.models.transformers import TransformerModel
from backend.utils.logger import logger


class EmbeddingModel:
    def __init__(self, transformer_model: TransformerModel):
        """Initialize the embedding model using a TransformerModel instance."""
        try:
            if not isinstance(transformer_model, TransformerModel):
                raise TypeError("Expected a TransformerModel instance.")
            self.model = transformer_model
            logger.info("EmbeddingModel initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing EmbeddingModel: {e}")
            self.model = None

    def get_embedding(self, text: str):
        """Get the embedding for a given text."""
        if not self.model:
            logger.error("EmbeddingModel is not initialized correctly.")
            return []

        try:
            embedding = self.model.get_embedding(text)
            if (
                embedding is None
                or not isinstance(embedding, list)
                or len(embedding) == 0
            ):
                logger.error(
                    f"Embedding model returned invalid embedding for text: {text}"
                )
                return []  # Consider returning None or specific error code if you want to distinguish this case
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding for text '{text}': {e}")
            return []
