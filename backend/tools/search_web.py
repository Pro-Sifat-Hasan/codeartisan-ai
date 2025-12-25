import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from typing import List, Dict
from urllib.parse import unquote


def search_web(
    query: str,
    *,
    max_results: int = 5,
    timeout: int = 10,
) -> List[Dict[str, str]]:
    """
    Perform a free web search using DuckDuckGo (no API required).

    Args:
        query (str): Search query
        max_results (int): Max number of results to return
        timeout (int): Request timeout in seconds

    Returns:
        List[dict]: Search results with title, url, and snippet
    """

    url = "https://duckduckgo.com/html/"
    params = {
        "q": query,
        "kl": "us-en"
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results: List[Dict[str, str]] = []

    for result in soup.select("div.result"):
        if len(results) >= max_results:
            break

        link = result.select_one("a.result__a")
        snippet = result.select_one("a.result__snippet, div.result__snippet")

        if not link:
            continue

        href = link.get("href", "")

        # DuckDuckGo wraps URLs like /l/?uddg=ENCODED_URL
        if "uddg=" in href:
            href = unquote(href.split("uddg=")[-1])

        results.append({
            "title": link.get_text(strip=True),
            "url": href,
            "snippet": snippet.get_text(strip=True) if snippet else ""
        })

    return results