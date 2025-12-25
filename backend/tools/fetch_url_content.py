import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore


def fetch_url_content(url: str, *, timeout: int = 15) -> str:
    """
    Fetch and extract the full readable text content from a URL.

    Args:
        url (str): Web page URL
        timeout (int): Request timeout in seconds

    Returns:
        str: Cleaned textual content of the page
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup([
        "script",
        "style",
        "noscript",
        "header",
        "footer",
        "nav",
        "aside",
        "form",
        "iframe",
    ]):
        tag.decompose()

    # Prefer main/article content if present
    main = soup.find("main") or soup.find("article") or soup.body
    if not main:
        return ""

    text = main.get_text(separator="\n")

    # Normalize whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)