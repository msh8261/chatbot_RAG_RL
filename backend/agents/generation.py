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

from backend.models.transformers import TransformerModel
from backend.utils.logger import logger
import groq


def generate_response(
    query: str, knowledge: list, transformer_model: TransformerModel
) -> str:
    """
    Generate a response using a Groq LLM with the retrieved knowledge.
    """
    try:
        # Ensure knowledge is formatted as a string
        context = (
            "\n".join(knowledge) if knowledge else "No additional context available."
        )

        # Construct the prompt (adjust format based on model behavior)
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"

        # Generate response using the transformer model
        response = transformer_model.get_response(
            prompt
        )  # Ensure TransformerModel supports `get_response`

        return response
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Error generating response"


def generate_response_llm(prompt, model, api_key, temperature=0.1, max_tokens=256):
    """
    Generate a response using the Groq API asynchronously for better performance.
    """
    try:
        client = groq.Client(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.choices:
            result = response.choices[0].message.content.strip()
            logger.info(f"Generated response: {result}")
            return result
    except Exception as e:
        logger.error(f"Unexpected error in Groq API call: {str(e)}")
        return None
