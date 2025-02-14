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

import shap
from backend.models.transformers import TransformerModel


def explain_response(model: TransformerModel, query: str, knowledge: list):
    """
    Use SHAP to explain the model's response generation process.
    """
    # Prepare input for SHAP
    explainer = shap.Explainer(model.generate)
    shap_values = explainer([query] + knowledge)

    return shap_values
