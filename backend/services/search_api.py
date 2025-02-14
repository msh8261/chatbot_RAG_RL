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

import requests
from bs4 import BeautifulSoup


class DuckDuckGoSearchAPI:
    def search(self, query: str):
        """Perform a web search using DuckDuckGo (no API key required)."""
        url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get(url)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result__title"):
            title = result.text.strip()
            link = result.a["href"]
            results.append({"title": title, "link": link})

        return results


class GoogleSearchAPI:
    def __init__(self, api_key: str, cx: str):
        """Initialize Google Search API client with API key and search engine ID."""
        self.api_key = api_key
        self.cx = cx

    def search(self, query: str):
        """Perform a web search using Google Custom Search JSON API."""
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={self.api_key}&cx={self.cx}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
