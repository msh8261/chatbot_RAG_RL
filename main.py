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


import uvicorn
import threading
import uuid
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from backend.agents.query_preprocessing import preprocess_query
from backend.agents.retrieval import retrieve_knowledge
from backend.agents.generation import generate_response, generate_response_llm
from backend.agents.fact_checking import fact_check
from backend.agents.explainability import explain_response
from backend.database.milvus_client import MilvusClient
from backend.database.chromadb_client import ChromaDBClient
from backend.database.db import init_db
from backend.database.db_client import DatabaseClient
from backend.models.embeddings import EmbeddingModel
from backend.models.transformers import TransformerModel
from backend.services.search_api import GoogleSearchAPI, DuckDuckGoSearchAPI
from backend.utils.logger import logger
from backend.agents.feedback import store_feedback
from backend.agents.reinforcement_learning import ChatbotRLAgent
from backend.database.redis_client import RedisClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

milv_host = os.getenv("milv_host")
milv_port = os.getenv("milv_port")
milv_collection_name = os.getenv("milv_collection_name")

transformer_model_name = os.getenv("transformer_model_name")

search_api_key = os.getenv("search_api_key")
cx = os.getenv("cx")

app = FastAPI(title="Scalable Multi-Agent Chatbot")

# Initialize
init_db()
# milvus_client = MilvusClient(milv_host, milv_port, milv_collection_name)
chromadb_client = ChromaDBClient("my_knowledge_base")
database_client = DatabaseClient()
transformer_model = TransformerModel(transformer_model_name)
embedding_model = EmbeddingModel(transformer_model)
# search_api = GoogleSearchAPI(search_api_key, cx)
search_api = DuckDuckGoSearchAPI()
redis_client = RedisClient(REDIS_HOST, REDIS_PORT, 0)
rl_agent = ChatbotRLAgent(database_client)


class ChatRequest(BaseModel):
    user_id: str
    user_input: str


class FeedbackRequest(BaseModel):
    session_id: str
    user_feedback: str


chat_sessions = {}  # Tracks session IDs


@app.post("/chat/")
async def chat_endpoint(chat_request: ChatRequest):
    try:
        logger.info(f"Received input from user {chat_request.user_id}")

        # Step 1: Retrieve past chat history
        chat_history = redis_client.get_chat_history(chat_request.user_id)

        logger.debug(f"chat_history: {chat_history}")

        # Step 2: Preprocess the query
        processed_query = preprocess_query(chat_request.user_input)

        logger.debug(f"processed_query: {processed_query}")

        # Step 3: Retrieve relevant knowledge
        retrieved_knowledge = chromadb_client.retrieve_knowledge(
            processed_query, embedding_model
        )

        logger.debug(f"retrieved_knowledge: {retrieved_knowledge}")

        # # Step 4: Generate response (pass chat history for continuity)
        # raw_response = generate_response(processed_query, retrieved_knowledge, transformer_model)
        raw_response = generate_response_llm(processed_query, GROQ_MODEL, GROQ_API_KEY)

        logger.debug(f"raw_response: {raw_response}")

        # Step 5: Fact-check the response
        validated_response = fact_check(raw_response, search_api)

        logger.debug(f"validated_response: {validated_response}")

        # # Step 6: RL-based response strategy
        # action = rl_agent.get_best_action(processed_query)
        # if action == "negative":
        #     validated_response += " (Note: This response may need improvement.)"

        # Step 7: Explainability (SHAP Analysis)
        explanation = explain_response(
            processed_query, retrieved_knowledge, validated_response
        )
        logger.debug(f"explanation: {explanation}")

        # Step 8: Store conversation in Redis (chat memory)
        redis_client.store_chat_history(
            chat_request.user_id, chat_request.user_input, validated_response
        )

        # Step 9: Generate session ID for feedback tracking
        session_id = str(uuid.uuid4())
        chat_sessions[session_id] = {
            "user_id": chat_request.user_id,
            "user_input": chat_request.user_input,
            "response": validated_response,
        }

        return {
            "session_id": session_id,
            "response": validated_response,
            "explanation": explanation,
            "chat_history": chat_history,
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")


@app.post("/feedback/")
async def feedback_endpoint(feedback: FeedbackRequest):
    try:
        session_data = chat_sessions.get(feedback.session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        try:
            store_feedback(
                session_data["user_id"],
                session_data["user_input"],
                session_data["response"],
                feedback.user_feedback,
                database_client,
            )
            logger.info("Feedback collected successfully")
            return {"message": "Feedback received. Thank you!"}
        except Exception as e:
            logger.error(f"Error storing feedback: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to store feedback")
    except Exception as e:
        logger.error(f"Error in feedback endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")


@app.delete("/clear_chat/{user_id}")
async def clear_chat_memory(user_id: str):
    try:
        redis_client.clear_chat_history(user_id)
        return {"message": "Chat history cleared successfully."}
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")


@app.get("/")
def read_root():
    return {"message": "Backend server is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
