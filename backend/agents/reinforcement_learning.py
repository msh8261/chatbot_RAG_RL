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

import os
import sys
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from datetime import datetime, timedelta
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from backend.utils.logger import logger


# ✅ Custom Chatbot Environment for RL
class ChatbotEnv(gym.Env):
    """Custom Gym environment for training an RL-based chatbot."""

    def __init__(self, training_data):
        super(ChatbotEnv, self).__init__()

        # Define action and observation spaces
        self.action_space = spaces.Discrete(
            2
        )  # 0 = Negative response, 1 = Positive response
        self.observation_space = spaces.Box(
            low=0, high=1000, shape=(1,), dtype=np.float32
        )

        # Load training data
        self.training_data = training_data
        self.current_index = 0

    def reset(self):
        """Reset the environment."""
        try:
            self.current_index = 0
            return np.array([self.training_data[self.current_index]])
        except Exception as e:
            logger.error(f"Error resetting ChatbotEnv: {e}")
            return np.array([0])

    def step(self, action):
        """Take an action and return the next state, reward, done, and info."""
        try:
            reward = (
                1 if action == 1 else -1
            )  # Assign reward based on positive or negative response

            # Move to the next training sample
            self.current_index += 1
            done = self.current_index >= len(self.training_data)

            if done:
                next_state = np.array([0])
            else:
                next_state = np.array([self.training_data[self.current_index]])

            return next_state, reward, done, {}
        except Exception as e:
            logger.error(f"Error in ChatbotEnv step: {e}")
            return np.array([0]), 0, True, {}


class ChatbotRLAgent:
    def __init__(self, database_client):
        """
        Initialize the RL agent, fetch training data, and set up the model.
        """
        try:
            self.database_client = database_client

            # Load training data from PostgreSQL
            training_data = self.load_training_data()

            # ✅ Ensure PPO has a valid environment
            self.env = DummyVecEnv([lambda: ChatbotEnv(training_data)])
            self.model = PPO("MlpPolicy", self.env, verbose=1)
        except Exception as e:
            logger.error(f"Error initializing ChatbotRLAgent: {e}")

    def load_training_data(self):
        """
        Load feedback data from PostgreSQL, apply time-based weighting, and prepare RL training data.
        """
        try:
            query = "SELECT user_input, response, reward, timestamp FROM feedback"
            data = self.database_client.fetch_all(query)

            if not data:
                return [1]  # Dummy input if no data is available

            df = pd.DataFrame(
                data, columns=["user_input", "response", "reward", "timestamp"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["time_weight"] = df["timestamp"].apply(self.calculate_time_weight)
            df["adjusted_reward"] = df["reward"] * df["time_weight"]

            return np.array([self.embed_text(text) for text in df["user_input"]])
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return [1]

    def calculate_time_weight(self, timestamp):
        """
        Assign higher weights to recent feedback, decaying over time.
        """
        try:
            now = datetime.now()
            delta_days = (now - timestamp).days
            decay_factor = 0.95**delta_days  # Exponential decay
            return max(decay_factor, 0.1)  # Ensure a minimum weight of 0.1
        except Exception as e:
            logger.error(f"Error calculating time weight: {e}")
            return 0.1

    def embed_text(self, text):
        """Convert text to embeddings (simple length-based encoding for now)."""
        try:
            return len(text)
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            return 0

    def train_model(self, timesteps=10000):
        """Train the RL model using chatbot interactions."""
        try:
            self.model.learn(total_timesteps=timesteps)
            self.model.save("chatbot_rl_model")
        except Exception as e:
            logger.error(f"Error training model: {e}")

    def get_best_action(self, observation):
        """Predict the best chatbot action based on trained RL model."""
        try:
            observation = np.array(
                [float(len(observation))]
            )  # Ensure the observation is a float array
            action, _ = self.model.predict(observation)
            return "positive" if action == 1 else "negative"
        except Exception as e:
            logger.error(f"Error getting best action: {e}")
            return "negative"
