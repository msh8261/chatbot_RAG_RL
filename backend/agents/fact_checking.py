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

from backend.services.search_api import GoogleSearchAPI


def fact_check(response: str, search_api: GoogleSearchAPI) -> str:
    """
    Validate the generated response using Google Search API.
    """
    # Perform web search for response validation
    search_results = search_api.search(response)

    # Compare response with top search results
    validated_response = (
        response
        if any(response in result for result in search_results)
        else "Response needs verification."
    )

    return validated_response
