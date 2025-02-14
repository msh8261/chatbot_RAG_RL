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


import chromadb
from backend.utils.logger import logger


class ChromaDBClient:
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection_name = collection_name

            # Ensure we're working with a collection, not the client itself
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logger.info(f"ChromaDB collection '{collection_name}' initialized.")
        except Exception as e:
            logger.error(f"Error initializing ChromaDBClient: {e}")
            self.collection = None

    def add_document(self, doc_id: str, embedding: list[float], metadata: dict = None):
        """Add a document with an embedding to the collection."""
        if not self.collection:
            logger.error("ChromaDB collection is not initialized.")
            return

        try:
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[metadata] if metadata else [{}],
            )
            logger.info(f"Document {doc_id} added to ChromaDB.")
        except Exception as e:
            logger.error(f"Error adding document to ChromaDB: {e}")

    def search(self, query_embedding: list[float], top_k=5):
        """Search for similar embeddings in the collection."""
        if not self.collection:
            logger.error("ChromaDB collection is not initialized.")
            return []

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=top_k
            )
            return results
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []

    def retrieve_knowledge(self, query, embedding_model):
        """Retrieve relevant knowledge based on the query."""
        if not self.collection:
            logger.error("ChromaDB collection is not initialized.")
            return []

        logger.info(f"Retrieving knowledge for query: {query}")

        # Get the embedding for the query
        query_embedding = embedding_model.get_embedding(query)
        logger.debug(f"Query embedding: {query_embedding}")

        if not query_embedding:  # Ensure embedding is valid
            logger.error("Query embedding is empty. Skipping retrieval.")
            return []

        try:
            search_results = self.collection.query(
                query_embeddings=[query_embedding], n_results=5
            )
            logger.debug(f"Search results: {search_results}")

            knowledge = []
            if search_results and "documents" in search_results:
                for doc_list in search_results["documents"]:
                    if isinstance(doc_list, list):
                        knowledge.extend(
                            doc for doc in doc_list if isinstance(doc, str)
                        )

            if not knowledge:
                logger.warning("No relevant knowledge retrieved.")

            return knowledge

        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []
