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

import redis
import json
import os


class RedisClient:
    def __init__(self, host="localhost", port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def store_chat_history(self, user_id, message, response):
        """Stores chat history for a user."""
        chat_key = f"chat:{user_id}"
        chat_entry = {"message": message, "response": response}

        # Append new chat to the list
        self.client.rpush(chat_key, json.dumps(chat_entry))

        # Limit stored chats to last 20 messages
        self.client.ltrim(chat_key, -20, -1)

    def get_chat_history(self, user_id, limit=5):
        """Retrieves last N chat messages for context."""
        chat_key = f"chat:{user_id}"
        chat_history = self.client.lrange(chat_key, -limit, -1)
        return [json.loads(chat) for chat in chat_history] if chat_history else []

    def clear_chat_history(self, user_id):
        """Clears chat history for a user."""
        chat_key = f"chat:{user_id}"
        self.client.delete(chat_key)
