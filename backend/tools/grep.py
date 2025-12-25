from pathlib import Path
import re
from typing import List, Dict, Union, Iterable



def grep(
    pattern: str,
    *,
    root_path: str | None = None,
    files: Union[str, List[str], None] = None,
    use_regex: bool = False,
    case_sensitive: bool = True,
    file_extensions: List[str] | None = None,
) -> List[Dict[str, Union[str, int]]]:

    """
    Search for exact keywords or regex patterns within files.

    Args:
        root_path (str): Root directory or file to search
        files (str | list[str] | None): Specific file(s) to search
        pattern (str): Keyword or regex pattern
        use_regex (bool): Whether pattern is a regex
        file_extensions (list[str] | None): Limit search to extensions (e.g. ['.py'])
        case_sensitive (bool): Case-sensitive search

    Returns:
        List[dict]: Matches with file path, line number, and line content
    """

    if not root_path and not files:
        raise ValueError("Either root_path or files must be provided")

    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern if use_regex else re.escape(pattern), flags)

    results: List[Dict[str, Union[str, int]]] = []

    def iter_files() -> Iterable[Path]:
        if files:
            if isinstance(files, str):
                yield Path(files)
            else:
                for f in files:
                    yield Path(f)
        else:
            root = Path(root_path)
            if not root.exists():
                raise FileNotFoundError(f"Path not found: {root}")
            yield from root.rglob("*")

    for file in iter_files():
        if not file.exists() or not file.is_file():
            continue

        if file_extensions and file.suffix not in file_extensions:
            continue

        try:
            with file.open("r", encoding="utf-8", errors="ignore") as f:
                for line_number, line in enumerate(f, start=1):
                    if regex.search(line):
                        results.append({
                            "file": str(file),
                            "file_name": file.name,
                            "line_number": line_number,
                            "line": line.rstrip()
                        })
        except OSError:
            continue

    return results