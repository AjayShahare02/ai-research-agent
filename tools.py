import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()

tavily_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_key) if tavily_key else None


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic."""
    if not tavily:
        return "Error: TAVILY_API_KEY is not set."

    try:
        results = tavily.search(query=query, max_results=5)
        out = []
        for r in results.get("results", []):
            out.append(
                f"Title: {r.get('title', 'N/A')}\n"
                f"URL: {r.get('url', 'N/A')}\n"
                f"Snippet: {r.get('content', '')[:300]}\n"
            )
        return "\n----\n".join(out) if out else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, timeout=10, headers=headers)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return text[:3000] if text else "Page contained no readable text."
    except Exception as e:
        return f"Could not scrape URL '{url}': {str(e)}"