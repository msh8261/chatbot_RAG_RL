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

from backend.database.milvus_client import MilvusClient
from backend.models.embeddings import EmbeddingModel
from backend.utils.logger import logger


def retrieve_knowledge(
    query: str, milvus_client: MilvusClient, embedding_model: EmbeddingModel
):
    """
    Retrieve relevant knowledge from Milvus based on query embeddings.
    """
    # Generate embedding for query
    query_embedding = embedding_model.get_embedding(query)

    # Perform vector search in Milvus
    search_results = milvus_client.search(query_embedding)

    # Extract relevant knowledge
    knowledge = [result["text"] for result in search_results]

    return knowledge
