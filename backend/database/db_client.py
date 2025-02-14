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

from backend.database.db import Feedback, SessionLocal
from backend.utils.logger import logger


class DatabaseClient:
    def __init__(self):
        """Initialize SQL client."""
        try:
            self.db = SessionLocal()
        except Exception as e:
            logger.error(f"Error initializing DatabaseClient: {e}")

    def insert_feedback(self, feedback_data: dict):
        """Insert user feedback into the database."""
        try:
            feedback = Feedback(
                user_id=feedback_data["user_id"],
                query=feedback_data["query"],
                response=feedback_data["response"],
                feedback=feedback_data["feedback"],
            )
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            return feedback
        except Exception as e:
            logger.error(f"Error inserting feedback: {e}")
            return None

    def fetch_all(self, query):
        """Fetch all records from the feedback table."""
        try:
            return self.db.query(Feedback).all()
        except Exception as e:
            logger.error(f"Error fetching all feedback: {e}")
            return []
