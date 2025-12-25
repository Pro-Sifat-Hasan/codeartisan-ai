from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict
from langchain_core.tools import tool # type: ignore

@tool
def search_files(
    root_path: str,
    query: str,
    *,
    min_score: float = 0.6,
    include_dirs: bool = False,
) -> List[Dict[str, str | float]]:
    """
    Find files by name using fuzzy matching.

    Args:
        root_path (str): Directory to search recursively
        query (str): Search query (partial or fuzzy name)
        min_score (float): Minimum similarity score (0.0 – 1.0)
        include_dirs (bool): Whether to include directories in results

    Returns:
        List[dict]: Matching files with similarity score
    """

    root = Path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    results: List[Dict[str, str | float]] = []

    query_lower = query.lower()

    for path in root.rglob("*"):
        if path.is_dir() and not include_dirs:
            continue

        name = path.name.lower()

        score = SequenceMatcher(None, query_lower, name).ratio()

        if score >= min_score:
            results.append({
                "path": str(path),
                "name": path.name,
                "score": round(score, 3),
            })

    # Best matches first
    results.sort(key=lambda x: x["score"], reverse=True)

    return results