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

from backend.utils.logger import logger
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType


class MilvusClient:
    def __init__(self, host: str, port: str, collection_name: str):
        """Initialize Milvus client and collection."""
        try:
            # Connect to Milvus
            connections.connect(alias="default", host=host, port=port)
            self.collection_name = collection_name
            self.collection = Collection(collection_name)
        except Exception as e:
            logger.error(f"Error initializing MilvusClient: {e}")

    def search(self, query_embedding, top_k=5):
        """Search the collection for similar embeddings."""
        try:
            search_params = {
                "metric_type": "L2",  # Change to "IP" if using cosine similarity
                "params": {"nprobe": 10},
            }

            results = self.collection.search(
                data=[query_embedding],  # Query vector
                anns_field="embedding",  # The field where embeddings are stored
                param=search_params,
                limit=top_k,
                output_fields=["text"],  # Return associated text data
            )
            return results
        except Exception as e:
            logger.error(f"Error searching MilvusClient: {e}")
            return []
