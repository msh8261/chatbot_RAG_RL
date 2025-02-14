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


def store_feedback(user_id, user_input, response, user_feedback, postgres_client):
    """
    Store user feedback in PostgreSQL and assign rewards for RL training.
    """
    reward = 0  # Default reward

    # Assign reward values
    if "good" in user_feedback.lower() or "helpful" in user_feedback.lower():
        reward = 1
    elif "bad" in user_feedback.lower() or "incorrect" in user_feedback.lower():
        reward = -1
    else:
        reward = 0  # Neutral feedback

    # Store in PostgreSQL
    query = """
    INSERT INTO feedback (user_id, user_input, response, feedback, reward, timestamp)
    VALUES (%s, %s, %s, %s, %s, NOW())
    """
    values = (user_id, user_input, response, user_feedback, reward)

    postgres_client.execute_query(query, values)
