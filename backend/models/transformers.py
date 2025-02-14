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

import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from backend.utils.logger import logger


class TransformerModel:
    def __init__(self, model_name: str, device: str = None):
        """Load pre-trained Hugging Face Transformer model and tokenizer."""
        try:
            self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name).to(
                self.device
            )
        except Exception as e:
            logger.error(f"Error initializing TransformerModel: {e}")
            raise RuntimeError("Failed to load Transformer model.")

    def get_embedding(self, text):
        try:
            inputs = self.tokenizer(
                text, return_tensors="pt", padding=True, truncation=True
            ).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Use the correct attribute for embeddings
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy().tolist()

            if isinstance(embedding, list) and isinstance(embedding[0], list):
                return embedding[0]  # Ensure it's a flat list
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None  # Return None instead of an empty list to indicate failure

    def get_response(self, prompt: str) -> str:
        try:
            inputs = self.tokenizer(
                prompt, return_tensors="pt", padding=True, truncation=True
            ).to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(**inputs)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Error generating response"
